"""DASH-015: Factory Overview KPIs, Filters, and Production Summary API."""
from collections import defaultdict
from datetime import date, datetime, timedelta
import re

import frappe
from frappe.utils import flt, getdate, now_datetime

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
	_parse,
	invalid,
	read_errors,
)

FEATURE_KEYS = {
	"company",
	"from_date",
	"to_date",
	"status",
	"project",
	"customer",
	"workstation",
	"review_days",
	"reference_at",
}

VALID_STATUSES = {
	"",
	"All",
	"Active",
	"Not Started",
	"In Process",
	"Completed",
	"Stopped",
	"Cancelled",
	"Overdue",
	"Due soon",
}


def get_target_completion_date(row):
	"""Returns target completion date with fallback to expected_delivery_date."""
	target = row.get("planned_end_date") or row.get("expected_delivery_date")
	if not target:
		return None
	if isinstance(target, datetime):
		return target.date()
	if isinstance(target, date):
		return target
	if isinstance(target, str):
		try:
			return date.fromisoformat(target[:10])
		except (ValueError, TypeError):
			return None
	return None


def validate_factory_filters(filters):
	"""Server-side strict validation for factory overview filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - FEATURE_KEYS:
		invalid("Unsupported factory overview filter.")

	values = {k: v for k, v in values.items() if v is not None and v != ""}
	
	company_arg = values.get("company")
	if not company_arg or company_arg in ("All organizations", "All"):
		user_default_company = (
			frappe.defaults.get_user_default("Company")
			or frappe.defaults.get_global_default("company")
			or frappe.db.get_single_value("Global Defaults", "default_company")
		)
		if user_default_company and frappe.has_permission("Company", "read", user_default_company):
			company_arg = user_default_company
		else:
			company_arg = None
	values["company"] = _company(company_arg)

	# Validate dates
	for key in ("from_date", "to_date"):
		if key in values:
			_date(values[key])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate status
	status = values.get("status", "")
	if status not in VALID_STATUSES:
		invalid("Unsupported Work Order status filter.")

	# Validate project link
	if values.get("project"):
		if not frappe.db.exists("Project", values["project"]):
			invalid("Selected project does not exist.")
		proj = check_record("Project", values["project"])
		if proj.company != values["company"]:
			deny()
		if values.get("customer") and proj.customer != values["customer"]:
			deny()

	# Validate customer link
	if values.get("customer"):
		if not frappe.db.exists("Customer", values["customer"]):
			invalid("Selected customer does not exist.")
		check_record("Customer", values["customer"])

	# Validate workstation link
	if values.get("workstation"):
		if not frappe.db.exists("Workstation", values["workstation"]):
			invalid("Selected workstation does not exist.")
		check_record("Workstation", values["workstation"])

	# Validate review_days
	raw_window = values.get("review_days", 7)
	if isinstance(raw_window, bool):
		invalid("Review window must be an integer from 0 to 90 days.")
	try:
		window = int(raw_window)
	except (ValueError, TypeError):
		invalid("Review window must be an integer from 0 to 90 days.")
	if window < 0 or window > 90:
		invalid("Review window must be an integer from 0 to 90 days.")
	values["review_days"] = window

	# Validate reference_at
	ref = values.get("reference_at")
	if ref is not None:
		if not isinstance(ref, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", ref):
			invalid("Reference time must be a site-local ISO date and time.")
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
def get_factory_overview(filters=None, **extra):
	"""
	Core Factory Overview API for Production Management Control Tower (DASH-015).
	Returns verified production KPIs, summary progress by item and UOM,
	workstation options, status distribution, and concise overdue/upcoming job queues.
	"""
	_extra(extra)
	values, ref_dt = validate_factory_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	review_days = values["review_days"]
	selected_status = values.get("status", "")

	if not frappe.has_permission("Work Order", "read"):
		return {
			"available": False,
			"reason": "Work Orders are unavailable for your permission scope.",
		}

	# 1. Base query for Work Orders
	conditions = [["company", "=", company]]

	if values.get("project"):
		conditions.append(["project", "=", values["project"]])

	# Date bounds filter on planned_start_date or creation
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
		"planned_start_date",
		"planned_end_date",
		"expected_delivery_date",
		"stock_uom",
	]

	all_wos = frappe.get_all(
		"Work Order",
		filters=conditions,
		fields=wo_fields,
		order_by="creation desc",
		limit_page_length=2000,
	)

	# If customer filter provided, scope through Sales Order or Project
	if values.get("customer"):
		cust = values["customer"]
		# Find projects and sales orders for this customer
		valid_proj = set(frappe.get_all("Project", filters={"customer": cust, "company": company}, pluck="name"))
		valid_so = set(frappe.get_all("Sales Order", filters={"customer": cust, "company": company}, pluck="name"))
		all_wos = [w for w in all_wos if (w.get("project") in valid_proj) or (w.get("sales_order") in valid_so)]

	# If workstation filter provided, scope through Job Cards
	if values.get("workstation"):
		ws_name = values["workstation"]
		wos_with_ws = set(
			frappe.get_all(
				"Job Card",
				filters={"workstation": ws_name, "docstatus": ["<", 2]},
				pluck="work_order",
			)
		)
		all_wos = [w for w in all_wos if w.get("name") in wos_with_ws]

	# 2. Status distribution across all submitted and draft Work Orders
	status_dist = defaultdict(int)
	for w in all_wos:
		st = w.get("status") or "Unknown"
		if w.get("docstatus") == 0:
			status_dist["Draft"] += 1
		elif w.get("docstatus") == 2:
			status_dist["Cancelled"] += 1
		else:
			status_dist[st] += 1

	# Classify active vs completed vs overdue vs due soon
	active_wos = []
	overdue_wos = []
	approaching_wos = []

	for w in all_wos:
		# Active definition: docstatus = 1 and status in ('Not Started', 'In Process')
		if w.get("docstatus") == 1 and w.get("status") in ("Not Started", "In Process"):
			target = get_target_completion_date(w)
			days_diff = (target - ref_date).days if target else None

			w_copy = dict(w)
			w_copy["target_completion_date"] = str(target) if target else None
			w_copy["days_diff"] = days_diff

			active_wos.append(w_copy)

			if days_diff is not None:
				if days_diff < 0:
					overdue_wos.append(w_copy)
				elif days_diff <= review_days:
					approaching_wos.append(w_copy)

	# Apply status filter if specific status chosen
	filtered_cohort = all_wos
	if selected_status in ("Active", ""):
		filtered_cohort = active_wos
	elif selected_status == "All":
		filtered_cohort = [w for w in all_wos if w.get("docstatus") != 2]
	elif selected_status == "Overdue":
		filtered_cohort = overdue_wos
	elif selected_status == "Due soon":
		filtered_cohort = approaching_wos
	elif selected_status == "Draft":
		filtered_cohort = [w for w in all_wos if w.get("docstatus") == 0]
	elif selected_status == "Cancelled":
		filtered_cohort = [w for w in all_wos if w.get("docstatus") == 2]
	else:
		filtered_cohort = [w for w in all_wos if w.get("docstatus") == 1 and w.get("status") == selected_status]

	# 3. Production Planned vs Actual Output Calculations
	# Calculate planned and produced quantities by Item & UOM to avoid mixing units
	planned_by_uom = defaultdict(float)
	produced_by_uom = defaultdict(float)
	item_summary_map = {}

	for w in filtered_cohort:
		uom = w.get("stock_uom") or "Nos"
		planned = flt(w.get("qty"))
		produced = flt(w.get("produced_qty"))
		planned_by_uom[uom] += planned
		produced_by_uom[uom] += produced

		item_code = w.get("production_item")
		if item_code not in item_summary_map:
			item_summary_map[item_code] = {
				"item_code": item_code,
				"item_name": w.get("item_name") or item_code,
				"stock_uom": uom,
				"planned_qty": 0.0,
				"produced_qty": 0.0,
				"active_orders": 0,
				"work_orders": [],
			}
		item_summary_map[item_code]["planned_qty"] += planned
		item_summary_map[item_code]["produced_qty"] += produced
		item_summary_map[item_code]["active_orders"] += 1
		item_summary_map[item_code]["work_orders"].append(w.get("name"))

	# Format item production summary list
	item_production_summary = []
	for it in sorted(item_summary_map.values(), key=lambda x: x["item_code"]):
		p = it["planned_qty"]
		a = it["produced_qty"]
		ach_pct = round((a / p * 100.0), 1) if p > 0 else 0.0
		it["achievement_pct"] = ach_pct
		item_production_summary.append(it)

	# Overall planned & actual values
	total_planned_lines = len(filtered_cohort)
	total_uoms = len(planned_by_uom)
	if total_uoms == 1:
		single_uom = next(iter(planned_by_uom))
		total_planned_val = planned_by_uom[single_uom]
		total_produced_val = produced_by_uom[single_uom]
		planned_formatted = f"{total_planned_val:,.1f} {single_uom}"
		produced_formatted = f"{total_produced_val:,.1f} {single_uom}"
		achievement_pct = round((total_produced_val / total_planned_val * 100.0), 1) if total_planned_val > 0 else 0.0
	elif total_uoms > 1:
		total_planned_val = sum(planned_by_uom.values())
		total_produced_val = sum(produced_by_uom.values())
		planned_formatted = f"{len(item_production_summary)} items ({total_uoms} UOMs)"
		produced_formatted = f"{total_produced_val:,.1f} total output"
		achievement_pct = round((total_produced_val / total_planned_val * 100.0), 1) if total_planned_val > 0 else 0.0
	else:
		total_planned_val = 0.0
		total_produced_val = 0.0
		planned_formatted = "0"
		produced_formatted = "0"
		achievement_pct = 0.0

	# 4. Open Job Cards count
	open_job_cards_count = 0
	if frappe.has_permission("Job Card", "read"):
		jc_conditions = [
			["docstatus", "<", 2],
			["status", "in", ["Open", "Work In Progress"]],
		]
		active_wo_names = [w["name"] for w in active_wos]
		if active_wo_names:
			jc_conditions.append(["work_order", "in", active_wo_names])
			if values.get("workstation"):
				jc_conditions.append(["workstation", "=", values["workstation"]])
			open_job_cards_count = frappe.db.count("Job Card", filters=jc_conditions)

	# 5. Material Shortage Blockers calculation
	shortage_wo_count = 0
	shortage_details = []
	active_wo_names = [w["name"] for w in active_wos]

	if active_wo_names and frappe.has_permission("Work Order Item", "read") and frappe.has_permission("Bin", "read"):
		wo_items = frappe.get_all(
			"Work Order Item",
			filters={"parent": ["in", active_wo_names]},
			fields=["parent", "item_code", "item_name", "source_warehouse", "required_qty", "transferred_qty"],
			limit_page_length=2000,
		)
		bin_keys = list({(it.item_code, it.source_warehouse) for it in wo_items if it.source_warehouse})
		items_needed = list({k[0] for k in bin_keys})
		warehouses_needed = list({k[1] for k in bin_keys})

		bin_map = {}
		if items_needed and warehouses_needed:
			bins = frappe.get_all(
				"Bin",
				filters={"item_code": ["in", items_needed], "warehouse": ["in", warehouses_needed]},
				fields=["item_code", "warehouse", "actual_qty", "reserved_qty"],
				limit_page_length=5000,
			)
			for b in bins:
				bin_map[(b.item_code, b.warehouse)] = b

		shortage_wos = set()
		for it in wo_items:
			req = flt(it.required_qty)
			trans = flt(it.transferred_qty)
			rem_req = max(0.0, req - trans)
			if rem_req <= 0.0:
				continue

			bin_rec = bin_map.get((it.item_code, it.source_warehouse))
			actual_stock = flt(bin_rec.actual_qty) if bin_rec else 0.0
			reserved_stock = flt(bin_rec.reserved_qty) if bin_rec else 0.0
			available_stock = max(0.0, actual_stock - reserved_stock)

			shortage = max(0.0, rem_req - available_stock)
			if shortage > 0.0:
				shortage_wos.add(it.parent)
				shortage_details.append({
					"work_order": it.parent,
					"item_code": it.item_code,
					"warehouse": it.source_warehouse,
					"shortage_qty": shortage,
				})

		shortage_wo_count = len(shortage_wos)

	# 6. Concise Overdue and Approaching Job queues
	formatted_overdue_jobs = []
	for w in sorted(overdue_wos, key=lambda x: x["days_diff"] or 0):
		formatted_overdue_jobs.append({
			"work_order": w["name"],
			"production_item": w["production_item"],
			"item_name": w["item_name"] or w["production_item"],
			"stock_uom": w.get("stock_uom") or "Nos",
			"planned_qty": flt(w["qty"]),
			"produced_qty": flt(w["produced_qty"]),
			"status": w["status"],
			"target_date": w["target_completion_date"],
			"days_overdue": abs(w["days_diff"]) if w["days_diff"] is not None else 0,
			"drilldown_route": ["Form", "Work Order", w["name"]],
		})

	formatted_approaching_jobs = []
	for w in sorted(approaching_wos, key=lambda x: x["days_diff"] or 0):
		formatted_approaching_jobs.append({
			"work_order": w["name"],
			"production_item": w["production_item"],
			"item_name": w["item_name"] or w["production_item"],
			"stock_uom": w.get("stock_uom") or "Nos",
			"planned_qty": flt(w["qty"]),
			"produced_qty": flt(w["produced_qty"]),
			"status": w["status"],
			"target_date": w["target_completion_date"],
			"days_remaining": w["days_diff"] if w["days_diff"] is not None else 0,
			"drilldown_route": ["Form", "Work Order", w["name"]],
		})

	# 7. Workstations options list for filter dropdown
	ws_options = []
	if frappe.has_permission("Workstation", "read"):
		ws_list = frappe.get_all(
			"Workstation",
			fields=["name", "workstation_name", "workstation_type", "status"],
			order_by="name asc",
			limit_page_length=200,
		)
		ws_options = [
			{"value": w.name, "label": f"{w.workstation_name or w.name} ({w.workstation_type or 'General'})"}
			for w in ws_list
		]

	return {
		"available": True,
		"applied_filters": values,
		"reference_date": str(ref_date),
		"reference_at": str(ref_dt),
		"review_days": review_days,
		"kpis": {
			"active_work_orders": {
				"label": "Active Work Orders",
				"value": len(active_wos),
				"description": "Submitted Work Orders currently in Not Started or In Process status.",
			},
			"planned_production": {
				"label": "Planned Production",
				"value": planned_formatted,
				"raw_qty": total_planned_val,
				"uom_counts": dict(planned_by_uom),
				"lines": total_planned_lines,
				"description": f"Planned production volume across {total_planned_lines} orders.",
			},
			"actual_production": {
				"label": "Actual Production",
				"value": produced_formatted,
				"raw_qty": total_produced_val,
				"uom_counts": dict(produced_by_uom),
				"description": "Authoritative completed quantity recorded on Work Orders.",
			},
			"production_achievement": {
				"label": "Production Achievement",
				"value": f"{achievement_pct}%",
				"pct": achievement_pct,
				"description": "Actual produced output vs. planned quantity.",
			},
			"overdue_work_orders": {
				"label": "Overdue Work Orders",
				"value": len(overdue_wos),
				"description": "Active Work Orders past target completion date.",
			},
			"open_job_cards": {
				"label": "Open Job Cards",
				"value": open_job_cards_count,
				"description": "Job Cards currently open or in progress on the shop floor.",
			},
			"material_blockers": {
				"label": "Material Blockers",
				"value": shortage_wo_count,
				"description": "Active Work Orders missing required raw materials in warehouse.",
			},
		},
		"summary": {
			"status_distribution": dict(status_dist),
			"item_production_summary": item_production_summary,
			"planned_by_uom": dict(planned_by_uom),
			"produced_by_uom": dict(produced_by_uom),
			"overdue_jobs": formatted_overdue_jobs,
			"approaching_jobs": formatted_approaching_jobs,
		},
		"workstations": ws_options,
		"generated_at": str(now_datetime()),
	}
