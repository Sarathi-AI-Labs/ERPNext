"""Dashboard capabilities layered on native Frappe permissions, never replacing them."""

from contextvars import ContextVar
from functools import wraps
import inspect
import re

import frappe
from frappe.model import get_permitted_fields
from frappe.utils import getdate

OWNER_ROLES = {"Sarathi Owner", "System Manager"}
PRODUCTION_ROLES = {"Manufacturing Manager", "Sarathi Super Admin", "System Manager", "Sarathi Owner"}
SHOP_ROLES = {"Sarathi Supervisor", "Sarathi Operator"}
FINANCE_ROLES = {"Sarathi Owner", "Accounts Manager", "Accounts User", "Auditor", "System Manager"}
FINANCIAL_DOCTYPES = {
	"GL Entry",
	"Account",
	"Cost Center",
	"Budget",
	"Budget Account",
	"Sales Invoice",
	"Sales Invoice Item",
	"Purchase Invoice",
	"Purchase Invoice Item",
	"Payment Entry",
	"Payment Entry Reference",
	"Journal Entry",
	"Bank Account",
	"Bank Transaction",
	"Bank Guarantee",
	"Shareholder",
	"Share Transfer",
	"Subscription",
	"Subscription Plan",
}
MONEY_FIELDS = {
	"rate",
	"amount",
	"stock_value",
	"valuation_rate",
	"grand_total",
	"net_total",
	"outstanding_amount",
	"advance_paid",
	"estimated_costing",
	"total_costing_amount",
	"total_billed_amount",
	"total_sales_amount",
	"total",
	"total_amount",
}
_request_scope = ContextVar("sarathi_permission_scope", default=None)
DENIED = "This resource or action is not available for your permissions."


def deny():
	frappe.throw(DENIED, frappe.PermissionError)


def require_session():
	if not frappe.session.user or frappe.session.user == "Guest":
		deny()
	if frappe.get_cached_value("User", frappe.session.user, "user_type") != "System User":
		deny()


def has_capability(capability, user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	if user == "Administrator":
		return True
	roles = set(frappe.get_roles(user))
	allowed = {
		"owner": OWNER_ROLES,
		"production": PRODUCTION_ROLES,
		"shop": SHOP_ROLES,
		"finance": FINANCE_ROLES,
		"admin": {"System Manager", "Sarathi Super Admin"},
	}
	return bool(roles & allowed[capability])


def require_capability(capability):
	require_session()
	if not has_capability(capability):
		deny()


def can_finance():
	return has_capability("finance")


def operational_payload(value):
	"""Remove monetary-derived fields as well as raw Currency fields for managers."""
	if can_finance():
		return value
	monetary = re.compile(
		r"(?:cost|price|amount|revenue|expense|profit|receivable|payable|budget|tax|valuation|capital|spend|financial|cash|bank|margin)",
		re.I,
	)
	extra = {
		"material_with_suppliers",
		"material_with_subcontractors",
		"material_value_at_subcontractors",
		"stock_value",
		"rate",
		"grand_total",
		"net_total",
		"material_value",
	}
	if isinstance(value, dict):
		result = type(value)(
			{k: operational_payload(v) for k, v in value.items() if not monetary.search(k) and k not in extra}
		)
		if "columns" in result:
			result["columns"] = [
				c
				for c in result["columns"]
				if c.get("fieldtype") != "Currency"
				and not monetary.search(c.get("fieldname", ""))
				and c.get("fieldname") not in extra
			]
		return result
	if isinstance(value, (list, tuple)):
		return [operational_payload(v) for v in value]
	return value


def check_record(doctype, name, permission="read"):
	"""Missing and forbidden names deliberately have the same outward error."""
	require_session()
	if not isinstance(name, str) or not name or len(name) > 140:
		deny()
	messages = list(getattr(frappe.local, "message_log", []) or [])
	try:
		doc = frappe.get_doc(doctype, name)
		doc.check_permission(permission)
		if permission != "read":
			doc.check_permission("read")
		return doc
	except (frappe.DoesNotExistError, frappe.PermissionError):
		frappe.local.message_log = messages
		deny()


def validate_filters(filters=None, **links):
	require_session()
	try:
		parsed = frappe.parse_json(filters) if isinstance(filters, str) else filters
	except (ValueError, TypeError):
		frappe.throw("Invalid dashboard filters.")
	if parsed is not None and not isinstance(parsed, dict):
		frappe.throw("Invalid dashboard filters.")
	result = dict(parsed or {})
	result.update({k: v for k, v in links.items() if v is not None})
	for field, dt in {
		"company": "Company",
		"customer": "Customer",
		"project": "Project",
		"warehouse": "Warehouse",
		"workstation": "Workstation",
		"work_order": "Work Order",
		"job_card": "Job Card",
		"supplier": "Supplier",
		"account": "Account",
		"cost_center": "Cost Center",
	}.items():
		value = result.get(field)
		if value and not (field == "customer" and value == "__unassigned__"):
			doc = check_record(dt, value)
			if (
				result.get("company")
				and doc.meta.has_field("company")
				and doc.get("company") != result["company"]
			):
				deny()
			if (
				field == "project"
				and result.get("customer")
				and (doc.get("customer") or "__unassigned__") != result["customer"]
			):
				deny()
	for field in ("from_date", "to_date"):
		if result.get(field):
			try:
				result[field] = str(getdate(result[field]))
			except (ValueError, TypeError):
				frappe.throw("Invalid dashboard date.")
	if result.get("from_date") and result.get("to_date") and result["from_date"] > result["to_date"]:
		frappe.throw("From date must be on or before To date.")
	return result


def authorized(capability):
	"""Gate direct API calls and validate named filters before any query runs."""

	def decorate(fn):
		signature = inspect.signature(fn)

		@wraps(fn)
		def guarded(*args, **kwargs):
			require_capability(capability)
			bound = signature.bind(*args, **kwargs)
			if "filters" in bound.arguments:
				bound.arguments["filters"] = validate_filters(bound.arguments["filters"])
			direct = {
				k: v
				for k, v in bound.arguments.items()
				if k in {"company", "customer", "project", "warehouse", "workstation"} and v
			}
			if direct:
				validate_filters(**direct)
			token = None
			if _request_scope.get() is None:
				token = _request_scope.set({})
			try:
				result = fn(*bound.args, **bound.kwargs)
				return operational_payload(result) if capability == "production" else result
			finally:
				if token is not None:
					_request_scope.reset(token)

		return guarded

	return decorate


def _parents(doctype):
	"""Metadata lookup only; actual parent names are obtained with get_list."""
	definitions = frappe.get_all(
		"DocField",
		filters={"options": doctype, "fieldtype": ["in", ["Table", "Table MultiSelect"]]},
		fields=["parent", "fieldname"],
	)
	definitions += frappe.get_all(
		"Custom Field",
		filters={"options": doctype, "fieldtype": ["in", ["Table", "Table MultiSelect"]]},
		fields=["dt as parent", "fieldname"],
	)
	return [(r.parent, r.fieldname) for r in definitions if frappe.db.exists("DocType", r.parent)]


def _names(doctype):
	scope = _request_scope.get()
	key = (frappe.session.user, doctype)
	if scope is not None and key in scope:
		return scope[key]
	if doctype in FINANCIAL_DOCTYPES and not can_finance():
		names = []
	elif not frappe.has_permission(doctype, "read"):
		names = []
	else:
		names = []
		start = 0
		while True:
			batch = frappe.get_list(
				doctype, fields=["name"], order_by="name asc", start=start, page_length=250
			)
			names.extend(r.name for r in batch)
			if len(batch) < 250:
				break
			start += 250
	if scope is not None:
		scope[key] = names
	return names


def _in(column, names):
	return f"`{column}` IN ({','.join(frappe.db.escape(n) for n in names)})" if names else "1=0"


def _row_condition(doctype):
	if frappe.get_meta(doctype).istable:
		clauses = [
			f"(`parenttype`={frappe.db.escape(parent)} AND `parentfield`={frappe.db.escape(field)} AND {_in('parent', _names(parent))})"
			for parent, field in _parents(doctype)
		]
		return "(" + " OR ".join(clauses) + ")" if clauses else "1=0"
	return _in("name", _names(doctype))


def allowed_fields(doctype):
	meta = frappe.get_meta(doctype)
	if meta.istable:
		parent_fields = [
			set(get_permitted_fields(doctype, parenttype=p))
			for p, _ in _parents(doctype)
			if frappe.has_permission(p, "read")
		]
		permitted = set.intersection(*parent_fields) if parent_fields else set()
	else:
		permitted = set(get_permitted_fields(doctype)) if frappe.has_permission(doctype, "read") else set()
	if not can_finance():
		permitted -= MONEY_FIELDS
		permitted -= {f.fieldname for f in meta.fields if f.fieldtype == "Currency"}
	return permitted


def scoped_sql(query, values=None, **kwargs):
	"""Scope existing read-only aggregate SQL using native permitted row IDs.

	Only the custom apps call this adapter; Frappe/ERPNext functions are untouched.
	Row identifiers are server-derived and DB-escaped, never client identifiers.
	Unknown/unsupported SQL fails closed. No formula or grouping is changed.
	"""
	require_session()
	if (
		not isinstance(query, str)
		or not re.match(r"^\s*SELECT\b", query, re.I)
		or re.search(r";|--|/\*|\b(?:UNION|INTO|OUTFILE|FOR\s+UPDATE)\b", query, re.I)
	):
		deny()
	if frappe.session.user == "Administrator":
		return frappe.db.sql(query, **kwargs) if values is None else frappe.db.sql(query, values, **kwargs)
	pattern = re.compile(
		r"\b(FROM|JOIN)\s+`tab([^`]+)`(?:\s+(?:AS\s+)?((?!(?:WHERE|ON|INNER|LEFT|RIGHT|JOIN|GROUP|ORDER|LIMIT|HAVING|UNION)\b)[a-zA-Z_]\w*))?",
		re.I,
	)
	if not pattern.search(query):
		deny()

	def table(match):
		dt = match.group(2)
		if not frappe.db.exists("DocType", dt):
			deny()
		meta = frappe.get_meta(dt)
		permitted = allowed_fields(dt)
		# NULL preserves legacy result shapes without loading forbidden fields.
		columns = [f"`{f}`" if f in permitted else f"NULL AS `{f}`" for f in meta.get_valid_columns()]
		alias = match.group(3) or f"`tab{dt}`"
		return (
			f"{match.group(1)} (SELECT {','.join(columns)} FROM `tab{dt}` WHERE {_row_condition(dt)}) {alias}"
		)

	scoped = pattern.sub(table, query)
	# Every literal tab-reference must be handled; reject unquoted sources.
	if re.search(r"\b(?:FROM|JOIN)\s+tab\w", scoped, re.I):
		deny()
	return frappe.db.sql(scoped, **kwargs) if values is None else frappe.db.sql(scoped, values, **kwargs)


def scoped_rows(doctype, *args, **kwargs):
	require_session()
	if frappe.session.user == "Administrator":
		return frappe.get_all(doctype, *args, **kwargs)
	if doctype in FINANCIAL_DOCTYPES and not can_finance():
		return []
	meta = frappe.get_meta(doctype)
	if not meta.istable and not frappe.has_permission(doctype, "read"):
		return []
	if args:
		raise TypeError("Use named query parameters for dashboard reads")
	requested = kwargs.get("fields") or ([kwargs["pluck"]] if kwargs.get("pluck") else ["name"])
	if isinstance(requested, str):
		requested = [requested]
	if requested == ["*"]:
		requested = meta.get_valid_columns()
	permitted = allowed_fields(doctype)
	selected = [f for f in requested if f in permitted]
	hidden = set(requested) - set(selected)
	if not selected:
		selected = ["name"]
	kwargs["fields"] = selected
	pluck = kwargs.pop("pluck", None)
	kwargs.setdefault("limit_page_length", 0)
	if meta.istable:
		# Reuse the same parent-authorized condition as aggregate reads.
		condition = _row_condition(doctype)
		names = [
			r.name for r in scoped_sql(f"SELECT name FROM `tab{doctype}` WHERE {condition}", as_dict=True)
		]
		filters = kwargs.pop("filters", None) or []
		if isinstance(filters, dict):
			filters = [
				[k, v[0], v[1]] if isinstance(v, (list, tuple)) else [k, "=", v] for k, v in filters.items()
			]
		kwargs["filters"] = list(filters) + [["name", "in", names or ["__none__"]]]
		result = frappe.get_all(doctype, **kwargs)
	else:
		result = frappe.get_list(doctype, **kwargs)
	for row in result:
		for field in hidden:
			row[field] = None
	return [row.get(pluck) for row in result] if pluck else result


def scoped_value(doctype, filters=None, fieldname="name", as_dict=False, **kwargs):
	fields = [fieldname] if isinstance(fieldname, str) else list(fieldname)
	if isinstance(filters, str):
		filters = {"name": filters}
	rows = scoped_rows(doctype, fields=fields, filters=filters, limit_page_length=1)
	if not rows:
		return None
	if as_dict:
		return rows[0]
	values = tuple(rows[0].get(f) for f in fields)
	return values[0] if isinstance(fieldname, str) else values


def scoped_count(doctype, filters=None, **kwargs):
	return len(scoped_rows(doctype, fields=["name"], filters=filters))


def check_shop_job(name, permission="read"):
	"""Assignment gate for future workboard callers; not a new production API."""
	require_session()
	if permission not in ("read", "write"):
		deny()
	if not (has_capability("shop") or has_capability("production")):
		deny()
	job = check_record("Job Card", name, permission)
	for dt, key in (("Company", "company"), ("Workstation", "workstation"), ("Work Order", "work_order")):
		if job.get(key):
			check_record(dt, job.get(key))
	if has_capability("production"):
		return job
	# ToDo is Frappe's native explicit assignment record. Lookup is constrained
	# to the authenticated user's identity and the already-authorized Job Card.
	assigned = frappe.db.exists(
		"ToDo",
		{
			"reference_type": "Job Card",
			"reference_name": name,
			"allocated_to": frappe.session.user,
			"status": "Open",
		},
	)
	supervisor = "Sarathi Supervisor" in frappe.get_roles()
	workstation_scope = frappe.permissions.get_user_permissions(frappe.session.user).get("Workstation", [])
	team_allowed = (
		supervisor
		and job.get("workstation")
		and any(
			r.get("doc") == job.workstation and r.get("applicable_for") in (None, "", "Job Card")
			for r in workstation_scope
		)
	)
	if not assigned and not team_allowed:
		deny()
	return job


def save_draft_changes(doctype, name, changes, allowed):
	"""Existing legacy edits stay draft-only and never perform workflow transitions."""
	from frappe.model.workflow import get_workflow_name

	doc = check_record(doctype, name, "write")
	if not isinstance(changes, dict) or not changes or set(changes) - set(allowed):
		frappe.throw("Unsupported dashboard changes.")
	# Lock only after permission checking; reload before checking state.
	frappe.db.get_value(doctype, name, "name", for_update=True)
	doc.reload()
	doc.check_permission("write")
	if doc.docstatus != 0 or get_workflow_name(doctype):
		frappe.throw("Use the authorized ERPNext workflow for this document.")
	levels = doc.meta.get_permlevel_access(permission_type="write", user=frappe.session.user)
	for field in changes:
		meta_field = doc.meta.get_field(field)
		if not meta_field or meta_field.read_only or (meta_field.permlevel or 0) not in levels:
			deny()
	if any(doc.get(k) != v for k, v in changes.items()):
		doc.update(changes)
		doc.save()
	return doc
