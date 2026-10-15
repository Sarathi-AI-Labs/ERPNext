"""
DASH-024: Assigned-Job and Current-Operation API.
Provides secure, permission-aware, read-focused backend APIs for the Shop-Floor
Supervisor & Operator Dashboard in Sarathi Industrial Control Tower.
"""
from datetime import date, datetime
import re

import frappe
from frappe import _
from frappe.utils import cint, flt, get_datetime, getdate, now_datetime

from sarathi_visibility.api.access import (
	check_record,
	check_shop_job,
	deny,
	has_capability,
	require_session,
)
from sarathi_visibility.api.data_helpers import (
	_date,
	_extra,
	_identifier,
	_parse,
	invalid,
	pagination,
	read_errors,
)

SHOPFLOOR_FILTER_KEYS = {
	"company",
	"status",
	"work_order",
	"production_item",
	"item_code",
	"operation",
	"workstation",
	"from_date",
	"to_date",
	"search",
	"employee",
	"employee_id",
}

VALID_STATUSES = {"All", "Open", "Work In Progress", "Completed", "Blocked"}

JC_SORT_FIELDS = {
	"name",
	"expected_start_date",
	"expected_end_date",
	"actual_start_date",
	"creation",
	"modified",
	"operation",
	"workstation",
	"sequence_id",
}


def validate_shopfloor_filters(filters):
	"""Strict allowlist validation for shop-floor workboard queries."""
	require_session()
	if not (has_capability("shop") or has_capability("production")):
		deny()

	values = _parse(filters)
	if set(values) - SHOPFLOOR_FILTER_KEYS:
		invalid("Unsupported shop-floor filter parameter.")

	status = values.get("status")
	if status and status not in VALID_STATUSES:
		invalid(f"Invalid status filter. Must be one of: {', '.join(sorted(VALID_STATUSES))}")

	# Validate dates
	for key in ("from_date", "to_date"):
		if key in values and values[key]:
			_date(values[key])

	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate record links
	if values.get("workstation"):
		_identifier(values["workstation"])
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	if values.get("work_order"):
		_identifier(values["work_order"])
		if not frappe.db.exists("Work Order", values["work_order"]):
			invalid("Selected Work Order does not exist.")
		check_record("Work Order", values["work_order"])

	if values.get("company"):
		_identifier(values["company"])
		if not frappe.db.exists("Company", values["company"]):
			invalid("Selected company does not exist.")
		check_record("Company", values["company"])

	if values.get("employee"):
		_identifier(values["employee"])
	if values.get("employee_id"):
		_identifier(values["employee_id"])

	return values


def resolve_shopfloor_context(user=None):
	"""
	Authoritatively resolves the authenticated user's shop-floor context and eligible Job Cards.
	Enforces role boundaries:
	- Operator: Strict direct assignment via open ToDo or linked active Employee.
	- Supervisor: Workstations in User Permission + direct ToDo assignments.
	- Manager: Company-wide production scope.
	"""
	user = user or frappe.session.user
	user_roles = set(frappe.get_roles(user))

	is_supervisor = "Sarathi Supervisor" in user_roles
	is_operator = "Sarathi Operator" in user_roles
	is_manager = has_capability("production", user)

	user_name = frappe.utils.get_fullname(user) or user
	employee = None
	employee_id = None
	employee_name = None
	department = None
	designation = None

	if frappe.db.table_exists("Employee"):
		emp_rows = frappe.get_all(
			"Employee",
			filters={"user_id": user, "status": "Active"},
			fields=["name", "employee_name", "department", "designation", "company"],
			limit_page_length=1,
		)
		if emp_rows:
			employee = emp_rows[0]
			employee_id = employee.name
			employee_name = employee.employee_name
			department = employee.department
			designation = employee.designation

	role_label = (
		"Production Manager" if is_manager else ("Shop-Floor Supervisor" if is_supervisor else "Machine Operator")
	)

	user_context = {
		"user_id": user,
		"user_name": user_name,
		"role_label": role_label,
		"is_operator": is_operator,
		"is_supervisor": is_supervisor,
		"is_manager": is_manager,
		"employee_id": employee_id,
		"employee_name": employee_name,
		"department": department,
		"designation": designation,
	}

	eligible_jc_names = set()
	unconfigured_reason = None

	if is_manager:
		# Production Manager: full company-level visibility
		all_manager_jcs = frappe.get_all("Job Card", filters=[["docstatus", "<", 2]], pluck="name", limit_page_length=2000)
		eligible_jc_names.update(all_manager_jcs)

	elif is_supervisor:
		# Supervisor: check workstation scope in User Permissions
		user_perms = frappe.permissions.get_user_permissions(user).get("Workstation", [])
		supervisor_workstations = [
			r.get("doc") for r in user_perms
			if r.get("doc") and r.get("applicable_for") in (None, "", "Job Card")
		]

		# Direct ToDo assignments to the supervisor
		todo_jcs = frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "Job Card",
				"allocated_to": user,
				"status": "Open",
			},
			pluck="reference_name",
			limit_page_length=500,
		)
		eligible_jc_names.update(todo_jcs)

		if supervisor_workstations:
			station_jcs = frappe.get_all(
				"Job Card",
				filters={
					"workstation": ["in", supervisor_workstations],
					"docstatus": ["<", 2],
				},
				pluck="name",
				limit_page_length=500,
			)
			eligible_jc_names.update(station_jcs)

		if not eligible_jc_names:
			unconfigured_reason = (
				"No supervisor workstation scope or assigned Job Cards found. "
				"Supervisors require User Permissions for Workstation or explicit Job Card assignments."
			)

	else:
		# Machine Operator: Strict direct assignment only
		todo_jcs = frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "Job Card",
				"allocated_to": user,
				"status": "Open",
			},
			pluck="reference_name",
			limit_page_length=500,
		)
		eligible_jc_names.update(todo_jcs)

		if employee_id:
			emp_jcs = frappe.get_all(
				"Job Card",
				filters={
					"employee": employee_id,
					"docstatus": ["<", 2],
				},
				pluck="name",
				limit_page_length=500,
			)
			eligible_jc_names.update(emp_jcs)

		if not eligible_jc_names:
			unconfigured_reason = (
				"No jobs are currently assigned to you. In this ERPNext installation, "
				"operators receive work via explicit Frappe Assignments (ToDo) or Employee linking."
			)

	return user_context, eligible_jc_names, unconfigured_reason


def fetch_and_enrich_job_cards(eligible_jc_names, values, todo_user_map=None):
	"""
	Retrieves and enriches Job Card records with operational metrics, active downtime blockers,
	and quality rework notices. Applies server-side filters.
	"""
	if not eligible_jc_names:
		return []

	ref_date = now_datetime().date()

	jc_fields = [
		"name",
		"work_order",
		"production_item",
		"item_name",
		"operation",
		"workstation",
		"workstation_type",
		"status",
		"docstatus",
		"company",
		"for_quantity",
		"total_completed_qty",
		"transferred_qty",
		"stock_uom",
		"expected_start_date",
		"expected_end_date",
		"actual_start_date",
		"actual_end_date",
		"total_time_in_mins",
		"is_paused",
		"is_corrective_job_card",
		"quality_inspection",
		"sequence_id",
		"modified",
		"creation",
		"employee",
	]

	raw_jcs = frappe.get_all(
		"Job Card",
		filters={"name": ["in", list(eligible_jc_names)]},
		fields=jc_fields,
		order_by="expected_start_date asc, sequence_id asc, creation asc",
		limit_page_length=1000,
	)

	todo_user_map = todo_user_map or {}

	# Fetch active downtime stops if Workstations exist
	workstations = {j.workstation for j in raw_jcs if j.workstation}
	active_downtimes = {}
	if workstations and frappe.db.table_exists("Downtime Entry"):
		dt_records = frappe.get_all(
			"Downtime Entry",
			filters={"workstation": ["in", list(workstations)], "docstatus": 1},
			fields=["name", "workstation", "from_time", "to_time", "downtime_reason"],
			limit_page_length=200,
		)
		for d in dt_records:
			if not d.to_time:
				active_downtimes[d.workstation] = d

	fullname_cache = {}
	def _cached_fullname(u):
		if not u:
			return ""
		if u not in fullname_cache:
			fullname_cache[u] = frappe.utils.get_fullname(u)
		return fullname_cache[u]

	job_cards_list = []
	for j in raw_jcs:
		fq = flt(j.get("for_quantity") or 0.0)
		cq = flt(j.get("total_completed_qty") or 0.0)
		tq = flt(j.get("transferred_qty") or 0.0)
		comp_pct = round((cq / fq * 100.0), 1) if fq > 0 else (100.0 if j.get("status") == "Completed" else 0.0)
		rem_qty = max(0.0, fq - cq)

		exp_end = getdate(j.get("expected_end_date")) if j.get("expected_end_date") else None
		is_overdue = bool(exp_end and exp_end < ref_date and j.get("status") != "Completed")
		delay_days = (ref_date - exp_end).days if is_overdue and exp_end else 0

		assigned_user = todo_user_map.get(j.name)
		assigned_emp = j.get("employee")
		assigned_op_id = assigned_emp or assigned_user
		assigned_op_name = _cached_fullname(assigned_user) if assigned_user else (assigned_emp or "Unassigned")

		# Detect genuine blockers
		blocker = None
		if j.get("is_corrective_job_card"):
			blocker = {
				"has_blocker": True,
				"type": "Quality Rework",
				"severity": "High",
				"description": "Corrective rework operation required following quality rejection.",
				"source_doc": j.get("quality_inspection") or j.name,
			}
		elif j.workstation in active_downtimes:
			dt = active_downtimes[j.workstation]
			blocker = {
				"has_blocker": True,
				"type": "Workstation Downtime",
				"severity": "Critical",
				"description": f"Workstation {j.workstation} has active recorded downtime: {dt.downtime_reason or 'Breakdown'}.",
				"source_doc": dt.name,
			}
		elif j.get("status") == "On Hold" or j.get("is_paused"):
			blocker = {
				"has_blocker": True,
				"type": "Paused Operation",
				"severity": "Medium",
				"description": "Operation is currently paused on the shop floor.",
				"source_doc": j.name,
			}

		card = {
			"name": j.name,
			"work_order": j.work_order,
			"production_item": j.production_item,
			"item_name": j.item_name or j.production_item,
			"operation": j.operation,
			"workstation": j.workstation,
			"workstation_type": j.workstation_type,
			"status": j.status,
			"docstatus": j.docstatus,
			"company": j.company,
			"stock_uom": j.get("stock_uom") or "Nos",
			"for_quantity": fq,
			"total_completed_qty": cq,
			"remaining_qty": rem_qty,
			"transferred_qty": tq,
			"completion_percent": comp_pct,
			"sequence_id": j.get("sequence_id") or 0,
			"expected_start_date": str(j.expected_start_date) if j.expected_start_date else None,
			"expected_end_date": str(j.expected_end_date) if j.expected_end_date else None,
			"actual_start_date": str(j.actual_start_date) if j.actual_start_date else None,
			"actual_end_date": str(j.actual_end_date) if j.actual_end_date else None,
			"total_time_in_mins": flt(j.get("total_time_in_mins") or 0.0),
			"is_overdue": is_overdue,
			"delay_days": delay_days,
			"is_paused": bool(j.is_paused),
			"is_corrective": bool(j.is_corrective_job_card),
			"quality_inspection": j.quality_inspection,
			"has_blocker": bool(blocker),
			"blocker": blocker,
			"employee": assigned_emp,
			"assigned_user": assigned_user,
			"assigned_operator_id": assigned_op_id,
			"assigned_operator_name": assigned_op_name,
			"drill_down_link": f"/desk#Form/Job Card/{j.name}",
			"work_order_link": f"/desk#Form/Work Order/{j.work_order}" if j.work_order else None,
		}
		job_cards_list.append(card)

	# Apply server-side filters
	filtered = job_cards_list

	if values.get("company"):
		filtered = [j for j in filtered if j["company"] == values["company"]]

	if values.get("work_order"):
		filtered = [j for j in filtered if j["work_order"] == values["work_order"]]

	if values.get("workstation"):
		filtered = [j for j in filtered if j["workstation"] == values["workstation"]]

	if values.get("operation"):
		filtered = [j for j in filtered if j["operation"] == values["operation"]]

	item_filter = values.get("item_code") or values.get("production_item")
	if item_filter:
		filtered = [j for j in filtered if j["production_item"] == item_filter]

	emp_filter = values.get("employee") or values.get("employee_id")
	if emp_filter:
		filtered = [
			j for j in filtered
			if j.get("employee") == emp_filter
			or j.get("assigned_operator_id") == emp_filter
			or j.get("assigned_user") == emp_filter
		]

	if values.get("from_date"):
		filtered = [j for j in filtered if j["expected_start_date"] and j["expected_start_date"] >= values["from_date"]]

	if values.get("to_date"):
		filtered = [j for j in filtered if j["expected_start_date"] and j["expected_start_date"] <= values["to_date"]]

	status_filter = values.get("status", "All")
	if status_filter == "Blocked":
		filtered = [j for j in filtered if j["has_blocker"]]
	elif status_filter and status_filter != "All":
		filtered = [j for j in filtered if j["status"] == status_filter]

	if values.get("search"):
		q = values["search"].strip().lower()
		filtered = [
			j for j in filtered
			if q in str(j["name"]).lower()
			or q in str(j["work_order"] or "").lower()
			or q in str(j["operation"] or "").lower()
			or q in str(j["production_item"] or "").lower()
			or q in str(j["item_name"] or "").lower()
			or q in str(j["workstation"] or "").lower()
			or q in str(j["assigned_operator_name"] or "").lower()
		]

	return filtered


# =============================================================================
# API A — Retrieve Eligible Jobs
# =============================================================================
@frappe.whitelist(methods=["GET"])
@read_errors
def get_assigned_jobs(filters=None, start=0, page_length=20, sort_by="expected_start_date", sort_order="asc", **extra):
	"""
	API A (DASH-024): Returns paginated, authorized Job Cards eligible for the authenticated user.
	"""
	_extra(extra)
	values = validate_shopfloor_filters(filters)
	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()

	all_filtered_jobs = fetch_and_enrich_job_cards(eligible_jc_names, values)

	# Sort order
	reverse = (sort_order.lower() == "desc")
	sort_key = sort_by if sort_by in JC_SORT_FIELDS else "expected_start_date"
	all_filtered_jobs.sort(key=lambda j: (j.get(sort_key) is None, j.get(sort_key) or ""), reverse=reverse)

	start_offset, limit = pagination(start, page_length)
	total_count = len(all_filtered_jobs)
	paged_slice = all_filtered_jobs[start_offset:start_offset + limit]

	return {
		"success": True,
		"jobs": paged_slice,
		"total": total_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": (start_offset + limit) < total_count,
		"user_context": user_context,
		"unconfigured_reason": unconfigured_reason if not eligible_jc_names else None,
		"applied_filters": values,
	}


# =============================================================================
# API B — Retrieve Current Operation
# =============================================================================
@frappe.whitelist(methods=["GET"])
@read_errors
def get_current_operation(**extra):
	"""
	API B (DASH-024): Identifies the user's active operation(s) in Work In Progress.
	Returns all legitimately active operations without arbitrary selection.
	"""
	_extra(extra)
	require_session()
	if not (has_capability("shop") or has_capability("production")):
		deny()

	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()
	all_jobs = fetch_and_enrich_job_cards(eligible_jc_names, {})

	in_progress_jobs = [j for j in all_jobs if j["status"] == "Work In Progress"]

	# Check for open time logs on active operations (batched to prevent N+1 queries)
	if in_progress_jobs and frappe.db.table_exists("Job Card Time Log"):
		now_dt = now_datetime()
		op_names = [op["name"] for op in in_progress_jobs]
		active_logs = frappe.get_all(
			"Job Card Time Log",
			filters={"parent": ["in", op_names], "to_time": ["is", "not set"]},
			fields=["name", "parent", "from_time", "employee", "time_in_mins"],
			limit_page_length=max(10, len(op_names) * 2),
		)
		log_by_op = {}
		for log in active_logs:
			p = getattr(log, "parent", None) or (log.get("parent") if isinstance(log, dict) else None)
			if p and p not in log_by_op:
				log_by_op[p] = log
		for op in in_progress_jobs:
			if op["name"] in log_by_op:
				log = log_by_op[op["name"]]
				from_t = get_datetime(log.from_time) if getattr(log, "from_time", None) else None
				time_mins = getattr(log, "time_in_mins", 0.0)
				elapsed = round((now_dt - from_t).total_seconds() / 60.0, 1) if from_t else flt(time_mins)
				op["active_time_log"] = {
					"name": log.name,
					"from_time": str(getattr(log, "from_time", "")),
					"elapsed_mins": elapsed,
					"employee": getattr(log, "employee", None),
				}

	return {
		"success": True,
		"has_active_operation": bool(in_progress_jobs),
		"active_operations": in_progress_jobs,
		"current_operation": in_progress_jobs[0] if in_progress_jobs else None,
		"count": len(in_progress_jobs),
		"user_context": user_context,
		"unconfigured_reason": unconfigured_reason if not eligible_jc_names else None,
	}


# =============================================================================
# API C — Retrieve Eligible Next Jobs
# =============================================================================
@frappe.whitelist(methods=["GET"])
@read_errors
def get_next_jobs(filters=None, limit=5, **extra):
	"""
	API C (DASH-024): Returns upcoming waiting operations (status == 'Open') prioritized
	by expected start date, sequence_id, and creation date.
	"""
	_extra(extra)
	values = validate_shopfloor_filters(filters)
	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()

	all_jobs = fetch_and_enrich_job_cards(eligible_jc_names, values)
	open_jobs = [j for j in all_jobs if j["status"] == "Open"]

	# Prioritized by scheduled start date, routing sequence_id, and creation
	open_jobs.sort(key=lambda j: (j.get("expected_start_date") or "9999-99-99", j.get("sequence_id") or 9999, j.get("name")))

	max_limit = min(max(cint(limit), 1), 25)
	next_slice = open_jobs[:max_limit]

	return {
		"success": True,
		"next_jobs": next_slice,
		"total_waiting": len(open_jobs),
		"ordering_basis": "expected_start_date asc, sequence_id asc, name asc",
		"user_context": user_context,
		"unconfigured_reason": unconfigured_reason if not eligible_jc_names else None,
	}


# =============================================================================
# API D — Retrieve Workboard Summary
# =============================================================================
@frappe.whitelist(methods=["GET"])
@read_errors
def get_shop_floor_summary(filters=None, **extra):
	"""
	API D (DASH-024): Returns status counts and blocker totals based on unique eligible Job Cards.
	"""
	_extra(extra)
	values = validate_shopfloor_filters(filters)
	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()

	all_jobs = fetch_and_enrich_job_cards(eligible_jc_names, values)

	in_progress = sum(1 for j in all_jobs if j["status"] == "Work In Progress")
	waiting = sum(1 for j in all_jobs if j["status"] == "Open")
	completed = sum(1 for j in all_jobs if j["status"] == "Completed")
	blocked = sum(1 for j in all_jobs if j["has_blocker"])

	summary = {
		"total_assigned_jobs": len(all_jobs),
		"jobs_in_progress": in_progress,
		"waiting_jobs": waiting,
		"completed_jobs": completed,
		"blocked_jobs": blocked,
	}

	return {
		"success": True,
		"summary": summary,
		"user_context": user_context,
		"applied_filters": values,
		"unconfigured_reason": unconfigured_reason if not eligible_jc_names else None,
	}


# =============================================================================
# DASH-023 Integrated Workboard Endpoint
# =============================================================================
@frappe.whitelist(methods=["GET"])
@read_errors
def get_shopfloor_workboard(filters=None, **extra):
	"""
	Consolidated dashboard endpoint for DASH-023. Composes assigned jobs,
	active operations, next queued job, and blockers in a single round-trip.
	"""
	_extra(extra)
	values = validate_shopfloor_filters(filters)
	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()

	all_jobs = fetch_and_enrich_job_cards(eligible_jc_names, values)

	in_progress_jobs = [j for j in all_jobs if j["status"] == "Work In Progress"]
	open_jobs = [j for j in all_jobs if j["status"] == "Open"]
	open_jobs.sort(key=lambda j: (j.get("expected_start_date") or "9999-99-99", j.get("sequence_id") or 9999, j.get("name")))

	completed_count = sum(1 for j in all_jobs if j["status"] == "Completed")
	blocked_count = sum(1 for j in all_jobs if j["has_blocker"])

	all_blockers = [
		{
			"job_card": j["name"],
			"operation": j["operation"],
			"workstation": j["workstation"],
			"work_order": j["work_order"],
			**j["blocker"],
		}
		for j in all_jobs
		if j["has_blocker"] and j["blocker"]
	]

	summary = {
		"total_assigned_jobs": len(all_jobs),
		"jobs_in_progress": len(in_progress_jobs),
		"waiting_jobs": len(open_jobs),
		"completed_jobs": completed_count,
		"blocked_jobs": blocked_count,
	}

	return {
		"available": True,
		"user_context": user_context,
		"summary": summary,
		"active_operations": in_progress_jobs,
		"current_operation": in_progress_jobs[0] if in_progress_jobs else None,
		"next_queued_job": open_jobs[0] if open_jobs else None,
		"assigned_jobs": all_jobs,
		"total_filtered_jobs": len(all_jobs),
		"blockers": all_blockers,
		"unconfigured_reason": unconfigured_reason if not eligible_jc_names else None,
		"applied_filters": values,
		"capabilities": {
			"reporting_actions": True,
			"supervisor_team_overview": True,
		},
	}


# =============================================================================
# DASH-025: Shop-Floor Validated Reporting Actions
# =============================================================================

def authorize_and_get_job_card(job_card_name, require_write=True):
	"""
	Validates session, capability, existence, and caller's assignment boundary on Job Card.
	Returns (doc, user_context, employee_id).
	"""
	require_session()
	if not (has_capability("shop") or has_capability("production")):
		deny()

	if not job_card_name or not isinstance(job_card_name, str):
		frappe.throw("Job Card identifier is required.", frappe.ValidationError)

	_identifier(job_card_name)

	if not frappe.db.exists("Job Card", job_card_name):
		frappe.throw(f"Job Card {job_card_name} does not exist.", frappe.ValidationError)

	doc = frappe.get_doc("Job Card", job_card_name)
	perm_type = "write" if require_write else "read"
	frappe.has_permission("Job Card", perm_type, doc=doc, throw=True)

	user_context, eligible_jc_names, unconfigured_reason = resolve_shopfloor_context()
	if not user_context.get("is_manager"):
		if doc.name not in eligible_jc_names:
			deny()

	employee_id = user_context.get("employee_id")
	return doc, user_context, employee_id


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def start_job(job_card, **extra):
	"""
	Action A (DASH-025): Starts an eligible Job Card for the authenticated operator.
	Preserves native ERPNext sequence validation, material transfer checks, and open time logs.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus == 2:
		frappe.throw(f"Cancelled Job Card {doc.name} cannot be started.", frappe.ValidationError)
	if doc.docstatus == 1:
		frappe.throw(f"Job Card {doc.name} is already submitted.", frappe.ValidationError)
	if getattr(doc, "is_paused", 0):
		frappe.throw(f"Job Card {doc.name} is paused. Please use Resume Operation.", frappe.ValidationError)

	# Idempotency check: if already in WIP with an open log for this employee
	if doc.status == "Work In Progress":
		has_open_log = False
		if hasattr(doc, "time_logs") and doc.time_logs:
			for log in doc.time_logs:
				if not log.to_time and (not employee_id or log.employee == employee_id):
					has_open_log = True
					break
		if has_open_log:
			return {
				"success": True,
				"idempotent": True,
				"job_card": doc.name,
				"status": doc.status,
				"started_at": str(doc.actual_start_date or now_datetime()),
				"message": f"Job Card {doc.name} is already in progress.",
			}

	# Sequence validation
	if callable(getattr(doc, "validate_sequence_id", None)):
		doc.validate_sequence_id()

	# Material transfer check
	if callable(getattr(doc, "validate_transfer_qty", None)):
		doc.validate_transfer_qty()

	start_time = now_datetime()
	if callable(getattr(doc, "start_timer", None)):
		doc.start_timer(start_time=start_time, employees=employee_id)
	elif callable(getattr(doc, "add_time_logs", None)):
		doc.add_time_logs(from_time=start_time, employees=[{"employee": employee_id}] if employee_id else None)
		if callable(getattr(doc, "set_status", None)):
			doc.set_status(update_status=True)
	else:
		if callable(getattr(doc, "append", None)):
			doc.append("time_logs", {
				"from_time": start_time,
				"employee": employee_id,
				"completed_qty": 0.0,
			})
		doc.db_set("status", "Work In Progress")

	if not doc.actual_start_date:
		doc.db_set("actual_start_date", start_time)

	if doc.status != "Work In Progress":
		doc.db_set("status", "Work In Progress")

	return {
		"success": True,
		"job_card": doc.name,
		"status": "Work In Progress",
		"started_at": str(start_time),
		"employee": employee_id,
		"message": f"Job Card {doc.name} successfully started.",
	}


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def record_job_progress(job_card, completed_qty=0.0, pending_qty=0.0, process_loss_qty=0.0, remarks=None, **extra):
	"""
	Action B (DASH-025): Records progress / completed quantities on an active Job Card.
	Validates quantities against remaining limits and updates native time logs.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus != 0:
		frappe.throw(f"Cannot record progress on submitted or cancelled Job Card {doc.name}.", frappe.ValidationError)

	cq = flt(completed_qty)
	pq = flt(pending_qty)
	plq = flt(process_loss_qty)

	if cq < 0 or pq < 0 or plq < 0:
		frappe.throw("Quantities cannot be negative.", frappe.ValidationError)

	if cq == 0 and pq == 0 and plq == 0 and not remarks:
		frappe.throw("Please enter a valid completed quantity or remarks to record progress.", frappe.ValidationError)

	total_after = flt(doc.total_completed_qty) + cq
	target_qty = flt(doc.for_quantity)
	if target_qty > 0 and total_after > target_qty * 1.5:
		frappe.throw(
			f"Reported quantity ({cq}) brings total completed ({total_after}) beyond allowable limit for Job Card {doc.name}.",
			frappe.ValidationError,
		)

	now_dt = now_datetime()
	updated_log = False
	if getattr(doc, "time_logs", None):
		for log in doc.time_logs:
			if not log.to_time and (not employee_id or log.employee == employee_id):
				log.to_time = now_dt
				from_t = get_datetime(log.from_time) if log.from_time else now_dt
				log.time_in_mins = round((now_dt - from_t).total_seconds() / 60.0, 2)
				log.completed_qty = cq
				if callable(getattr(log, "db_update", None)):
					log.db_update()
				updated_log = True
				if callable(getattr(doc, "append", None)):
					doc.append("time_logs", {
						"from_time": now_dt,
						"employee": employee_id,
						"completed_qty": 0.0,
					})
				break

	if not updated_log and cq > 0 and callable(getattr(doc, "append", None)):
		doc.append("time_logs", {
			"from_time": now_dt,
			"to_time": now_dt,
			"time_in_mins": 0.0,
			"employee": employee_id,
			"completed_qty": cq,
		})

	if callable(getattr(doc, "validate_time_logs", None)):
		doc.validate_time_logs(save=True)
	else:
		doc.total_completed_qty = flt(doc.total_completed_qty) + cq
		doc.db_set("total_completed_qty", doc.total_completed_qty)

	if remarks and isinstance(remarks, str) and remarks.strip():
		clean_rem = remarks.strip()
		existing = (doc.remarks or "").strip()
		new_rem = f"{existing}\n[{now_dt.strftime('%Y-%m-%d %H:%M')}] {clean_rem}".strip()
		doc.db_set("remarks", new_rem)

	return {
		"success": True,
		"job_card": doc.name,
		"status": doc.status,
		"reported_qty": cq,
		"total_completed_qty": doc.total_completed_qty,
		"remaining_qty": max(0.0, flt(doc.for_quantity) - flt(doc.total_completed_qty)),
		"completion_percent": round((doc.total_completed_qty / doc.for_quantity * 100.0), 1) if doc.for_quantity > 0 else 0.0,
		"stock_uom": doc.get("stock_uom") or "Nos",
		"message": f"Successfully recorded {cq} {doc.get('stock_uom') or 'Nos'} on Job Card {doc.name}.",
	}


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def pause_job(job_card, **extra):
	"""
	Action C (DASH-025): Pauses an active Job Card. Sets is_paused = 1 and status = 'On Hold'.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus != 0:
		frappe.throw(f"Cannot pause Job Card {doc.name} in current docstatus ({doc.docstatus}).", frappe.ValidationError)

	if getattr(doc, "is_paused", 0) and doc.status == "On Hold":
		return {
			"success": True,
			"idempotent": True,
			"job_card": doc.name,
			"status": "On Hold",
			"is_paused": True,
			"message": f"Job Card {doc.name} is already paused.",
		}

	end_time = now_datetime()
	if callable(getattr(doc, "pause_job", None)):
		doc.pause_job(end_time=end_time)
	else:
		doc.db_set("is_paused", 1)
		doc.db_set("status", "On Hold")
		if getattr(doc, "time_logs", None):
			for log in doc.time_logs:
				if not log.to_time:
					log.to_time = end_time
					if callable(getattr(log, "db_update", None)):
						log.db_update()

	return {
		"success": True,
		"job_card": doc.name,
		"status": "On Hold",
		"is_paused": True,
		"paused_at": str(end_time),
		"message": f"Job Card {doc.name} paused.",
	}


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def resume_job(job_card, **extra):
	"""
	Action C (DASH-025): Resumes a paused Job Card. Sets is_paused = 0 and status = 'Work In Progress'.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus != 0:
		frappe.throw(f"Cannot resume Job Card {doc.name} in current docstatus ({doc.docstatus}).", frappe.ValidationError)

	if not getattr(doc, "is_paused", 0) and doc.status == "Work In Progress":
		return {
			"success": True,
			"idempotent": True,
			"job_card": doc.name,
			"status": "Work In Progress",
			"is_paused": False,
			"message": f"Job Card {doc.name} is already active.",
		}

	start_time = now_datetime()
	if callable(getattr(doc, "resume_job", None)):
		doc.resume_job(start_time=start_time)
	else:
		doc.db_set("is_paused", 0)
		doc.db_set("status", "Work In Progress")
		if callable(getattr(doc, "append", None)):
			doc.append("time_logs", {
				"from_time": start_time,
				"employee": employee_id,
				"completed_qty": 0.0,
			})

	return {
		"success": True,
		"job_card": doc.name,
		"status": "Work In Progress",
		"is_paused": False,
		"resumed_at": str(start_time),
		"message": f"Job Card {doc.name} resumed.",
	}


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def stop_job(job_card, completed_qty=0.0, **extra):
	"""
	Action C (DASH-025): Stops current working cycle / time log on a Job Card without final submission.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus != 0:
		frappe.throw(f"Cannot stop Job Card {doc.name} in current docstatus ({doc.docstatus}).", frappe.ValidationError)

	cq = flt(completed_qty)
	if cq < 0:
		frappe.throw("Completed quantity cannot be negative.", frappe.ValidationError)

	end_time = now_datetime()
	updated = False
	if getattr(doc, "time_logs", None):
		for log in doc.time_logs:
			if not log.to_time and (not employee_id or log.employee == employee_id):
				log.to_time = end_time
				from_t = get_datetime(log.from_time) if log.from_time else end_time
				log.time_in_mins = round((end_time - from_t).total_seconds() / 60.0, 2)
				if cq > 0:
					log.completed_qty = cq
				if callable(getattr(log, "db_update", None)):
					log.db_update()
				updated = True

	if callable(getattr(doc, "validate_time_logs", None)):
		doc.validate_time_logs(save=True)
	elif cq > 0:
		doc.total_completed_qty = flt(doc.total_completed_qty) + cq
		doc.db_set("total_completed_qty", doc.total_completed_qty)

	if getattr(doc, "is_paused", 0):
		doc.db_set("is_paused", 0)

	has_other_open = False
	if getattr(doc, "time_logs", None):
		has_other_open = any(not log.to_time for log in doc.time_logs)

	if not has_other_open:
		new_status = "Open" if flt(doc.total_completed_qty) < flt(doc.for_quantity) else "Work In Progress"
		doc.db_set("status", new_status)

	return {
		"success": True,
		"job_card": doc.name,
		"status": doc.status,
		"total_completed_qty": doc.total_completed_qty,
		"stopped_at": str(end_time),
		"message": f"Operation stopped on Job Card {doc.name}.",
	}


@frappe.whitelist(methods=["POST", "GET"])
@read_errors
def complete_job(job_card, completed_qty=None, pending_qty=0.0, process_loss_qty=0.0, auto_submit=True, **extra):
	"""
	Action D (DASH-025): Completes and submits an eligible Job Card.
	Validates quality inspections, material transfers, and quantity splits before calling native complete/submit.
	"""
	_extra(extra)
	doc, user_context, employee_id = authorize_and_get_job_card(job_card, require_write=True)

	if doc.docstatus == 1 and doc.status == "Completed":
		return {
			"success": True,
			"idempotent": True,
			"job_card": doc.name,
			"status": "Completed",
			"docstatus": 1,
			"message": f"Job Card {doc.name} is already completed.",
		}

	if doc.docstatus == 2:
		frappe.throw(f"Cancelled Job Card {doc.name} cannot be completed.", frappe.ValidationError)

	if getattr(doc, "is_paused", 0):
		frappe.throw(f"Job Card {doc.name} is on hold. Please resume before completing.", frappe.ValidationError)

	if doc.work_order and frappe.db.exists("Work Order", doc.work_order):
		wo_status = frappe.db.get_value("Work Order", doc.work_order, "status")
		if wo_status in ("Closed", "Stopped", "Cancelled"):
			frappe.throw(f"Cannot complete Job Card against {wo_status} Work Order {doc.work_order}.", frappe.ValidationError)

	if callable(getattr(doc, "validate_inspection", None)):
		doc.validate_inspection()

	if callable(getattr(doc, "validate_transfer_qty", None)):
		doc.validate_transfer_qty()

	rem_qty = max(0.0, flt(doc.for_quantity) - flt(doc.total_completed_qty))
	cq = flt(completed_qty if completed_qty is not None else rem_qty)
	pq = flt(pending_qty or 0.0)
	plq = flt(process_loss_qty or 0.0)

	if cq < 0 or pq < 0 or plq < 0:
		frappe.throw("Quantities cannot be negative.", frappe.ValidationError)

	accounted = cq + pq + plq
	if accounted <= 0 and flt(doc.for_quantity) > 0:
		frappe.throw("Completed, pending, or process loss quantity must be greater than zero.", frappe.ValidationError)

	end_time = now_datetime()
	if callable(getattr(doc, "complete_job_card", None)):
		doc.complete_job_card(
			qty=cq,
			for_quantity=accounted if accounted else doc.for_quantity,
			pending_qty=pq,
			process_loss_qty=plq,
			end_time=end_time,
			auto_submit=auto_submit,
		)
	else:
		doc.total_completed_qty = flt(doc.total_completed_qty) + cq
		doc.pending_qty = pq
		doc.process_loss_qty = plq
		doc.actual_end_date = end_time
		doc.db_set("status", "Completed")
		if auto_submit and callable(getattr(doc, "submit", None)):
			doc.submit()

	if callable(getattr(doc, "reload", None)):
		doc.reload()

	return {
		"success": True,
		"job_card": doc.name,
		"status": doc.status,
		"docstatus": doc.docstatus,
		"total_completed_qty": doc.total_completed_qty,
		"stock_uom": doc.get("stock_uom") or "Nos",
		"work_order": doc.work_order,
		"message": f"Job Card {doc.name} successfully completed.",
	}


# =============================================================================
# DASH-026: Supervisor Team Overview
# =============================================================================

def resolve_supervisor_team_scope(user=None):
	"""
	DASH-026: Authoritatively resolves the supervisor's permitted team members,
	workstations, and eligible Job Cards.
	Enforces role boundaries:
	- Caller must have 'Sarathi Supervisor' role, production capability, or System Manager/Administrator.
	- Operators calling this method are strictly rejected with PermissionError.
	- Discovers team members via:
	  1. Direct reports in Employee doctype (reports_to == supervisor_emp.name).
	  2. Workstation team: operators working at or assigned to Job Cards at supervisor's permitted workstations.
	  3. Direct ToDo assignments to/from the supervisor.
	- Production Manager has company-wide team and workstation scope.
	- If no team members or permitted workstations are found, returns a truthful unconfigured reason.
	"""
	user = user or frappe.session.user
	if not user or user == "Guest":
		frappe.throw(_("Authentication required."), frappe.PermissionError)

	user_roles = set(frappe.get_roles(user))
	is_supervisor = "Sarathi Supervisor" in user_roles
	is_manager = has_capability("production", user) or "System Manager" in user_roles or user == "Administrator"

	if not (is_supervisor or is_manager):
		frappe.throw(
			_("Supervisor or Production Manager access required for Team Overview."),
			frappe.PermissionError,
		)

	user_name = frappe.utils.get_fullname(user) or user
	supervisor_emp = None
	supervisor_emp_id = None
	supervisor_emp_name = None
	department = None
	company = None

	if frappe.db.table_exists("Employee"):
		emp_rows = frappe.get_all(
			"Employee",
			filters={"user_id": user, "status": "Active"},
			fields=["name", "employee_name", "department", "designation", "company"],
			limit_page_length=1,
		)
		if emp_rows:
			supervisor_emp = emp_rows[0]
			supervisor_emp_id = supervisor_emp.name
			supervisor_emp_name = supervisor_emp.employee_name
			department = supervisor_emp.department
			company = supervisor_emp.company

	supervisor_workstations = []
	if not is_manager:
		user_perms = frappe.permissions.get_user_permissions(user).get("Workstation", [])
		supervisor_workstations = [
			r.get("doc") for r in user_perms
			if r.get("doc") and r.get("applicable_for") in (None, "", "Job Card")
		]

	# Gather Team Members
	team_members_dict = {}

	# 1. Direct reports if supervisor has an Employee record
	if supervisor_emp_id and frappe.db.table_exists("Employee"):
		direct_reports = frappe.get_all(
			"Employee",
			filters={"reports_to": supervisor_emp_id, "status": "Active"},
			fields=["name", "employee_name", "user_id", "department", "designation"],
			limit_page_length=200,
		)
		for rep in direct_reports:
			team_members_dict[rep.name] = {
				"employee_id": rep.name,
				"employee_name": rep.employee_name,
				"user_id": rep.user_id,
				"department": rep.department,
				"designation": rep.designation or "Operator",
				"source": "Direct Report",
			}

	# 2. Eligible Job Cards
	eligible_jc_names = set()

	if is_manager:
		# Production Manager: All active Job Cards in company (limit 2000)
		jc_filters = [["docstatus", "<", 2]]
		if company:
			jc_filters.append(["company", "=", company])
		eligible_jcs = frappe.get_all("Job Card", filters=jc_filters, pluck="name", limit_page_length=2000)
		eligible_jc_names.update(eligible_jcs)

		# Include active manufacturing employees
		if frappe.db.table_exists("Employee"):
			mgr_emp_filters = {"status": "Active"}
			if company:
				mgr_emp_filters["company"] = company
			all_active_emps = frappe.get_all(
				"Employee",
				filters=mgr_emp_filters,
				fields=["name", "employee_name", "user_id", "department", "designation"],
				limit_page_length=500,
			)
			for e in all_active_emps:
				team_members_dict[e.name] = {
					"employee_id": e.name,
					"employee_name": e.employee_name,
					"user_id": e.user_id,
					"department": e.department,
					"designation": e.designation or "Operator",
					"source": "Company Scope",
				}
	else:
		# Direct ToDo assignments to supervisor
		todo_jcs = frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "Job Card",
				"allocated_to": user,
				"status": "Open",
			},
			pluck="reference_name",
			limit_page_length=500,
		)
		eligible_jc_names.update(todo_jcs)

		# Job Cards at supervisor workstations
		if supervisor_workstations:
			station_jcs = frappe.get_all(
				"Job Card",
				filters={
					"workstation": ["in", supervisor_workstations],
					"docstatus": ["<", 2],
				},
				fields=["name", "workstation", "employee"],
				limit_page_length=1000,
			)
			for sjc in station_jcs:
				eligible_jc_names.add(sjc.name)
				if sjc.employee and sjc.employee not in team_members_dict:
					team_members_dict[sjc.employee] = {
						"employee_id": sjc.employee,
						"employee_name": sjc.employee,
						"user_id": None,
						"department": None,
						"designation": "Operator",
						"source": "Workstation Job Card",
					}

		# Direct reports' assigned Job Cards
		direct_emp_ids = [m["employee_id"] for m in team_members_dict.values()]
		direct_user_ids = [m["user_id"] for m in team_members_dict.values() if m.get("user_id")]

		if direct_emp_ids:
			emp_jcs = frappe.get_all(
				"Job Card",
				filters={"employee": ["in", direct_emp_ids], "docstatus": ["<", 2]},
				pluck="name",
				limit_page_length=500,
			)
			eligible_jc_names.update(emp_jcs)

		if direct_user_ids:
			rep_todos = frappe.get_all(
				"ToDo",
				filters={
					"reference_type": "Job Card",
					"allocated_to": ["in", direct_user_ids],
					"status": "Open",
				},
				pluck="reference_name",
				limit_page_length=500,
			)
			eligible_jc_names.update(rep_todos)

	# 3. For any discovered Job Cards, also check who is currently working (open Time Log) or assigned (ToDo)
	if eligible_jc_names:
		active_tls = frappe.get_all(
			"Job Card Time Log",
			filters={"parent": ["in", list(eligible_jc_names)]},
			fields=["employee", "parent"],
			order_by="from_time desc",
			limit_page_length=1000,
		)
		for tl in active_tls:
			if tl.employee and tl.employee not in team_members_dict:
				team_members_dict[tl.employee] = {
					"employee_id": tl.employee,
					"employee_name": tl.employee,
					"user_id": None,
					"department": None,
					"designation": "Operator",
					"source": "Active Time Log",
				}

		jc_todos = frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "Job Card",
				"reference_name": ["in", list(eligible_jc_names)],
				"status": "Open",
			},
			fields=["allocated_to", "reference_name"],
			limit_page_length=1000,
		)
		for td in jc_todos:
			if td.allocated_to:
				matched = False
				for m in team_members_dict.values():
					if m.get("user_id") == td.allocated_to:
						matched = True
						break
				if not matched:
					team_members_dict[td.allocated_to] = {
						"employee_id": td.allocated_to,
						"employee_name": frappe.utils.get_fullname(td.allocated_to) or td.allocated_to,
						"user_id": td.allocated_to,
						"department": None,
						"designation": "Operator",
						"source": "Job Assignment (ToDo)",
					}

	# Enrich employee names and details from Employee doctype if needed
	missing_emp_ids = [k for k, v in team_members_dict.items() if v["employee_name"] == k and frappe.db.table_exists("Employee")]
	if missing_emp_ids:
		fetched_emps = frappe.get_all(
			"Employee",
			filters={"name": ["in", missing_emp_ids]},
			fields=["name", "employee_name", "department", "designation", "user_id"],
			limit_page_length=len(missing_emp_ids),
		)
		for fe in fetched_emps:
			if fe.name in team_members_dict:
				team_members_dict[fe.name].update({
					"employee_name": fe.employee_name,
					"department": fe.department or team_members_dict[fe.name].get("department"),
					"designation": fe.designation or team_members_dict[fe.name].get("designation"),
					"user_id": fe.user_id or team_members_dict[fe.name].get("user_id"),
				})

	unconfigured_reason = None
	if not team_members_dict and not eligible_jc_names and not supervisor_workstations and not is_manager:
		unconfigured_reason = (
			"No team members or permitted workstations found for your supervisor profile. "
			"Supervisors require User Permissions for Workstation, linked direct reports (Employee.reports_to), "
			"or active Job Card assignments."
		)

	user_context = {
		"user_id": user,
		"user_name": user_name,
		"role_label": "Production Manager" if is_manager else "Shop-Floor Supervisor",
		"is_supervisor": is_supervisor,
		"is_manager": is_manager,
		"employee_id": supervisor_emp_id,
		"employee_name": supervisor_emp_name,
		"department": department,
		"supervisor_workstations": supervisor_workstations,
	}

	return user_context, list(team_members_dict.values()), eligible_jc_names, supervisor_workstations, unconfigured_reason


@frappe.whitelist(methods=["GET"])
@read_errors
def get_supervisor_team_overview(filters=None):
	"""
	DASH-026: Authoritative supervisor team overview.
	Returns comprehensive team metrics, workload breakdown, active floor operations,
	completed work in period, and verified blockers & attention notices.
	"""
	values = validate_shopfloor_filters(filters)
	user_context, team_members, eligible_jc_names, supervisor_workstations, unconfigured_reason = (
		resolve_supervisor_team_scope()
	)

	if unconfigured_reason:
		return {
			"success": True,
			"user_context": user_context,
			"team_summary": {
				"total_team_members": 0,
				"operators_with_jobs": 0,
				"operators_active": 0,
				"operators_without_work": 0,
				"active_job_cards": 0,
				"waiting_job_cards": 0,
				"completed_job_cards": 0,
				"blocked_job_cards": 0,
				"overdue_job_cards": 0,
			},
			"team_workload": [],
			"active_operations": [],
			"completed_work": [],
			"blockers": [],
			"workstations": [],
			"filters_applied": values,
			"unconfigured_reason": unconfigured_reason,
			"refreshed_at": now_datetime().isoformat(),
		}

	# Retrieve and enrich all eligible Job Cards matching server-side filters
	enriched_cards = fetch_and_enrich_job_cards(eligible_jc_names, values)

	# Query open time logs for accurate elapsed duration
	open_tls = frappe.get_all(
		"Job Card Time Log",
		filters={"parent": ["in", [c["name"] for c in enriched_cards]], "to_time": ["is", "not set"]},
		fields=["parent", "from_time", "employee"],
		limit_page_length=1000,
	)
	open_tl_map = {t.parent: t for t in open_tls}

	for c in enriched_cards:
		if c["status"] == "Work In Progress" and c["name"] in open_tl_map:
			otl = open_tl_map[c["name"]]
			if otl.from_time:
				c["elapsed_mins"] = max(0.0, round((now_datetime() - otl.from_time).total_seconds() / 60.0, 1))
		else:
			c["elapsed_mins"] = c.get("total_time_in_mins") or 0.0

	# Ensure any operator found in enriched cards is in team members list
	known_op_ids = {m["employee_id"] for m in team_members}
	known_op_users = {m.get("user_id") for m in team_members if m.get("user_id")}

	for c in enriched_cards:
		op_id = c.get("assigned_operator_id")
		op_name = c.get("assigned_operator_name")
		if op_id and op_id != "Unassigned" and op_id not in known_op_ids and op_id not in known_op_users:
			team_members.append({
				"employee_id": op_id,
				"employee_name": op_name or op_id,
				"user_id": c.get("assigned_user"),
				"department": None,
				"designation": "Operator",
				"source": "Active Operation",
			})
			known_op_ids.add(op_id)

	# Calculate operator workload breakdown
	team_workload = []
	for m in team_members:
		m_emp = m["employee_id"]
		m_user = m.get("user_id")
		m_cards = [
			c for c in enriched_cards
			if (m_emp and c.get("assigned_operator_id") == m_emp)
			or (m_user and c.get("assigned_user") == m_user)
			or (m_emp and c.get("employee") == m_emp)
		]
		in_prog = [c for c in m_cards if c["status"] == "Work In Progress"]
		waiting = [c for c in m_cards if c["status"] == "Open"]
		completed = [c for c in m_cards if c["status"] == "Completed"]
		blocked = [c for c in m_cards if c["has_blocker"]]

		active_op = in_prog[0] if in_prog else None
		status_label = "Working" if in_prog else ("Assigned" if waiting else "No Active Job")
		mult_active = len(in_prog) > 1

		team_workload.append({
			"employee_id": m["employee_id"],
			"employee_name": m["employee_name"],
			"user_id": m.get("user_id"),
			"department": m.get("department"),
			"designation": m.get("designation") or "Operator",
			"assigned_job_count": len([c for c in m_cards if c["status"] in ("Open", "Work In Progress")]),
			"in_progress_count": len(in_prog),
			"waiting_count": len(waiting),
			"completed_count": len(completed),
			"blocked_count": len(blocked),
			"has_multiple_active": mult_active,
			"workload_status": status_label,
			"active_operation": {
				"job_card": active_op["name"],
				"work_order": active_op["work_order"],
				"operation": active_op["operation"],
				"workstation": active_op["workstation"],
				"item_name": active_op["item_name"],
				"for_quantity": active_op["for_quantity"],
				"total_completed_qty": active_op["total_completed_qty"],
				"stock_uom": active_op["stock_uom"],
				"completion_percent": active_op["completion_percent"],
				"elapsed_mins": active_op.get("elapsed_mins") or 0.0,
			} if active_op else None,
		})

	# Sort workload: active operators first, then waiting, then idle
	status_rank = {"Working": 0, "Assigned": 1, "No Active Job": 2}
	team_workload.sort(key=lambda x: (status_rank.get(x["workload_status"], 3), -x["in_progress_count"], x["employee_name"]))

	# Active floor operations
	active_operations = [c for c in enriched_cards if c["status"] == "Work In Progress"]

	# Completed operations in selected period
	completed_work = [c for c in enriched_cards if c["status"] == "Completed"]

	# Team Summary KPIs
	total_members = len(team_workload)
	operators_active = sum(1 for op in team_workload if op["in_progress_count"] > 0)
	operators_with_jobs = sum(1 for op in team_workload if (op["in_progress_count"] + op["waiting_count"]) > 0)
	operators_without_work = max(0, total_members - operators_with_jobs)

	team_summary = {
		"total_team_members": total_members,
		"operators_with_jobs": operators_with_jobs,
		"operators_active": operators_active,
		"operators_without_work": operators_without_work,
		"active_job_cards": len(active_operations),
		"waiting_job_cards": len([c for c in enriched_cards if c["status"] == "Open"]),
		"completed_job_cards": len(completed_work),
		"blocked_job_cards": len([c for c in enriched_cards if c["has_blocker"]]),
		"overdue_job_cards": len([c for c in enriched_cards if c["is_overdue"]]),
	}

	# Consolidated Blockers and Attention Queue
	blockers = []
	seen_blocker_keys = set()

	# 1. Operators with multiple active jobs
	for op in team_workload:
		if op["has_multiple_active"]:
			b_key = ("multiple_jobs", op["employee_id"])
			if b_key not in seen_blocker_keys:
				seen_blocker_keys.add(b_key)
				blockers.append({
					"category": "Workload Alert",
					"type": "Multiple Active Operations",
					"severity": "High",
					"title": f"Multiple Active Jobs: {op['employee_name']}",
					"description": f"Operator has {op['in_progress_count']} concurrent active WIP jobs on the shop floor.",
					"affected_entity": op["employee_name"],
					"source_doc": op["employee_id"],
					"drill_down_link": f"/desk#Form/Employee/{op['employee_id']}" if op.get("employee_id") else None,
					"suggested_action": "Review operator stations and pause excess jobs to ensure accurate time tracking.",
				})

	# 2. Overdue operations
	for c in enriched_cards:
		if c["is_overdue"]:
			b_key = ("overdue", c["name"])
			if b_key not in seen_blocker_keys:
				seen_blocker_keys.add(b_key)
				blockers.append({
					"category": "Overdue Operation",
					"type": "Schedule Delay",
					"severity": "High",
					"title": f"Overdue: {c['name']} ({c['operation']})",
					"description": f"Operation is {c['delay_days']} days past expected end date ({c['expected_end_date']}).",
					"affected_entity": c["name"],
					"source_doc": c["work_order"] or c["name"],
					"drill_down_link": c["drill_down_link"],
					"suggested_action": "Expedite floor execution or update delivery milestone in Work Order.",
				})

	# 3. Document-level blockers (downtime, rework, paused)
	for c in enriched_cards:
		if c["has_blocker"] and c.get("blocker"):
			b = c["blocker"]
			b_key = (b.get("type"), c["name"])
			if b_key not in seen_blocker_keys:
				seen_blocker_keys.add(b_key)
				blockers.append({
					"category": b.get("type") or "Production Hold",
					"type": b.get("type"),
					"severity": b.get("severity") or "Medium",
					"title": f"{b.get('type')}: {c['name']}",
					"description": b.get("description"),
					"affected_entity": c["workstation"] or c["name"],
					"source_doc": b.get("source_doc") or c["name"],
					"drill_down_link": c["drill_down_link"],
					"suggested_action": "Investigate root cause before resuming production.",
				})

	# 4. Unassigned waiting jobs
	unassigned_waiting = [c for c in enriched_cards if c["status"] == "Open" and (not c.get("assigned_operator_id") or c.get("assigned_operator_name") == "Unassigned")]
	if unassigned_waiting:
		b_key = ("unassigned_waiting", "global")
		if b_key not in seen_blocker_keys:
			seen_blocker_keys.add(b_key)
			blockers.append({
				"category": "Assignment Needed",
				"type": "Unassigned Operations",
				"severity": "Medium",
				"title": f"Unassigned Waiting Operations ({len(unassigned_waiting)})",
				"description": f"{len(unassigned_waiting)} operations are ready to start but have no assigned operator.",
				"affected_entity": unassigned_waiting[0]["workstation"] or "Workstation Queue",
				"source_doc": unassigned_waiting[0]["name"],
				"drill_down_link": unassigned_waiting[0]["drill_down_link"],
				"suggested_action": "Assign operators using Frappe ToDo assignments or Job Card assignment.",
			})

	# Workstations Overview
	workstations_list = []
	all_stations = sorted(list({c["workstation"] for c in enriched_cards if c.get("workstation")} | set(supervisor_workstations)))
	for ws in all_stations:
		ws_cards = [c for c in enriched_cards if c.get("workstation") == ws]
		act_cnt = sum(1 for c in ws_cards if c["status"] == "Work In Progress")
		wait_cnt = sum(1 for c in ws_cards if c["status"] == "Open")
		has_dt = any(c.get("blocker", {}).get("type") == "Workstation Downtime" for c in ws_cards if c.get("has_blocker"))
		workstations_list.append({
			"workstation": ws,
			"active_job_count": act_cnt,
			"waiting_job_count": wait_cnt,
			"has_downtime": has_dt,
			"status": "Downtime" if has_dt else ("Running" if act_cnt > 0 else "Idle"),
			"drill_down_link": f"/desk#Form/Workstation/{ws}",
		})

	return {
		"success": True,
		"user_context": user_context,
		"team_summary": team_summary,
		"team_workload": team_workload,
		"active_operations": active_operations,
		"completed_work": completed_work,
		"blockers": blockers,
		"workstations": workstations_list,
		"filters_applied": values,
		"refreshed_at": now_datetime().isoformat(),
	}



