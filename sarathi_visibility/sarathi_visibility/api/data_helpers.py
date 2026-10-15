"""DASH-006: explicit, bounded read contracts; no transactions or metric formulas."""

from dataclasses import dataclass
from datetime import date
import json
import re
from functools import wraps

import frappe
from frappe.utils import add_days

from sarathi_visibility.api.access import (
	allowed_fields, check_record, check_shop_job, deny, has_capability, require_session,
)


@dataclass(frozen=True)
class Resource:
	doctype: str
	fields: tuple
	filters: tuple = ()
	date_field: str | None = None
	company: bool = False
	label: str = "name"


# Server-owned field/DocType expressions only. Shared masters deliberately have no Company filter.
RESOURCES = {
	"projects": Resource("Project", ("name", "project_name", "company", "customer", "status", "expected_start_date"), ("customer", "status", "docstatus"), "expected_start_date", True, "project_name"),
	"work_orders": Resource("Work Order", ("name", "company", "project", "status", "production_item", "qty", "produced_qty", "planned_start_date"), ("project", "status", "docstatus"), "planned_start_date", True),
	"job_cards": Resource("Job Card", ("name", "company", "project", "work_order", "workstation", "operation", "status", "posting_date", "total_completed_qty"), ("project", "work_order", "workstation", "status", "docstatus"), "posting_date", True),
	"warehouses": Resource("Warehouse", ("name", "warehouse_name", "company", "is_group"), ("is_group",), company=True, label="warehouse_name"),
	"customers": Resource("Customer", ("name", "customer_name"), label="customer_name"),
	"companies": Resource("Company", ("name",), label="name"),
	"workstations": Resource("Workstation", ("name", "status"), ("status",)),
}
LINKS = {"company": "Company", "customer": "Customer", "project": "Project", "work_order": "Work Order", "workstation": "Workstation"}
MAX_PAGE_SIZE = 100
MAX_OFFSET = 100_000


class DashboardReadError(Exception):
	http_status_code = 500


def read_errors(fn):
	"""Use Frappe's supported per-request traceback suppression; sanitize internal errors."""
	@wraps(fn)
	def guarded(*args, **kwargs):
		frappe.local.flags.disable_traceback = True
		try:
			require_session()
			return fn(*args, **kwargs)
		except (frappe.PermissionError, frappe.ValidationError, DashboardReadError):
			raise
		except Exception:
			frappe.log_error(title="Sarathi dashboard read failed", message=frappe.get_traceback())
			frappe.throw("Could not load dashboard records. Please try again later.", DashboardReadError)
	return guarded


def invalid(message="Invalid dashboard query."):
	frappe.throw(message, frappe.ValidationError)


def pagination(start=0, page_length=25):
	"""Strict integers (including HTTP integer strings), bounded offset and limit."""
	def number(value, minimum, maximum):
		if isinstance(value, bool) or not isinstance(value, (str, int)) or len(str(value)) > 6 or not re.fullmatch(r"[0-9]+", str(value)):
			invalid("Pagination must use whole numbers.")
		result = int(value)
		if not minimum <= result <= maximum:
			invalid("Pagination is outside the supported range.")
		return result
	return number(start, 0, MAX_OFFSET), number(page_length, 1, MAX_PAGE_SIZE)


def _resource(resource):
	require_session()
	if not (has_capability("owner") or has_capability("production")):
		deny()
	if not isinstance(resource, str) or resource not in RESOURCES:
		invalid("Unsupported dashboard resource.")
	spec = RESOURCES[resource]
	if not frappe.has_permission(spec.doctype, "read"):
		deny()
	return spec


def _identifier(value):
	if not isinstance(value, str) or not value.strip() or len(value) > 140 or any(ord(c) < 32 for c in value):
		invalid("Invalid record identifier.")
	return value


def _company(value=None):
	"""A unique readable Company may be selected; never pick the first of many."""
	if value is not None:
		_identifier(value)
	filters = {"name": value} if value is not None else {}
	rows = frappe.get_list("Company", filters=filters, fields=["name"], order_by="name asc", page_length=2)
	if not rows:
		deny()
	if len(rows) != 1:
		invalid("Select an authorized Company before requesting records.")
	check_record("Company", rows[0].name)
	return rows[0].name


def _parse(filters):
	if filters is None:
		return {}
	if isinstance(filters, str):
		if len(filters) > 4096:
			invalid("Dashboard filters are too large.")
		try:
			filters = json.loads(filters)
		except (ValueError, TypeError):
			invalid("Invalid dashboard filters.")
	if not isinstance(filters, dict) or any(not isinstance(k, str) for k in filters):
		invalid("Filters must be an object.")
	return dict(filters)


def _date(value):
	if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
		invalid("Dates must use YYYY-MM-DD.")
	try:
		date.fromisoformat(value)
	except ValueError:
		invalid("Invalid calendar date.")
	return value


def validated_filters(spec, filters=None):
	"""Trusted Resource declaration, untrusted scalar filters -> native filter conditions."""
	values = _parse(filters)
	allowed = {"name", *spec.filters}
	if spec.company:
		allowed.add("company")
	if spec.date_field:
		allowed.update(("from_date", "to_date"))
	if set(values) - allowed:
		invalid("This resource does not support one or more requested filters.")
	values = {k: v for k, v in values.items() if v is not None and v != ""}
	meta = frappe.get_meta(spec.doctype)
	permitted = allowed_fields(spec.doctype)
	conditions = []
	if spec.company:
		values["company"] = _company(values.get("company"))
	for key, value in values.items():
		if key in ("from_date", "to_date"):
			_date(value)
			continue
		if key not in permitted:
			deny()
		if key not in ("name", "docstatus") and not meta.has_field(key):
			invalid("This filter is unavailable in the installed configuration.")
		if key in LINKS or key == "name":
			_identifier(value)
			doc = check_record(LINKS.get(key, spec.doctype), value)
			if spec.company and doc.meta.has_field("company") and doc.get("company") != values["company"]:
				deny()
		elif key in ("docstatus", "is_group"):
			valid = (0, 1, 2) if key == "docstatus" else (0, 1)
			if isinstance(value, bool) or not isinstance(value, (int, str)) or str(value) not in {str(v) for v in valid}:
				invalid("Invalid document status or group flag.")
			value = int(value)
		elif key == "status":
			field = meta.get_field("status")
			if not isinstance(value, str) or field.fieldtype != "Select" or value not in (field.options or "").splitlines():
				invalid("Unsupported status for this resource.")
		conditions.append([key, "=", value])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("From date must be on or before To date.")
	if spec.date_field and (values.get("from_date") or values.get("to_date")):
		field = meta.get_field(spec.date_field)
		if not field or spec.date_field not in permitted:
			deny()
		if values.get("from_date"):
			conditions.append([spec.date_field, ">=", values["from_date"]])
		if values.get("to_date"):
			try:
				end = add_days(values["to_date"], 1) if field.fieldtype == "Datetime" else values["to_date"]
			except (ValueError, OverflowError):
				invalid("Date range is outside the supported calendar.")
			conditions.append([spec.date_field, "<" if field.fieldtype == "Datetime" else "<=", end])
	# Reject incompatible linked scopes, even when each individual link is readable.
	if values.get("project") and values.get("work_order"):
		if check_record("Work Order", values["work_order"]).get("project") != values["project"]:
			deny()
	return conditions, values


def _selection(spec):
	meta = frappe.get_meta(spec.doctype)
	permitted = allowed_fields(spec.doctype)
	fields = [f for f in spec.fields if f in permitted and (f == "name" or meta.has_field(f))]
	if "name" not in fields:
		deny()
	return fields


def _ordering(spec, fields, sort_by, sort_direction):
	if not isinstance(sort_by, str) or sort_by not in fields:
		invalid("Unsupported sorting field.")
	if sort_direction not in ("asc", "desc"):
		invalid("Sort direction must be asc or desc.")
	return f"{sort_by} {sort_direction}" + (", name asc" if sort_by != "name" else "")


def _extra(extra):
	# Frappe v1 passes its dispatcher command through **kwargs. It is not a query field.
	extra.pop("cmd", None)
	extra.pop("_", None)  # Browser GET cache-buster, never used in data selection.
	if extra:
		invalid("Unsupported dashboard query parameters.")


@frappe.whitelist(methods=["GET"])
@read_errors
def get_records(resource, filters=None, start=0, page_length=25, sort_by="name", sort_direction="asc", **extra):
	_extra(extra)
	spec = _resource(resource)
	start, length = pagination(start, page_length)
	conditions, applied = validated_filters(spec, filters)
	fields = _selection(spec)
	order = _ordering(spec, fields, sort_by, sort_direction)
	rows = frappe.get_list(spec.doctype, filters=conditions, fields=fields, order_by=order, start=start, page_length=length + 1)
	return {"rows": rows[:length], "start": start, "page_length": length, "has_next": len(rows) > length, "applied_filters": applied}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_record(resource, name, filters=None, **extra):
	_extra(extra)
	values = _parse(filters)
	if "name" in values and values["name"] != name:
		invalid("Conflicting record identifiers.")
	values["name"] = _identifier(name)
	result = get_records(resource, values, page_length=1)
	if not result["rows"]:
		deny()
	return result["rows"][0]


@frappe.whitelist(methods=["GET"])
@read_errors
def get_options(resource, filters=None, search="", start=0, page_length=25, **extra):
	_extra(extra)
	spec = _resource(resource)
	start, length = pagination(start, page_length)
	if not isinstance(search, str) or len(search) > 140 or any(ord(c) < 32 for c in search):
		invalid("Invalid option search.")
	conditions, applied = validated_filters(spec, filters)
	fields = _selection(spec)
	label = spec.label if spec.label in fields else "name"
	if search:
		# Escape LIKE metacharacters; values remain ORM parameters, never SQL fragments.
		term = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
		conditions.append([label, "like", "%" + term + "%"])
	rows = frappe.get_list(spec.doctype, filters=conditions, fields=list(dict.fromkeys(("name", label))), order_by=f"{label} asc, name asc" if label != "name" else "name asc", start=start, page_length=length + 1)
	return {"options": [{"value": r.name, "label": r.get(label) or r.name} for r in rows[:length]], "start": start, "page_length": length, "has_next": len(rows) > length, "applied_filters": applied}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_count(resource, filters=None, **extra):
	_extra(extra)
	spec = _resource(resource)
	conditions, applied = validated_filters(spec, filters)
	_selection(spec)
	rows = frappe.get_list(spec.doctype, filters=conditions, fields=[{"COUNT": "name", "as": "total"}], page_length=1)
	return {"count": int(rows[0].total) if rows else 0, "applied_filters": applied}


def get_shop_job(name):
	"""Internal read helper only; preserves DASH-003 assignment/team and native checks."""
	job = check_shop_job(_identifier(name), "read")
	fields = _selection(RESOURCES["job_cards"])
	return {field: job.get(field) for field in fields}
