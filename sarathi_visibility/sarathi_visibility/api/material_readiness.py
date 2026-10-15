"""
DASH-018: Material Readiness and Shortages API for Production Management Control Tower.
Provides secure, permission-aware, high-performance material readiness evaluation,
warehouse-aware stock availability, component shortage calculations, and affected
Work Order tracking using actual ERPNext manufacturing and inventory records with zero N+1 queries.
"""
from collections import defaultdict
from datetime import date, datetime
import re

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.access import (
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
	pagination,
	read_errors,
)
from sarathi_visibility.api.factory_overview import get_target_completion_date

# Allowlist of supported filters for material readiness
READINESS_FILTER_KEYS = {
	"company",
	"from_date",
	"to_date",
	"status",
	"production_item",
	"item_code",
	"warehouse",
	"source_warehouse",
	"readiness_status",
	"project",
	"customer",
	"work_order",
	"search",
	"reference_at",
	"shortage_only",
}

READINESS_STATUS_CHOICES = {
	"All",
	"Ready",
	"Partially Ready",
	"Shortage",
	"Unknown",
	"Not Applicable",
}

WO_ACTIVE_STATUSES = ("Not Started", "In Process")


def validate_material_readiness_filters(filters):
	"""Strict server-side validation for material readiness filters."""
	require_capability("production")
	values = _parse(filters)
	if set(values) - READINESS_FILTER_KEYS:
		invalid("Unsupported material readiness filter parameter.")

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

	# Validate warehouse link
	wh = values.get("warehouse") or values.get("source_warehouse")
	if wh:
		_identifier(wh)
		if not frappe.db.exists("Warehouse", wh):
			invalid("Selected warehouse does not exist.")
		wh_doc = check_record("Warehouse", wh)
		if wh_doc.company and wh_doc.company != values["company"]:
			deny()
		values["warehouse"] = wh

	# Validate readiness status filter
	if values.get("readiness_status"):
		rs = values["readiness_status"]
		if rs not in READINESS_STATUS_CHOICES:
			invalid("Unsupported readiness status filter.")

	# Validate shortage_only boolean
	if "shortage_only" in values:
		raw = values["shortage_only"]
		values["shortage_only"] = str(raw).lower() in ("true", "1", "yes")
	else:
		values["shortage_only"] = False

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
def get_material_readiness(filters=None, start=0, page_length=20, **extra):
	"""
	API for Material Readiness and Shortages (DASH-018).
	Calculates raw material demand vs leaf warehouse stock availability,
	detects component shortages, evaluates Work Order readiness states,
	and provides permission-safe drill-downs with zero N+1 queries.
	"""
	_extra(extra)
	values, ref_dt = validate_material_readiness_filters(filters)
	company = values["company"]
	ref_date = ref_dt.date()
	start_offset, limit = pagination(start, page_length)

	# -------------------------------------------------------------
	# 1. Retrieve Candidate Work Orders (Single Indexed Query)
	# -------------------------------------------------------------
	wo_filters = [
		["company", "=", company],
		["docstatus", "=", 1],
	]

	# Work Order status scoping
	status_filter = values.get("status", "Active")
	if status_filter == "Active":
		wo_filters.append(["status", "in", list(WO_ACTIVE_STATUSES)])
	elif status_filter == "All":
		pass
	elif status_filter in ("Not Started", "In Process", "Completed", "Stopped"):
		wo_filters.append(["status", "=", status_filter])

	if values.get("production_item"):
		wo_filters.append(["production_item", "=", values["production_item"]])

	if values.get("project"):
		wo_filters.append(["project", "=", values["project"]])

	wo_records = frappe.get_all(
		"Work Order",
		filters=wo_filters,
		fields=[
			"name",
			"production_item",
			"item_name",
			"qty",
			"produced_qty",
			"stock_uom",
			"status",
			"docstatus",
			"planned_start_date",
			"planned_end_date",
			"expected_delivery_date",
			"project",
			"sales_order",
			"source_warehouse",
			"wip_warehouse",
			"material_transferred_for_manufacturing",
		],
		order_by="planned_start_date asc, modified desc",
		limit_page_length=2000,
	)

	# If customer filter is active, resolve linked customer
	if values.get("customer") and wo_records:
		cust_val = values["customer"]
		# Collect projects and sales orders
		projs = list({wo.project for wo in wo_records if wo.project})
		sos = list({wo.sales_order for wo in wo_records if wo.sales_order})
		valid_projs = set(frappe.get_all("Project", filters={"name": ["in", projs], "customer": cust_val}, pluck="name")) if projs else set()
		valid_sos = set(frappe.get_all("Sales Order", filters={"name": ["in", sos], "customer": cust_val}, pluck="name")) if sos else set()
		wo_records = [
			wo for wo in wo_records
			if (wo.project and wo.project in valid_projs) or (wo.sales_order and wo.sales_order in valid_sos)
		]

	# If search/work_order substring filter
	search_query = values.get("work_order") or values.get("search")
	if search_query and wo_records:
		sq = str(search_query).strip().lower()
		wo_records = [
			wo for wo in wo_records
			if sq in wo.name.lower() or sq in (wo.production_item or "").lower() or sq in (wo.item_name or "").lower()
		]

	# If date range bounds
	from_d = values.get("from_date")
	to_d = values.get("to_date")
	if (from_d or to_d) and wo_records:
		filtered_wos = []
		for wo in wo_records:
			target = get_target_completion_date(wo)
			if target:
				target_str = str(target)
				if from_d and target_str < from_d:
					continue
				if to_d and target_str > to_d:
					continue
			filtered_wos.append(wo)
		wo_records = filtered_wos

	if not wo_records:
		return {
			"available": True,
			"reference_date": str(ref_date),
			"summary": {
				"total_work_orders": 0,
				"ready_work_orders": 0,
				"partially_ready_work_orders": 0,
				"shortage_work_orders": 0,
				"unknown_work_orders": 0,
				"critical_shortage_orders": 0,
				"distinct_shortage_items": 0,
				"total_shortage_lines": 0,
			},
			"readiness_distribution": {
				"Ready": 0,
				"Partially Ready": 0,
				"Shortage": 0,
				"Unknown": 0,
			},
			"shortage_items_aggregate": [],
			"shortage_lines": [],
			"work_orders_readiness": [],
			"total_lines": 0,
			"start": start_offset,
			"page_length": limit,
			"has_next_page": False,
			"applied_filters": values,
		}

	wo_names = [wo.name for wo in wo_records]
	wo_map = {wo.name: wo for wo in wo_records}

	# -------------------------------------------------------------
	# 2. Batch Retrieve Work Order Items (Zero N+1)
	# -------------------------------------------------------------
	wo_items = frappe.get_all(
		"Work Order Item",
		filters={"parent": ["in", wo_names]},
		fields=[
			"parent",
			"name",
			"item_code",
			"item_name",
			"source_warehouse",
			"stock_uom",
			"required_qty",
			"transferred_qty",
			"consumed_qty",
		],
		limit_page_length=10000,
	)

	# -------------------------------------------------------------
	# 3. Resolve Leaf Warehouses and Batch Query Bins
	# -------------------------------------------------------------
	# Determine effective leaf warehouse for each requirement
	needed_bins = set()
	needed_items = set()
	for row in wo_items:
		wo = wo_map.get(row.parent)
		eff_wh = row.source_warehouse or (wo.source_warehouse if wo else None)
		if eff_wh:
			needed_bins.add((row.item_code, eff_wh))
		if row.item_code:
			needed_items.add(row.item_code)

	# Filter by specific warehouse if filter is active
	target_wh = values.get("warehouse")
	raw_item_filter = values.get("item_code")

	bin_map = {}
	if needed_bins:
		item_list = list({k[0] for k in needed_bins})
		wh_list = list({k[1] for k in needed_bins})
		bins = frappe.get_all(
			"Bin",
			filters={"item_code": ["in", item_list], "warehouse": ["in", wh_list]},
			fields=["item_code", "warehouse", "actual_qty", "reserved_qty", "projected_qty"],
			limit_page_length=10000,
		)
		for b in bins:
			bin_map[(b.item_code, b.warehouse)] = b

	# Batch Item master metadata for names and units
	item_meta_map = {}
	if needed_items:
		items = frappe.get_all(
			"Item",
			filters={"name": ["in", list(needed_items)]},
			fields=["name", "item_name", "stock_uom"],
			limit_page_length=10000,
		)
		for it in items:
			item_meta_map[it.name] = {
				"item_name": it.item_name or it.name,
				"stock_uom": it.stock_uom or "Nos",
			}

	# -------------------------------------------------------------
	# 4. Group Items by Work Order and Evaluate Shortages
	# -------------------------------------------------------------
	wo_items_by_wo = defaultdict(list)
	for row in wo_items:
		wo_items_by_wo[row.parent].append(row)

	all_shortage_lines = []
	all_requirement_lines = []
	wo_readiness_list = []

	# Aggregators across factory
	aggregate_demand = defaultdict(lambda: {
		"total_remaining_demand": 0.0,
		"available_stock": 0.0,
		"actual_stock": 0.0,
		"reserved_stock": 0.0,
		"projected_stock": 0.0,
		"stock_uom": "Nos",
		"item_name": "",
		"affected_work_orders": set(),
		"demanding_work_orders": set(),
	})

	ready_wo_count = 0
	partial_wo_count = 0
	shortage_wo_count = 0
	unknown_wo_count = 0
	critical_shortage_orders = set()

	for wo in wo_records:
		target_date = get_target_completion_date(wo)
		days_to_target = (target_date - ref_date).days if target_date else None
		is_overdue = bool(days_to_target is not None and days_to_target < 0)
		is_due_soon = bool(days_to_target is not None and 0 <= days_to_target <= 7)
		is_time_critical = is_overdue or is_due_soon

		items_for_this_wo = wo_items_by_wo.get(wo.name, [])

		if not items_for_this_wo:
			wo_readiness = "Not Applicable"
			readiness_note = "No component requirements recorded"
			total_lines = 0
			short_lines = 0
		else:
			total_lines = len(items_for_this_wo)
			lines_evaluated = []
			has_unconfigured_wh = False

			for row in items_for_this_wo:
				eff_wh = row.source_warehouse or wo.source_warehouse
				req_qty = flt(row.required_qty)
				trans_qty = flt(row.transferred_qty)
				rem_req = max(0.0, req_qty - trans_qty)

				meta = item_meta_map.get(row.item_code, {})
				item_name = row.item_name or meta.get("item_name") or row.item_code
				uom = row.stock_uom or meta.get("stock_uom") or "Nos"

				if not eff_wh:
					has_unconfigured_wh = True
					source_wh_display = "Unconfigured"
					actual_stock = 0.0
					reserved_stock = 0.0
					avail_stock = 0.0
					proj_stock = 0.0
					shortage_qty = rem_req
				else:
					source_wh_display = eff_wh
					b = bin_map.get((row.item_code, eff_wh))
					actual_stock = flt(b.actual_qty) if b else 0.0
					reserved_stock = flt(b.reserved_qty) if b else 0.0
					avail_stock = max(0.0, actual_stock - reserved_stock)
					proj_stock = flt(b.projected_qty) if b else 0.0
					shortage_qty = max(0.0, rem_req - avail_stock)

				has_short = shortage_qty > 0.0

				# Record aggregate factory demand
				if eff_wh and rem_req > 0:
					agg = aggregate_demand[(row.item_code, eff_wh)]
					agg["total_remaining_demand"] += rem_req
					agg["available_stock"] = avail_stock
					agg["actual_stock"] = actual_stock
					agg["reserved_stock"] = reserved_stock
					agg["projected_stock"] = proj_stock
					agg["stock_uom"] = uom
					agg["item_name"] = item_name
					agg["demanding_work_orders"].add(wo.name)
					if has_short:
						agg["affected_work_orders"].add(wo.name)

				line_data = {
					"work_order": wo.name,
					"production_item": wo.production_item,
					"production_item_name": wo.item_name or wo.production_item,
					"project": wo.project,
					"target_date": str(target_date) if target_date else None,
					"days_to_target": days_to_target,
					"is_overdue": is_overdue,
					"is_due_soon": is_due_soon,
					"is_time_critical": is_time_critical,
					"item_code": row.item_code,
					"item_name": item_name,
					"source_warehouse": source_wh_display,
					"stock_uom": uom,
					"required_qty": round(req_qty, 2),
					"transferred_qty": round(trans_qty, 2),
					"remaining_required": round(rem_req, 2),
					"actual_stock": round(actual_stock, 2),
					"reserved_stock": round(reserved_stock, 2),
					"available_stock": round(avail_stock, 2),
					"projected_stock": round(proj_stock, 2),
					"shortage_qty": round(shortage_qty, 2),
					"has_shortage": has_short,
					"is_fully_transferred": rem_req <= 0.0,
					"drilldown_records": [
						{"doctype": "Work Order", "name": wo.name},
						{"doctype": "Item", "name": row.item_code},
						{"doctype": "Warehouse", "name": source_wh_display} if eff_wh else None,
					],
				}
				# Clean None drilldown records
				line_data["drilldown_records"] = [d for d in line_data["drilldown_records"] if d]

				lines_evaluated.append(line_data)
				all_requirement_lines.append(line_data)
				if has_short:
					all_shortage_lines.append(line_data)

			# Classify Work Order Readiness
			short_lines = len([l for l in lines_evaluated if l["has_shortage"]])
			active_demand_lines = [l for l in lines_evaluated if not l["is_fully_transferred"]]

			if has_unconfigured_wh:
				wo_readiness = "Unknown"
				readiness_note = "Missing source warehouse configuration"
				unknown_wo_count += 1
			elif len(active_demand_lines) == 0:
				wo_readiness = "Ready"
				readiness_note = "100% of materials already transferred to WIP"
				ready_wo_count += 1
			elif short_lines == 0:
				wo_readiness = "Ready"
				readiness_note = "100% available in warehouse"
				ready_wo_count += 1
			elif short_lines == len(active_demand_lines) and all(l["available_stock"] == 0 for l in active_demand_lines):
				wo_readiness = "Shortage"
				readiness_note = f"0% available stock ({short_lines} items missing)"
				shortage_wo_count += 1
				if is_time_critical:
					critical_shortage_orders.add(wo.name)
			else:
				wo_readiness = "Partially Ready"
				readiness_note = f"{len(active_demand_lines) - short_lines} of {len(active_demand_lines)} materials available"
				partial_wo_count += 1
				if is_time_critical and short_lines > 0:
					critical_shortage_orders.add(wo.name)

		wo_readiness_list.append({
			"work_order": wo.name,
			"production_item": wo.production_item,
			"production_item_name": wo.item_name or wo.production_item,
			"status": wo.status,
			"qty": flt(wo.qty),
			"produced_qty": flt(wo.produced_qty),
			"stock_uom": wo.stock_uom,
			"target_date": str(target_date) if target_date else None,
			"days_to_target": days_to_target,
			"is_overdue": is_overdue,
			"is_due_soon": is_due_soon,
			"readiness_status": wo_readiness,
			"readiness_note": readiness_note,
			"total_components": len(items_for_this_wo),
			"shortage_components_count": short_lines,
		})

	# -------------------------------------------------------------
	# 5. Build Aggregate Shortage Summary by Item & Warehouse
	# -------------------------------------------------------------
	shortage_items_aggregate = []
	for (itm_code, wh_name), agg_data in sorted(aggregate_demand.items(), key=lambda x: x[0][0]):
		net_shortage = max(0.0, agg_data["total_remaining_demand"] - agg_data["available_stock"])
		affected = agg_data["demanding_work_orders"] if net_shortage > 0 else agg_data["affected_work_orders"]
		if net_shortage > 0 or len(affected) > 0:
			shortage_items_aggregate.append({
				"item_code": itm_code,
				"item_name": agg_data["item_name"],
				"warehouse": wh_name,
				"stock_uom": agg_data["stock_uom"],
				"total_remaining_demand": round(agg_data["total_remaining_demand"], 2),
				"available_stock": round(agg_data["available_stock"], 2),
				"actual_stock": round(agg_data["actual_stock"], 2),
				"reserved_stock": round(agg_data["reserved_stock"], 2),
				"projected_stock": round(agg_data["projected_stock"], 2),
				"net_shortage": round(net_shortage, 2),
				"affected_orders_count": len(affected),
				"affected_work_orders": sorted(list(affected)),
				"drilldown_records": [
					{"doctype": "Item", "name": itm_code},
					{"doctype": "Warehouse", "name": wh_name},
				],
			})

	# Sort aggregate items by largest net shortage descending
	shortage_items_aggregate.sort(key=lambda x: (x["net_shortage"] <= 0, -x["net_shortage"], x["item_code"]))

	# -------------------------------------------------------------
	# 6. Filter and Paginate Shortage Lines
	# -------------------------------------------------------------
	# Decide which lines to present in detail:
	# If shortage_only is requested (or by default in detailed view), show shortage lines
	lines_pool = all_shortage_lines if values.get("shortage_only") else all_requirement_lines

	# Apply warehouse and item_code filters if supplied
	if target_wh:
		lines_pool = [l for l in lines_pool if l["source_warehouse"] == target_wh]
		shortage_items_aggregate = [s for s in shortage_items_aggregate if s["warehouse"] == target_wh]

	if raw_item_filter:
		lines_pool = [l for l in lines_pool if l["item_code"] == raw_item_filter]
		shortage_items_aggregate = [s for s in shortage_items_aggregate if s["item_code"] == raw_item_filter]

	# Apply readiness_status filter to Work Orders list
	target_readiness = values.get("readiness_status")
	if target_readiness and target_readiness != "All":
		wo_readiness_list = [w for w in wo_readiness_list if w["readiness_status"] == target_readiness]
		allowed_wos = {w["work_order"] for w in wo_readiness_list}
		lines_pool = [l for l in lines_pool if l["work_order"] in allowed_wos]

	# Sort detail lines: shortages first, then time-critical orders (overdue / due soon), then days_to_target
	lines_pool.sort(
		key=lambda l: (
			not l["has_shortage"],
			not l["is_time_critical"],
			l["days_to_target"] if l["days_to_target"] is not None else 9999,
			l["work_order"],
		)
	)

	total_lines_count = len(lines_pool)
	paged_lines = lines_pool[start_offset:start_offset + limit]
	has_next = (start_offset + limit) < total_lines_count

	# Calculate summary
	distinct_shortage_items = len({l["item_code"] for l in all_shortage_lines})
	total_shortage_units = round(sum(l["shortage_qty"] for l in all_shortage_lines), 2)

	summary = {
		"total_work_orders": len(wo_records),
		"ready_work_orders": ready_wo_count,
		"partially_ready_work_orders": partial_wo_count,
		"shortage_work_orders": shortage_wo_count,
		"unknown_work_orders": unknown_wo_count,
		"critical_shortage_orders": len(critical_shortage_orders),
		"distinct_shortage_items": distinct_shortage_items,
		"total_shortage_units": total_shortage_units,
		"total_shortage_lines": len(all_shortage_lines),
	}

	readiness_distribution = {
		"Ready": ready_wo_count,
		"Partially Ready": partial_wo_count,
		"Shortage": shortage_wo_count,
		"Unknown": unknown_wo_count,
	}

	return {
		"available": True,
		"reference_date": str(ref_date),
		"summary": summary,
		"readiness_distribution": readiness_distribution,
		"shortage_items_aggregate": shortage_items_aggregate,
		"shortage_lines": paged_lines,
		"work_orders_readiness": wo_readiness_list,
		"total_lines": total_lines_count,
		"start": start_offset,
		"page_length": limit,
		"has_next_page": has_next,
		"applied_filters": values,
	}
