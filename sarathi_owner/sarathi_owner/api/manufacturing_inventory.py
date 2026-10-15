"""DASH-012: Permission-aware manufacturing overview, production output, inventory valuation, stock risk, and material shortage summary."""
from collections import defaultdict
from datetime import date, datetime, timedelta
import decimal
import math
import re

import frappe
from frappe.utils import flt, get_datetime, getdate, now_datetime

from sarathi_visibility.api.access import (
	allowed_fields,
	check_record,
	deny,
	require_capability,
	require_session,
	can_finance,
)
from sarathi_visibility.api.data_helpers import (
	_company,
	_date,
	_extra,
	_parse,
	invalid,
	pagination,
	read_errors,
)

FEATURE_KEYS = {
	"warehouse",
	"mfg_status",
	"shortage_only",
	"reference_at",
	"review_days",
	"wo_start",
	"wo_page_length",
	"stock_start",
	"stock_page_length",
	"shortage_start",
	"shortage_page_length",
}
BASE_KEYS = {"company", "customer", "project", "from_date", "to_date"}
WO_STATUS_CHOICES = ("", "All", "Active", "Completed", "Overdue", "Due soon", "Draft", "Cancelled", "Stopped")

WO_FIELDS = {
	"name", "production_item", "item_name", "qty", "produced_qty", "stock_uom",
	"status", "docstatus", "company", "project", "planned_start_date",
	"planned_end_date", "expected_delivery_date", "actual_start_date", "actual_end_date",
}
WO_ITEM_FIELDS = {
	"name", "parent", "item_code", "item_name", "source_warehouse",
	"required_qty", "transferred_qty", "consumed_qty",
}
BIN_FIELDS = {
	"name", "item_code", "warehouse", "actual_qty", "reserved_qty",
	"projected_qty", "stock_value", "valuation_rate",
}


def readable(doctype, fields):
	"""Enforce that the calling user has permission to read the required fields on doctype."""
	if not frappe.has_permission(doctype, "read"):
		deny()
	if not set(fields) <= allowed_fields(doctype):
		deny()
	if frappe.get_hooks("has_permission", {}).get(doctype):
		deny()


def validate_filters(filters):
	"""Strict server-side validation of all filter parameters."""
	values = _parse(filters)
	if set(values) - BASE_KEYS - FEATURE_KEYS:
		invalid("Unsupported manufacturing/inventory filter.")
	values = {k: v for k, v in values.items() if v is not None and v != ""}
	values["company"] = _company(values.get("company"))

	for key in ("from_date", "to_date"):
		if key in values:
			_date(values[key])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate customer link
	if values.get("customer"):
		if not frappe.db.exists("Customer", values["customer"]):
			invalid("Selected customer does not exist.")
		check_record("Customer", values["customer"])

	# Validate project link and company/customer alignment
	if values.get("project"):
		if not frappe.db.exists("Project", values["project"]):
			invalid("Selected project does not exist.")
		project_doc = check_record("Project", values["project"])
		if project_doc.company != values["company"] or (values.get("customer") and project_doc.customer != values["customer"]):
			deny()

	# Validate warehouse link and company alignment
	if values.get("warehouse"):
		if not frappe.db.exists("Warehouse", values["warehouse"]):
			invalid("Selected warehouse does not exist.")
		wh_doc = check_record("Warehouse", values["warehouse"])
		if wh_doc.company != values["company"]:
			deny()

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

	# Validate review_days
	_, window = pagination(0, values.get("review_days", 7)) if str(values.get("review_days", 7)) != "0" else (0, 0)
	if isinstance(values.get("review_days"), bool) or window > 90:
		invalid("Review window must be an integer from 0 to 90 days.")

	# Validate mfg_status
	mfg_status = values.get("mfg_status", "")
	if mfg_status not in WO_STATUS_CHOICES:
		invalid("Unsupported manufacturing status filter.")
	values.setdefault("mfg_status", "")

	# Validate shortage_only
	if "shortage_only" in values:
		raw = values["shortage_only"]
		values["shortage_only"] = str(raw).lower() in ("true", "1", "yes")

	# Validate pagination
	for prefix in ("wo", "stock", "shortage"):
		start_k = f"{prefix}_start"
		len_k = f"{prefix}_page_length"
		values[start_k], values[len_k] = pagination(values.get(start_k, 0), values.get(len_k, 25))

	values.update(reference_at=str(ref_dt), review_days=window)
	return values, ref_dt


def get_target_completion_date(row):
	"""Extract the verified target completion date from planned_end_date or expected_delivery_date."""
	target = row.get("planned_end_date") or row.get("expected_delivery_date")
	if not target:
		return None
	try:
		if isinstance(target, datetime):
			return target.date()
		if isinstance(target, date):
			return target
		return date.fromisoformat(str(target)[:10])
	except (TypeError, ValueError):
		return None


def classify_work_order(row, ref_date, review_days=7):
	"""
	Classify a Work Order into an explicit lifecycle status and health state.
	Status rules:
	- Draft: docstatus == 0
	- Cancelled: docstatus == 2 or status == 'Cancelled'
	- Stopped: status == 'Stopped'
	- Completed: docstatus == 1 and status == 'Completed'
	- Active: docstatus == 1 and status in ('Not Started', 'In Process', 'Submitted')
	Health state for active work orders:
	- Overdue: target completion date < ref_date
	- Due soon: ref_date <= target completion date <= ref_date + review_days
	- On track: target completion date > ref_date + review_days
	- Unknown: target completion date is missing
	"""
	docstatus = row.get("docstatus", 1)
	status = row.get("status", "")

	if docstatus == 0 or status == "Draft":
		return "Draft", "Draft"
	if docstatus == 2 or status == "Cancelled":
		return "Cancelled", "Cancelled"
	if status == "Stopped":
		return "Stopped", "Stopped"
	if status == "Completed":
		return "Completed", "Completed"

	# Active work orders
	target = get_target_completion_date(row)
	if target is None:
		return "Active", "Unknown"
	if target < ref_date:
		return "Active", "Overdue"
	if target <= ref_date + timedelta(days=review_days):
		return "Active", "Due soon"
	return "Active", "On track"


def get_manufacturing_summary(values, ref_dt):
	"""
	Fetch and compute manufacturing summary KPIs:
	- Counts of Active, Completed, Overdue, Due Soon, Draft, Cancelled Work Orders.
	- Planned vs Actual production grouped by stock_uom (never mix units).
	- Paginated Work Order records.
	"""
	readable("Work Order", WO_FIELDS)
	ref_date = ref_dt.date()
	review_days = values["review_days"]
	company = values["company"]

	# Resolve projects for customer filter if customer is specified without a direct project
	project_filter = values.get("project")
	customer_project_ids = None
	if values.get("customer") and not project_filter:
		customer_project_ids = frappe.get_all(
			"Project",
			filters={"company": company, "customer": values["customer"]},
			pluck="name",
		)
		if not customer_project_ids:
			# No matching projects for customer -> empty manufacturing scope
			return {
				"available": True,
				"counts": {
					"total": 0, "active": 0, "completed": 0, "overdue": 0,
					"due_soon": 0, "draft": 0, "cancelled": 0, "stopped": 0,
				},
				"production_output": {"uom_summaries": [], "item_summaries": []},
				"rows": [],
				"has_next": False,
				"total_count": 0,
				"matching_count": 0,
				"basis": "Customer-scoped Work Orders through linked Projects. Excludes unlinked orders.",
			}

	# Build base query conditions
	conditions = [["company", "=", company]]
	if project_filter:
		conditions.append(["project", "=", project_filter])
	elif customer_project_ids is not None:
		conditions.append(["project", "in", customer_project_ids])

	# Date bounds filter on planned_start_date or actual_start_date
	if values.get("from_date"):
		conditions.append(["planned_start_date", ">=", values["from_date"]])
	if values.get("to_date"):
		conditions.append(["planned_start_date", "<=", values["to_date"]])

	fields = [
		"name", "production_item", "item_name", "qty", "produced_qty", "stock_uom",
		"status", "docstatus", "company", "project", "planned_start_date",
		"planned_end_date", "expected_delivery_date", "actual_start_date", "actual_end_date",
	]

	# Query all matching Work Orders for accurate aggregations (bounded by portfolio size)
	all_wos = frappe.get_list("Work Order", filters=conditions, fields=fields, order_by="creation desc", limit_page_length=2000)

	counts = {
		"total": len(all_wos),
		"active": 0,
		"completed": 0,
		"overdue": 0,
		"due_soon": 0,
		"draft": 0,
		"cancelled": 0,
		"stopped": 0,
	}

	# Output aggregations: UOM -> {planned_qty, produced_qty}
	uom_totals = defaultdict(lambda: {"planned_qty": 0.0, "produced_qty": 0.0, "wo_count": 0})
	item_totals = defaultdict(lambda: {"planned_qty": 0.0, "produced_qty": 0.0, "stock_uom": "", "item_name": "", "wo_count": 0})

	enriched_wos = []
	for wo in all_wos:
		lifecycle, health = classify_work_order(wo, ref_date, review_days)
		if lifecycle == "Active":
			counts["active"] += 1
			if health == "Overdue":
				counts["overdue"] += 1
			elif health == "Due soon":
				counts["due_soon"] += 1
		elif lifecycle == "Completed":
			counts["completed"] += 1
		elif lifecycle == "Draft":
			counts["draft"] += 1
		elif lifecycle == "Cancelled":
			counts["cancelled"] += 1
		elif lifecycle == "Stopped":
			counts["stopped"] += 1

		# Production output metrics include active and completed orders (exclude draft/cancelled)
		if wo.docstatus == 1 and wo.status != "Cancelled":
			uom = wo.stock_uom or "Nos"
			qty = flt(wo.qty)
			produced = flt(wo.produced_qty)
			uom_totals[uom]["planned_qty"] += qty
			uom_totals[uom]["produced_qty"] += produced
			uom_totals[uom]["wo_count"] += 1

			prod_item = wo.production_item
			item_totals[prod_item]["planned_qty"] += qty
			item_totals[prod_item]["produced_qty"] += produced
			item_totals[prod_item]["stock_uom"] = uom
			item_totals[prod_item]["item_name"] = wo.item_name or prod_item
			item_totals[prod_item]["wo_count"] += 1

		target_date = get_target_completion_date(wo)
		days_to_target = (target_date - ref_date).days if target_date else None
		pct = round((flt(wo.produced_qty) / flt(wo.qty) * 100), 1) if flt(wo.qty) > 0 else 0.0

		enriched_wos.append({
			"name": wo.name,
			"production_item": wo.production_item,
			"item_name": wo.item_name or wo.production_item,
			"qty": flt(wo.qty),
			"produced_qty": flt(wo.produced_qty),
			"stock_uom": wo.stock_uom or "Nos",
			"status": wo.status,
			"lifecycle": lifecycle,
			"health": health,
			"progress_pct": pct,
			"planned_start_date": str(wo.planned_start_date)[:10] if wo.planned_start_date else None,
			"target_completion_date": str(target_date) if target_date else None,
			"days_to_target": days_to_target,
			"project": wo.project,
		})

	# Format UOM summaries
	uom_summaries = []
	for uom, data in sorted(uom_totals.items()):
		planned = data["planned_qty"]
		produced = data["produced_qty"]
		var = round(produced - planned, 2)
		achieve = round((produced / planned * 100), 1) if planned > 0 else 0.0
		uom_summaries.append({
			"stock_uom": uom,
			"planned_qty": round(planned, 2),
			"produced_qty": round(produced, 2),
			"variance": var,
			"achievement_pct": achieve,
			"order_count": data["wo_count"],
		})

	# Format Item summaries (top items)
	item_summaries = []
	for item_code, data in sorted(item_totals.items(), key=lambda x: x[1]["planned_qty"], reverse=True)[:15]:
		planned = data["planned_qty"]
		produced = data["produced_qty"]
		var = round(produced - planned, 2)
		achieve = round((produced / planned * 100), 1) if planned > 0 else 0.0
		item_summaries.append({
			"item_code": item_code,
			"item_name": data["item_name"],
			"stock_uom": data["stock_uom"],
			"planned_qty": round(planned, 2),
			"produced_qty": round(produced, 2),
			"variance": var,
			"achievement_pct": achieve,
			"order_count": data["wo_count"],
		})

	# Filter detail list by mfg_status if specified
	filtered_rows = enriched_wos
	mfg_status = values.get("mfg_status")
	if mfg_status:
		if mfg_status == "Active":
			filtered_rows = [r for r in filtered_rows if r["lifecycle"] == "Active"]
		elif mfg_status == "Completed":
			filtered_rows = [r for r in filtered_rows if r["lifecycle"] == "Completed"]
		elif mfg_status == "Overdue":
			filtered_rows = [r for r in filtered_rows if r["health"] == "Overdue"]
		elif mfg_status == "Due soon":
			filtered_rows = [r for r in filtered_rows if r["health"] == "Due soon"]
		elif mfg_status == "Draft":
			filtered_rows = [r for r in filtered_rows if r["lifecycle"] == "Draft"]
		elif mfg_status == "Cancelled":
			filtered_rows = [r for r in filtered_rows if r["lifecycle"] == "Cancelled"]
		elif mfg_status == "Stopped":
			filtered_rows = [r for r in filtered_rows if r["lifecycle"] == "Stopped"]

	matching_count = len(filtered_rows)
	start = values["wo_start"]
	length = values["wo_page_length"]
	paged_rows = filtered_rows[start:start + length]
	has_next = (start + length) < matching_count

	return {
		"available": True,
		"counts": counts,
		"production_output": {
			"uom_summaries": uom_summaries,
			"item_summaries": item_summaries,
		},
		"rows": paged_rows,
		"has_next": has_next,
		"total_count": len(all_wos),
		"matching_count": matching_count,
		"basis": "Counts cover all matching company Work Orders. Overdue logic uses target completion date < reference date for open/active orders.",
	}


def get_inventory_valuation(values):
	"""
	Fetch inventory valuation using actual ERPNext stock valuation logic:
	- If to_date is present and in the past: calls ERPNext Stock Balance report logic.
	- Otherwise: uses native Bin.stock_value grouped by company leaf warehouses.
	- Enforces leaf warehouse boundaries and company scoping.
	"""
	readable("Bin", BIN_FIELDS)
	company = values["company"]
	warehouse_filter = values.get("warehouse")

	# Find authorized leaf warehouses for the company
	wh_conditions = {"company": company, "is_group": 0}
	if warehouse_filter:
		wh_conditions["name"] = warehouse_filter
	leaf_warehouses = frappe.get_all("Warehouse", filters=wh_conditions, pluck="name")
	if not leaf_warehouses:
		return {
			"available": True,
			"valuation": 0.0,
			"currency": frappe.get_cached_value("Company", company, "default_currency") or "INR",
			"total_items": 0,
			"total_actual_qty": 0.0,
			"total_reserved_qty": 0.0,
			"total_available_qty": 0.0,
			"total_projected_qty": 0.0,
			"warehouse_scope": warehouse_filter or "None configured",
			"method": "Perpetual Inventory / ERPNext valuation engine",
			"basis": "No active leaf warehouses found for company.",
		}

	to_date = values.get("to_date")
	today_str = str(getdate())
	is_historical = bool(to_date and to_date < today_str)

	currency = frappe.get_cached_value("Company", company, "default_currency") or "INR"

	if is_historical:
		# Use standard ERPNext Stock Balance report logic for historical as-of-date valuation
		try:
			from erpnext.stock.report.stock_balance.stock_balance import execute as execute_stock_balance
			rep_filters = frappe._dict({
				"company": company,
				"to_date": to_date,
			})
			if warehouse_filter:
				rep_filters["warehouse"] = warehouse_filter
			_, rep_rows = execute_stock_balance(rep_filters)
			total_val = sum(flt(r.get("bal_val", 0)) for r in rep_rows if isinstance(r, dict))
			total_actual = sum(flt(r.get("bal_qty", 0)) for r in rep_rows if isinstance(r, dict))
			total_reserved = sum(flt(r.get("reserved_stock", 0)) for r in rep_rows if isinstance(r, dict))
			distinct_items = len({r.get("item_code") for r in rep_rows if isinstance(r, dict) and r.get("item_code")})
			return {
				"available": True,
				"valuation": round(total_val, 2),
				"currency": currency,
				"total_items": distinct_items,
				"total_actual_qty": round(total_actual, 2),
				"total_reserved_qty": round(total_reserved, 2),
				"total_available_qty": round(max(0.0, total_actual - total_reserved), 2),
				"total_projected_qty": round(total_actual - total_reserved, 2),
				"warehouse_scope": warehouse_filter or f"{len(leaf_warehouses)} company warehouses",
				"method": "ERPNext Historical Stock Balance Report",
				"basis": f"Calculated as of historical date {to_date} using Stock Balance report.",
			}
		except Exception:
			# Fallback to Bin query if stock balance report cannot execute
			pass

	# Current valuation from Bin table
	bin_records = frappe.get_all(
		"Bin",
		filters={"warehouse": ["in", leaf_warehouses]},
		fields=["item_code", "warehouse", "actual_qty", "reserved_qty", "projected_qty", "stock_value", "valuation_rate"],
		limit_page_length=5000,
	)

	total_val = sum(flt(b.stock_value) for b in bin_records)
	total_actual = sum(flt(b.actual_qty) for b in bin_records)
	total_reserved = sum(flt(b.reserved_qty) for b in bin_records)
	total_projected = sum(flt(b.projected_qty) for b in bin_records)
	distinct_items = len({b.item_code for b in bin_records})

	return {
		"available": True,
		"valuation": round(total_val, 2),
		"currency": currency,
		"total_items": distinct_items,
		"total_actual_qty": round(total_actual, 2),
		"total_reserved_qty": round(total_reserved, 2),
		"total_available_qty": round(max(0.0, total_actual - total_reserved), 2),
		"total_projected_qty": round(total_projected, 2),
		"warehouse_scope": warehouse_filter or f"{len(leaf_warehouses)} company warehouses",
		"method": "ERPNext Perpetual Stock Valuation (Bin stock_value)",
		"basis": "Current valuation from ERPNext Bin records across company leaf warehouses.",
	}


def get_stock_risk_summary(values):
	"""
	Fetch stock availability and inventory risk indicators:
	- Distinguish actual, reserved, available, and projected stock.
	- Evaluate low-stock against Item Reorder levels or Item safety_stock.
	- Explicitly label items with no configured threshold.
	- Paginated item inventory rows.
	"""
	readable("Bin", BIN_FIELDS)
	company = values["company"]
	warehouse_filter = values.get("warehouse")

	wh_conditions = {"company": company, "is_group": 0}
	if warehouse_filter:
		wh_conditions["name"] = warehouse_filter
	leaf_warehouses = frappe.get_all("Warehouse", filters=wh_conditions, pluck="name")
	if not leaf_warehouses:
		return {
			"available": True,
			"counts": {"low_stock_items": 0, "negative_projected_items": 0, "zero_stock_with_demand": 0, "unconfigured_items": 0},
			"rows": [],
			"has_next": False,
			"total_count": 0,
			"basis": "No active warehouses in scope.",
		}

	# Retrieve bins
	bins = frappe.get_all(
		"Bin",
		filters={"warehouse": ["in", leaf_warehouses]},
		fields=["item_code", "warehouse", "actual_qty", "reserved_qty", "projected_qty", "stock_value", "valuation_rate"],
		order_by="item_code asc, warehouse asc",
		limit_page_length=5000,
	)

	# Fetch Item details (item_name, stock_uom, safety_stock)
	item_codes = list({b.item_code for b in bins})
	item_map = {}
	if item_codes:
		items = frappe.get_all(
			"Item",
			filters={"name": ["in", item_codes]},
			fields=["name", "item_name", "stock_uom", "safety_stock"],
			limit_page_length=5000,
		)
		for it in items:
			item_map[it.name] = {
				"item_name": it.item_name or it.name,
				"stock_uom": it.stock_uom or "Nos",
				"safety_stock": flt(it.safety_stock) if it.safety_stock else 0.0,
			}

	# Fetch Item Reorder thresholds
	reorder_map = {}
	if item_codes:
		reorders = frappe.get_all(
			"Item Reorder",
			filters={"parent": ["in", item_codes]},
			fields=["parent", "warehouse", "warehouse_reorder_level", "warehouse_reorder_qty"],
			limit_page_length=5000,
		)
		for ro in reorders:
			reorder_map[(ro.parent, ro.warehouse)] = flt(ro.warehouse_reorder_level)

	low_stock_count = 0
	neg_proj_count = 0
	zero_demand_count = 0
	unconfigured_count = 0

	rows = []
	for b in bins:
		actual = flt(b.actual_qty)
		reserved = flt(b.reserved_qty)
		available = max(0.0, actual - reserved)
		projected = flt(b.projected_qty)
		val_rate = flt(b.valuation_rate)
		stock_val = flt(b.stock_value)

		meta = item_map.get(b.item_code, {"item_name": b.item_code, "stock_uom": "Nos", "safety_stock": 0.0})

		# Determine reorder threshold: warehouse-specific Item Reorder > Item safety stock > None
		wh_reorder = reorder_map.get((b.item_code, b.warehouse))
		if wh_reorder is not None:
			threshold = wh_reorder
			threshold_source = "Warehouse Reorder Level"
		elif meta["safety_stock"] > 0:
			threshold = meta["safety_stock"]
			threshold_source = "Item Safety Stock"
		else:
			threshold = None
			threshold_source = "Unconfigured"

		# Determine risk classification
		risk_status = "Healthy"
		if threshold is not None:
			if available <= threshold or projected <= threshold:
				risk_status = "Low Stock"
				low_stock_count += 1
		else:
			unconfigured_count += 1
			risk_status = "No threshold configured"

		if projected < 0:
			neg_proj_count += 1
			if risk_status != "Low Stock":
				risk_status = "Negative Projected"

		if actual <= 0 and reserved > 0:
			zero_demand_count += 1
			if risk_status not in ("Low Stock", "Negative Projected"):
				risk_status = "Zero Stock with Demand"

		rows.append({
			"item_code": b.item_code,
			"item_name": meta["item_name"],
			"warehouse": b.warehouse,
			"actual_qty": round(actual, 2),
			"reserved_qty": round(reserved, 2),
			"available_qty": round(available, 2),
			"projected_qty": round(projected, 2),
			"stock_uom": meta["stock_uom"],
			"stock_value": round(stock_val, 2),
			"valuation_rate": round(val_rate, 4),
			"threshold": round(threshold, 2) if threshold is not None else None,
			"threshold_source": threshold_source,
			"risk_status": risk_status,
		})

	# Sort rows: Low Stock and risks first
	priority = {"Low Stock": 0, "Negative Projected": 1, "Zero Stock with Demand": 2, "No threshold configured": 3, "Healthy": 4}
	rows.sort(key=lambda r: (priority.get(r["risk_status"], 5), r["item_code"]))

	matching_count = len(rows)
	start = values["stock_start"]
	length = values["stock_page_length"]
	paged_rows = rows[start:start + length]
	has_next = (start + length) < matching_count

	return {
		"available": True,
		"counts": {
			"low_stock_items": low_stock_count,
			"negative_projected_items": neg_proj_count,
			"zero_stock_with_demand": zero_demand_count,
			"unconfigured_items": unconfigured_count,
		},
		"rows": paged_rows,
		"has_next": has_next,
		"total_count": matching_count,
		"basis": "Low stock checks configured warehouse reorder levels or item safety stock. Items without thresholds are clearly labeled.",
	}


def get_material_shortages(values, ref_dt):
	"""
	Evaluate raw material shortages affecting active Work Orders:
	- Scope: Active Work Orders (docstatus = 1 and status in ('Not Started', 'In Process')).
	- Child items: Work Order Item required_qty - transferred_qty = remaining_required.
	- Available stock: max(0, actual_qty - reserved_qty) in source_warehouse.
	- Shortage: max(0, remaining_required - available_stock).
	- Links: Work Order, item_code, source_warehouse, expected completion date.
	"""
	readable("Work Order", WO_FIELDS)
	readable("Work Order Item", WO_ITEM_FIELDS)
	readable("Bin", BIN_FIELDS)
	company = values["company"]
	ref_date = ref_dt.date()

	project_filter = values.get("project")
	customer_project_ids = None
	if values.get("customer") and not project_filter:
		customer_project_ids = frappe.get_all(
			"Project",
			filters={"company": company, "customer": values["customer"]},
			pluck="name",
		)
		if not customer_project_ids:
			return {
				"available": True,
				"counts": {"shortage_work_orders": 0, "shortage_items": 0, "total_shortage_lines": 0},
				"rows": [],
				"has_next": False,
				"total_count": 0,
				"basis": "Customer-scoped Work Orders through linked Projects.",
			}

	# Active Work Orders
	wo_conditions = [
		["company", "=", company],
		["docstatus", "=", 1],
		["status", "in", ["Not Started", "In Process"]],
	]
	if project_filter:
		wo_conditions.append(["project", "=", project_filter])
	elif customer_project_ids is not None:
		wo_conditions.append(["project", "in", customer_project_ids])

	active_wos = frappe.get_list(
		"Work Order",
		filters=wo_conditions,
		fields=["name", "production_item", "item_name", "qty", "produced_qty", "stock_uom", "status", "planned_start_date", "planned_end_date", "expected_delivery_date", "project"],
		limit_page_length=1000,
	)
	if not active_wos:
		return {
			"available": True,
			"counts": {"shortage_work_orders": 0, "shortage_items": 0, "total_shortage_lines": 0},
			"rows": [],
			"has_next": False,
			"total_count": 0,
			"basis": "No active Work Orders in scope.",
		}

	wo_names = [wo.name for wo in active_wos]
	wo_dict = {wo.name: wo for wo in active_wos}

	# Query child Work Order Items
	wo_items = frappe.get_all(
		"Work Order Item",
		filters={"parent": ["in", wo_names]},
		fields=["parent", "item_code", "item_name", "source_warehouse", "required_qty", "transferred_qty", "consumed_qty"],
		limit_page_length=5000,
	)

	# Fetch Bins for the distinct (item_code, source_warehouse) pairs
	bin_keys = list({(it.item_code, it.source_warehouse) for it in wo_items if it.source_warehouse})
	items_needed = list({k[0] for k in bin_keys})
	warehouses_needed = list({k[1] for k in bin_keys})

	bin_map = {}
	if items_needed and warehouses_needed:
		bins = frappe.get_all(
			"Bin",
			filters={"item_code": ["in", items_needed], "warehouse": ["in", warehouses_needed]},
			fields=["item_code", "warehouse", "actual_qty", "reserved_qty", "projected_qty"],
			limit_page_length=5000,
		)
		for b in bins:
			bin_map[(b.item_code, b.warehouse)] = b

	# Fetch Item UOM
	item_uoms = {}
	if items_needed:
		for itm in frappe.get_all("Item", filters={"name": ["in", items_needed]}, fields=["name", "stock_uom"]):
			item_uoms[itm.name] = itm.stock_uom or "Nos"

	shortage_lines = []
	affected_wo_names = set()
	shortage_item_codes = set()

	for row in wo_items:
		wo = wo_dict.get(row.parent)
		if not wo:
			continue
		req = flt(row.required_qty)
		trans = flt(row.transferred_qty)
		remaining_req = max(0.0, req - trans)

		# If material is already transferred, it's not a shortage for this Work Order
		if remaining_req <= 0.0:
			continue

		source_wh = row.source_warehouse or "Unspecified"
		bin = bin_map.get((row.item_code, row.source_warehouse))
		actual_stock = flt(bin.actual_qty) if bin else 0.0
		reserved_stock = flt(bin.reserved_qty) if bin else 0.0
		available_stock = max(0.0, actual_stock - reserved_stock)

		shortage_qty = max(0.0, remaining_req - available_stock)
		target_date = get_target_completion_date(wo)
		days_to_target = (target_date - ref_date).days if target_date else None

		line_data = {
			"work_order": wo.name,
			"production_item": wo.production_item,
			"production_item_name": wo.item_name or wo.production_item,
			"project": wo.project,
			"expected_completion": str(target_date) if target_date else None,
			"days_to_target": days_to_target,
			"item_code": row.item_code,
			"item_name": row.item_name or row.item_code,
			"source_warehouse": source_wh,
			"required_qty": round(req, 2),
			"transferred_qty": round(trans, 2),
			"remaining_required": round(remaining_req, 2),
			"available_stock": round(available_stock, 2),
			"shortage_qty": round(shortage_qty, 2),
			"stock_uom": item_uoms.get(row.item_code, "Nos"),
			"has_shortage": shortage_qty > 0.0,
		}

		if shortage_qty > 0.0:
			affected_wo_names.add(wo.name)
			shortage_item_codes.add(row.item_code)

		shortage_lines.append(line_data)

	# If shortage_only filter is active (default True if user didn't specify otherwise), filter lines
	shortage_only = values.get("shortage_only", True)
	if shortage_only:
		display_lines = [l for l in shortage_lines if l["has_shortage"]]
	else:
		display_lines = shortage_lines

	# Sort: shortages first, then earliest expected completion
	display_lines.sort(key=lambda l: (not l["has_shortage"], l["days_to_target"] if l["days_to_target"] is not None else 9999))

	matching_count = len(display_lines)
	start = values["shortage_start"]
	length = values["shortage_page_length"]
	paged_lines = display_lines[start:start + length]
	has_next = (start + length) < matching_count

	return {
		"available": True,
		"counts": {
			"shortage_work_orders": len(affected_wo_names),
			"shortage_items": len(shortage_item_codes),
			"total_shortage_lines": len([l for l in shortage_lines if l["has_shortage"]]),
		},
		"rows": paged_lines,
		"has_next": has_next,
		"total_count": len([l for l in shortage_lines if l["has_shortage"]]),
		"matching_count": matching_count,
		"basis": "Shortages compare remaining required quantity (required - transferred) against available stock (actual - reserved) in the source warehouse.",
	}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_manufacturing_inventory_summary(filters=None, **extra):
	"""
	Main entry point for Owner & Executive Manufacturing and Inventory Summary.
	Returns:
	- manufacturing overview and planned vs actual production
	- inventory valuation
	- stock quantity and risk indicators
	- material shortages affecting active production
	"""
	require_capability("owner")
	_extra(extra)
	values, ref_dt = validate_filters(filters)

	# Manufacturing summary
	try:
		mfg_summary = get_manufacturing_summary(values, ref_dt)
	except frappe.PermissionError:
		mfg_summary = {"available": False, "reason": "Work Orders are unavailable for your permissions."}

	# Inventory valuation
	try:
		inv_summary = get_inventory_valuation(values)
	except frappe.PermissionError:
		inv_summary = {"available": False, "reason": "Inventory valuation is unavailable for your permissions."}

	# Stock risk summary
	try:
		risk_summary = get_stock_risk_summary(values)
	except frappe.PermissionError:
		risk_summary = {"available": False, "reason": "Stock indicators are unavailable for your permissions."}

	# Material shortages
	try:
		shortage_summary = get_material_shortages(values, ref_dt)
	except frappe.PermissionError:
		shortage_summary = {"available": False, "reason": "Material shortages are unavailable for your permissions."}

	currency = frappe.get_cached_value("Company", values["company"], "default_currency") or "INR"

	return {
		"applied_filters": values,
		"reference_at": str(ref_dt),
		"reference_date": str(ref_dt.date()),
		"review_days": values["review_days"],
		"currency": currency,
		"manufacturing": mfg_summary,
		"inventory": inv_summary,
		"stock_risk": risk_summary,
		"shortages": shortage_summary,
		"generated_at": str(now_datetime()),
	}
