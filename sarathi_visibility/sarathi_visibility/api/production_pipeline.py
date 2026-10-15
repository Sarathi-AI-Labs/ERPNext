"""
DASH-017: Production Pipeline and Bottleneck Views API for Production Control Tower.
Provides secure, permission-aware, high-performance pipeline tracking, operation
sequence and dependency resolution, delayed job detection, and defensible bottleneck
analysis using actual ERPNext manufacturing records with zero N+1 queries.
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
import re

import frappe
from frappe.utils import cint, flt, getdate, now_datetime

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

# Allowlist of supported filters for the production pipeline
PIPELINE_FILTER_KEYS = {
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


def validate_pipeline_filters(filters):
	"""Strict server-side validation for production pipeline filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - PIPELINE_FILTER_KEYS:
		invalid("Unsupported pipeline filter parameter.")

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


@frappe.whitelist(methods=["GET"])
@read_errors
def get_production_pipeline(filters=None, **extra):
	"""
	API: Production Pipeline and Bottleneck Analysis (DASH-017).
	Returns verified stage progression, operation sequences, dependencies,
	overdue operations, and defensible bottleneck signals using actual ERPNext
	manufacturing records with zero N+1 database queries.
	"""
	_extra(extra)
	values, ref_dt = validate_pipeline_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()

	if not frappe.has_permission("Work Order", "read"):
		deny()

	# 1. Base query conditions on Work Order
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
		"actual_start_date",
		"actual_end_date",
		"material_transferred_for_manufacturing",
		"wip_warehouse",
		"fg_warehouse",
		"creation",
		"modified",
	]

	all_wos = frappe.get_all(
		"Work Order",
		filters=conditions,
		fields=wo_fields,
		order_by="modified desc",
		limit_page_length=5000,
	)

	# 2. Scope by Customer (via Project or Sales Order)
	if values.get("customer"):
		cust = values["customer"]
		valid_proj = set(frappe.get_all("Project", filters={"customer": cust, "company": company}, pluck="name"))
		valid_so = set(frappe.get_all("Sales Order", filters={"customer": cust, "company": company}, pluck="name"))
		all_wos = [w for w in all_wos if (w.get("project") in valid_proj) or (w.get("sales_order") in valid_so)]

	# 3. Scope by Workstation or Operation
	if values.get("workstation") or values.get("operation"):
		jc_filters = {"docstatus": ["<", 2]}
		if values.get("workstation"):
			jc_filters["workstation"] = values["workstation"]
		if values.get("operation"):
			jc_filters["operation"] = values["operation"]
		wos_with_jc = set(frappe.get_all("Job Card", filters=jc_filters, pluck="work_order"))
		all_wos = [w for w in all_wos if w.get("name") in wos_with_jc]

	# 4. Search query (substring on Work Order ID, item code, or item name)
	if values.get("search") or values.get("work_order"):
		q = (values.get("search") or values.get("work_order")).strip().lower()
		all_wos = [
			w for w in all_wos
			if q in str(w.get("name", "")).lower()
			or q in str(w.get("production_item", "")).lower()
			or q in str(w.get("item_name", "")).lower()
		]

	# 5. Filter by Work Order Status
	status_arg = values.get("status", "")
	if status_arg in ("Active", ""):
		candidate_wos = [w for w in all_wos if w.get("docstatus") == 1 and w.get("status") in ("Not Started", "In Process")]
	elif status_arg == "All":
		candidate_wos = [w for w in all_wos if w.get("docstatus") != 2]
	elif status_arg == "Draft":
		candidate_wos = [w for w in all_wos if w.get("docstatus") == 0]
	elif status_arg == "Cancelled":
		candidate_wos = [w for w in all_wos if w.get("docstatus") == 2]
	else:
		candidate_wos = [w for w in all_wos if w.get("status") == status_arg]

	wo_names = [w["name"] for w in candidate_wos]

	# 6. Batch Queries (Zero N+1)
	# Batch resolve Job Cards
	job_cards_by_wo = defaultdict(list)
	if wo_names and frappe.has_permission("Job Card", "read"):
		all_jcs = frappe.get_all(
			"Job Card",
			filters={"work_order": ["in", wo_names], "docstatus": ["<", 2]},
			fields=[
				"name",
				"work_order",
				"operation",
				"workstation",
				"workstation_type",
				"sequence_id",
				"status",
				"docstatus",
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
			],
			order_by="sequence_id asc, creation asc",
			limit_page_length=10000,
		)
		for j in all_jcs:
			job_cards_by_wo[j["work_order"]].append(j)

	# Batch resolve Customers
	proj_names = list({w["project"] for w in candidate_wos if w.get("project")})
	so_names = list({w["sales_order"] for w in candidate_wos if w.get("sales_order")})

	proj_cust_map = {}
	if proj_names and frappe.has_permission("Project", "read"):
		projs = frappe.get_all("Project", filters={"name": ["in", proj_names]}, fields=["name", "customer"])
		proj_cust_map = {p.name: p.customer for p in projs}

	so_cust_map = {}
	if so_names and frappe.has_permission("Sales Order", "read"):
		sos = frappe.get_all("Sales Order", filters={"name": ["in", so_names]}, fields=["name", "customer"])
		so_cust_map = {s.name: s.customer for s in sos}

	# Batch resolve Manufacture Stock Entries
	manufacture_entries_by_wo = defaultdict(list)
	if wo_names and frappe.has_permission("Stock Entry", "read"):
		entries = frappe.get_all(
			"Stock Entry",
			filters={"work_order": ["in", wo_names], "purpose": "Manufacture", "docstatus": 1},
			fields=["name", "work_order", "posting_date", "fg_completed_qty"],
			order_by="posting_date desc",
			limit_page_length=5000,
		)
		for se in entries:
			manufacture_entries_by_wo[se["work_order"]].append(se)

	# 7. Process Pipeline Jobs & Operation Sequences
	pipeline_jobs = []
	delayed_operations = []
	workstation_queues = defaultdict(list)
	workstation_overdue = defaultdict(list)
	predecessor_lags = defaultdict(list)
	material_blocked_wos = []

	# Counter for pipeline stages
	stage_counts = {
		"Material Staging": 0,
		"In Production": 0,
		"Manufacture Receipt": 0,
		"Completed": 0,
		"Draft": 0,
		"Cancelled": 0,
	}

	for w in candidate_wos:
		wo_name = w["name"]
		qty = flt(w.get("qty"))
		produced = flt(w.get("produced_qty"))
		rem_qty = max(0.0, qty - produced)
		comp_pct = round((produced / qty * 100.0), 1) if qty > 0 else 0.0

		target = get_target_completion_date(w)
		days_diff = (target - ref_date).days if target else None
		is_active = (w.get("docstatus") == 1 and w.get("status") in ("Not Started", "In Process"))
		is_overdue = bool(is_active and days_diff is not None and days_diff < 0)

		cust = proj_cust_map.get(w.get("project")) or so_cust_map.get(w.get("sales_order")) or None

		# Linked Job Cards sorted by sequence
		jcs = job_cards_by_wo.get(wo_name, [])

		# 8. Operation Sequencing & Dependency Resolution
		operations = []
		any_op_in_progress = False
		any_op_completed = False
		all_ops_completed = len(jcs) > 0

		for idx, jc in enumerate(jcs):
			fq = flt(jc.get("for_quantity"))
			cq = flt(jc.get("total_completed_qty"))
			op_comp_pct = round((cq / fq * 100.0), 1) if fq > 0 else (100.0 if jc.get("status") == "Completed" else 0.0)

			# Operation target & overdue evaluation
			jc_expected_end = jc.get("expected_end_date")
			jc_target_date = getdate(jc_expected_end) if jc_expected_end else target
			jc_days_diff = (jc_target_date - ref_date).days if jc_target_date else None
			jc_is_overdue = bool(jc.get("status") in ("Open", "Work In Progress") and jc_days_diff is not None and jc_days_diff < 0)

			# Determine operation status & dependency
			if jc.get("status") == "Completed" or (fq > 0 and cq >= fq):
				op_status = "Completed"
				any_op_completed = True
			elif jc.get("status") == "Work In Progress" or (cq > 0 and cq < fq) or jc.get("actual_start_date"):
				op_status = "In Progress"
				any_op_in_progress = True
				all_ops_completed = False
			elif idx > 0 and operations and operations[-1]["status"] != "Completed":
				# Predecessor operation is incomplete -> Waiting on Predecessor
				op_status = "Waiting on Predecessor"
				all_ops_completed = False
			else:
				op_status = "Ready to Start"
				all_ops_completed = False

			op_row = {
				"job_card": jc["name"],
				"operation": jc.get("operation"),
				"workstation": jc.get("workstation"),
				"workstation_type": jc.get("workstation_type"),
				"sequence": idx + 1,
				"for_quantity": fq,
				"completed_qty": cq,
				"completion_percent": op_comp_pct,
				"status": op_status,
				"raw_status": jc.get("status"),
				"is_overdue": jc_is_overdue,
				"days_diff": jc_days_diff,
				"expected_end_date": str(jc_expected_end) if jc_expected_end else None,
				"waiting_on": operations[-1]["operation"] if op_status == "Waiting on Predecessor" else None,
			}
			operations.append(op_row)

			# Record for queue and overdue tracking
			ws = jc.get("workstation")
			if ws:
				if jc.get("status") in ("Open", "Work In Progress"):
					workstation_queues[ws].append({
						"job_card": jc["name"],
						"work_order": wo_name,
						"operation": jc.get("operation"),
						"status": op_status,
					})
				if jc_is_overdue:
					workstation_overdue[ws].append({
						"job_card": jc["name"],
						"work_order": wo_name,
						"operation": jc.get("operation"),
						"days_overdue": abs(jc_days_diff),
					})

			# Add to delayed operations list if overdue
			if jc_is_overdue:
				delayed_operations.append({
					"job_card": jc["name"],
					"work_order": wo_name,
					"production_item": w.get("production_item"),
					"item_name": w.get("item_name") or w.get("production_item"),
					"operation": jc.get("operation"),
					"workstation": ws,
					"status": op_status,
					"expected_end_date": str(jc_target_date) if jc_target_date else None,
					"days_overdue": abs(jc_days_diff),
					"drilldown_route": ["Form", "Job Card", jc["name"]],
				})

			# Predecessor lag tracking
			if op_status == "Waiting on Predecessor":
				pred_op = operations[idx - 1]
				predecessor_lags[pred_op.get("operation") or "Upstream"].append({
					"waiting_job_card": jc["name"],
					"blocked_operation": jc.get("operation"),
					"work_order": wo_name,
					"predecessor_job_card": pred_op.get("job_card"),
					"predecessor_status": pred_op.get("status"),
				})

		# Link previous and next operations in sequence
		for idx, op in enumerate(operations):
			op["previous_operation"] = operations[idx - 1]["operation"] if idx > 0 else None
			op["next_operation"] = operations[idx + 1]["operation"] if idx < len(operations) - 1 else None

		# 9. Determine Overall Work Order Manufacturing Stage
		mat_trans = flt(w.get("material_transferred_for_manufacturing"))
		docstatus = w.get("docstatus")

		if docstatus == 0:
			stage = "Draft"
		elif docstatus == 2:
			stage = "Cancelled"
		elif w.get("status") == "Completed" or (qty > 0 and produced >= qty):
			stage = "Completed"
		elif produced > 0:
			stage = "Manufacture Receipt"
		elif mat_trans > 0 or any_op_in_progress or any_op_completed:
			stage = "In Production"
		else:
			stage = "Material Staging"

		stage_counts[stage] = stage_counts.get(stage, 0) + 1

		# Identify current, next, and previous active operation
		current_op = next((op for op in operations if op["status"] in ("In Progress", "Ready to Start", "Waiting on Predecessor")), None)
		if not current_op and operations:
			current_op = operations[-1] if all_ops_completed else operations[0]

		# Blocker detection
		is_mat_blocked = bool(is_active and mat_trans == 0.0 and len(jcs) > 0 and stage == "Material Staging")
		if is_mat_blocked:
			material_blocked_wos.append(wo_name)

		is_pred_blocked = bool(current_op and current_op["status"] == "Waiting on Predecessor")

		job_summary = {
			"work_order": wo_name,
			"production_item": w.get("production_item"),
			"item_name": w.get("item_name") or w.get("production_item"),
			"customer": cust,
			"project": w.get("project"),
			"qty": qty,
			"produced_qty": produced,
			"remaining_qty": rem_qty,
			"completion_percent": comp_pct,
			"status": w.get("status"),
			"docstatus": docstatus,
			"stage": stage,
			"is_active": is_active,
			"is_overdue": is_overdue,
			"days_diff": days_diff,
			"target_completion_date": str(target) if target else None,
			"planned_start_date": str(w.get("planned_start_date")) if w.get("planned_start_date") else None,
			"material_transferred": mat_trans,
			"is_material_blocked": is_mat_blocked,
			"is_predecessor_blocked": is_pred_blocked,
			"current_operation": current_op["operation"] if current_op else None,
			"current_workstation": current_op["workstation"] if current_op else None,
			"current_op_status": current_op["status"] if current_op else None,
			"operations_count": len(operations),
			"operations": operations,
			"drilldown_route": ["Form", "Work Order", wo_name],
		}
		pipeline_jobs.append(job_summary)

	# Sort delayed operations by days overdue descending
	delayed_operations.sort(key=lambda x: x["days_overdue"], reverse=True)

	# 10. Synthesize Defensible Bottleneck Signals
	bottlenecks = []

	# Signal 1: Workstation Queue Accumulation (>= 2 open jobs queued)
	for ws, items in workstation_queues.items():
		distinct_wos = sorted(list({i["work_order"] for i in items}))
		if len(items) >= 2:
			bottlenecks.append({
				"id": f"queue-{ws}",
				"type": "queue",
				"title": f"Queue Backlog: {ws}",
				"workstation": ws,
				"operation": items[0]["operation"] if items else None,
				"severity": "high" if len(items) >= 4 else "medium",
				"affected_work_orders_count": len(distinct_wos),
				"affected_work_orders": distinct_wos,
				"queue_depth": len(items),
				"overdue_operations_count": len([i for i in workstation_overdue.get(ws, [])]),
				"oldest_overdue_days": max([i["days_overdue"] for i in workstation_overdue.get(ws, [])], default=0),
				"reason": f"{len(items)} jobs queued at workstation accumulating production backlog across {len(distinct_wos)} Work Order(s).",
				"drilldown_records": [{"doctype": "Workstation", "name": ws}] + [{"doctype": "Job Card", "name": i["job_card"]} for i in items[:5]],
			})

	# Signal 2: Overdue Operation Clusters
	for ws, items in workstation_overdue.items():
		distinct_wos = sorted(list({i["work_order"] for i in items}))
		if items and not any(b["workstation"] == ws and b["type"] == "queue" for b in bottlenecks):
			max_overdue = max(i["days_overdue"] for i in items)
			bottlenecks.append({
				"id": f"overdue-{ws}",
				"type": "overdue",
				"title": f"Overdue Operations: {ws}",
				"workstation": ws,
				"operation": items[0]["operation"] if items else None,
				"severity": "high" if max_overdue >= 7 else "medium",
				"affected_work_orders_count": len(distinct_wos),
				"affected_work_orders": distinct_wos,
				"queue_depth": len(workstation_queues.get(ws, [])),
				"overdue_operations_count": len(items),
				"oldest_overdue_days": max_overdue,
				"reason": f"{len(items)} operation(s) missed expected completion date; oldest delayed by {max_overdue} day(s).",
				"drilldown_records": [{"doctype": "Workstation", "name": ws}] + [{"doctype": "Job Card", "name": i["job_card"]} for i in items[:5]],
			})

	# Signal 3: Predecessor Dependency Lags
	for pred_op, items in predecessor_lags.items():
		distinct_wos = sorted(list({i["work_order"] for i in items}))
		if len(items) >= 1:
			bottlenecks.append({
				"id": f"predecessor-{pred_op}",
				"type": "predecessor",
				"title": f"Upstream Delay: {pred_op}",
				"workstation": None,
				"operation": pred_op,
				"severity": "medium",
				"affected_work_orders_count": len(distinct_wos),
				"affected_work_orders": distinct_wos,
				"queue_depth": len(items),
				"overdue_operations_count": 0,
				"oldest_overdue_days": 0,
				"reason": f"Downstream operations waiting on incomplete predecessor '{pred_op}' across {len(distinct_wos)} Work Order(s).",
				"drilldown_records": [{"doctype": "Job Card", "name": i["waiting_job_card"]} for i in items[:5]],
			})

	# Signal 4: Material Readiness Blocker
	if material_blocked_wos:
		distinct_mat_wos = sorted(list(set(material_blocked_wos)))
		bottlenecks.append({
			"id": "blocker-material-staging",
			"type": "material",
			"title": "Material Transfer Pending",
			"workstation": None,
			"operation": "Stores Material Issue",
			"severity": "high",
			"affected_work_orders_count": len(distinct_mat_wos),
			"affected_work_orders": distinct_mat_wos,
			"queue_depth": len(distinct_mat_wos),
			"overdue_operations_count": 0,
			"oldest_overdue_days": 0,
			"reason": f"Raw materials have not been transferred from stores to WIP warehouse for {len(distinct_mat_wos)} active Work Order(s), holding back shop-floor execution.",
			"drilldown_records": [{"doctype": "Work Order", "name": w} for w in distinct_mat_wos[:5]],
		})

	# Sort bottlenecks: high severity first, then by affected Work Orders count descending
	sev_weight = {"high": 2, "medium": 1, "low": 0}
	bottlenecks.sort(key=lambda b: (sev_weight.get(b["severity"], 0), b["affected_work_orders_count"]), reverse=True)

	# 11. Pipeline Stages Summary & Structure
	stages_data = [
		{
			"key": "Material Staging",
			"label": "1. Material Staging",
			"description": "Work Orders pending raw material issue/transfer",
			"count": stage_counts["Material Staging"],
			"jobs": [j for j in pipeline_jobs if j["stage"] == "Material Staging"],
		},
		{
			"key": "In Production",
			"label": "2. In Production",
			"description": "Active operations and Job Cards on the shop floor",
			"count": stage_counts["In Production"],
			"jobs": [j for j in pipeline_jobs if j["stage"] == "In Production"],
		},
		{
			"key": "Manufacture Receipt",
			"label": "3. Manufacture Receipt",
			"description": "Partial finished goods received via Stock Entry",
			"count": stage_counts["Manufacture Receipt"],
			"jobs": [j for j in pipeline_jobs if j["stage"] == "Manufacture Receipt"],
		},
		{
			"key": "Completed",
			"label": "4. Completed",
			"description": "100% finished goods produced and closed",
			"count": stage_counts["Completed"],
			"jobs": [j for j in pipeline_jobs if j["stage"] == "Completed"],
		},
	]

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": {
			"total_work_orders": len(pipeline_jobs),
			"material_staging": stage_counts["Material Staging"],
			"in_production": stage_counts["In Production"],
			"manufacture_receipt": stage_counts["Manufacture Receipt"],
			"completed": stage_counts["Completed"],
			"overdue_work_orders": len([j for j in pipeline_jobs if j["is_overdue"]]),
			"overdue_operations": len(delayed_operations),
			"bottlenecks_detected": len(bottlenecks),
		},
		"stages": stages_data,
		"pipeline_jobs": pipeline_jobs,
		"delayed_operations": delayed_operations,
		"bottlenecks": bottlenecks,
		"applied_filters": values,
	}
