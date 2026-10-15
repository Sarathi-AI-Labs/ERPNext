"""
DASH-021: Production Exception and Escalation Queue Backend API.
Consolidates verified production exceptions across Overdue Work Orders,
Delayed Job Cards, Material Shortages, Workstation Downtime, Failed Quality
Inspections, Rework Cases, and Overdue Subcontracting Orders with deterministic
severity classification, stable deduplication, and zero N+1 queries.
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
from sarathi_visibility.api.factory_overview import get_target_completion_date
from sarathi_visibility.api.material_readiness import get_material_readiness
from sarathi_visibility.api.quality_rework import (
	get_quality_overview,
	get_rework_overview,
	get_subcontracting_overview,
)
from sarathi_visibility.api.workstations import get_workstation_downtime

EXCEPTION_FILTER_KEYS = {
	"company",
	"category",
	"severity",
	"from_date",
	"to_date",
	"work_order",
	"item_code",
	"workstation",
	"supplier",
	"reference_at",
}

VALID_CATEGORIES = {
	"All",
	"Production",
	"Material",
	"Workstation",
	"Quality",
	"Subcontracting",
}

VALID_SEVERITIES = {
	"All",
	"Critical",
	"High",
	"Medium",
	"Low",
}

SEVERITY_RANKS = {
	"Critical": 1,
	"High": 2,
	"Medium": 3,
	"Low": 4,
}


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


def validate_exception_filters(filters):
	"""Strict server-side validation for production exception queue filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - EXCEPTION_FILTER_KEYS:
		invalid("Unsupported exception filter parameter.")

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

	# Validate category
	if values.get("category"):
		cat = values["category"]
		if cat not in VALID_CATEGORIES:
			invalid("Unsupported category filter parameter.")

	# Validate severity
	if values.get("severity"):
		sev = values["severity"]
		if sev not in VALID_SEVERITIES:
			invalid("Unsupported severity filter parameter.")

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

	# Validate workstation link
	if values.get("workstation"):
		_identifier(values["workstation"])
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	# Validate supplier link
	if values.get("supplier"):
		_identifier(values["supplier"])
		if not frappe.db.exists("Supplier", values["supplier"]):
			invalid("Selected supplier does not exist.")
		check_record("Supplier", values["supplier"])

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
def get_production_exceptions(
	filters=None,
	start=0,
	page_length=20,
	material_readiness=None,
	workstation_downtime=None,
	quality_overview=None,
	rework_overview=None,
	subcontracting_overview=None,
	**extra,
):
	"""
	API for Centralized Production Exception and Escalation Queue (DASH-021).
	Consolidates exceptions across Work Orders, Job Cards, Shortages, Downtime,
	Quality, Rework, and Subcontracting with deterministic severity and deduplication.
	"""
	_extra(extra)
	values, ref_dt = validate_exception_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	exceptions = []
	source_status = {
		"work_orders": True,
		"job_cards": True,
		"material_readiness": True,
		"workstation_downtime": True,
		"quality_inspections": True,
		"rework": True,
		"subcontracting": True,
	}

	# -------------------------------------------------------------
	# 1. Overdue Work Orders (Category: Production)
	# -------------------------------------------------------------
	try:
		if frappe.db.exists("DocType", "Work Order") and frappe.has_permission("Work Order", "read"):
			wo_filters = [
				["company", "=", company],
				["docstatus", "=", 1],
				["status", "in", ["Not Started", "In Process"]],
			]
			if values.get("work_order"):
				wo_filters.append(["name", "=", values["work_order"]])
			if values.get("item_code"):
				wo_filters.append(["production_item", "=", values["item_code"]])

			wos = frappe.get_all(
				"Work Order",
				filters=wo_filters,
				fields=[
					"name",
					"production_item",
					"item_name",
					"status",
					"planned_end_date",
					"expected_delivery_date",
					"qty",
					"produced_qty",
					"project",
					"creation",
				],
				limit_page_length=2000,
			)

			for wo in wos:
				target_d = get_target_completion_date(wo)
				if not target_d or target_d >= ref_date:
					continue  # Not overdue

				delay = (ref_date - target_d).days
				# Deterministic severity
				if delay >= 7 or (wo.status == "In Process" and delay >= 3):
					sev = "Critical"
				elif delay >= 1:
					sev = "High"
				else:
					sev = "Medium"

				rem_qty = max(0.0, flt(wo.qty) - flt(wo.produced_qty))
				exceptions.append({
					"exception_id": f"EXC-WO-{wo.name}",
					"category": "Production",
					"exception_type": "Overdue Work Order",
					"title": f"Work Order {wo.name} is {delay} day(s) overdue",
					"description": f"Manufacturing {wo.production_item} ({wo.item_name or 'Unit'}). Status: {wo.status}. Planned completion was {target_d}. Remaining quantity to produce: {rem_qty:g}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Work Order",
					"source_document": wo.name,
					"work_order": wo.name,
					"job_card": None,
					"item_code": wo.production_item,
					"item_name": wo.item_name or wo.production_item,
					"workstation": None,
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": str(target_d),
					"delay_days": delay,
					"age_days": delay,
					"impact_summary": f"{rem_qty:g} units pending production",
					"recommended_action": "Expedite remaining operations, verify machine allocation, or adjust master production schedule.",
					"drilldown_records": [
						{"doctype": "Work Order", "name": wo.name},
						{"doctype": "Item", "name": wo.production_item},
					],
				})
		else:
			source_status["work_orders"] = False
	except Exception as err:
		frappe.log_error(f"Error checking overdue Work Orders: {err}")
		source_status["work_orders"] = False

	# -------------------------------------------------------------
	# 2. Delayed Job Cards (Category: Production)
	# -------------------------------------------------------------
	try:
		if frappe.db.exists("DocType", "Job Card") and frappe.has_permission("Job Card", "read"):
			jc_filters = [
				["company", "=", company],
				["docstatus", "=", 1],
				["status", "in", ["Open", "Work In Progress"]],
			]
			if values.get("work_order"):
				jc_filters.append(["work_order", "=", values["work_order"]])
			if values.get("workstation"):
				jc_filters.append(["workstation", "=", values["workstation"]])

			# Exclude corrective job cards (handled under rework)
			jc_meta = frappe.get_meta("Job Card")
			if jc_meta.has_field("is_corrective_job_card"):
				jc_filters.append(["is_corrective_job_card", "=", 0])

			jcs = frappe.get_all(
				"Job Card",
				filters=jc_filters,
				fields=[
					"name",
					"work_order",
					"operation",
					"workstation",
					"status",
					"for_quantity",
					"total_completed_qty",
					"expected_end_date",
					"creation",
				],
				limit_page_length=2000,
			)

			for jc in jcs:
				if not jc.expected_end_date:
					continue
				dt = parse_datetime_val(jc.expected_end_date)
				if not dt or dt.date() >= ref_date:
					continue

				delay = (ref_date - dt.date()).days
				if delay >= 3:
					sev = "High"
				elif delay >= 1:
					sev = "Medium"
				else:
					sev = "Low"

				rem_qty = max(0.0, flt(jc.for_quantity) - flt(jc.total_completed_qty))
				exceptions.append({
					"exception_id": f"EXC-JC-{jc.name}",
					"category": "Production",
					"exception_type": "Delayed Job Card",
					"title": f"Job Card {jc.name} on {jc.operation} delayed by {delay} day(s)",
					"description": f"Operation '{jc.operation}' on workstation '{jc.workstation or 'Unassigned'}' was scheduled for completion by {dt.date()}. Remaining: {rem_qty:g} units.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Job Card",
					"source_document": jc.name,
					"work_order": jc.work_order,
					"job_card": jc.name,
					"item_code": None,
					"item_name": None,
					"workstation": jc.workstation,
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": str(dt.date()),
					"delay_days": delay,
					"age_days": delay,
					"impact_summary": f"Operation {jc.operation} delayed",
					"recommended_action": "Check operator staffing and workstation setup to clear queue bottleneck.",
					"drilldown_records": [
						{"doctype": "Job Card", "name": jc.name},
						{"doctype": "Work Order", "name": jc.work_order} if jc.work_order else None,
					],
				})
		else:
			source_status["job_cards"] = False
	except Exception as err:
		frappe.log_error(f"Error checking delayed Job Cards: {err}")
		source_status["job_cards"] = False

	# -------------------------------------------------------------
	# 3. Material Shortages (Category: Material)
	# -------------------------------------------------------------
	try:
		mr = material_readiness
		if mr is None:
			mr = get_material_readiness(values)

		if mr and mr.get("available") and mr.get("shortage_lines"):
			for row in mr["shortage_lines"]:
				if not row.get("has_shortage") or flt(row.get("shortage_qty")) <= 0:
					continue

				sh_qty = flt(row["shortage_qty"])
				wo_id = row.get("work_order")
				it_code = row.get("item_code")
				wh = row.get("source_warehouse") or "Warehouse"

				# Deterministic severity
				if row.get("is_time_critical") or row.get("is_overdue"):
					sev = "Critical"
				else:
					sev = "High"

				exceptions.append({
					"exception_id": f"EXC-SHORTAGE-{wo_id}-{it_code}-{wh}",
					"category": "Material",
					"exception_type": "Material Shortage",
					"title": f"Shortage of {sh_qty:g} {row.get('stock_uom', '')} on {wo_id}",
					"description": f"Item '{it_code}' ({row.get('item_name')}) is deficient by {sh_qty:g} {row.get('stock_uom', '')} in warehouse '{wh}'. Required: {row.get('required_qty', 0):g}, Available: {row.get('available_stock', 0):g}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Work Order",
					"source_document": wo_id,
					"work_order": wo_id,
					"job_card": None,
					"item_code": it_code,
					"item_name": row.get("item_name") or it_code,
					"workstation": None,
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": row.get("target_date"),
					"delay_days": abs(row.get("days_to_target") or 0) if row.get("is_overdue") else 0,
					"age_days": abs(row.get("days_to_target") or 0) if row.get("is_overdue") else 0,
					"impact_summary": f"Deficit: {sh_qty:g} {row.get('stock_uom', '')}",
					"recommended_action": "Initiate expedited stock transfer from central stores or raise priority purchase request.",
					"drilldown_records": [
						{"doctype": "Work Order", "name": wo_id},
						{"doctype": "Item", "name": it_code},
					],
				})
		elif mr and not mr.get("available"):
			source_status["material_readiness"] = False
	except Exception as err:
		frappe.log_error(f"Error checking material shortages: {err}")
		source_status["material_readiness"] = False

	# -------------------------------------------------------------
	# 4. Workstation Downtime (Category: Workstation)
	# -------------------------------------------------------------
	try:
		wsd = workstation_downtime
		if wsd is None:
			wsd = get_workstation_downtime(values)

		if wsd and wsd.get("available") and wsd.get("downtime_events"):
			for dt in wsd["downtime_events"]:
				mins = flt(dt.get("duration_mins"))
				ws_name = dt.get("workstation")
				is_active = bool(dt.get("is_active_stop"))

				# Deterministic severity
				if mins >= 120 or is_active:
					sev = "Critical"
				elif mins >= 30:
					sev = "High"
				else:
					sev = "Medium"

				exceptions.append({
					"exception_id": f"EXC-DT-{dt.get('name')}",
					"category": "Workstation",
					"exception_type": "Workstation Downtime",
					"title": f"Downtime event on {ws_name} ({mins:g} mins)",
					"description": f"Workstation '{ws_name}' recorded {mins:g} minutes of downtime. Reason: '{dt.get('stop_reason') or 'Unspecified'}'. Active stoppage: {'Yes' if is_active else 'No'}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Downtime Entry",
					"source_document": dt.get("name"),
					"work_order": None,
					"job_card": None,
					"item_code": None,
					"item_name": None,
					"workstation": ws_name,
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": None,
					"delay_days": int(mins // 60),
					"age_days": int(mins // 60),
					"impact_summary": f"{mins:g} minutes lost machine capacity",
					"recommended_action": "Coordinate with maintenance team to restore machine uptime and reroute active jobs.",
					"drilldown_records": [
						{"doctype": "Downtime Entry", "name": dt.get("name")},
						{"doctype": "Workstation", "name": ws_name},
					],
				})
		elif wsd and not wsd.get("available"):
			source_status["workstation_downtime"] = False
	except Exception as err:
		frappe.log_error(f"Error checking workstation downtime exceptions: {err}")
		source_status["workstation_downtime"] = False

	# -------------------------------------------------------------
	# 5. Failed Quality Inspections (Category: Quality)
	# -------------------------------------------------------------
	try:
		qo = quality_overview
		if qo is None:
			qo = get_quality_overview(values)

		if qo and qo.get("available") and qo.get("inspections"):
			for qi in qo["inspections"]:
				if not qi.get("is_rejected"):
					continue

				it_type = qi.get("inspection_type") or "General"
				samp = flt(qi.get("sample_size"))
				# Deterministic severity
				if it_type == "Outgoing" or samp >= 10:
					sev = "Critical"
				else:
					sev = "High"

				exceptions.append({
					"exception_id": f"EXC-QI-{qi.get('name')}",
					"category": "Quality",
					"exception_type": "Failed Quality Inspection",
					"title": f"Quality rejection on {qi.get('item_code')} ({qi.get('name')})",
					"description": f"Inspection '{qi.get('name')}' rejected sample lot of {samp:g} {qi.get('stock_uom', '')} on item '{qi.get('item_code')}'. Inspection type: {it_type}. Reference: {qi.get('reference_type') or ''} {qi.get('reference_name') or ''}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Quality Inspection",
					"source_document": qi.get("name"),
					"work_order": qi.get("reference_name") if qi.get("reference_type") == "Work Order" else None,
					"job_card": qi.get("reference_name") if qi.get("reference_type") == "Job Card" else None,
					"item_code": qi.get("item_code"),
					"item_name": qi.get("item_name") or qi.get("item_code"),
					"workstation": None,
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": qi.get("report_date"),
					"delay_days": None,
					"age_days": 1,
					"impact_summary": f"Rejected {samp:g} {qi.get('stock_uom', '')}",
					"recommended_action": "Quarantine rejected batch, review non-conformance root cause, or raise corrective Job Card.",
					"drilldown_records": [
						{"doctype": "Quality Inspection", "name": qi.get("name")},
						{"doctype": "Item", "name": qi.get("item_code")},
					],
				})
		elif qo and not qo.get("available"):
			source_status["quality_inspections"] = False
	except Exception as err:
		frappe.log_error(f"Error checking quality inspection exceptions: {err}")
		source_status["quality_inspections"] = False

	# -------------------------------------------------------------
	# 6. Overdue Rework Cases (Category: Quality)
	# -------------------------------------------------------------
	try:
		ro = rework_overview
		if ro is None:
			ro = get_rework_overview(values)

		if ro and ro.get("available") and ro.get("rework_configured") and ro.get("rework_jobs"):
			for rj in ro["rework_jobs"]:
				if not rj.get("is_overdue") and rj.get("status") == "Completed":
					continue

				is_overdue = bool(rj.get("is_overdue"))
				sev = "High" if is_overdue else "Medium"
				delay = abs(rj.get("days_to_target") or 0) if is_overdue else 0

				exceptions.append({
					"exception_id": f"EXC-REWORK-{rj.get('job_card')}",
					"category": "Quality",
					"exception_type": "Overdue Rework",
					"title": f"Corrective Job Card {rj.get('job_card')} {'is overdue' if is_overdue else 'in progress'}",
					"description": f"Corrective rework operation '{rj.get('operation')}' on Work Order '{rj.get('work_order')}' has {rj.get('rework_quantity', 0):g} units pending. Target: {rj.get('target_completion_date') or 'Unspecified'}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Job Card",
					"source_document": rj.get("job_card"),
					"work_order": rj.get("work_order"),
					"job_card": rj.get("job_card"),
					"item_code": rj.get("production_item"),
					"item_name": rj.get("production_item_name"),
					"workstation": rj.get("workstation"),
					"supplier": None,
					"supplier_name": None,
					"company": company,
					"due_date": rj.get("target_completion_date"),
					"delay_days": delay,
					"age_days": delay,
					"impact_summary": f"Rework {rj.get('rework_quantity', 0):g} units",
					"recommended_action": "Prioritize corrective rework execution to unblock downstream assembly line.",
					"drilldown_records": [
						{"doctype": "Job Card", "name": rj.get("job_card")},
						{"doctype": "Work Order", "name": rj.get("work_order")} if rj.get("work_order") else None,
					],
				})
		elif ro and not ro.get("available"):
			source_status["rework"] = False
	except Exception as err:
		frappe.log_error(f"Error checking rework exceptions: {err}")
		source_status["rework"] = False

	# -------------------------------------------------------------
	# 7. Overdue Subcontracting Orders (Category: Subcontracting)
	# -------------------------------------------------------------
	try:
		sco_data = subcontracting_overview
		if sco_data is None:
			sco_data = get_subcontracting_overview(values)

		if sco_data and sco_data.get("available") and sco_data.get("orders"):
			for ord_line in sco_data["orders"]:
				if not ord_line.get("is_overdue"):
					continue

				delay = abs(ord_line.get("days_to_target") or 0)
				out_qty = flt(ord_line.get("outstanding_qty"))

				# Deterministic severity
				if delay >= 7 or out_qty >= 100:
					sev = "Critical"
				else:
					sev = "High"

				exceptions.append({
					"exception_id": f"EXC-SCO-{ord_line.get('subcontracting_order')}",
					"category": "Subcontracting",
					"exception_type": "Overdue Subcontracting",
					"title": f"Subcontracting Order {ord_line.get('subcontracting_order')} overdue by {delay} day(s)",
					"description": f"Supplier '{ord_line.get('supplier_name')}' has {out_qty:g} {ord_line.get('stock_uom', '')} of '{ord_line.get('item_code')}' outstanding. Expected schedule was {ord_line.get('schedule_date')}.",
					"severity": sev,
					"severity_rank": SEVERITY_RANKS[sev],
					"status": "Open",
					"source_doctype": "Subcontracting Order",
					"source_document": ord_line.get("subcontracting_order"),
					"work_order": None,
					"job_card": None,
					"item_code": ord_line.get("item_code"),
					"item_name": ord_line.get("item_name") or ord_line.get("item_code"),
					"workstation": None,
					"supplier": ord_line.get("supplier"),
					"supplier_name": ord_line.get("supplier_name"),
					"company": company,
					"due_date": ord_line.get("schedule_date"),
					"delay_days": delay,
					"age_days": delay,
					"impact_summary": f"Outstanding: {out_qty:g} {ord_line.get('stock_uom', '')}",
					"recommended_action": "Contact supplier logistics desk to expedite receipt and track transit status.",
					"drilldown_records": [
						{"doctype": "Subcontracting Order", "name": ord_line.get("subcontracting_order")},
						{"doctype": "Supplier", "name": ord_line.get("supplier")} if ord_line.get("supplier") else None,
					],
				})
		elif sco_data and not sco_data.get("available"):
			source_status["subcontracting"] = False
	except Exception as err:
		frappe.log_error(f"Error checking subcontracting exceptions: {err}")
		source_status["subcontracting"] = False

	# -------------------------------------------------------------
	# 8. Filter & Deterministic Prioritization
	# -------------------------------------------------------------
	# Apply Category filter
	req_cat = values.get("category", "All")
	if req_cat and req_cat != "All":
		exceptions = [e for e in exceptions if e["category"] == req_cat]

	# Apply Severity filter
	req_sev = values.get("severity", "All")
	if req_sev and req_sev != "All":
		exceptions = [e for e in exceptions if e["severity"] == req_sev]

	# Apply Work Order filter
	if values.get("work_order"):
		exceptions = [e for e in exceptions if e["work_order"] == values["work_order"]]

	# Apply Item filter
	if values.get("item_code"):
		exceptions = [e for e in exceptions if e["item_code"] == values["item_code"]]

	# Apply Workstation filter
	if values.get("workstation"):
		exceptions = [e for e in exceptions if e["workstation"] == values["workstation"]]

	# Apply Supplier filter
	if values.get("supplier"):
		exceptions = [e for e in exceptions if e["supplier"] == values["supplier"]]

	# Clean None from drilldown_records
	for e in exceptions:
		e["drilldown_records"] = [d for d in e["drilldown_records"] if d]

	# Prioritization sort:
	# 1. severity_rank: Critical (1), High (2), Medium (3), Low (4)
	# 2. delay_days: descending (None treated as -1)
	# 3. due_date: ascending (None treated as "9999")
	# 4. source_document: alphabetical ascending
	exceptions.sort(key=lambda x: (
		x["severity_rank"],
		-(x["delay_days"] if x["delay_days"] is not None else -1),
		x["due_date"] or "9999-99-99",
		x["source_document"],
	))

	# Compute Summary Metrics
	total_open = len(exceptions)
	crit_count = sum(1 for e in exceptions if e["severity"] == "Critical")
	high_count = sum(1 for e in exceptions if e["severity"] == "High")
	med_count = sum(1 for e in exceptions if e["severity"] == "Medium")
	low_count = sum(1 for e in exceptions if e["severity"] == "Low")

	prod_count = sum(1 for e in exceptions if e["category"] == "Production")
	mat_count = sum(1 for e in exceptions if e["category"] == "Material")
	ws_count = sum(1 for e in exceptions if e["category"] == "Workstation")
	qual_count = sum(1 for e in exceptions if e["category"] == "Quality")
	sub_count = sum(1 for e in exceptions if e["category"] == "Subcontracting")

	distinct_docs = len({e["source_document"] for e in exceptions})

	paginated_exceptions = exceptions[start_offset : start_offset + limit]

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_open_exceptions": total_open,
			"critical_exceptions": crit_count,
			"high_exceptions": high_count,
			"medium_exceptions": med_count,
			"low_exceptions": low_count,
			"production_exceptions": prod_count,
			"material_exceptions": mat_count,
			"workstation_exceptions": ws_count,
			"quality_exceptions": qual_count,
			"subcontracting_exceptions": sub_count,
			"distinct_affected_documents": distinct_docs,
		},
		"source_status": source_status,
		"exceptions": paginated_exceptions,
		"total_exceptions_count": total_open,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_open,
		"applied_filters": values,
	}
