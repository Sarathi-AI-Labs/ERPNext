"""
DASH-016: Work Order and Job Card APIs for Production Management Control Tower.
Provides secure, permission-aware, paginated APIs for Work Order and Job Card
list and detail views, using actual ERPNext manufacturing records and verified semantics.
"""
from collections import defaultdict
from datetime import date, datetime
import math
import re

import frappe
from frappe.utils import flt, cint, getdate, now_datetime

from sarathi_visibility.api.access import (
	can_finance,
	check_record,
	deny,
	require_capability,
)
from sarathi_visibility.api.data_helpers import (
	_company,
	_date,
	_extra,
	_identifier,
	_parse,
	invalid,
	read_errors,
)
from sarathi_visibility.api.factory_overview import get_target_completion_date

# Allowlist of supported filters for Work Order list
WO_FILTER_KEYS = {
	"company",
	"from_date",
	"to_date",
	"status",
	"production_item",
	"item_code",
	"project",
	"customer",
	"workstation",
	"operation",
	"work_order",
	"search",
	"reference_at",
}

# Allowlist of supported sorting fields for Work Order list
WO_SORT_FIELDS = {
	"name",
	"modified",
	"creation",
	"planned_start_date",
	"planned_end_date",
	"expected_delivery_date",
	"status",
	"qty",
	"produced_qty",
	"production_item",
}

# Allowlist of supported filters for Job Card list
JC_FILTER_KEYS = {
	"company",
	"work_order",
	"operation",
	"workstation",
	"status",
	"from_date",
	"to_date",
	"production_item",
	"project",
	"employee",
	"search",
}

# Allowlist of supported sorting fields for Job Card list
JC_SORT_FIELDS = {
	"name",
	"modified",
	"creation",
	"expected_start_date",
	"actual_start_date",
	"for_quantity",
	"total_completed_qty",
	"status",
	"operation",
	"workstation",
}

MAX_PAGE_SIZE = 100
MAX_OFFSET = 100_000


def validate_work_order_filters(filters):
	"""Strict server-side validation for Work Order list filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - WO_FILTER_KEYS:
		invalid("Unsupported Work Order filter parameter.")

	values = {k: v for k, v in values.items() if v is not None and v != ""}

	# Resolve and validate company
	company_arg = values.get("company")
	if not company_arg:
		user_default_company = frappe.defaults.get_user_default("Company")
		if user_default_company and frappe.has_permission("Company", "read", user_default_company):
			company_arg = user_default_company
	values["company"] = _company(company_arg)

	# Validate dates
	for key in ("from_date", "to_date"):
		if key in values:
			_date(values[key])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate project link
	if values.get("project"):
		_identifier(values["project"])
		if not frappe.db.exists("Project", values["project"]):
			invalid("Selected project does not exist.")
		proj = check_record("Project", values["project"])
		if proj.company != values["company"]:
			deny()
		if values.get("customer") and proj.customer != values["customer"]:
			deny()

	# Validate customer link
	if values.get("customer"):
		_identifier(values["customer"])
		if not frappe.db.exists("Customer", values["customer"]):
			invalid("Selected customer does not exist.")
		check_record("Customer", values["customer"])

	# Validate workstation link
	if values.get("workstation"):
		_identifier(values["workstation"])
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	# Validate reference_at
	ref = values.get("reference_at")
	if ref is not None:
		if not isinstance(ref, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", ref):
			invalid("Reference time must be an ISO date and time.")
		try:
			ref_dt = datetime.fromisoformat(ref)
		except ValueError:
			invalid("Invalid reference time.")
	else:
		ref_dt = now_datetime().replace(microsecond=0)

	values["reference_at"] = str(ref_dt)
	return values, ref_dt


def validate_job_card_filters(filters):
	"""Strict server-side validation for Job Card list filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - JC_FILTER_KEYS:
		invalid("Unsupported Job Card filter parameter.")

	values = {k: v for k, v in values.items() if v is not None and v != ""}

	# Resolve and validate company
	company_arg = values.get("company")
	if not company_arg:
		user_default_company = frappe.defaults.get_user_default("Company")
		if user_default_company and frappe.has_permission("Company", "read", user_default_company):
			company_arg = user_default_company
	values["company"] = _company(company_arg)

	# Validate dates
	for key in ("from_date", "to_date"):
		if key in values:
			_date(values[key])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate work_order link
	if values.get("work_order"):
		_identifier(values["work_order"])
		if not frappe.db.exists("Work Order", values["work_order"]):
			invalid("Selected Work Order does not exist.")
		wo = check_record("Work Order", values["work_order"])
		if wo.company != values["company"]:
			deny()

	# Validate workstation link
	if values.get("workstation"):
		_identifier(values["workstation"])
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	# Validate project link
	if values.get("project"):
		_identifier(values["project"])
		if not frappe.db.exists("Project", values["project"]):
			invalid("Selected project does not exist.")
		proj = check_record("Project", values["project"])
		if proj.company != values["company"]:
			deny()

	return values


def parse_pagination(start, page_length):
	"""Validates start offset and limit page length within safe bounds."""
	try:
		s = int(start) if start is not None else 0
		l = int(page_length) if page_length is not None else 20
	except (ValueError, TypeError):
		invalid("Pagination parameters must be non-negative integers.")
	if s < 0 or s > MAX_OFFSET:
		invalid(f"Start offset must be between 0 and {MAX_OFFSET}.")
	if l < 1 or l > MAX_PAGE_SIZE:
		invalid(f"Page length must be between 1 and {MAX_PAGE_SIZE}.")
	return s, l


def parse_sorting(sort_by, sort_order, allowed_fields, default_field="modified"):
	"""Validates sort field against allowlist and sort order against asc/desc."""
	sb = sort_by or default_field
	so = (sort_order or "desc").lower()
	if sb not in allowed_fields:
		invalid("Unsupported sort field.")
	if so not in ("asc", "desc"):
		invalid("Sort order must be 'asc' or 'desc'.")
	return f"{sb} {so}" + (", name asc" if sb != "name" else "")


@frappe.whitelist(methods=["GET"])
@read_errors
def get_work_orders(filters=None, start=0, page_length=20, sort_by="modified", sort_order="desc", **extra):
	"""
	API A: Work Order List for Production Management Control Tower (DASH-016).
	Returns paginated, permission-scoped Work Orders with verified planned and
	produced quantities, derived remaining quantities, completion percentages,
	target dates, overdue indicators, and linked Job Card counts.
	"""
	_extra(extra)
	values, ref_dt = validate_work_order_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = parse_pagination(start, page_length)
	order_by = parse_sorting(sort_by, sort_order, WO_SORT_FIELDS, default_field="modified")

	if not frappe.has_permission("Work Order", "read"):
		deny()

	# 1. Build base query conditions
	conditions = [["company", "=", company]]

	if values.get("project"):
		conditions.append(["project", "=", values["project"]])

	if values.get("production_item") or values.get("item_code"):
		item = values.get("production_item") or values.get("item_code")
		conditions.append(["production_item", "=", item])

	if values.get("from_date"):
		conditions.append(["planned_start_date", ">=", values["from_date"]])
	if values.get("to_date"):
		conditions.append(["planned_start_date", "<=", values["to_date"] + " 23:59:59"])

	# Base DocType fields
	wo_fields = [
		"name",
		"production_item",
		"item_name",
		"qty",
		"produced_qty",
		"status",
		"docstatus",
		"company",
		"project",
		"sales_order",
		"bom_no",
		"stock_uom",
		"planned_start_date",
		"planned_end_date",
		"expected_delivery_date",
		"wip_warehouse",
		"fg_warehouse",
		"material_transferred_for_manufacturing",
		"creation",
		"modified",
	]

	# Fetch candidate records within company scope
	all_wos = frappe.get_all(
		"Work Order",
		filters=conditions,
		fields=wo_fields,
		order_by=order_by,
		limit_page_length=5000,
	)

	# 2. Scope by Customer (via Project or Sales Order)
	if values.get("customer"):
		cust = values["customer"]
		valid_proj = set(frappe.get_all("Project", filters={"customer": cust, "company": company}, pluck="name"))
		valid_so = set(frappe.get_all("Sales Order", filters={"customer": cust, "company": company}, pluck="name"))
		all_wos = [w for w in all_wos if (w.get("project") in valid_proj) or (w.get("sales_order") in valid_so)]

	# 3. Scope by Workstation or Operation (via Job Cards or WO Operations)
	if values.get("workstation") or values.get("operation"):
		jc_filters = {"docstatus": ["<", 2]}
		if values.get("workstation"):
			jc_filters["workstation"] = values["workstation"]
		if values.get("operation"):
			jc_filters["operation"] = values["operation"]
		wos_with_jc = set(frappe.get_all("Job Card", filters=jc_filters, pluck="work_order"))
		all_wos = [w for w in all_wos if w.get("name") in wos_with_jc]

	# 4. Search query (substring on name, item code, or item name)
	if values.get("search") or values.get("work_order"):
		q = (values.get("search") or values.get("work_order")).strip().lower()
		all_wos = [
			w for w in all_wos
			if q in str(w.get("name", "")).lower()
			or q in str(w.get("production_item", "")).lower()
			or q in str(w.get("item_name", "")).lower()
		]

	# 5. Enrich rows with target date, overdue flag, remaining qty, and completion %
	enriched = []
	for w in all_wos:
		target = get_target_completion_date(w)
		days_diff = (target - ref_date).days if target else None
		is_active = (w.get("docstatus") == 1 and w.get("status") in ("Not Started", "In Process"))
		is_overdue = bool(is_active and days_diff is not None and days_diff < 0)

		qty = flt(w.get("qty"))
		produced = flt(w.get("produced_qty"))
		rem_qty = max(0.0, qty - produced)
		comp_pct = round((produced / qty * 100.0), 1) if qty > 0 else 0.0

		row = dict(w)
		row["qty"] = qty
		row["produced_qty"] = produced
		row["remaining_qty"] = rem_qty
		row["completion_percent"] = comp_pct
		row["target_completion_date"] = str(target) if target else None
		row["is_active"] = is_active
		row["is_overdue"] = is_overdue
		row["days_diff"] = days_diff
		enriched.append(row)

	# 6. Apply status filter
	status_arg = values.get("status", "")
	if status_arg in ("Active", ""):
		filtered = [w for w in enriched if w.get("is_active")]
	elif status_arg == "All":
		filtered = [w for w in enriched if w.get("docstatus") != 2]
	elif status_arg == "Overdue":
		filtered = [w for w in enriched if w.get("is_overdue")]
	elif status_arg == "Due soon":
		filtered = [w for w in enriched if w.get("is_active") and w.get("days_diff") is not None and 0 <= w.get("days_diff") <= 7]
	elif status_arg == "Draft":
		filtered = [w for w in enriched if w.get("docstatus") == 0]
	elif status_arg == "Cancelled":
		filtered = [w for w in enriched if w.get("docstatus") == 2]
	else:
		filtered = [w for w in enriched if w.get("status") == status_arg]

	total_count = len(filtered)
	paged_slice = filtered[start_offset:start_offset + limit]

	# 7. Batch resolve Customer names and Job Card counts (Zero N+1 queries)
	paged_wo_names = [r["name"] for r in paged_slice]
	proj_names = list({r["project"] for r in paged_slice if r.get("project")})
	so_names = list({r["sales_order"] for r in paged_slice if r.get("sales_order")})

	# Customer maps
	proj_cust_map = {}
	if proj_names and frappe.has_permission("Project", "read"):
		projs = frappe.get_all("Project", filters={"name": ["in", proj_names]}, fields=["name", "customer"])
		proj_cust_map = {p.name: p.customer for p in projs}

	so_cust_map = {}
	if so_names and frappe.has_permission("Sales Order", "read"):
		sos = frappe.get_all("Sales Order", filters={"name": ["in", so_names]}, fields=["name", "customer"])
		so_cust_map = {s.name: s.customer for s in sos}

	# Job card counts map
	jc_counts = defaultdict(lambda: {"open": 0, "total": 0})
	if paged_wo_names and frappe.has_permission("Job Card", "read"):
		jcs = frappe.get_all(
			"Job Card",
			filters={"work_order": ["in", paged_wo_names], "docstatus": ["<", 2]},
			fields=["work_order", "status"],
			limit_page_length=5000,
		)
		for jc in jcs:
			wo_key = jc.work_order
			jc_counts[wo_key]["total"] += 1
			if jc.status in ("Open", "Work In Progress"):
				jc_counts[wo_key]["open"] += 1

	for row in paged_slice:
		cust = proj_cust_map.get(row.get("project")) or so_cust_map.get(row.get("sales_order")) or None
		row["customer"] = cust
		wo_key = row["name"]
		row["open_job_cards_count"] = jc_counts[wo_key]["open"]
		row["total_job_cards_count"] = jc_counts[wo_key]["total"]

	return {
		"work_orders": paged_slice,
		"total": total_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_count,
		"applied_filters": values,
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_work_order_detail(work_order=None, **extra):
	"""
	API B: Work Order Detail for Production Management Control Tower (DASH-016).
	Returns verified production details for an individual Work Order including
	child operations, required items, linked Job Cards, and manufacture Stock Entries.
	Enforces document-level permissions and masks financial fields for operational roles.
	"""
	_extra(extra)
	require_capability("production")
	if not work_order or not isinstance(work_order, str):
		invalid("A valid Work Order identifier is required.")
	_identifier(work_order)

	# Document-level permission enforcement
	wo_doc = check_record("Work Order", work_order, "read")
	ref_date = now_datetime().date()

	# Resolve customer link
	customer = None
	if wo_doc.project and frappe.has_permission("Project", "read"):
		customer = frappe.db.get_value("Project", wo_doc.project, "customer")
	elif wo_doc.sales_order and frappe.has_permission("Sales Order", "read"):
		customer = frappe.db.get_value("Sales Order", wo_doc.sales_order, "customer")

	target = get_target_completion_date(wo_doc.as_dict())
	days_diff = (target - ref_date).days if target else None
	qty = flt(wo_doc.qty)
	produced = flt(wo_doc.produced_qty)
	rem_qty = max(0.0, qty - produced)
	comp_pct = round((produced / qty * 100.0), 1) if qty > 0 else 0.0
	is_active = (wo_doc.docstatus == 1 and wo_doc.status in ("Not Started", "In Process"))
	is_overdue = bool(is_active and days_diff is not None and days_diff < 0)

	detail = {
		"name": wo_doc.name,
		"production_item": wo_doc.production_item,
		"item_name": wo_doc.item_name or wo_doc.production_item,
		"company": wo_doc.company,
		"status": wo_doc.status,
		"docstatus": wo_doc.docstatus,
		"bom_no": wo_doc.bom_no,
		"sales_order": wo_doc.sales_order,
		"project": wo_doc.project,
		"customer": customer,
		"stock_uom": wo_doc.stock_uom,
		"qty": qty,
		"produced_qty": produced,
		"remaining_qty": rem_qty,
		"completion_percent": comp_pct,
		"planned_start_date": str(wo_doc.planned_start_date) if wo_doc.planned_start_date else None,
		"planned_end_date": str(wo_doc.planned_end_date) if wo_doc.planned_end_date else None,
		"expected_delivery_date": str(wo_doc.expected_delivery_date) if wo_doc.expected_delivery_date else None,
		"target_completion_date": str(target) if target else None,
		"actual_start_date": str(wo_doc.actual_start_date) if wo_doc.actual_start_date else None,
		"actual_end_date": str(wo_doc.actual_end_date) if wo_doc.actual_end_date else None,
		"is_overdue": is_overdue,
		"days_diff": days_diff,
		"wip_warehouse": wo_doc.wip_warehouse,
		"fg_warehouse": wo_doc.fg_warehouse,
		"source_warehouse": wo_doc.source_warehouse,
		"scrap_warehouse": wo_doc.scrap_warehouse,
		"lead_time": flt(wo_doc.lead_time),
		"material_transferred_for_manufacturing": flt(wo_doc.material_transferred_for_manufacturing),
		"track_semi_finished_goods": bool(wo_doc.track_semi_finished_goods),
		"description": wo_doc.description,
	}

	# Financial field masking
	if can_finance():
		detail["planned_operating_cost"] = flt(wo_doc.planned_operating_cost)
		detail["actual_operating_cost"] = flt(wo_doc.actual_operating_cost)
		detail["total_operating_cost"] = flt(wo_doc.total_operating_cost)
	else:
		detail["planned_operating_cost"] = None
		detail["actual_operating_cost"] = None
		detail["total_operating_cost"] = None

	# 1. Operations child table
	operations_list = []
	if frappe.has_permission("Work Order Operation", "read"):
		for op in wo_doc.get("operations") or []:
			operations_list.append({
				"name": op.name,
				"operation": op.operation,
				"workstation": op.workstation,
				"workstation_type": op.workstation_type,
				"sequence_id": op.sequence_id or op.idx,
				"status": op.status,
				"time_in_mins": flt(op.time_in_mins),
				"completed_qty": flt(op.completed_qty),
				"process_loss_qty": flt(op.process_loss_qty),
				"actual_operation_time": flt(op.actual_operation_time),
			})

	# 2. Required items child table
	required_items_list = []
	if frappe.has_permission("Work Order Item", "read"):
		for it in wo_doc.get("required_items") or []:
			required_items_list.append({
				"name": it.name,
				"item_code": it.item_code,
				"item_name": it.item_name or it.item_code,
				"source_warehouse": it.source_warehouse,
				"stock_uom": it.stock_uom,
				"required_qty": flt(it.required_qty),
				"transferred_qty": flt(it.transferred_qty),
				"consumed_qty": flt(it.consumed_qty),
			})

	# 3. Linked Job Cards
	job_cards_list = []
	if frappe.has_permission("Job Card", "read"):
		jcs = frappe.get_all(
			"Job Card",
			filters={"work_order": work_order, "docstatus": ["<", 2]},
			fields=[
				"name",
				"operation",
				"workstation",
				"status",
				"docstatus",
				"for_quantity",
				"total_completed_qty",
				"transferred_qty",
				"total_time_in_mins",
				"expected_start_date",
				"expected_end_date",
				"actual_start_date",
				"actual_end_date",
				"quality_inspection",
			],
			order_by="creation asc",
			limit_page_length=500,
		)
		for j in jcs:
			fq = flt(j.for_quantity)
			cq = flt(j.total_completed_qty)
			cp = round((cq / fq * 100.0), 1) if fq > 0 else (100.0 if j.status == "Completed" else 0.0)
			job_cards_list.append({
				"name": j.name,
				"operation": j.operation,
				"workstation": j.workstation,
				"status": j.status,
				"docstatus": j.docstatus,
				"for_quantity": fq,
				"total_completed_qty": cq,
				"transferred_qty": flt(j.transferred_qty),
				"completion_percent": cp,
				"total_time_in_mins": flt(j.total_time_in_mins),
				"expected_start_date": str(j.expected_start_date) if j.expected_start_date else None,
				"expected_end_date": str(j.expected_end_date) if j.expected_end_date else None,
				"actual_start_date": str(j.actual_start_date) if j.actual_start_date else None,
				"actual_end_date": str(j.actual_end_date) if j.actual_end_date else None,
				"quality_inspection": j.quality_inspection,
			})

	# 4. Linked Manufacture Stock Entries
	stock_entries_list = []
	if frappe.has_permission("Stock Entry", "read"):
		entries = frappe.get_all(
			"Stock Entry",
			filters={"work_order": work_order, "purpose": "Manufacture", "docstatus": 1},
			fields=["name", "posting_date", "fg_completed_qty", "docstatus", "to_warehouse"],
			order_by="posting_date desc",
			limit_page_length=100,
		)
		for se in entries:
			stock_entries_list.append({
				"name": se.name,
				"posting_date": str(se.posting_date),
				"fg_completed_qty": flt(se.fg_completed_qty),
				"docstatus": se.docstatus,
				"target_warehouse": se.to_warehouse,
			})

	return {
		"work_order": detail,
		"operations": operations_list,
		"required_items": required_items_list,
		"job_cards": job_cards_list,
		"stock_entries": stock_entries_list,
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_job_cards(filters=None, start=0, page_length=20, sort_by="modified", sort_order="desc", **extra):
	"""
	API C: Job Card List for Production Monitoring (DASH-016).
	Returns paginated, permission-scoped Job Cards with operation, workstation,
	and planned vs completed operation quantities.
	Note: Job Card quantities represent individual operation volume, NOT finished output.
	"""
	_extra(extra)
	values = validate_job_card_filters(filters)
	company = values["company"]
	start_offset, limit = parse_pagination(start, page_length)
	order_by = parse_sorting(sort_by, sort_order, JC_SORT_FIELDS, default_field="modified")

	if not frappe.has_permission("Job Card", "read"):
		deny()

	# 1. Base query conditions
	conditions = [["company", "=", company]]

	if values.get("work_order"):
		conditions.append(["work_order", "=", values["work_order"]])

	if values.get("workstation"):
		conditions.append(["workstation", "=", values["workstation"]])

	if values.get("operation"):
		conditions.append(["operation", "=", values["operation"]])

	if values.get("project"):
		conditions.append(["project", "=", values["project"]])

	if values.get("production_item"):
		conditions.append(["production_item", "=", values["production_item"]])

	if values.get("from_date"):
		conditions.append(["posting_date", ">=", values["from_date"]])
	if values.get("to_date"):
		conditions.append(["posting_date", "<=", values["to_date"]])

	# Status handling
	status_arg = values.get("status", "")
	if status_arg and status_arg != "All":
		conditions.append(["status", "=", status_arg])
	else:
		conditions.append(["docstatus", "<", 2])

	jc_fields = [
		"name",
		"work_order",
		"production_item",
		"item_name",
		"stock_uom",
		"operation",
		"workstation",
		"status",
		"docstatus",
		"company",
		"project",
		"for_quantity",
		"total_completed_qty",
		"transferred_qty",
		"expected_start_date",
		"expected_end_date",
		"actual_start_date",
		"actual_end_date",
		"total_time_in_mins",
		"quality_inspection",
		"is_corrective_job_card",
		"creation",
		"modified",
	]

	all_jcs = frappe.get_all(
		"Job Card",
		filters=conditions,
		fields=jc_fields,
		order_by=order_by,
		limit_page_length=5000,
	)

	# Substring search if provided
	if values.get("search"):
		q = values["search"].strip().lower()
		all_jcs = [
			j for j in all_jcs
			if q in str(j.get("name", "")).lower()
			or q in str(j.get("work_order", "")).lower()
			or q in str(j.get("operation", "")).lower()
			or q in str(j.get("production_item", "")).lower()
		]

	total_count = len(all_jcs)
	paged_slice = all_jcs[start_offset:start_offset + limit]

	# Format quantities and completion percentage
	formatted_rows = []
	for j in paged_slice:
		fq = flt(j.get("for_quantity"))
		cq = flt(j.get("total_completed_qty"))
		cp = round((cq / fq * 100.0), 1) if fq > 0 else (100.0 if j.get("status") == "Completed" else 0.0)

		row = dict(j)
		row["for_quantity"] = fq
		row["total_completed_qty"] = cq
		row["transferred_qty"] = flt(j.get("transferred_qty"))
		row["completion_percent"] = cp
		row["total_time_in_mins"] = flt(j.get("total_time_in_mins"))
		row["expected_start_date"] = str(j.get("expected_start_date")) if j.get("expected_start_date") else None
		row["expected_end_date"] = str(j.get("expected_end_date")) if j.get("expected_end_date") else None
		row["actual_start_date"] = str(j.get("actual_start_date")) if j.get("actual_start_date") else None
		row["actual_end_date"] = str(j.get("actual_end_date")) if j.get("actual_end_date") else None
		formatted_rows.append(row)

	return {
		"job_cards": formatted_rows,
		"total": total_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_count,
		"applied_filters": values,
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_job_card_detail(job_card=None, **extra):
	"""
	API D: Job Card Detail for Production Monitoring (DASH-016).
	Returns verified operational details for an individual Job Card including
	time logs, sub-operations, required items, and parent Work Order summary.
	Enforces document-level permissions and masks financial rate fields.
	"""
	_extra(extra)
	require_capability("production")
	if not job_card or not isinstance(job_card, str):
		invalid("A valid Job Card identifier is required.")
	_identifier(job_card)

	# Document-level permission enforcement
	jc_doc = check_record("Job Card", job_card, "read")

	fq = flt(jc_doc.for_quantity)
	cq = flt(jc_doc.total_completed_qty)
	cp = round((cq / fq * 100.0), 1) if fq > 0 else (100.0 if jc_doc.status == "Completed" else 0.0)

	detail = {
		"name": jc_doc.name,
		"work_order": jc_doc.work_order,
		"production_item": jc_doc.production_item,
		"item_name": jc_doc.item_name or jc_doc.production_item,
		"stock_uom": jc_doc.stock_uom,
		"operation": jc_doc.operation,
		"workstation": jc_doc.workstation,
		"workstation_type": jc_doc.workstation_type,
		"status": jc_doc.status,
		"docstatus": jc_doc.docstatus,
		"company": jc_doc.company,
		"project": jc_doc.project,
		"for_quantity": fq,
		"total_completed_qty": cq,
		"transferred_qty": flt(jc_doc.transferred_qty),
		"completion_percent": cp,
		"expected_start_date": str(jc_doc.expected_start_date) if jc_doc.expected_start_date else None,
		"expected_end_date": str(jc_doc.expected_end_date) if jc_doc.expected_end_date else None,
		"actual_start_date": str(jc_doc.actual_start_date) if jc_doc.actual_start_date else None,
		"actual_end_date": str(jc_doc.actual_end_date) if jc_doc.actual_end_date else None,
		"total_time_in_mins": flt(jc_doc.total_time_in_mins),
		"wip_warehouse": jc_doc.wip_warehouse,
		"quality_inspection": jc_doc.quality_inspection,
		"is_corrective_job_card": bool(jc_doc.is_corrective_job_card),
		"remarks": jc_doc.remarks,
	}

	# Financial field masking
	if can_finance():
		detail["hour_rate"] = flt(jc_doc.hour_rate)
	else:
		detail["hour_rate"] = None

	# 1. Time logs child table
	time_logs_list = []
	if frappe.has_permission("Job Card Time Log", "read"):
		for tl in jc_doc.get("time_logs") or []:
			time_logs_list.append({
				"name": tl.name,
				"employee": tl.employee,
				"from_time": str(tl.from_time) if tl.from_time else None,
				"to_time": str(tl.to_time) if tl.to_time else None,
				"time_in_mins": flt(tl.time_in_mins),
				"completed_qty": flt(tl.completed_qty),
			})

	# 2. Sub-operations child table
	sub_ops_list = []
	if frappe.has_permission("Job Card Operation", "read"):
		for so in jc_doc.get("sub_operations") or []:
			sub_ops_list.append({
				"name": so.name,
				"sub_operation": so.sub_operation,
				"status": so.status,
				"completed_qty": flt(so.completed_qty),
			})

	# 3. Job Card required items child table
	items_list = []
	if frappe.has_permission("Job Card Item", "read"):
		for it in jc_doc.get("items") or []:
			items_list.append({
				"name": it.name,
				"item_code": it.item_code,
				"item_name": it.item_name or it.item_code,
				"source_warehouse": it.source_warehouse,
				"uom": it.uom,
				"required_qty": flt(it.required_qty),
				"transferred_qty": flt(it.transferred_qty),
			})

	# 4. Parent Work Order summary
	parent_wo = {}
	if jc_doc.work_order and frappe.has_permission("Work Order", "read"):
		wo = frappe.get_doc("Work Order", jc_doc.work_order)
		parent_wo = {
			"work_order": wo.name,
			"status": wo.status,
			"planned_qty": flt(wo.qty),
			"produced_qty": flt(wo.produced_qty),
			"stock_uom": wo.stock_uom,
		}

	return {
		"job_card": detail,
		"time_logs": time_logs_list,
		"sub_operations": sub_ops_list,
		"items": items_list,
		"parent_work_order": parent_wo,
	}
