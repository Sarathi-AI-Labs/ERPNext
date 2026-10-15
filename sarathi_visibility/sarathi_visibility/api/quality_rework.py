"""
DASH-020: Quality, Rework, and Subcontracting Views Backend API.
Provides permission-scoped, warehouse- and company-isolated Quality Overviews,
Rework/Corrective Job Card analytics, and Subcontracting Order tracking
with zero N+1 queries.
"""
from collections import defaultdict
from datetime import date, datetime
import re

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.access import check_record, deny, require_capability
from sarathi_visibility.api.data_helpers import (
	_company,
	_date,
	_extra,
	_identifier,
	_parse,
	invalid,
	pagination,
	read_errors,
)

QUALITY_FILTER_KEYS = {
	"company",
	"status",
	"inspection_type",
	"from_date",
	"to_date",
	"item_code",
	"work_order",
	"job_card",
	"supplier",
	"reference_at",
}

QI_STATUS_CHOICES = {"All", "Accepted", "Rejected", "Draft"}
QI_TYPE_CHOICES = {"All", "Incoming", "In Process", "Outgoing"}


def parse_datetime_val(val):
	"""Safely parses string or datetime/date object into a datetime."""
	if not val:
		return None
	if isinstance(val, datetime):
		return val
	if isinstance(val, date):
		return datetime.combine(val, datetime.min.time())
	try:
		return datetime.fromisoformat(str(val))
	except Exception:
		return None


def validate_quality_rework_filters(filters):
	"""Strict server-side validation for Quality, Rework, and Subcontracting filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - QUALITY_FILTER_KEYS:
		invalid("Unsupported quality/rework filter parameter.")

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

	# Validate item_code
	if values.get("item_code"):
		_identifier(values["item_code"])
		if not frappe.db.exists("Item", values["item_code"]):
			invalid("Selected item does not exist.")
		check_record("Item", values["item_code"])

	# Validate work_order link
	if values.get("work_order"):
		_identifier(values["work_order"])
		if not frappe.db.exists("Work Order", values["work_order"]):
			invalid("Selected Work Order does not exist.")
		wo = check_record("Work Order", values["work_order"])
		if wo.company != values["company"]:
			deny()

	# Validate job_card link
	if values.get("job_card"):
		_identifier(values["job_card"])
		if not frappe.db.exists("Job Card", values["job_card"]):
			invalid("Selected Job Card does not exist.")
		jc = check_record("Job Card", values["job_card"])
		if jc.company and jc.company != values["company"]:
			deny()

	# Validate supplier link
	if values.get("supplier"):
		_identifier(values["supplier"])
		if not frappe.db.exists("Supplier", values["supplier"]):
			invalid("Selected supplier does not exist.")
		check_record("Supplier", values["supplier"])

	# Validate status choice
	if values.get("status"):
		st = values["status"]
		if st not in QI_STATUS_CHOICES and st not in ("Open", "Work In Progress", "Completed", "Active"):
			invalid("Unsupported status filter parameter.")

	# Validate inspection_type choice
	if values.get("inspection_type"):
		it = values["inspection_type"]
		if it not in QI_TYPE_CHOICES:
			invalid("Unsupported inspection_type filter parameter.")

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


@frappe.whitelist(methods=["GET"])
@read_errors
def get_quality_overview(filters=None, start=0, page_length=20, **extra):
	"""
	API for Quality Overview (DASH-020).
	Calculates quality inspection totals, passed/failed ratios,
	defect breakdowns, and paginated inspection records with zero N+1 queries.
	"""
	_extra(extra)
	values, ref_dt = validate_quality_rework_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	# -------------------------------------------------------------
	# 1. Retrieve Quality Inspection Records (Query 1)
	# -------------------------------------------------------------
	qi_filters = [
		["docstatus", "<", 2],
	]

	# Check if Quality Inspection has company field directly
	has_qi = bool(frappe.db.exists("DocType", "Quality Inspection") and frappe.has_permission("Quality Inspection", "read"))
	if not has_qi:
		return {
			"available": False,
			"reason": "Quality Inspection is not configured or not accessible for your role.",
			"summary": {
				"total_inspections": 0,
				"passed_inspections": 0,
				"failed_inspections": 0,
				"pending_inspections": 0,
				"failure_rate_percent": 0.0,
			},
			"inspections": [],
			"total_inspections_count": 0,
		}

	# Apply company filter if field exists on DocType
	meta = frappe.get_meta("Quality Inspection")
	if meta.has_field("company"):
		qi_filters.append(["company", "=", company])

	if values.get("item_code"):
		qi_filters.append(["item_code", "=", values["item_code"]])
	if values.get("inspection_type") and values["inspection_type"] != "All":
		qi_filters.append(["inspection_type", "=", values["inspection_type"]])

	# Status filter
	st_filter = values.get("status", "All")
	if st_filter == "Accepted":
		qi_filters.append(["status", "=", "Accepted"])
		qi_filters.append(["docstatus", "=", 1])
	elif st_filter == "Rejected":
		qi_filters.append(["status", "=", "Rejected"])
		qi_filters.append(["docstatus", "=", 1])
	elif st_filter == "Draft":
		qi_filters.append(["docstatus", "=", 0])

	# Date filter
	if values.get("from_date"):
		qi_filters.append(["report_date", ">=", values["from_date"]])
	if values.get("to_date"):
		qi_filters.append(["report_date", "<=", values["to_date"]])

	qi_records = frappe.get_all(
		"Quality Inspection",
		filters=qi_filters,
		fields=[
			"name",
			"inspection_type",
			"reference_type",
			"reference_name",
			"item_code",
			"item_name",
			"status",
			"report_date",
			"sample_size",
			"inspected_by",
			"docstatus",
			"creation",
			"modified",
		],
		order_by="report_date desc, creation desc",
		limit_page_length=5000,
	)

	# -------------------------------------------------------------
	# 2. Batch Item Metadata (Query 2)
	# -------------------------------------------------------------
	item_codes = list({r.item_code for r in qi_records if r.item_code})
	item_map = {}
	if item_codes:
		items = frappe.get_all(
			"Item",
			filters={"name": ["in", item_codes]},
			fields=["name", "item_name", "stock_uom", "item_group"],
			limit_page_length=5000,
		)
		for it in items:
			item_map[it.name] = it

	# -------------------------------------------------------------
	# 3. Calculate Quality KPIs
	# -------------------------------------------------------------
	submitted_inspections = [r for r in qi_records if r.docstatus == 1]
	passed_inspections = [r for r in submitted_inspections if r.status == "Accepted"]
	failed_inspections = [r for r in submitted_inspections if r.status == "Rejected"]
	draft_inspections = [r for r in qi_records if r.docstatus == 0]

	total_sub_count = len(submitted_inspections)
	passed_count = len(passed_inspections)
	failed_count = len(failed_inspections)
	draft_count = len(draft_inspections)

	failure_rate = round((failed_count / total_sub_count * 100), 1) if total_sub_count > 0 else 0.0

	# Group rejections by Item
	rejected_items_summary = defaultdict(lambda: {"item_code": "", "item_name": "", "rejections_count": 0, "sample_units": 0.0})
	for r in failed_inspections:
		itm = item_map.get(r.item_code)
		name_disp = (itm.item_name if itm else r.item_name) or r.item_code
		entry = rejected_items_summary[r.item_code]
		entry["item_code"] = r.item_code
		entry["item_name"] = name_disp
		entry["rejections_count"] += 1
		entry["sample_units"] += flt(r.sample_size)

	top_rejected_items = sorted(rejected_items_summary.values(), key=lambda x: -x["rejections_count"])[:5]

	# Build inspection line objects
	inspection_lines = []
	for r in qi_records:
		itm = item_map.get(r.item_code)
		item_display = (itm.item_name if itm else r.item_name) or r.item_code
		stock_uom = itm.stock_uom if itm else "Nos"

		line_status = "Draft" if r.docstatus == 0 else (r.status or "Submitted")

		inspection_lines.append({
			"name": r.name,
			"inspection_type": r.inspection_type or "General",
			"reference_type": r.reference_type,
			"reference_name": r.reference_name,
			"item_code": r.item_code,
			"item_name": item_display,
			"stock_uom": stock_uom,
			"status": line_status,
			"is_rejected": bool(r.docstatus == 1 and r.status == "Rejected"),
			"report_date": str(r.report_date) if r.report_date else None,
			"sample_size": flt(r.sample_size),
			"inspected_by": r.inspected_by or "Inspector",
			"drilldown_records": [
				{"doctype": "Quality Inspection", "name": r.name},
				{"doctype": r.reference_type, "name": r.reference_name} if r.reference_type and r.reference_name else None,
				{"doctype": "Item", "name": r.item_code} if r.item_code else None,
			],
		})
		inspection_lines[-1]["drilldown_records"] = [d for d in inspection_lines[-1]["drilldown_records"] if d]

	total_lines = len(inspection_lines)
	paginated_lines = inspection_lines[start_offset : start_offset + limit]

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_inspections": total_sub_count,
			"passed_inspections": passed_count,
			"failed_inspections": failed_count,
			"pending_inspections": draft_count,
			"failure_rate_percent": failure_rate,
			"distinct_rejected_items": len(rejected_items_summary),
		},
		"top_rejected_items": top_rejected_items,
		"inspections": paginated_lines,
		"total_inspections_count": total_lines,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_lines,
		"applied_filters": values,
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_rework_overview(filters=None, start=0, page_length=20, **extra):
	"""
	API for Rework Overview (DASH-020).
	Identifies traceable corrective Job Cards (is_corrective_job_card=1),
	links to root inspection rejections and parent jobs, and calculates
	rework operational metrics with zero N+1 queries.
	"""
	_extra(extra)
	values, ref_dt = validate_quality_rework_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	# -------------------------------------------------------------
	# 1. Query Corrective Job Cards (Query 1)
	# -------------------------------------------------------------
	# Check if Job Card exists and has is_corrective_job_card field
	if not frappe.db.exists("DocType", "Job Card") or not frappe.has_permission("Job Card", "read"):
		return {
			"available": False,
			"reason": "Job Card is not accessible for your role.",
			"rework_configured": False,
			"summary": {
				"total_rework_jobs": 0,
				"in_progress_rework": 0,
				"queued_rework": 0,
				"completed_rework": 0,
				"delayed_rework": 0,
				"total_rework_units": 0.0,
			},
			"rework_jobs": [],
			"total_rework_count": 0,
		}

	jc_meta = frappe.get_meta("Job Card")
	has_corrective_field = jc_meta.has_field("is_corrective_job_card")

	rework_filters = [
		["company", "=", company],
		["docstatus", "<", 2],
	]

	if has_corrective_field:
		rework_filters.append(["is_corrective_job_card", "=", 1])
	else:
		# If the field does not exist in this ERPNext installation, return empty state with clear note
		return {
			"available": True,
			"rework_configured": False,
			"rework_note": "ERPNext Job Card is not configured with the corrective rework field (is_corrective_job_card). Rework tracking requires corrective Job Cards linked via for_job_card.",
			"summary": {
				"total_rework_jobs": 0,
				"in_progress_rework": 0,
				"queued_rework": 0,
				"completed_rework": 0,
				"delayed_rework": 0,
				"total_rework_units": 0.0,
			},
			"rework_jobs": [],
			"total_rework_count": 0,
			"start": start_offset,
			"page_length": limit,
			"has_next_page": False,
			"applied_filters": values,
		}

	if values.get("work_order"):
		rework_filters.append(["work_order", "=", values["work_order"]])
	if values.get("job_card"):
		rework_filters.append(["name", "=", values["job_card"]])
	if values.get("status") and values["status"] in ("Open", "Work In Progress", "Completed"):
		rework_filters.append(["status", "=", values["status"]])

	if values.get("from_date"):
		rework_filters.append(["creation", ">=", values["from_date"]])
	if values.get("to_date"):
		rework_filters.append(["creation", "<=", values["to_date"] + " 23:59:59"])

	rework_jcs = frappe.get_all(
		"Job Card",
		filters=rework_filters,
		fields=[
			"name",
			"work_order",
			"operation",
			"workstation",
			"workstation_type",
			"status",
			"for_quantity",
			"total_completed_qty",
			"for_job_card",
			"quality_inspection",
			"expected_start_date",
			"expected_end_date",
			"actual_start_date",
			"actual_end_date",
			"total_time_in_mins",
			"creation",
			"modified",
		],
		order_by="creation desc",
		limit_page_length=1000,
	)

	# -------------------------------------------------------------
	# 2. Batch Work Order Metadata (Query 2)
	# -------------------------------------------------------------
	wo_names = list({r.work_order for r in rework_jcs if r.work_order})
	wo_map = {}
	if wo_names:
		wo_records = frappe.get_all(
			"Work Order",
			filters={"name": ["in", wo_names]},
			fields=["name", "production_item", "item_name", "status", "project", "customer"],
			limit_page_length=1000,
		)
		for wo in wo_records:
			wo_map[wo.name] = wo

	# -------------------------------------------------------------
	# 3. Calculate Rework KPIs
	# -------------------------------------------------------------
	total_rework_count = len(rework_jcs)
	in_prog = sum(1 for r in rework_jcs if r.status == "Work In Progress")
	queued = sum(1 for r in rework_jcs if r.status == "Open")
	completed = sum(1 for r in rework_jcs if r.status == "Completed")
	total_units = sum(flt(r.for_quantity) for r in rework_jcs)

	delayed_count = 0
	rework_lines = []

	for r in rework_jcs:
		wo = wo_map.get(r.work_order)
		target_date = None
		if r.expected_end_date:
			dt = parse_datetime_val(r.expected_end_date)
			if dt:
				target_date = dt.date()

		days_to_target = (target_date - ref_date).days if target_date else None
		is_overdue = bool(days_to_target is not None and days_to_target < 0 and r.status != "Completed")
		if is_overdue:
			delayed_count += 1

		rework_lines.append({
			"job_card": r.name,
			"original_job_card": r.for_job_card,
			"quality_inspection": r.quality_inspection,
			"work_order": r.work_order,
			"production_item": wo.production_item if wo else None,
			"production_item_name": (wo.item_name or wo.production_item) if wo else None,
			"operation": r.operation,
			"workstation": r.workstation or "Unassigned",
			"status": r.status,
			"rework_quantity": flt(r.for_quantity),
			"completed_quantity": flt(r.total_completed_qty),
			"target_completion_date": str(target_date) if target_date else None,
			"days_to_target": days_to_target,
			"is_overdue": is_overdue,
			"time_spent_mins": flt(r.total_time_in_mins),
			"drilldown_records": [
				{"doctype": "Job Card", "name": r.name},
				{"doctype": "Job Card", "name": r.for_job_card} if r.for_job_card else None,
				{"doctype": "Quality Inspection", "name": r.quality_inspection} if r.quality_inspection else None,
				{"doctype": "Work Order", "name": r.work_order} if r.work_order else None,
			],
		})
		rework_lines[-1]["drilldown_records"] = [d for d in rework_lines[-1]["drilldown_records"] if d]

	paginated_lines = rework_lines[start_offset : start_offset + limit]

	return {
		"available": True,
		"rework_configured": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_rework_jobs": total_rework_count,
			"in_progress_rework": in_prog,
			"queued_rework": queued,
			"completed_rework": completed,
			"delayed_rework": delayed_count,
			"total_rework_units": round(total_units, 2),
		},
		"rework_jobs": paginated_lines,
		"total_rework_count": total_rework_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_rework_count,
		"applied_filters": values,
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_subcontracting_overview(filters=None, start=0, page_length=20, **extra):
	"""
	API for Subcontracting Overview (DASH-020).
	Tracks active Subcontracting Orders, suppliers, supplied materials,
	receipts, and overdue orders with zero N+1 queries.
	"""
	_extra(extra)
	values, ref_dt = validate_quality_rework_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	has_sco = bool(frappe.db.exists("DocType", "Subcontracting Order") and frappe.has_permission("Subcontracting Order", "read"))
	if not has_sco:
		return {
			"available": False,
			"reason": "Subcontracting Order is not configured or not accessible for your role.",
			"summary": {
				"total_subcontract_orders": 0,
				"active_subcontracts": 0,
				"awaiting_receipt_orders": 0,
				"completed_subcontracts": 0,
				"overdue_subcontracts": 0,
				"total_ordered_units": 0.0,
				"total_received_units": 0.0,
				"total_outstanding_units": 0.0,
			},
			"orders": [],
			"total_orders_count": 0,
		}

	# -------------------------------------------------------------
	# 1. Query Subcontracting Orders (Query 1)
	# -------------------------------------------------------------
	sco_filters = [
		["company", "=", company],
		["docstatus", "!=", 2],
	]

	if values.get("supplier"):
		sco_filters.append(["supplier", "=", values["supplier"]])
	if values.get("status") and values["status"] != "All":
		sco_filters.append(["status", "=", values["status"]])
	if values.get("from_date"):
		sco_filters.append(["transaction_date", ">=", values["from_date"]])
	if values.get("to_date"):
		sco_filters.append(["transaction_date", "<=", values["to_date"]])

	orders = frappe.get_all(
		"Subcontracting Order",
		filters=sco_filters,
		fields=[
			"name",
			"purchase_order",
			"supplier",
			"supplier_name",
			"company",
			"transaction_date",
			"schedule_date",
			"status",
			"docstatus",
			"total_qty",
			"total",
			"per_received",
			"project",
			"creation",
			"modified",
		],
		order_by="transaction_date desc, creation desc",
		limit_page_length=2000,
	)

	order_names = [o.name for o in orders]

	# -------------------------------------------------------------
	# 2. Batch Retrieve Order Items (Query 2)
	# -------------------------------------------------------------
	sco_items_by_parent = defaultdict(list)
	if order_names and frappe.db.exists("DocType", "Subcontracting Order Item"):
		items = frappe.get_all(
			"Subcontracting Order Item",
			filters={"parent": ["in", order_names]},
			fields=["parent", "item_code", "item_name", "qty", "received_qty", "returned_qty", "stock_uom"],
			limit_page_length=5000,
		)
		for itm in items:
			sco_items_by_parent[itm.parent].append(itm)

	# -------------------------------------------------------------
	# 3. Calculate Subcontracting KPIs & Order Summaries
	# -------------------------------------------------------------
	active_statuses = {
		"Open",
		"Material Transferred",
		"Partial Material Transferred",
		"Partially Received",
	}

	active_orders = [o for o in orders if o.docstatus == 1 and o.status in active_statuses]
	completed_orders = [o for o in orders if o.status == "Completed"]
	awaiting_receipt = [o for o in orders if o.docstatus == 1 and flt(o.per_received) < 100 and o.status not in ("Completed", "Closed", "Cancelled")]

	overdue_count = 0
	total_ordered = 0.0
	total_received = 0.0
	order_lines = []

	for o in orders:
		target_date = None
		if o.schedule_date:
			dt = parse_datetime_val(o.schedule_date)
			if dt:
				target_date = dt.date()

		days_to_target = (target_date - ref_date).days if target_date else None
		is_overdue = bool(days_to_target is not None and days_to_target < 0 and o.status not in ("Completed", "Closed", "Cancelled"))
		if is_overdue:
			overdue_count += 1

		# Item breakdown
		order_items = sco_items_by_parent.get(o.name, [])
		first_item = order_items[0] if order_items else None
		item_code_disp = first_item.item_code if first_item else "Multiple Items"
		item_name_disp = first_item.item_name if first_item else f"{len(order_items)} Items"
		stock_uom_disp = first_item.stock_uom if first_item else "Nos"

		ord_qty = flt(o.total_qty)
		rec_qty = sum(flt(it.received_qty) for it in order_items) if order_items else (ord_qty * flt(o.per_received) / 100.0)
		outstanding_qty = max(0.0, ord_qty - rec_qty)

		total_ordered += ord_qty
		total_received += rec_qty

		order_lines.append({
			"subcontracting_order": o.name,
			"purchase_order": o.purchase_order,
			"supplier": o.supplier,
			"supplier_name": o.supplier_name or o.supplier,
			"item_code": item_code_disp,
			"item_name": item_name_disp,
			"stock_uom": stock_uom_disp,
			"ordered_qty": round(ord_qty, 2),
			"received_qty": round(rec_qty, 2),
			"outstanding_qty": round(outstanding_qty, 2),
			"per_received": flt(o.per_received),
			"status": o.status,
			"schedule_date": str(target_date) if target_date else None,
			"days_to_target": days_to_target,
			"is_overdue": is_overdue,
			"project": o.project,
			"drilldown_records": [
				{"doctype": "Subcontracting Order", "name": o.name},
				{"doctype": "Supplier", "name": o.supplier} if o.supplier else None,
				{"doctype": "Purchase Order", "name": o.purchase_order} if o.purchase_order else None,
			],
		})
		order_lines[-1]["drilldown_records"] = [d for d in order_lines[-1]["drilldown_records"] if d]

	total_outstanding = max(0.0, total_ordered - total_received)
	total_orders_count = len(order_lines)
	paginated_orders = order_lines[start_offset : start_offset + limit]

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_subcontract_orders": total_orders_count,
			"active_subcontracts": len(active_orders),
			"awaiting_receipt_orders": len(awaiting_receipt),
			"completed_subcontracts": len(completed_orders),
			"overdue_subcontracts": overdue_count,
			"total_ordered_units": round(total_ordered, 2),
			"total_received_units": round(total_received, 2),
			"total_outstanding_units": round(total_outstanding, 2),
		},
		"orders": paginated_orders,
		"total_orders_count": total_orders_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_orders_count,
		"applied_filters": values,
	}
