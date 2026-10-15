"""Shared, permission-aware discovery of the installed Frappe navigation and schema.

No stored copy of the ERPNext module list. Native screens handle writes and specialised
workflows; this endpoint only supplies metadata and read-only previews.
"""
import hashlib
import importlib
import json
from urllib.parse import quote, urlencode, urlsplit

import frappe
from sarathi_visibility.api.access import check_record, authorized, FINANCIAL_DOCTYPES, MONEY_FIELDS, can_finance, deny
from frappe.utils import cint, now

SCALAR_TYPES = {
	"Data",
	"Link",
	"Dynamic Link",
	"Select",
	"Date",
	"Datetime",
	"Time",
	"Currency",
	"Float",
	"Int",
	"Percent",
	"Check",
	"Small Text",
	"Text",
	"Long Text",
	"Read Only",
	"Duration",
	"Color",
	"Phone",
	"Autocomplete",
}
LAYOUT_TYPES = {"Tab Break", "Section Break", "Column Break"}
RECURSIVE_PAGES = {"sarathiownertower", "sarathicontroltower"}


def _require_desk():
	if (
		frappe.session.user == "Guest"
		or frappe.get_cached_value("User", frappe.session.user, "user_type") != "System User"
	):
		frappe.throw("A signed-in Desk user is required.", frappe.PermissionError)


def versions():
	return {
		app: getattr(importlib.import_module(app), "__version__", "unknown")
		for app in frappe.get_installed_apps()
	}


def _revision():
	state = {"versions": versions()}
	for dt in (
		"Workspace Sidebar",
		"Workspace Sidebar Item",
		"Desktop Icon",
		"Workspace",
		"DocType",
		"Custom Field",
		"Property Setter",
		"Report",
		"Custom Role",
		"Role Permission for Page and Report",
		"Has Role",
		"DocPerm",
		"Custom DocPerm",
		"User Permission",
		"User",
		"Role",
		"Module Profile",
		"Block Module",
		"Active Domain",
		"Page",
		"Module Def",
		"User Type",
	):
		if frappe.db.exists("DocType", dt) and frappe.db.table_exists(dt):
			latest = frappe.get_all(dt, fields=["modified"], order_by="modified desc", limit_page_length=1)
			state[dt] = [frappe.db.count(dt), str(latest[0].modified) if latest else None]
	state["user"] = frappe.session.user
	state["roles"] = sorted(frappe.get_roles())
	state["blocked"] = frappe.get_cached_doc("User", frappe.session.user).get_blocked_modules()
	return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def _options(value):
	if not value:
		return {}
	try:
		result = frappe.parse_json(value) if isinstance(value, str) else value
		return result if isinstance(result, dict) else {}
	except (TypeError, ValueError):
		return {}


def _route(item):
	target, kind = item.get("link_to"), item.get("link_type")
	if kind == "DocType" and target:
		route = "/desk/" + quote(target.lower().replace(" ", "-"), safe="-")
	elif kind == "Report" and target:
		report_type = frappe.db.get_value("Report", target, "report_type")
		if report_type == "Report Builder":
			dt = frappe.db.get_value("Report", target, "ref_doctype")
			route = (
				"/desk/"
				+ quote(dt.lower().replace(" ", "-"), safe="-")
				+ "/view/report/"
				+ quote(target, safe="")
			)
		else:
			route = "/desk/query-report/" + quote(target, safe="") + "?ignore_prepared_report=1"
	elif kind == "Page" and target and target not in RECURSIVE_PAGES:
		route = "/desk/" + quote(target, safe="-")
	elif kind == "Workspace" and target:
		route = "/desk/" + quote(target.lower().replace(" ", "-"), safe="-")
	elif kind == "Dashboard" and target:
		route = "/desk/dashboard-view/" + quote(target, safe="")
	elif kind == "URL":
		route = item.get("url") or ""
		parsed = urlsplit(route)
		if parsed.scheme or parsed.netloc or not route.startswith(("/desk/", "/app/")) or "\\" in route:
			return None
		if any(name in route for name in RECURSIVE_PAGES):
			return None
	else:
		return None
	options = {**_options(item.get("filters")), **_options(item.get("route_options"))}
	if options:
		route += ("&" if "?" in route else "?") + urlencode(
			{k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in options.items()}
		)
	return route


def _build_modules():
	# Reuse native v16 filtering, including workspace roles, domains and personal sidebars.
	from frappe.boot import get_sidebar_items
	from frappe.desk.desk_views import DeskViews
	from frappe.desk.desktop import get_workspaces

	workspaces = [p["name"] for p in get_workspaces()["pages"]]
	sidebars = get_sidebar_items(workspaces)
	private = {
		s.name.lower(): s.for_user
		for s in frappe.get_all("Workspace Sidebar", fields=["name", "for_user"])
		if s.for_user
	}
	blocked = set(frappe.get_cached_doc("User", frappe.session.user).get_blocked_modules())
	allowed_reports = DeskViews.get_allowed_reports(cache=False)
	icons = {
		d.name: d
		for d in frappe.get_all(
			"Desktop Icon", fields=["name", "parent_icon", "icon", "app", "idx", "hidden"], order_by="idx asc"
		)
	}
	modules = []
	for key, sidebar in sidebars.items():
		if key in private and private[key] != frappe.session.user:
			continue
		if sidebar.get("module") in blocked:
			continue
		entries, section = [], ""
		for item in sidebar["items"]:
			if item.get("type") == "Section Break":
				section = item.get("label") or ""
				continue
			kind, target = item.get("link_type"), item.get("link_to")
			if kind == "Page" and target in RECURSIVE_PAGES:
				continue
			if kind == "DocType" and (
				not target
				or not frappe.db.exists("DocType", target)
				or not frappe.has_permission(target, "read")
			):
				continue
			if kind == "Report" and (
				target not in allowed_reports or frappe.db.get_value("Report", target, "disabled")
			):
				continue
			route = _route(item)
			entry = {
				"label": item.get("label") or target or "Untitled",
				"kind": kind,
				"target": target,
				"section": section,
				"icon": item.get("icon"),
				"route": route,
				"filters": {**_options(item.get("filters")), **_options(item.get("route_options"))},
				"mode": "native" if route else "unsupported",
			}
			if kind == "DocType" and route:
				meta = frappe.get_meta(target)
				entry["mode"] = "native" if meta.issingle or meta.is_virtual else "preview-and-native"
				entry["is_single"] = bool(meta.issingle)
			entry["id"] = hashlib.sha256(
				json.dumps([key, entry], sort_keys=True, default=str).encode()
			).hexdigest()[:24]
			entries.append(entry)
		if not entries:
			continue
		label = sidebar["label"]
		icon = icons.get(label) or {}
		modules.append(
			{
				"id": key,
				"label": label,
				"app": sidebar.get("app") or icon.get("app") or "frappe",
				"group": icon.get("parent_icon")
				or ("ERPNext" if (sidebar.get("app") or icon.get("app")) == "erpnext" else "Framework"),
				"icon": sidebar.get("header_icon") or icon.get("icon"),
				"entries": entries,
			}
		)
	return sorted(modules, key=lambda m: (m["group"], m["label"]))


def _modules():
	key = "sarathi:modules:" + _revision()
	result = frappe.cache.get_value(key)
	if result is None:
		result = _build_modules()
		frappe.cache.set_value(key, result, expires_in_sec=60)
	return result


@frappe.whitelist()
@authorized("production")
def get_catalog(known_revision=None):
	_require_desk()
	revision = _revision()
	if known_revision == revision:
		return {"unchanged": True, "revision": revision, "checked_at": now()}
	modules = _modules()
	return {
		"revision": revision,
		"versions": versions(),
		"modules": modules,
		"checked_at": now(),
		"counts": {"modules": len(modules), "entries": sum(len(m["entries"]) for m in modules)},
	}


def _entry(module, entry):
	_require_desk()
	for group in _modules():
		if group["id"] == module:
			for item in group["entries"]:
				if item["id"] == entry:
					return item
	frappe.throw(
		"This entry is no longer available or you do not have permission to view it.", frappe.PermissionError
	)


def _fields(meta, parenttype=None):
	permitted = set(meta.get_permitted_fieldnames(parenttype=parenttype, user=frappe.session.user))
	levels = set(
		meta.get_permlevel_access(permission_type="read", parenttype=parenttype, user=frappe.session.user)
	)
	permitted.update(
		f.fieldname
		for f in meta.fields
		if f.fieldtype in ("Table", "Table MultiSelect") and cint(f.permlevel) in levels
	)
	# Password/HTML/code and masked values are deliberately handled only by native controls.
	return [
		f
		for f in meta.fields
		if f.fieldname in permitted
		and not f.hidden
		and (can_finance() or (f.fieldtype != "Currency" and f.fieldname not in MONEY_FIELDS))
		and not f.get("mask")
		and f.fieldtype in SCALAR_TYPES | {"Table", "Table MultiSelect"}
	]


def _schema(meta):
	fields = {f.fieldname: f for f in _fields(meta)}
	output = []
	for f in meta.fields:
		if f.fieldname not in fields and f.fieldtype not in LAYOUT_TYPES:
			continue
		if f.hidden:
			continue
		output.append(
			{
				k: f.get(k)
				for k in (
					"fieldname",
					"label",
					"fieldtype",
					"options",
					"reqd",
					"read_only",
					"depends_on",
					"mandatory_depends_on",
					"read_only_depends_on",
				)
			}
		)
	return output


@frappe.whitelist()
@authorized("production")
def get_entry(module, entry, name=None, search="", start=0):
	item = _entry(module, entry)
	response = {"entry": item, "updated_at": now()}
	if item["kind"] != "DocType":
		return response
	dt = item["target"]
	if dt in FINANCIAL_DOCTYPES and not can_finance():
		deny()
	if not frappe.has_permission(dt, "read"):
		frappe.throw("Read access is required.", frappe.PermissionError)
	meta = frappe.get_meta(dt)
	fields = _fields(meta)
	response.update(
		{
			"schema": _schema(meta),
			"permissions": {
				p: bool(frappe.has_permission(dt, p)) for p in ("read", "create", "write", "submit", "cancel")
			},
		}
	)
	if meta.is_virtual:
		return response
	if name or meta.issingle:
		doc = check_record(dt, name or dt)
		doc.apply_fieldlevel_read_permissions()
		response["name"] = doc.name
		response["values"] = {
			f.fieldname: doc.get(f.fieldname) for f in fields if f.fieldtype in SCALAR_TYPES
		}
		tables = []
		for f in fields:
			if f.fieldtype not in ("Table", "Table MultiSelect") or not f.options:
				continue
			child_fields = [
				c for c in _fields(frappe.get_meta(f.options), parenttype=dt) if c.fieldtype in SCALAR_TYPES
			]
			rows = doc.get(f.fieldname) or []
			tables.append(
				{
					"label": f.label,
					"columns": [
						{"fieldname": c.fieldname, "label": c.label, "fieldtype": c.fieldtype}
						for c in child_fields
					],
					"rows": [{c.fieldname: r.get(c.fieldname) for c in child_fields} for r in rows[:100]],
					"total": len(rows),
				}
			)
		response["tables"] = tables
		return response
	names = {f.fieldname for f in fields if f.fieldtype in SCALAR_TYPES}
	candidates = [meta.title_field] + [f.fieldname for f in fields if f.in_list_view] + ["status", "modified"]
	selected = ["name"]
	for key in candidates:
		if key and key in names | {"modified"} and key not in selected:
			selected.append(key)
	selected = selected[:8]
	by_name = {f.fieldname: f for f in fields}
	response["columns"] = [
		{
			"fieldname": key,
			"label": by_name[key].label if key in by_name else key.title(),
			"fieldtype": by_name[key].fieldtype if key in by_name else "Data",
		}
		for key in selected
	]
	allowed_filter_names = names | {"name", "docstatus", "modified", "owner"}
	filters = {k: v for k, v in item["filters"].items() if k in allowed_filter_names}
	or_filters = (
		[
			[dt, key, "like", "%" + str(search)[:100] + "%"]
			for key in dict.fromkeys(["name", meta.title_field if meta.title_field in names else "name"])
		]
		if search
		else None
	)
	offset = max(0, cint(start))
	rows = frappe.get_list(
		dt,
		fields=selected,
		filters=filters,
		or_filters=or_filters,
		limit_start=offset,
		limit_page_length=26,
		order_by="modified desc",
	)
	response.update({"rows": rows[:25], "start": offset, "has_more": len(rows) > 25})
	return response


def broadcast_change(doc=None, method=None):
	metadata = {
		"Workspace",
		"Workspace Sidebar",
		"Workspace Sidebar Item",
		"Desktop Icon",
		"DocType",
		"Custom Field",
		"Property Setter",
		"Report",
		"Role",
		"User",
		"Custom DocPerm",
		"Custom Role",
		"User Permission",
		"Module Profile",
		"Domain Settings",
		"Page",
		"Module Def",
		"User Type",
	}
	event = "sarathi_catalog_changed" if doc and doc.doctype in metadata else "sarathi_records_changed"
	frappe.publish_realtime(event, {}, after_commit=True)


def after_migrate():
	frappe.publish_realtime("sarathi_catalog_changed", {}, after_commit=True)


def inventory():
	"""Read-only upgrade/audit manifest, invoked by bench execute as Administrator."""
	frappe.only_for("System Manager")
	catalog = get_catalog()
	doctypes = sorted(
		{e["target"] for m in catalog["modules"] for e in m["entries"] if e["kind"] == "DocType"}
	)
	catalog["schema_manifest"] = {}
	for dt in doctypes:
		meta = frappe.get_meta(dt)
		catalog["schema_manifest"][dt] = {
			"module": meta.module,
			"single": bool(meta.issingle),
			"virtual": bool(meta.is_virtual),
			"fields": [
				{
					"name": f.fieldname,
					"type": f.fieldtype,
					"options": f.options,
					"required": bool(f.reqd),
					"read_only": bool(f.read_only),
				}
				for f in meta.fields
			],
		}
	return catalog
