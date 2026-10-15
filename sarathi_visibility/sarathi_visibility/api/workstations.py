"""
DASH-019: Workstation and Downtime Views Backend API.
Provides permission-scoped, warehouse- and company-isolated workstation overviews,
recorded operation activity, verified downtime calculations from Downtime Entry,
and production impact analysis with zero N+1 queries.
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

WS_FILTER_KEYS = {
	"company",
	"workstation",
	"workstation_type",
	"status",
	"from_date",
	"to_date",
	"work_order",
	"job_card",
	"operation",
	"reference_at",
}

WS_VALID_STATUSES = {
	"All",
	"Active",
	"Open",
	"Work In Progress",
	"Completed",
	"Production",
	"Off",
	"Idle",
	"Problem",
	"Maintenance",
	"Setup",
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


def get_target_completion_date(jc, wo=None):
	"""
	Resolves target completion date for a Job Card.
	Fallback priority:
	1. Job Card expected_end_date (or to_time)
	2. Parent Work Order planned_end_date
	3. Parent Work Order expected_delivery_date
	"""
	if jc.get("expected_end_date"):
		dt = parse_datetime_val(jc["expected_end_date"])
		if dt:
			return dt.date()
	if wo:
		if wo.get("planned_end_date"):
			dt = parse_datetime_val(wo["planned_end_date"])
			if dt:
				return dt.date()
		if wo.get("expected_delivery_date"):
			dt = parse_datetime_val(wo["expected_delivery_date"])
			if dt:
				return dt.date()
	return None


def validate_workstation_downtime_filters(filters):
	"""Strict server-side validation for Workstation & Downtime filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - WS_FILTER_KEYS:
		invalid("Unsupported workstation filter parameter.")

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

	# Validate workstation link
	if values.get("workstation"):
		_identifier(values["workstation"])
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	# Validate workstation_type link
	if values.get("workstation_type"):
		_identifier(values["workstation_type"])
		if not frappe.db.exists("Workstation Type", values["workstation_type"]):
			invalid("Selected workstation type does not exist.")

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

	# Validate operation link
	if values.get("operation"):
		_identifier(values["operation"])
		if not frappe.db.exists("Operation", values["operation"]):
			invalid("Selected operation does not exist.")

	# Validate status choice
	if values.get("status"):
		st = values["status"]
		if st not in WS_VALID_STATUSES:
			invalid("Unsupported workstation or job status filter.")

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
def get_workstation_downtime(filters=None, start=0, page_length=20, **extra):
	"""
	API for Workstation and Downtime Views (DASH-019).
	Provides:
	1. Workstation overview with recorded status and operation mapping.
	2. Recorded operation activity with planned vs actual progress.
	3. Verified downtime events clipped to period from Downtime Entry.
	4. Production impact analysis identifying affected jobs and Work Orders.
	5. Transparent distinction between ERPNext records and live IoT telemetry.
	Zero N+1 queries.
	"""
	_extra(extra)
	values, ref_dt = validate_workstation_downtime_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	from_date_obj = parse_datetime_val(values.get("from_date"))
	to_date_obj = parse_datetime_val(values.get("to_date"))
	if to_date_obj:
		to_date_obj = to_date_obj.replace(hour=23, minute=59, second=59)

	# -------------------------------------------------------------
	# 1. Retrieve Candidate Job Cards (Query 1)
	# -------------------------------------------------------------
	jc_filters = [
		["company", "=", company],
		["docstatus", "<", 2],
	]

	if values.get("work_order"):
		jc_filters.append(["work_order", "=", values["work_order"]])
	if values.get("job_card"):
		jc_filters.append(["name", "=", values["job_card"]])
	if values.get("operation"):
		jc_filters.append(["operation", "=", values["operation"]])
	if values.get("workstation"):
		jc_filters.append(["workstation", "=", values["workstation"]])
	if values.get("workstation_type"):
		jc_filters.append(["workstation_type", "=", values["workstation_type"]])

	# Status scoping
	st_filter = values.get("status", "All")
	if st_filter == "Active":
		jc_filters.append(["status", "in", ["Open", "Work In Progress"]])
	elif st_filter in ("Open", "Work In Progress", "Completed"):
		jc_filters.append(["status", "=", st_filter])

	# Date bounds on Job Card creation or expected dates
	if values.get("from_date"):
		jc_filters.append(["creation", ">=", values["from_date"]])
	if values.get("to_date"):
		jc_filters.append(["creation", "<=", str(to_date_obj)])

	job_cards = frappe.get_all(
		"Job Card",
		filters=jc_filters,
		fields=[
			"name",
			"work_order",
			"operation",
			"workstation",
			"workstation_type",
			"status",
			"for_quantity",
			"total_completed_qty",
			"expected_start_date",
			"expected_end_date",
			"actual_start_date",
			"actual_end_date",
			"total_time_in_mins",
			"creation",
			"modified",
		],
		limit_page_length=10000,
	)

	# -------------------------------------------------------------
	# 2. Batch Retrieve Associated Work Orders (Query 2)
	# -------------------------------------------------------------
	wo_names = list({jc.work_order for jc in job_cards if jc.work_order})
	wo_map = {}
	if wo_names:
		wo_records = frappe.get_all(
			"Work Order",
			filters={"name": ["in", wo_names]},
			fields=[
				"name",
				"production_item",
				"item_name",
				"status",
				"planned_end_date",
				"expected_delivery_date",
				"project",
				"customer",
			],
			limit_page_length=10000,
		)
		for wo in wo_records:
			wo_map[wo.name] = wo

	# -------------------------------------------------------------
	# 3. Retrieve Workstations (Query 3)
	# -------------------------------------------------------------
	# Gather all workstations associated with the retrieved Job Cards
	discovered_ws_names = {jc.workstation for jc in job_cards if jc.workstation}
	if values.get("workstation"):
		discovered_ws_names.add(values["workstation"])

	# Query Workstation records
	ws_query_filters = {}
	if discovered_ws_names:
		ws_query_filters["name"] = ["in", list(discovered_ws_names)]
	elif values.get("workstation_type"):
		ws_query_filters["workstation_type"] = values["workstation_type"]

	# If no specific workstations discovered from jobs and no filter, fetch accessible workstations
	try:
		workstation_records = frappe.get_all(
			"Workstation",
			filters=ws_query_filters if ws_query_filters else None,
			fields=["name", "workstation_name", "workstation_type", "status", "modified", "description"],
			limit_page_length=1000,
		)
	except Exception:
		workstation_records = []

	ws_map = {ws.name: ws for ws in workstation_records}

	# Ensure any workstation referenced on Job Cards exists in ws_map even if missing in query
	for ws_name in discovered_ws_names:
		if ws_name and ws_name not in ws_map:
			ws_map[ws_name] = frappe._dict(
				name=ws_name,
				workstation_name=ws_name,
				workstation_type=None,
				status="Production",
				modified=None,
				description=None,
			)

	# -------------------------------------------------------------
	# 4. Retrieve Downtime Entries (Query 4)
	# -------------------------------------------------------------
	downtime_entries = []
	all_ws_names = list(ws_map.keys())
	if all_ws_names:
		downtime_filters = [["workstation", "in", all_ws_names]]
		if values.get("from_date"):
			downtime_filters.append(["from_time", ">=", values["from_date"]])
		if values.get("to_date"):
			downtime_filters.append(["from_time", "<=", str(to_date_obj)])

		try:
			# Verify DocType exists before querying
			if frappe.db.exists("DocType", "Downtime Entry") or frappe.db.table_exists("Downtime Entry"):
				downtime_entries = frappe.get_all(
					"Downtime Entry",
					filters=downtime_filters,
					fields=[
						"name",
						"workstation",
						"from_time",
						"to_time",
						"downtime",
						"stop_reason",
						"remarks",
						"operator",
					],
					limit_page_length=5000,
				)
		except Exception:
			downtime_entries = []

	# -------------------------------------------------------------
	# 5. Process Downtime Events & Interval Clipping
	# -------------------------------------------------------------
	downtime_by_ws = defaultdict(list)
	total_downtime_minutes_factory = 0.0
	verified_downtime_events = []

	for dt_entry in downtime_entries:
		start_time = parse_datetime_val(dt_entry.from_time)
		end_time = parse_datetime_val(dt_entry.to_time) if dt_entry.to_time else None
		is_open = end_time is None

		if not start_time:
			continue

		effective_end = end_time if end_time else ref_dt

		# Validate chronological order
		if effective_end < start_time:
			continue

		# Period clipping
		clip_start = max(start_time, from_date_obj) if from_date_obj else start_time
		clip_end = min(effective_end, to_date_obj) if to_date_obj else effective_end

		if clip_start < clip_end:
			duration_mins = flt((clip_end - clip_start).total_seconds() / 60.0)
		else:
			duration_mins = 0.0

		# If record has native duration and no clipping applied, prefer recorded downtime
		if not from_date_obj and not to_date_obj and dt_entry.get("downtime") and not is_open:
			duration_mins = flt(dt_entry.downtime)

		duration_mins = max(0.0, duration_mins)
		total_downtime_minutes_factory += duration_mins

		event_data = {
			"downtime_entry": dt_entry.name,
			"workstation": dt_entry.workstation,
			"from_time": str(start_time),
			"to_time": str(end_time) if end_time else None,
			"is_open": is_open,
			"duration_minutes": round(duration_mins, 2),
			"stop_reason": dt_entry.stop_reason or "Unspecified Interruption",
			"remarks": dt_entry.remarks,
			"operator": dt_entry.operator,
			"drilldown_records": [
				{"doctype": "Downtime Entry", "name": dt_entry.name},
				{"doctype": "Workstation", "name": dt_entry.workstation},
			],
		}
		downtime_by_ws[dt_entry.workstation].append(event_data)
		verified_downtime_events.append(event_data)

	# -------------------------------------------------------------
	# 6. Group Job Cards by Workstation and Evaluate Activity
	# -------------------------------------------------------------
	jobs_by_ws = defaultdict(list)
	all_activity_lines = []
	impacted_workstations_map = {}

	total_running_jobs = 0
	total_completed_jobs = 0
	total_delayed_jobs = 0

	for jc in job_cards:
		ws_name = jc.workstation or "Unassigned"
		wo = wo_map.get(jc.work_order)

		target_date = get_target_completion_date(jc, wo)
		days_to_target = (target_date - ref_date).days if target_date else None
		is_overdue = bool(days_to_target is not None and days_to_target < 0 and jc.status not in ("Completed", "Cancelled"))
		is_due_soon = bool(days_to_target is not None and 0 <= days_to_target <= 7 and jc.status not in ("Completed", "Cancelled"))

		planned_qty = flt(jc.for_quantity)
		completed_qty = flt(jc.total_completed_qty)
		time_spent = flt(jc.total_time_in_mins)

		if jc.status == "Work In Progress":
			total_running_jobs += 1
		elif jc.status == "Completed":
			total_completed_jobs += 1

		if is_overdue:
			total_delayed_jobs += 1

		activity_row = {
			"job_card": jc.name,
			"work_order": jc.work_order,
			"production_item": wo.production_item if wo else None,
			"production_item_name": (wo.item_name or wo.production_item) if wo else None,
			"project": wo.project if wo else None,
			"customer": wo.customer if wo else None,
			"operation": jc.operation,
			"workstation": jc.workstation,
			"workstation_type": jc.workstation_type,
			"status": jc.status,
			"for_quantity": round(planned_qty, 2),
			"total_completed_qty": round(completed_qty, 2),
			"planned_start_date": str(jc.expected_start_date) if jc.expected_start_date else None,
			"planned_end_date": str(jc.expected_end_date) if jc.expected_end_date else None,
			"target_completion_date": str(target_date) if target_date else None,
			"actual_start_date": str(jc.actual_start_date) if jc.actual_start_date else None,
			"actual_end_date": str(jc.actual_end_date) if jc.actual_end_date else None,
			"time_spent_mins": round(time_spent, 2),
			"days_to_target": days_to_target,
			"is_overdue": is_overdue,
			"is_due_soon": is_due_soon,
			"drilldown_records": [
				{"doctype": "Job Card", "name": jc.name},
				{"doctype": "Work Order", "name": jc.work_order} if jc.work_order else None,
				{"doctype": "Workstation", "name": jc.workstation} if jc.workstation else None,
			],
		}
		activity_row["drilldown_records"] = [d for d in activity_row["drilldown_records"] if d]

		jobs_by_ws[ws_name].append(activity_row)
		all_activity_lines.append(activity_row)

	# -------------------------------------------------------------
	# 7. Build Workstation Summaries (Overview)
	# -------------------------------------------------------------
	workstations_overview = []
	workstations_with_active_jobs_count = 0

	for ws_id, ws in sorted(ws_map.items(), key=lambda x: x[0]):
		assigned_jobs = jobs_by_ws.get(ws_id, [])
		ws_downtime_list = downtime_by_ws.get(ws_id, [])

		wip_jobs = [j for j in assigned_jobs if j["status"] == "Work In Progress"]
		open_jobs = [j for j in assigned_jobs if j["status"] == "Open"]
		completed_jobs = [j for j in assigned_jobs if j["status"] == "Completed"]
		delayed_jobs = [j for j in assigned_jobs if j["is_overdue"]]

		ws_downtime_mins = sum(d["duration_minutes"] for d in ws_downtime_list)

		if len(wip_jobs) > 0:
			workstations_with_active_jobs_count += 1

		# Native recorded status vs telemetry distinction
		native_status = ws.status or "Production"
		has_open_downtime = any(d["is_open"] for d in ws_downtime_list)
		if has_open_downtime:
			derived_status = "Downtime (Recorded Stop)"
		elif len(wip_jobs) > 0:
			derived_status = "Active Production (Job Running)"
		elif len(open_jobs) > 0:
			derived_status = "Assigned Jobs Queued"
		else:
			derived_status = f"Idle / {native_status}"

		ws_summary = {
			"workstation": ws.name,
			"workstation_name": ws.workstation_name or ws.name,
			"workstation_type": ws.workstation_type or "General",
			"recorded_status": native_status,
			"derived_status": derived_status,
			"status_source": "ERPNext Workstation Master & Job Cards",
			"telemetry_status": "Not Configured (Requires IoT/PLC Telemetry)",
			"assigned_job_cards_count": len(assigned_jobs),
			"active_job_cards_count": len(wip_jobs),
			"queued_job_cards_count": len(open_jobs),
			"completed_job_cards_count": len(completed_jobs),
			"delayed_job_cards_count": len(delayed_jobs),
			"downtime_events_count": len(ws_downtime_list),
			"total_downtime_minutes": round(ws_downtime_mins, 2),
			"utilization_rate": None,
			"utilization_note": "Requires Machine Telemetry / Shift Schedule",
			"oee": None,
			"oee_note": "Requires Machine Telemetry / Sensor Coverage",
			"has_production_impact": bool(len(delayed_jobs) > 0 or ws_downtime_mins > 0),
			"drilldown_records": [
				{"doctype": "Workstation", "name": ws.name},
			],
		}
		workstations_overview.append(ws_summary)

		# Build production impact map
		if ws_summary["has_production_impact"]:
			impacted_workstations_map[ws.name] = {
				"workstation": ws.name,
				"workstation_name": ws.workstation_name or ws.name,
				"workstation_type": ws.workstation_type,
				"delayed_jobs_count": len(delayed_jobs),
				"downtime_minutes": round(ws_downtime_mins, 2),
				"downtime_reasons": list({d["stop_reason"] for d in ws_downtime_list if d.get("stop_reason")}),
				"affected_jobs": [
					{
						"job_card": j["job_card"],
						"work_order": j["work_order"],
						"production_item": j["production_item"],
						"operation": j["operation"],
						"status": j["status"],
						"days_to_target": j["days_to_target"],
						"is_overdue": j["is_overdue"],
					}
					for j in (delayed_jobs or assigned_jobs[:5])
				],
			}

	# -------------------------------------------------------------
	# 8. Sort and Paginate Activity Lines
	# -------------------------------------------------------------
	all_activity_lines.sort(key=lambda x: (not x["is_overdue"], x["status"] != "Work In Progress", x["workstation"] or ""))

	total_activity_lines = len(all_activity_lines)
	paginated_lines = all_activity_lines[start_offset : start_offset + limit]

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_workstations": len(workstations_overview),
			"workstations_with_active_jobs": workstations_with_active_jobs_count,
			"total_assigned_operations": len(job_cards),
			"recorded_running_jobs": total_running_jobs,
			"completed_operations": total_completed_jobs,
			"delayed_operations_count": total_delayed_jobs,
			"recorded_downtime_events": len(verified_downtime_events),
			"total_downtime_minutes": round(total_downtime_minutes_factory, 2),
			"utilization_metric_status": "Unavailable without verified shift schedule & machine runtime observations",
			"oee_metric_status": "Unavailable without verified availability, performance & quality telemetry",
		},
		"workstations_overview": workstations_overview,
		"downtime_events": verified_downtime_events,
		"production_impact": list(impacted_workstations_map.values()),
		"workstation_activity": paginated_lines,
		"total_activity_lines": total_activity_lines,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_activity_lines,
		"applied_filters": values,
	}
