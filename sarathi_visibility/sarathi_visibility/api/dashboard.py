"""Sarathi Industrial Dashboard API and shared report definitions."""

import csv
import io
import hashlib
from collections import defaultdict

import frappe

from sarathi_visibility.api.access import (authorized, can_finance, check_record)
from frappe.utils import cint, flt, now_datetime

from sarathi_visibility.api.accounting import get_accounting_card_summary
from sarathi_visibility.api.dashboard_data import grouped, load, readable
from sarathi_visibility.api.factory_overview import get_factory_overview
from sarathi_visibility.api.material_readiness import get_material_readiness
from sarathi_visibility.api.production_pipeline import get_production_pipeline
from sarathi_visibility.api.subcontracting import get_subcontracting_card_summary
from sarathi_visibility.api.work_orders import (
	get_job_card_detail,
	get_job_cards,
	get_work_order_detail,
	get_work_orders,
)
from sarathi_visibility.api.workstations import get_workstation_downtime
from sarathi_visibility.api.quality_rework import (
	get_quality_overview,
	get_rework_overview,
	get_subcontracting_overview,
)
from sarathi_visibility.api.production_exceptions import get_production_exceptions


@frappe.whitelist(methods=["POST"])
@authorized("production")
def associate_customer(company, customer):
	for doctype, name in (("Company", company), ("Customer", customer)):
		frappe.get_doc(doctype, name).check_permission("read")

	if not frappe.has_permission("Sarathi Customer Organization", "create"):
		frappe.throw("You cannot link customers to organizations.", frappe.PermissionError)

	existing = frappe.db.exists("Sarathi Customer Organization", {"company": company, "customer": customer})

	if existing:
		check_record("Sarathi Customer Organization", existing)
		return existing

	name = "SCO-" + hashlib.sha256(f"{company}\0{customer}".encode()).hexdigest()[:40]
	try:
		return (
		frappe.get_doc(
			{
				"doctype": "Sarathi Customer Organization",
				"company": company,
				"customer": customer,
			}
		)
		.insert(set_name=name)
		.name
		)
	except frappe.DuplicateEntryError:
		check_record("Sarathi Customer Organization", name)
		return name


def col(field, label, kind="Data", options=None, width=150):
	return dict(fieldname=field, label=label, fieldtype=kind, options=options, width=width)


PROJECT = col("project", "Project", "Link", "Project")

REPORTS = {
	"items": (
		"Items catalogue",
		"Item",
		[
			col("name", "Item Code", "Link", "Item"),
			col("item_name", "Item Name"),
			col("item_group", "Item Group", "Link", "Item Group"),
			col("stock_uom", "Stock Unit"),
			col("is_stock_item", "Stock Item", "Check"),
			col("default_warehouse", "Default Warehouse", "Link", "Warehouse"),
			col("valuation_rate", "Valuation Rate", "Currency"),
			col("standard_rate", "Standard Rate", "Currency"),
		],
	),
	"inventory": (
		"Warehouse stock & inventory balance",
		"Bin",
		[
			col("item_code", "Item Code", "Link", "Item"),
			col("item_name", "Item Name"),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("actual_qty", "Current Stock Qty", "Float"),
			col("stock_uom", "Unit"),
			col("valuation_rate", "Valuation Rate", "Currency"),
			col("stock_value", "Total Stock Value", "Currency"),
			col("reserved_qty", "Reserved Qty", "Float"),
		],
	),
	"procurement_exceptions": (
		"Unassigned / conflicting procurement",
		"Purchase Order",
		[
			col("doctype", "Record type"),
			col("name", "Record", "Dynamic Link", "doctype"),
			PROJECT,
			col("item_code", "Item", "Link", "Item"),
			col("issue", "Action needed", width=360),
		],
	),
	"material_history": (
		"Lifetime material consumption",
		"Work Order",
		[
			PROJECT,
			col("work_order", "Work Order", "Link", "Work Order"),
			col("work_order_status", "Production status"),
			col("item_code", "Material", "Link", "Item"),
			col("unit", "Stock unit"),
			col("required_qty", "Required", "Float"),
			col("transferred_qty", "Transferred", "Float"),
			col("consumed_qty", "Consumed", "Float"),
			col("source_warehouse", "Source warehouse", "Link", "Warehouse"),
		],
	),
	"stock_details": (
		"Lifetime stock movement items",
		"Stock Entry",
		[
			PROJECT,
			col("parent", "Stock Entry", "Link", "Stock Entry"),
			col("work_order", "Work Order", "Link", "Work Order"),
			col("job_card", "Job Card", "Link", "Job Card"),
			col("item_code", "Item", "Link", "Item"),
			col("transfer_qty", "Movement quantity", "Float"),
			col("stock_uom", "Unit"),
			col("s_warehouse", "From warehouse", "Link", "Warehouse"),
			col("t_warehouse", "To warehouse", "Link", "Warehouse"),
			col("purpose", "Purpose"),
			col("batch_no", "Batch"),
			col("posting_date", "Posting date", "Date"),
		],
	),
	"stock_ledger": (
		"Project voucher stock ledger",
		"Stock Ledger Entry",
		[
			PROJECT,
			col("voucher_type", "Voucher type"),
			col("voucher_no", "Voucher", "Dynamic Link", "voucher_type"),
			col("item_code", "Item", "Link", "Item"),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("actual_qty", "Signed stock movement", "Float"),
			col("stock_uom", "Unit"),
			col("posting_date", "Posting date", "Date"),
			col("posting_time", "Posting time"),
		],
	),
	"reservations": (
		"Project stock reservations",
		"Stock Reservation Entry",
		[
			PROJECT,
			col("name", "Reservation", "Link", "Stock Reservation Entry"),
			col("voucher_type", "Voucher type"),
			col("voucher_no", "Voucher", "Dynamic Link", "voucher_type"),
			col("item_code", "Item", "Link", "Item"),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("stock_uom", "Unit"),
			col("reserved_qty", "Reserved", "Float"),
			col("consumed_qty", "Consumed", "Float"),
			col("delivered_qty", "Delivered", "Float"),
			col("transferred_qty", "Transferred", "Float"),
			col("status", "Status"),
		],
	),
	"quality": (
		"Project quality inspections",
		"Quality Inspection",
		[
			PROJECT,
			col("name", "Inspection", "Link", "Quality Inspection"),
			col("reference_type", "Reference type"),
			col("reference_name", "Reference", "Dynamic Link", "reference_type"),
			col("item_code", "Item", "Link", "Item"),
			col("inspection_type", "Inspection type"),
			col("status", "Result"),
			col("sample_size", "Sample size (not rejected quantity)", "Float"),
			col("report_date", "Inspection date", "Date"),
		],
	),
	"job_logs": (
		"Job Card time history",
		"Job Card",
		[
			PROJECT,
			col("job_card", "Job Card", "Link", "Job Card"),
			col("operation", "Operation"),
			col("employee", "Employee", "Link", "Employee"),
			col("from_time", "Started", "Datetime"),
			col("to_time", "Ended", "Datetime"),
			col("completed_qty", "Recorded completion", "Float"),
			col("time_in_mins", "Minutes", "Float"),
		],
	),
	"job_suboperations": (
		"Job Card sub-operations",
		"Job Card",
		[
			PROJECT,
			col("job_card", "Job Card", "Link", "Job Card"),
			col("operation", "Sub-operation"),
			col("status", "Status"),
			col("completed_qty", "Completed", "Float"),
			col("time_in_mins", "Minutes", "Float"),
		],
	),
	"tracking_setup": (
		"Project part tracking setup",
		"Project",
		[
			PROJECT,
			col("customer", "Customer", "Link", "Customer"),
			col("main_bom", "Main BOM", "Link", "BOM"),
			col("validation", "Manufacturing validation"),
			col("physical_parts", "Physical part tracking", width=420),
		],
	),
	"part_production": (
		"Recorded operation output parts",
		"Stock Entry",
		[
			PROJECT,
			col("job_card", "Job Card", "Link", "Job Card"),
			col("work_order", "Work Order", "Link", "Work Order"),
			col("operation", "Operation"),
			col("workstation", "Workstation", "Link", "Workstation"),
			col("item_code", "Actual output part", "Link", "Item"),
			col("stock_uom", "Part unit"),
			col("transfer_qty", "Posted output", "Float"),
			col("parent", "Manufacture entry", "Link", "Stock Entry"),
			col("t_warehouse", "Output warehouse", "Link", "Warehouse"),
			col("posting_date", "Production date", "Date"),
		],
	),
	"live_activity": (
		"Live project activity",
		"Job Card",
		[
			PROJECT,
			col("customer", "Customer", "Link", "Customer"),
			col("job_card", "Job Card", "Link", "Job Card"),
			col("work_order", "Work Order", "Link", "Work Order"),
			col("operation", "Running operation"),
			col("workstation", "Workstation", "Link", "Workstation"),
			col("started_at", "Started", "Datetime"),
			col("last_activity", "Last activity", "Datetime"),
			col("planned", "Job Card planned", "Float"),
			col("completed", "Job Card completed", "Float"),
			col("remaining", "Job Card remaining", "Float"),
			col("unit", "Unit"),
			col("status", "Activity"),
		],
	),
	"operation_balance": (
		"Lifetime operation balances",
		"Work Order",
		[
			PROJECT,
			col("customer", "Customer", "Link", "Customer"),
			col("work_order", "Work Order", "Link", "Work Order"),
			col("operation", "Operation"),
			col("sequence", "Sequence", "Int"),
			col("workstation", "Workstation", "Link", "Workstation"),
			col("item", "Output item", "Link", "Item"),
			col("unit", "Unit"),
			col("planned", "Planned", "Float"),
			col("completed", "Completed", "Float"),
			col("process_loss", "Process loss", "Float"),
			col("remaining", "Remaining", "Float"),
			col("progress", "Completion", "Percent"),
			col("status", "Operation status"),
			col("work_order_status", "Work Order status"),
			col("corrective_jobs", "Corrective cards", "Int"),
			col("planned_hours", "Planned hours", "Float"),
			col("actual_hours", "Actual hours", "Float"),
			col("quantity_basis", "Quantity basis", width=360),
		],
	),
	"production_summary": (
		"Project production summary",
		"Project",
		[
			PROJECT,
			col("project_name", "Project name"),
			col("customer", "Customer", "Link", "Customer"),
			col("project_status", "Project status"),
			col("production_status", "Production status"),
			col("live_status", "Live project status"),
			col("running_count", "Running operations", "Int"),
			col("last_activity", "Last recorded activity", "Datetime"),
			col("work_orders", "Submitted work orders", "Int"),
			col("operations", "Operations", "Int"),
			col("finished_operations", "Finished operations", "Int"),
			col("open_operations", "Open operations", "Int"),
			col("stock_tracking", "Semi-finished tracking"),
			col("note", "Basis", width=260),
		],
	),
	"wip_stock": (
		"Semi-finished shared warehouse stock",
		"Bin",
		[
			col("item", "Semi-finished item", "Link", "Item"),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("unit", "Unit"),
			col("available", "Current shared stock", "Float"),
			col("operations", "Operations"),
			col("projects", "Related projects"),
			col("basis", "Stock basis", width=300),
		],
	),
	"deadlines": (
		"Upcoming and overdue deadlines",
		"Project",
		[
			col("doctype", "Record type"),
			col("name", "Record", "Dynamic Link", "doctype"),
			PROJECT,
			col("due_date", "Due date", "Date"),
			col("status", "Status"),
			col("days_remaining", "Days remaining", "Int"),
		],
	),
	"projects": (
		"Project portfolio",
		"Project",
		[
			col("name", "Project", "Link", "Project"),
			col("project_name", "Project name"),
			col("company", "Organization", "Link", "Company"),
			col("customer", "Customer", "Link", "Customer"),
			col("custom_sarathi_bom", "Main BOM", "Link", "BOM"),
			col("status", "Status"),
			col("percent_complete", "Project progress", "Percent"),
			col("expected_end_date", "Due date", "Date"),
		],
	),
	"orders": (
		"Sales orders",
		"Sales Order",
		[
			col("name", "Sales Order", "Link", "Sales Order"),
			PROJECT,
			col("customer", "Customer", "Link", "Customer"),
			col("transaction_date", "Order date", "Date"),
			col("status", "Status"),
			col("currency", "Currency"),
			col("grand_total", "Order value", "Currency", "currency"),
			col("value_scope", "Value basis"),
			col("per_delivered", "Delivered", "Percent"),
			col("per_billed", "Billed", "Percent"),
		],
	),
	"order_items": (
		"Order items and delivery",
		"Sales Order",
		[
			col("parent", "Sales Order", "Link", "Sales Order"),
			PROJECT,
			col("item_code", "Item", "Link", "Item"),
			col("qty", "Ordered", "Float"),
			col("delivered_qty", "Delivered", "Float"),
			col("uom", "Unit"),
			col("delivery_date", "Delivery date", "Date"),
		],
	),
	"work_orders": (
		"Work orders",
		"Work Order",
		[
			col("name", "Work Order", "Link", "Work Order"),
			PROJECT,
			col("bom_no", "BOM", "Link", "BOM"),
			col("sales_order", "Sales Order", "Link", "Sales Order"),
			col("production_item", "Item", "Link", "Item"),
			col("qty", "Planned", "Float"),
			col("produced_qty", "Produced", "Float"),
			col("stock_uom", "Unit"),
			col("status", "Status"),
			col("planned_end_date", "Planned end", "Datetime"),
		],
	),
	"job_cards": (
		"Job cards / shop floor",
		"Job Card",
		[
			col("name", "Job Card", "Link", "Job Card"),
			PROJECT,
			col("production_phase", "Production phase"),
			col("is_corrective_job_card", "Corrective work", "Check"),
			col("process_loss_qty", "Process loss", "Float"),
			col("work_order", "Work Order", "Link", "Work Order"),
			col("operation", "Operation"),
			col("workstation", "Workstation", "Link", "Workstation"),
			col("status", "Status"),
			col("for_quantity", "Planned", "Float"),
			col("total_completed_qty", "Completed", "Float"),
			col("stock_uom", "Unit"),
			col("planned_hours", "Planned hours", "Float"),
			col("actual_hours", "Actual hours", "Float"),
		],
	),
	"boms": (
		"Engineering / BOM revisions",
		"BOM",
		[
			col("name", "BOM", "Link", "BOM"),
			PROJECT,
			col("item", "Product", "Link", "Item"),
			col("assignment", "Assignment"),
			col("quantity", "BOM quantity", "Float"),
			col("uom", "Unit"),
			col("docstatus", "Document status", "Int"),
			col("currency", "Currency"),
			col("total_cost", "BOM cost", "Currency", "currency"),
		],
	),
	"components": (
		"Engineering components / purchased parts",
		"BOM",
		[
			col("parent", "BOM", "Link", "BOM"),
			col("item_code", "Component", "Link", "Item"),
			col("item_name", "Description"),
			col("qty", "Per BOM quantity", "Float"),
			col("uom", "Unit"),
			col("bom_no", "Subassembly BOM", "Link", "BOM"),
		],
	),
	"operations": (
		"Planned BOM operations",
		"BOM",
		[
			col("parent", "BOM", "Link", "BOM"),
			col("idx", "Sequence", "Int"),
			col("operation", "Operation"),
			col("workstation", "Workstation", "Link", "Workstation"),
			col("time_in_mins", "Planned minutes", "Float"),
		],
	),
	"materials": (
		"Material requirements / shared warehouse stock",
		"Work Order",
		[
			col("item_code", "Material", "Link", "Item"),
			col("company", "Organization", "Link", "Company"),
			col("warehouse", "Source warehouse", "Link", "Warehouse"),
			col("uom", "Unit"),
			col("required_qty", "Required", "Float"),
			col("remaining_qty", "Still to transfer", "Float"),
			col("available_qty", "Shared warehouse stock", "Float"),
			col("shortage_qty", "Potential shortage", "Float"),
		],
	),
	"stock": (
		"Stock movements",
		"Stock Entry",
		[
			col("name", "Stock Entry", "Link", "Stock Entry"),
			PROJECT,
			col("work_order", "Work Order", "Link", "Work Order"),
			col("purpose", "Purpose"),
			col("posting_date", "Posting date", "Date"),
			col("docstatus", "Document status", "Int"),
		],
	),
	"finished": (
		"Finished production receipts",
		"Stock Entry",
		[
			col("parent", "Stock Entry", "Link", "Stock Entry"),
			PROJECT,
			col("item_code", "Finished item", "Link", "Item"),
			col("transfer_qty", "Received", "Float"),
			col("stock_uom", "Unit"),
			col("t_warehouse", "Warehouse", "Link", "Warehouse"),
			col("posting_date", "Posting date", "Date"),
		],
	),
	"tasks": (
		"Project tasks / pipeline",
		"Task",
		[
			col("name", "Task", "Link", "Task"),
			PROJECT,
			col("subject", "Task"),
			col("status", "Status"),
			col("progress", "Progress", "Percent"),
			col("exp_end_date", "Due date", "Datetime"),
			col("expected_time", "Planned hours", "Float"),
			col("actual_time", "Actual hours", "Float"),
		],
	),
	"integrations": (
		"Machine integration logs",
		"Sarathi Machine Integration Log",
		[
			col("name", "Log", "Link", "Sarathi Machine Integration Log"),
			PROJECT,
			col("machine", "Machine"),
			col("source_system", "Source system"),
			col("sync_status", "Sync status"),
			col("planned_qty", "Planned", "Float"),
			col("completed_qty", "Completed", "Float"),
			col("rejected_qty", "Rejected", "Float"),
			col("modified", "Last updated", "Datetime"),
		],
	),
	"issues": (
		"Data quality and alerts",
		"Project",
		[
			col("doctype", "Record type"),
			col("name", "Record", "Dynamic Link", "doctype"),
			PROJECT,
			col("issue", "Action needed", width=460),
		],
	),
	"workstations": (
		"Workstations & workload",
		"Workstation",
		[
			col("name", "Workstation", "Link", "Workstation"),
			col("workstation_name", "Workstation Name"),
			col("workstation_type", "Workstation Type", "Link", "Workstation Type"),
			col("status", "Status"),
			col("production_capacity", "Capacity", "Float"),
			col("jobs", "Job cards", "Int"),
			col("open_jobs", "Open job cards", "Int"),
			col("planned_hours", "Planned hours", "Float"),
			col("actual_hours", "Actual hours", "Float"),
			col("plant_floor", "Plant Floor", "Link", "Plant Floor"),
		],
	),
	"operations_catalogue": (
		"Operations catalogue",
		"Operation",
		[
			col("name", "Operation ID", "Link", "Operation"),
			col("operation_name", "Operation Name"),
			col("workstation", "Default Workstation", "Link", "Workstation"),
			col("description", "Description"),
		],
	),
	"warehouses": (
		"Warehouses catalogue",
		"Warehouse",
		[
			col("name", "Warehouse", "Link", "Warehouse"),
			col("warehouse_name", "Warehouse Name"),
			col("company", "Organization", "Link", "Company"),
			col("is_group", "Is Group", "Check"),
			col("parent_warehouse", "Parent Warehouse", "Link", "Warehouse"),
		],
	),
	"customers": (
		"Customers catalogue",
		"Customer",
		[
			col("name", "Customer ID", "Link", "Customer"),
			col("customer_name", "Customer Name"),
			col("customer_type", "Type"),
			col("customer_group", "Customer Group", "Link", "Customer Group"),
			col("territory", "Territory", "Link", "Territory"),
		],
	),
	"suppliers": (
		"Suppliers catalogue",
		"Supplier",
		[
			col("name", "Supplier ID", "Link", "Supplier"),
			col("supplier_name", "Supplier Name"),
			col("supplier_group", "Supplier Group", "Link", "Supplier Group"),
			col("country", "Country"),
			col("is_transporter", "Transporter", "Check"),
		],
	),
	"workstation_types": (
		"Workstation types",
		"Workstation Type",
		[
			col("name", "Workstation Type", "Link", "Workstation Type"),
			col("description", "Description"),
		],
	),
	"plant_floors": (
		"Plant floors",
		"Plant Floor",
		[
			col("name", "Floor", "Link", "Plant Floor"),
			col("floor_name", "Floor Name"),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("company", "Company", "Link", "Company"),
		],
	),
	"routings": (
		"Routings",
		"Routing",
		[
			col("name", "Routing", "Link", "Routing"),
			col("routing_name", "Routing Name"),
			col("disabled", "Disabled", "Check"),
		],
	),
}


from sarathi_visibility.api.pipeline import DOCUMENTS

for _key, (_doctype, _child) in DOCUMENTS.items():
	REPORTS[_key] = (
		_doctype + " project items",
		_doctype,
		[
			PROJECT,
			col("name", _doctype, "Link", _doctype),
			col("item_code", "Item", "Link", "Item"),
			col("supplier", "Supplier", "Link", "Supplier"),
			col("customer", "Customer", "Link", "Customer"),
			col("qty", "Quantity", "Float"),
			col("uom", "Unit"),
			col("stock_qty", "Stock quantity", "Float"),
			col("stock_uom", "Stock unit"),
			col("ordered_qty", "Requested quantity ordered", "Float"),
			col("received_qty", "Received quantity", "Float"),
			col("returned_qty", "Returned", "Float"),
			col("rejected_qty", "Supplier rejected", "Float"),
			col("remaining_qty", "Outstanding request / order", "Float"),
			col("status", "Status"),
			col("docstatus", "Document status", "Int"),
			col("date", "Date", "Date"),
			col("currency", "Currency"),
			col("net_amount", "Item net value", "Currency", "currency"),
			col(
				"outstanding_amount",
				"Whole-document outstanding (repeated)",
				"Currency",
				"currency",
			),
			col("warehouse", "Warehouse", "Link", "Warehouse"),
			col("basis", "Project attribution"),
			col("value_basis", "Value basis", width=400),
		],
	)


def get_project_resource_ids(data, project_name):
	if not project_name:
		return {}

	proj = next((p for p in data.get("projects", []) if p.get("name") == project_name), {})
	proj_name = str(project_name).strip()
	proj_title = str(proj.get("project_name") or "").strip()

	# 1. BOMs explicitly linked to this project
	project_boms = set()
	if proj.get("custom_sarathi_bom"):
		project_boms.add(proj.get("custom_sarathi_bom"))
	for b in data.get("boms", []):
		b_proj = str(b.get("custom_sarathi_project") or b.get("project") or "")
		if b_proj == proj_name or proj_name in b_proj:
			project_boms.add(b.get("name"))
	for w in data.get("work_orders", []):
		if w.get("project") == proj_name and w.get("bom_no"):
			project_boms.add(w.get("bom_no"))

	# 2. Operations & workstations from project BOMs
	bom_stations = set()
	bom_ops = set()
	for op in data.get("operations", []):
		if op.get("parent") in project_boms:
			if op.get("workstation"):
				bom_stations.add(op.get("workstation"))
			if op.get("operation"):
				bom_ops.add(op.get("operation"))

	# 3. Work Orders
	wo_stations = set()
	wo_ops = set()
	wo_wh = set()
	wo_items = set()
	for w in data.get("work_orders", []):
		if w.get("project") == proj_name:
			if w.get("production_item"):
				wo_items.add(w.get("production_item"))
			for fld in (
				"source_warehouse",
				"fg_warehouse",
				"wip_warehouse",
				"scrap_warehouse",
			):
				if w.get(fld):
					wo_wh.add(w.get(fld))

	# 4. Job Cards
	j_stations = set()
	j_ops = set()
	j_items = set()
	for j in data.get("job_cards", []):
		if j.get("project") == proj_name:
			if j.get("workstation"):
				j_stations.add(j.get("workstation"))
			if j.get("operation"):
				j_ops.add(j.get("operation"))
			if j.get("production_item"):
				j_items.add(j.get("production_item"))
			if j.get("finished_good"):
				j_items.add(j.get("finished_good"))

	# 5. Live activity, operation balance, part production
	live_stations = {
		a.get("workstation")
		for a in data.get("live_activity", [])
		if (a.get("project") == proj_name or not a.get("project")) and a.get("workstation")
	}
	live_ops = {
		a.get("operation")
		for a in data.get("live_activity", [])
		if (a.get("project") == proj_name or not a.get("project")) and a.get("operation")
	}
	bal_stations = {
		b.get("workstation")
		for b in data.get("operation_balance", [])
		if b.get("project") == proj_name and b.get("workstation")
	}
	bal_ops = {
		b.get("operation")
		for b in data.get("operation_balance", [])
		if b.get("project") == proj_name and b.get("operation")
	}
	part_stations = {
		p.get("workstation")
		for p in data.get("part_production", [])
		if p.get("project") == proj_name and p.get("workstation")
	}
	part_ops = {
		p.get("operation")
		for p in data.get("part_production", [])
		if p.get("project") == proj_name and p.get("operation")
	}

	# 6. BOM components
	comp_items = set()
	comp_wh = set()
	for c in data.get("components", []):
		if c.get("parent") in project_boms:
			if c.get("item_code"):
				comp_items.add(c.get("item_code"))
			if c.get("source_warehouse"):
				comp_wh.add(c.get("source_warehouse"))

	# 7. Pipeline & inventory movements
	pipeline_items = set()
	pipeline_wh = set()

	for oi in data.get("order_items", []):
		if oi.get("project") == proj_name:
			if oi.get("item_code"):
				pipeline_items.add(oi.get("item_code"))
			if oi.get("warehouse"):
				pipeline_wh.add(oi.get("warehouse"))

	for doc_key in (
		"requests",
		"purchases",
		"receipts",
		"purchase_invoices",
		"deliveries",
		"sales_invoices",
		"material_history",
	):
		for r in data.get(doc_key, []):
			if r.get("project") == proj_name:
				if r.get("item_code"):
					pipeline_items.add(r.get("item_code"))
				for wfld in (
					"warehouse",
					"source_warehouse",
					"t_warehouse",
					"s_warehouse",
				):
					if r.get(wfld):
						pipeline_wh.add(r.get(wfld))

	for s in data.get("stock_details", []):
		if s.get("project") == proj_name:
			if s.get("item_code"):
				pipeline_items.add(s.get("item_code"))
			if s.get("s_warehouse"):
				pipeline_wh.add(s.get("s_warehouse"))
			if s.get("t_warehouse"):
				pipeline_wh.add(s.get("t_warehouse"))

	for f in data.get("finished", []):
		if f.get("project") == proj_name:
			if f.get("item_code"):
				pipeline_items.add(f.get("item_code"))
			if f.get("t_warehouse"):
				pipeline_wh.add(f.get("t_warehouse"))

	for l in data.get("stock_ledger", []):
		if l.get("project") == proj_name:
			if l.get("item_code"):
				pipeline_items.add(l.get("item_code"))
			if l.get("warehouse"):
				pipeline_wh.add(l.get("warehouse"))

	for r in data.get("reservations", []):
		if r.get("project") == proj_name:
			if r.get("item_code"):
				pipeline_items.add(r.get("item_code"))
			if r.get("warehouse"):
				pipeline_wh.add(r.get("warehouse"))

	for m in data.get("materials", []):
		if m.get("item_code"):
			pipeline_items.add(m.get("item_code"))
		if m.get("warehouse"):
			pipeline_wh.add(m.get("warehouse"))

	for w_ip in data.get("wip_stock", []):
		if w_ip.get("project") == proj_name:
			if w_ip.get("item_code"):
				pipeline_items.add(w_ip.get("item_code"))
			if w_ip.get("warehouse"):
				pipeline_wh.add(w_ip.get("warehouse"))

	for p in data.get("part_production", []):
		if p.get("project") == proj_name:
			if p.get("item_code"):
				pipeline_items.add(p.get("item_code"))

	# 8. Routings
	project_routings = set()
	for b in data.get("boms", []):
		if b.get("name") in project_boms and b.get("routing"):
			project_routings.add(b.get("routing"))
	for w in data.get("work_orders", []):
		if w.get("project") == proj_name and w.get("routing"):
			project_routings.add(w.get("routing"))

	# 9. Explicit project links or naming matches on master records
	proj_name_lower = proj_name.lower()
	proj_title_lower = proj_title.lower() if len(proj_title) >= 3 else ""

	def matches_project(doc, name_field, title_field=""):
		p_val = str(doc.get("project") or doc.get("custom_sarathi_project") or "").strip()
		if p_val == proj_name:
			return True
		doc_name = str(doc.get(name_field) or "").lower()
		doc_title = str(doc.get(title_field) or "").lower() if title_field else ""
		if proj_name_lower and (proj_name_lower in doc_name or (doc_title and proj_name_lower in doc_title)):
			return True
		if proj_title_lower and (
			proj_title_lower in doc_name or (doc_title and proj_title_lower in doc_title)
		):
			return True
		return False

	project_warehouses = {w for w in (wo_wh | comp_wh | pipeline_wh) if w}
	for wh in data.get("warehouses", []):
		if matches_project(wh, "name", "warehouse_name"):
			project_warehouses.add(wh.get("name"))

	project_operations = {o for o in (j_ops | bom_ops | bal_ops | live_ops | part_ops | wo_ops) if o}
	for op in data.get("operations_catalogue", []):
		if matches_project(op, "name", "operation_name"):
			project_operations.add(op.get("name"))

	project_workstations = {
		s
		for s in (j_stations | bom_stations | live_stations | bal_stations | part_stations | wo_stations)
		if s
	}
	for ws in data.get("workstations", []):
		if matches_project(ws, "name", "workstation_name"):
			project_workstations.add(ws.get("name"))

	for op in data.get("operations_catalogue", []):
		if (
			op.get("name") in project_operations or op.get("operation_name") in project_operations
		) and op.get("workstation"):
			project_workstations.add(op.get("workstation"))

	for rt in data.get("routings", []):
		if matches_project(rt, "name", "routing_name"):
			project_routings.add(rt.get("name"))

	main_item = proj.get("main_item")
	for b in data.get("boms", []):
		if b.get("name") in project_boms and b.get("item"):
			comp_items.add(b.get("item"))
	project_items = {i for i in ({main_item} | comp_items | wo_items | j_items | pipeline_items) if i}
	for it in data.get("items", []):
		if matches_project(it, "name", "item_name"):
			project_items.add(it.get("name"))

	all_ws = data.get("workstations", [])
	project_ws_types = {
		w.get("workstation_type")
		for w in all_ws
		if w.get("name") in project_workstations
		and w.get("workstation_type")
		and w.get("workstation_type") != "—"
	}
	for wt in data.get("workstation_types", []):
		if matches_project(wt, "name", "workstation_type"):
			project_ws_types.add(wt.get("name"))

	return {
		"workstations": project_workstations,
		"operations": project_operations,
		"warehouses": project_warehouses,
		"items": project_items,
		"workstation_types": project_ws_types,
		"routings": project_routings,
	}


def report_data(data, report, subset="", search=""):
	if report not in REPORTS:
		frappe.throw("Unknown dashboard report.")

	project_filter = data.get("filters", {}).get("project")
	res = get_project_resource_ids(data, project_filter) if project_filter else {}

	if report in (
		"workstations",
		"operations_catalogue",
		"warehouses",
		"customers",
		"suppliers",
		"workstation_types",
		"plant_floors",
		"routings",
		"items",
		"inventory",
	):
		result = list(data.get(report, []))

		# Project-specific scoping when a project is selected (unless subset=="all")
		if project_filter and subset != "all":
			if report == "warehouses":
				allowed = res.get("warehouses", set())
				result = [r for r in result if r.get("name") in allowed or r.get("warehouse_name") in allowed]
			elif report == "workstations":
				allowed = res.get("workstations", set())
				result = [
					r for r in result if r.get("name") in allowed or r.get("workstation_name") in allowed
				]
			elif report == "operations_catalogue":
				allowed = res.get("operations", set())
				result = [r for r in result if r.get("name") in allowed or r.get("operation_name") in allowed]
			elif report == "workstation_types":
				allowed = res.get("workstation_types", set())
				result = [
					r for r in result if r.get("name") in allowed or r.get("workstation_type") in allowed
				]
			elif report == "routings":
				allowed = res.get("routings", set())
				result = [r for r in result if r.get("name") in allowed or r.get("routing_name") in allowed]
			elif report == "items":
				allowed = res.get("items", set())
				result = [r for r in result if r.get("name") in allowed or r.get("item_code") in allowed]
			elif report == "inventory":
				allowed_wh = res.get("warehouses", set())
				allowed_it = res.get("items", set())
				result = [
					r
					for r in result
					if (r.get("warehouse") in allowed_wh or r.get("item_code") in allowed_it)
				]
			elif report == "plant_floors":
				allowed_wh = res.get("warehouses", set())
				result = [r for r in result if r.get("warehouse") in allowed_wh]

		if subset == "open" and report == "workstations":
			result = [r for r in result if r.get("open_jobs", 0) > 0]
		elif subset == "production" and report == "workstations":
			result = [r for r in result if r.get("status") == "Production"]
	else:
		result = list(data.get(report, []))

	if (data.get("filters", {}).get("from_date") or data.get("filters", {}).get("to_date")) and report in (
		"production_summary",
		"operation_balance",
		"live_activity",
	):
		scoped = {p.name for p in data.get("projects", [])}
		result = [r for r in result if r.get("project") in scoped]

	if subset == "active" and report == "projects":
		result = [r for r in result if r.status not in ("Completed", "Cancelled")]

	elif subset in ("completed", "ongoing", "on_hold") and report == "projects":
		result = [
			r
			for r in result
			if r.status == {"completed": "Completed", "ongoing": "Open", "on_hold": "On hold"}[subset]
		]

	elif subset == "ongoing" and report in ("operation_balance", "production_summary"):
		result = [r for r in result if r["project_status"] == "Open"]

	elif subset == "delayed" and report == "projects":
		result = [r for r in result if r.delayed]

	elif subset == "open" and report in ("orders", "work_orders", "job_cards"):
		result = [
			r
			for r in result
			if r.docstatus != 2
			and r.status not in ("Completed", "Cancelled", "Closed", "Stopped")
			and (report not in ("orders", "work_orders") or r.docstatus == 1)
			and (report != "job_cards" or r.get("production_phase") == "Executable pending")
		]

	elif subset == "planned" and report == "job_cards":
		result = [r for r in result if r.get("production_phase") == "Planned / draft Work Order"]
	elif subset == "rework" and report == "job_cards":
		result = [r for r in result if r.get("is_corrective_job_card") and r.docstatus != 2]
	elif subset == "shortages" and report == "materials":
		result = [r for r in result if r["shortage_qty"] is not None and r["shortage_qty"] > 0]

	elif subset in (
		"in_progress",
		"not_started",
		"paused",
		"closure_pending",
	) and report in ("production_summary", "operation_balance"):
		pass
	elif subset in ("all", "project"):
		pass
	elif subset:
		# Only known, server-defined subsets can change row selection.

		frappe.throw("Unsupported report subset.")

	if subset in (
		"in_progress",
		"not_started",
		"paused",
		"closure_pending",
	) and report in ("production_summary", "operation_balance"):
		matching = {
			r["project"]
			for r in data["production_summary"]
			if r["live_status"]
			== {
				"in_progress": "In progress",
				"not_started": "Not started",
				"paused": "On hold / Stopped",
				"closure_pending": "Production finished · Closure pending",
			}[subset]
		}
		result = [r for r in result if r["project"] in matching]
	if search:
		fields = [c["fieldname"] for c in REPORTS[report][2]]

		result = [
			r for r in result if search.casefold() in " ".join(str(r.get(k) or "") for k in fields).casefold()
		]

	return result


@frappe.whitelist()
@authorized("production")
def clear_dashboard_cache(**kwargs):
	"""Purges cached metadata and redis entries for Sarathi Visibility."""
	try:
		frappe.cache.delete_keys("sarathi:*")
		frappe.clear_cache()
		return {"status": "success", "message": "Cache purged"}
	except Exception as e:
		return {"status": "error", "message": str(e)}


@frappe.whitelist()
@authorized("production")
def get_summary(filters=None, **kwargs):
	raw_filters = frappe.parse_json(filters) if isinstance(filters, str) else dict(filters or {})
	legacy_filters = dict(raw_filters)
	project_statuses = {"", "Active", "Ongoing", "Completed", "Delayed", "Cancelled", "On hold"}
	if legacy_filters.get("status") not in project_statuses:
		legacy_filters["status"] = ""

	data = load(legacy_filters)

	projects = data["projects"]

	f = data.get("filters", {})
	if f.get("from_date") or f.get("to_date"):
		scoped_projects = {p.name for p in projects}
		data["production_summary"] = [
			r for r in data["production_summary"] if r.get("project") in scoped_projects
		]
		data["operation_balance"] = [
			r for r in data["operation_balance"] if r.get("project") in scoped_projects
		]
		data["pipeline_summary"] = [
			r for r in data["pipeline_summary"] if r.get("project") in scoped_projects
		]
		data["live_activity"] = [r for r in data["live_activity"] if r.get("project") in scoped_projects]

	# Keep this overview in project units: documents and inspections are counts,
	# while operation/stock quantities may have different units and cannot be added.
	project_health = []
	for project in projects:
		pid = project.name
		summary = next((row for row in data["production_summary"] if row["project"] == pid), {})
		operations = [row for row in data["operation_balance"] if row["project"] == pid]
		running = summary.get("running_operations") or []
		unfinished = [row for row in operations if row.get("remaining") is not None and row["remaining"] > 0]
		unfinished.sort(key=lambda row: (str(row.get("work_order") or ""), flt(row.get("sequence"))))
		inspections = [row for row in data["quality"] if row.project == pid and row.docstatus == 1]
		pipeline = next((row for row in data["pipeline_summary"] if row["project"] == pid), {})
		material_shortages = None
		if data["filters"].get("project") == pid and readable("Bin") and readable("Work Order"):
			if not any(
				row.get("shortage_qty") is None and flt(row.get("remaining_qty")) > 0
				for row in data["materials"]
			):
				material_shortages = sum(row["shortage_qty"] > 0 for row in data["materials"])
		project_health.append(
			dict(
				project=pid,
				live_status=summary.get("live_status") or "Access restricted",
				current_operations=[
					dict(
						operation=row.get("operation"),
						workstation=row.get("workstation"),
						job_card=row.get("job_card"),
						started_at=row.get("started_at"),
					)
					for row in running
				],
				next_operation=dict(unfinished[0]) if unfinished else None,
				operations_finished=summary.get("finished_operations"),
				operations_total=summary.get("operations"),
				last_activity=summary.get("last_activity"),
				material_shortages=material_shortages,
				purchase_orders=pipeline.get("purchases"),
				receipts=pipeline.get("receipts"),
				inspection_passed=(
					sum(row.status in ("Accepted", "Approved") for row in inspections)
					if readable("Quality Inspection")
					else None
				),
				inspection_rejected=(
					sum(row.status in ("Rejected", "Failed") for row in inspections)
					if readable("Quality Inspection")
					else None
				),
				deliveries=pipeline.get("deliveries"),
				sales_invoices=pipeline.get("sales_invoices"),
			)
		)

	def kpi(label, report, subset=""):
		return dict(
			label=label,
			value=len(report_data(data, report, subset)),
			report=report,
			subset=subset,
		)

	cards = [
		kpi("Total projects", "projects"),
		kpi("Total items", "items"),
		kpi("Warehouse stock", "inventory"),
		kpi("Warehouses", "warehouses"),
		kpi("Workstations", "workstations"),
		kpi("Operations", "operations_catalogue"),
		kpi("Workstation types", "workstation_types"),
		kpi("Routings", "routings"),
		kpi("Active BOMs", "boms"),
		kpi("Customers", "customers"),
		kpi("Suppliers", "suppliers"),
		kpi("Open orders", "orders", "open"),
		kpi("Active work orders", "work_orders", "open"),
		kpi("Executable Job Cards", "job_cards", "open"),
		kpi("Planned Job Cards", "job_cards", "planned"),
		kpi("Completed projects", "projects", "completed"),
		kpi("In progress", "production_summary", "in_progress"),
		kpi("Not started", "production_summary", "not_started"),
		kpi("Delayed projects", "projects", "delayed"),
	]

	selected = next(iter(projects), None) if data["filters"]["project"] else None

	if selected:
		cards = [
			dict(label="Project status", value=selected.status, report="projects"),
			dict(
				label="Due date",
				value=str(selected.expected_end_date or "Not set"),
				report="projects",
			),
			dict(
				label="Project progress",
				value=f"{flt(selected.percent_complete):g}%",
				report="tasks",
			),
			kpi("Project Warehouses", "warehouses"),
			kpi("Project Operations", "operations_catalogue"),
			kpi("Project Workstations", "workstations"),
			kpi("Project Workstation Types", "workstation_types"),
			kpi("Project Routings", "routings"),
			kpi("Project Items", "items"),
			kpi("Open orders", "orders", "open"),
			kpi("Active work orders", "work_orders", "open"),
			kpi("Executable Job Cards", "job_cards", "open"),
			kpi("Planned Job Cards", "job_cards", "planned"),
			kpi("Material shortages", "materials", "shortages"),
		]

	quantities = {}

	for w in data["work_orders"]:
		if w.docstatus != 1:
			continue

		label = f"{w.production_item} ({w.get('stock_uom') or 'units'})"

		q = quantities.setdefault(label, [0, 0])

		q[0] += flt(w.qty)

		q[1] += flt(w.produced_qty)

	sales = defaultdict(lambda: defaultdict(float))

	for o in data["orders"]:
		if o.docstatus == 1:
			sales[o.currency][str(o.transaction_date)[:7]] += flt(o.grand_total)

	live_counts = grouped(data["production_summary"], "live_status")
	charts = [
		dict(
			title="Live production status",
			type="donut",
			labels=list(live_counts),
			datasets=[dict(name="Projects", values=list(live_counts.values()))],
			report="production_summary",
		),
		dict(
			title="Project status",
			type="donut",
			labels=list(grouped(projects, "status")),
			datasets=[dict(name="Projects", values=list(grouped(projects, "status").values()))],
			report="projects",
		),
		dict(
			title="Project progress · first 12 projects",
			type="bar",
			labels=[p.project_name for p in projects[:12]],
			datasets=[
				dict(
					name="Progress %",
					values=[flt(p.percent_complete) for p in projects[:12]],
				)
			],
			report="projects",
		),
		dict(
			title="Sales order status",
			type="donut",
			labels=list(grouped(data["orders"], "status")),
			datasets=[
				dict(
					name="Orders",
					values=list(grouped(data["orders"], "status").values()),
				)
			],
			report="orders",
		),
		dict(
			title="Deadlines · days remaining (negative means overdue)",
			type="bar",
			labels=[r["name"] for r in data["deadlines"][:12]],
			datasets=[
				dict(
					name="Days remaining",
					values=[r["days_remaining"] for r in data["deadlines"][:12]],
				)
			],
			report="deadlines",
		),
		dict(
			title="Planned versus produced · by item and unit",
			type="bar",
			labels=list(quantities)[:12],
			datasets=[
				dict(
					name="Planned",
					values=[v[0] for v in list(quantities.values())[:12]],
				),
				dict(
					name="Produced",
					values=[v[1] for v in list(quantities.values())[:12]],
				),
			],
			report="work_orders",
		),
		dict(
			title="Operation hours · first 12 job cards",
			type="bar",
			labels=[j.name for j in data["job_cards"][:12] if j.docstatus != 2],
			datasets=[
				dict(
					name="Planned hours",
					values=[j.planned_hours for j in data["job_cards"][:12] if j.docstatus != 2],
				),
				dict(
					name="Actual hours",
					values=[j.actual_hours for j in data["job_cards"][:12] if j.docstatus != 2],
				),
			],
			report="job_cards",
		),
	]

	for currency, months in (sales.items() if can_finance() else []):
		charts.append(
			dict(
				title=f"Submitted sales orders · {currency}",
				type="line",
				labels=sorted(months),
				datasets=[dict(name=currency, values=[months[m] for m in sorted(months)])],
				report="orders",
			)
		)

	if selected:
		tasks = data["tasks"]

		jobs = [j for j in data["job_cards"] if j.docstatus != 2]

		charts.append(
			dict(
				title="Manufacturing pipeline · recorded progress",
				type="bar",
				labels=(
					[t.subject for t in tasks[:12]]
					if tasks
					else [f"{j.operation} · {j.name}" for j in jobs[:12]]
				),
				datasets=[
					dict(
						name="Progress %",
						values=(
							[flt(t.progress) for t in tasks[:12]]
							if tasks
							else [
								(
									min(
										100,
										flt(j.total_completed_qty) / flt(j.for_quantity) * 100,
									)
									if flt(j.for_quantity)
									else 0
								)
								for j in jobs[:12]
							]
						),
					)
				],
				report="tasks" if tasks else "job_cards",
			)
		)

	ops = data["operation_balance"] if selected else report_data(data, "operation_balance", "in_progress")

	for unit in sorted({r["unit"] or "Unit unavailable" for r in ops}):
		rows_for_unit = [
			r
			for r in ops
			if (r["unit"] or "Unit unavailable") == unit
			and r["completed"] is not None
			and r["remaining"] is not None
		][:12]

		charts.append(
			dict(
				title=f"Operation quantities · {unit} · first 12 operations",
				type="bar",
				labels=[
					f"{r['project']} · {r['operation']} · {r['work_order']} · {r['sequence']}"
					for r in rows_for_unit
				],
				datasets=[
					dict(
						name="Completed",
						values=[r["completed"] or 0 for r in rows_for_unit],
					),
					dict(
						name="Remaining",
						values=[r["remaining"] or 0 for r in rows_for_unit],
					),
				],
				report="operation_balance",
				subset="" if selected else "in_progress",
			)
		)

	for report_key, title, value_fields in [
		("purchases", "Procurement ordered / received", ("qty", "received_qty")),
		("part_production", "Recorded operation output parts", ("transfer_qty",)),
	]:
		entries = [r for r in data[report_key] if report_key == "part_production" or r.docstatus == 1]
		grouped_items = {}
		for r in entries:
			label = (
				f"{r.item_code} ({r.get('stock_uom') if report_key == 'part_production' else r.get('uom')})"
			)
			v = grouped_items.setdefault(label, [0] * len(value_fields))
			for i, field in enumerate(value_fields):
				v[i] += flt(r.get(field))
		charts.append(
			dict(
				title=title + " · first 12 items",
				type="bar",
				labels=list(grouped_items)[:12],
				datasets=[
					dict(
						name=field.replace("_", " ").title(),
						values=[v[i] for v in list(grouped_items.values())[:12]],
					)
					for i, field in enumerate(value_fields)
				],
				report=report_key,
			)
		)
	receipts = defaultdict(lambda: defaultdict(float))

	for r in data["finished"]:
		receipts[f"{r.item_code} ({r.stock_uom})"][str(r.posting_date)] += flt(r.transfer_qty)

	for item, dates in list(receipts.items())[:6]:
		labels = sorted(dates)[-12:]

		charts.append(
			dict(
				title=f"Finished receipts · {item} · latest 12 dates",
				type="line",
				labels=labels,
				datasets=[dict(name="Received quantity", values=[dates[d] for d in labels])],
				report="finished",
			)
		)

	shortages = [m for m in data["materials"] if m["shortage_qty"] is not None and m["shortage_qty"] > 0][:12]

	charts.append(
		dict(
			title="Potential material shortages · by item and unit",
			type="bar",
			labels=[f"{m['item_code']} ({m['uom']})" for m in shortages],
			datasets=[dict(name="Shortage", values=[m["shortage_qty"] for m in shortages])],
			report="materials",
			subset="shortages",
		)
	)

	if not data["filters"]["customer"]:
		charts.append(
			dict(
				title="Projects by customer",
				type="bar",
				labels=[c["customer_name"] for c in data["customers"][:12]],
				datasets=[
					dict(
						name="Projects",
						values=[c["project_count"] for c in data["customers"][:12]],
					)
				],
				report="projects",
			)
		)

	factory_overview = None
	try:
		f_filters = dict(raw_filters)
		if not f_filters.get("company") and data.get("filters", {}).get("company"):
			f_filters["company"] = data["filters"]["company"]
		factory_overview = get_factory_overview(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing factory overview: {err}")
		factory_overview = {
			"available": False,
			"reason": "Factory overview is currently unavailable.",
		}

	production_pipeline = None
	try:
		production_pipeline = get_production_pipeline(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing production pipeline: {err}")
		production_pipeline = {
			"available": False,
			"reason": "Production pipeline is currently unavailable.",
		}

	material_readiness = None
	try:
		material_readiness = get_material_readiness(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing material readiness: {err}")
		material_readiness = {
			"available": False,
			"reason": "Material readiness is currently unavailable.",
		}

	workstation_downtime = None
	try:
		workstation_downtime = get_workstation_downtime(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing workstation downtime: {err}")
		workstation_downtime = {
			"available": False,
			"reason": "Workstation and downtime view is currently unavailable.",
		}

	quality_overview = None
	try:
		quality_overview = get_quality_overview(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing quality overview: {err}")
		quality_overview = {
			"available": False,
			"reason": "Quality overview is currently unavailable.",
		}

	rework_overview = None
	try:
		rework_overview = get_rework_overview(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing rework overview: {err}")
		rework_overview = {
			"available": False,
			"reason": "Rework overview is currently unavailable.",
		}

	subcontracting_overview = None
	try:
		subcontracting_overview = get_subcontracting_overview(f_filters)
	except Exception as err:
		frappe.log_error(f"Error computing subcontracting overview: {err}")
		subcontracting_overview = {
			"available": False,
			"reason": "Subcontracting overview is currently unavailable.",
		}

	production_exceptions = None
	try:
		production_exceptions = get_production_exceptions(
			f_filters,
			material_readiness=material_readiness,
			workstation_downtime=workstation_downtime,
			quality_overview=quality_overview,
			rework_overview=rework_overview,
			subcontracting_overview=subcontracting_overview,
		)
	except Exception as err:
		frappe.log_error(f"Error computing production exceptions: {err}")
		production_exceptions = {
			"available": False,
			"reason": "Production exception queue is currently unavailable.",
		}

	return dict(
		factory_overview=factory_overview,
		production_pipeline=production_pipeline,
		material_readiness=material_readiness,
		workstation_downtime=workstation_downtime,
		quality_overview=quality_overview,
		rework_overview=rework_overview,
		subcontracting_overview=subcontracting_overview,
		production_exceptions=production_exceptions,
		accounting_summary=get_accounting_card_summary(data["filters"]),
		subcontracting_summary=get_subcontracting_card_summary(data["filters"]),
		project_health=project_health,
		pipeline_summary=data["pipeline_summary"],
		tracking_setup=data["tracking_setup"],
		procurement_exceptions=data["procurement_exceptions"][:20],
		procurement_exception_count=len(data["procurement_exceptions"]),
		production_summary=data["production_summary"],
		live_activity=data["live_activity"],
		operation_balance=data["operation_balance"],
		wip_stock=data["wip_stock"],
		filters={**data["filters"], **({"workstation": raw_filters["workstation"]} if "workstation" in raw_filters else {})},
		companies=data["companies"],
		customers=data["customers"],
		projects=projects,
		selected_project=selected,
		kpis=cards,
		charts=charts,
		alerts=data["issues"][:20],
		alert_count=len(data["issues"]),
		generated_at=str(now_datetime()),
		reports=[dict(key=k, title=v[0]) for k, v in REPORTS.items()],
		can_create={
			dt: bool(frappe.has_permission(dt, "create"))
			for dt in (
				"Company",
				"Customer",
				"Project",
				"BOM",
				"Sales Order",
				"Work Order",
				"Material Request",
				"Production Plan",
				"Pick List",
				"Stock Entry",
				"Job Card",
				"Item",
				"Warehouse",
				"Operation",
				"Workstation Type",
				"Workstation",
				"Plant Floor",
				"Routing",
				"Sarathi Customer Organization",
				"Supplier",
				"Purchase Order",
				"Purchase Receipt",
				"Purchase Invoice",
				"Delivery Note",
				"Sales Invoice",
				"Quality Inspection",
				"Subcontracting Order",
			)
		},
		restricted=[
			dt
			for dt in (
				"Project",
				"Customer",
				"Sales Order",
				"Work Order",
				"Job Card",
				"BOM",
				"Stock Entry",
				"Bin",
				"Purchase Order",
				"Purchase Receipt",
				"Purchase Invoice",
				"Stock Ledger Entry",
				"Stock Reservation Entry",
				"Quality Inspection",
				"Delivery Note",
				"Sales Invoice",
			)
			if not readable(dt)
		],
	)


@frappe.whitelist()
@authorized("production")
def get_report(filters=None, report="projects", subset="", search="", start=0, page_length=25, **kwargs):
	from sarathi_visibility.api.data_helpers import pagination

	start, length = pagination(start, page_length)
	data = load(filters)

	result = report_data(data, report, subset, search)

	return dict(
		title=REPORTS[report][0],
		columns=REPORTS[report][2],
		rows=result[start : start + length],
		total=len(result),
		start=start,
		page_length=length,
	)


@frappe.whitelist()
@authorized("production")
def get_record(filters, doctype, name, **kwargs):
	data = load(filters)

	keys = {dt: key for key, (dt, child) in DOCUMENTS.items()}
	keys.update(
		{
			"Item": "items",
			"Bin": "inventory",
			"Quality Inspection": "quality",
			"Stock Reservation Entry": "reservations",
		}
	)
	keys.update(
		{
			"Workstation": "workstations",
			"Operation": "operations_catalogue",
			"Warehouse": "warehouses",
			"Customer": "customers",
			"Supplier": "suppliers",
			"Workstation Type": "workstation_types",
			"Plant Floor": "plant_floors",
			"Routing": "routings",
		}
	)
	keys.update(
		{
			"Project": "projects",
			"BOM": "boms",
			"Sales Order": "orders",
			"Work Order": "work_orders",
			"Job Card": "job_cards",
			"Stock Entry": "stock",
			"Task": "tasks",
			"Sarathi Machine Integration Log": "integrations",
		}
	)

	key = keys.get(doctype)

	if not key:
		frappe.throw("Unsupported detail view.")

	row = next((r for r in data[key] if r.get("name") == name), None)

	if not row:
		frappe.throw(
			"Record is outside this selection or you do not have access.",
			frappe.PermissionError,
		)

	frappe.get_doc(doctype, name).check_permission("read")

	related = []

	links = {dt: [(key, "name")] for key, (dt, child) in DOCUMENTS.items()}
	links.update(
		{
			"Workstation": [("job_cards", "workstation")],
			"Warehouse": [("inventory", "warehouse")],
			"Customer": [("projects", "customer"), ("orders", "customer")],
			"Supplier": [("purchases", "supplier")],
			"Job Card": [
				("job_logs", "job_card"),
				("job_suboperations", "job_card"),
				("part_production", "job_card"),
			],
			"Stock Entry": [("stock_details", "parent")],
			"BOM": [("components", "parent"), ("operations", "parent")],
			"Work Order": [("job_cards", "work_order"), ("stock", "work_order")],
			"Sales Order": [("order_items", "parent")],
			"Project": [
				("tasks", "project"),
				("work_orders", "project"),
				("material_history", "project"),
				("part_production", "project"),
			],
		}
	)

	for report, field in links.get(doctype, []):
		matching = [r for r in data[report] if r.get(field) == name]

		related.append(
			dict(
				title=REPORTS[report][0],
				columns=REPORTS[report][2],
				rows=matching[:100],
				total=len(matching),
				report=report,
			)
		)

	return dict(columns=REPORTS[key][2], row=row, related=related)


def export_allowed(report, result=None):
	dt = REPORTS[report][1]
	if report == "procurement_exceptions":
		for source in {r["doctype"] for r in (result or [])}:
			if not frappe.has_permission(source, "export"):
				frappe.throw("Export permission required for " + source, frappe.PermissionError)
		if result:
			return

	if not frappe.has_permission(dt, "export"):
		frappe.throw("You do not have export permission for this report.", frappe.PermissionError)


@frappe.whitelist()
@authorized("production")
def export_report(filters=None, report="projects", subset="", search="", **kwargs):
	data = load(filters)

	result = report_data(data, report, subset, search)

	export_allowed(report, result)

	columns = REPORTS[report][2]

	output = io.StringIO()

	writer = csv.writer(output)

	writer.writerow([c["label"] for c in columns])

	for row in result:
		values = []

		for c in columns:
			value = row.get(c["fieldname"])

			text = "" if value is None else str(value)

			if isinstance(value, str) and text.lstrip().startswith(("=", "+", "-", "@")):
				text = "'" + text

			values.append(text)

		writer.writerow(values)

	frappe.response.update(
		type="download",
		filename=f"sarathi_{report}.csv",
		filecontent=output.getvalue(),
		display_content_as="attachment",
	)
