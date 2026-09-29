"""Manufacturing pipeline resolver for Sarathi Owner Dashboard.

Evaluates in-progress projects across the 5 stages:
1. Bill of Materials (BOM)
2. Production Plan (Optional / Not used)
3. Work Order (Planned vs Produced quantity)
4. Shop Floor Operations (Job Cards)
5. Manufactured Stock (Finished Goods receipts from submitted Manufacture Stock Entries)
"""

from collections import defaultdict

import frappe
from frappe.utils import flt, getdate


def get_project_pipeline(project_name: str) -> dict:
    """Builds a complete, multi-document manufacturing pipeline for a single Project."""
    if not frappe.db.exists("Project", project_name):
        return {}

    project = frappe.get_doc("Project", project_name)

    # 1. Resolve Customer (Project.customer or linked Sales Order)
    customer = project.customer
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={"project": project_name, "docstatus": ["!=", 2]},
        fields=["name", "customer", "status", "delivery_date", "grand_total"],
    )
    if not customer and sales_orders:
        customer = sales_orders[0].customer or "Unassigned Customer"
    elif not customer:
        customer = "Unassigned Customer"

    # 2. Stage 1: Bill of Materials (BOM)
    boms = _resolve_project_boms(project)
    submitted_active_boms = [
        b for b in boms if b.get("docstatus") == 1 and b.get("is_active")
    ]
    if submitted_active_boms:
        bom_status = "done"
        bom_badge = f"{len(submitted_active_boms)} Active BOM{'s' if len(submitted_active_boms) > 1 else ''}"
    elif boms:
        bom_status = "current"
        bom_badge = f"{len(boms)} Draft BOM{'s' if len(boms) > 1 else ''}"
    else:
        bom_status = "wait"
        bom_badge = "No BOM linked"

    # 3. Stage 2: Production Plan
    so_names = [so.name for so in sales_orders]
    plans = _resolve_production_plans(project_name, so_names)
    submitted_plans = [p for p in plans if p.get("docstatus") == 1]
    if submitted_plans:
        plan_status = "done"
        plan_badge = f"{len(submitted_plans)} Submitted Plan{'s' if len(submitted_plans) > 1 else ''}"
    elif plans:
        plan_status = "current"
        plan_badge = f"{len(plans)} Draft Plan{'s' if len(plans) > 1 else ''}"
    else:
        # Production Plan is optional in ERPNext
        plan_status = "optional"
        plan_badge = "Optional / Not used"

    # 4. Stage 3: Work Orders
    work_orders = frappe.get_all(
        "Work Order",
        filters={"project": project_name, "docstatus": ["!=", 2]},
        fields=[
            "name",
            "status",
            "production_item",
            "qty",
            "produced_qty",
            "bom_no",
            "planned_start_date",
            "planned_end_date",
            "docstatus",
        ],
    )
    # Also check Work Orders linked via project Sales Orders if project field is unpopulated
    if not work_orders and so_names:
        work_orders = frappe.get_all(
            "Work Order",
            filters={"sales_order": ["in", so_names], "docstatus": ["!=", 2]},
            fields=[
                "name",
                "status",
                "production_item",
                "qty",
                "produced_qty",
                "bom_no",
                "planned_start_date",
                "planned_end_date",
                "docstatus",
            ],
        )

    wo_planned_qty = sum(flt(w.qty) for w in work_orders if w.docstatus != 2)
    wo_produced_qty = sum(flt(w.produced_qty) for w in work_orders if w.docstatus != 2)
    mfg_progress = (
        round((wo_produced_qty / wo_planned_qty) * 100, 1)
        if wo_planned_qty > 0
        else (
            100.0
            if (work_orders and all(w.status == "Completed" for w in work_orders))
            else 0.0
        )
    )

    completed_wos = [w for w in work_orders if w.status == "Completed"]
    if work_orders and len(completed_wos) == len(work_orders):
        wo_status = "done"
        wo_badge = f"{len(work_orders)} Completed"
    elif any(
        w.status in ("In Process", "Not Started") and w.docstatus != 2
        for w in work_orders
    ):
        wo_status = "current"
        wo_badge = f"{wo_produced_qty:g} / {wo_planned_qty:g} Units ({mfg_progress}%)"
    elif work_orders:
        wo_status = "current"
        wo_badge = f"{len(work_orders)} Work Order{'s' if len(work_orders) > 1 else ''}"
    else:
        wo_status = "wait"
        wo_badge = "No Work Order"

    # 5. Stage 4: Production Execution (Work Order Manufacturing & Assembly Throughput)
    # Executive view: focuses on Work Order assembly progress without operator job card clutter
    wo_names = [w.name for w in work_orders]
    completed_wos = [w for w in work_orders if w.status == "Completed"]
    in_process_wos = [
        w
        for w in work_orders
        if w.status in ("In Process", "Not Started") and w.docstatus != 2
    ]

    if not work_orders:
        exec_status = "wait"
        exec_badge = "Pending Work Order"
        exec_info = "Work orders not yet released"
    elif len(completed_wos) == len(work_orders):
        exec_status = "done"
        exec_badge = f"All {len(work_orders)} Orders Assembled"
        exec_info = f"100% production completed ({wo_produced_qty:g} units)"
    elif in_process_wos or wo_produced_qty > 0:
        exec_status = "current"
        exec_badge = (
            f"{wo_produced_qty:g} / {wo_planned_qty:g} Assembled ({mfg_progress}%)"
        )
        exec_info = f"{len(in_process_wos)} Work Order(s) in active production"
    else:
        exec_status = "wait"
        exec_badge = f"{len(work_orders)} Orders Scheduled"
        exec_info = "Awaiting production release"

    # 6. Stage 5: Manufactured Stock (Stock Entries with purpose='Manufacture')
    stock_entries = []
    stock_filters = {"purpose": "Manufacture", "docstatus": 1}
    if wo_names:
        stock_entries = frappe.get_all(
            "Stock Entry",
            filters={"work_order": ["in", wo_names], **stock_filters},
            fields=["name", "work_order", "fg_completed_qty", "posting_date"],
        )
    if not stock_entries:
        stock_entries = frappe.get_all(
            "Stock Entry",
            filters={"project": project_name, **stock_filters},
            fields=["name", "work_order", "fg_completed_qty", "posting_date"],
        )

    fg_completed_total = sum(flt(se.fg_completed_qty) for se in stock_entries)
    # Stage 5 is complete only when submitted Manufacture Stock Entry satisfies intended Work Order qty
    if stock_entries and wo_planned_qty > 0 and fg_completed_total >= wo_planned_qty:
        stock_status = "done"
        stock_badge = f"{fg_completed_total:g} Produced (Completed)"
    elif stock_entries and fg_completed_total > 0:
        stock_status = "current"
        stock_badge = f"{fg_completed_total:g} / {wo_planned_qty:g} Finished Goods"
    elif stock_entries:
        stock_status = "current"
        stock_badge = f"{len(stock_entries)} Entry submitted"
    else:
        stock_status = "wait"
        stock_badge = "No Manufacture entry"

    return {
        "project": project.name,
        "project_name": project.project_name or project.name,
        "customer": customer,
        "status": project.status,
        "percent_complete": flt(project.percent_complete),
        "manufacturing_progress": mfg_progress,
        "wo_planned_qty": wo_planned_qty,
        "wo_produced_qty": wo_produced_qty,
        "expected_end_date": str(project.expected_end_date or ""),
        "sales_orders": sales_orders,
        "stages": [
            {
                "id": "bom",
                "label": "Bill of Materials",
                "doctype": "BOM",
                "icon": "▤",
                "status": bom_status,
                "badge": bom_badge,
                "count": len(boms),
                "records": [b.name for b in boms],
                "info": "Defines product structure, materials and operations",
            },
            {
                "id": "production_plan",
                "label": "Production Plan",
                "doctype": "Production Plan",
                "icon": "◷",
                "status": plan_status,
                "badge": plan_badge,
                "count": len(plans),
                "records": [p.name for p in plans],
                "info": "Optional material & capacity planning document",
            },
            {
                "id": "work_order",
                "label": "Work Order",
                "doctype": "Work Order",
                "icon": "▣",
                "status": wo_status,
                "badge": wo_badge,
                "count": len(work_orders),
                "records": [w.name for w in work_orders],
                "info": f"Planned: {wo_planned_qty:g}, Produced: {wo_produced_qty:g}",
            },
            {
                "id": "job_card",
                "label": "Production Execution",
                "doctype": "Work Order",
                "icon": "⚙",
                "status": exec_status,
                "badge": exec_badge,
                "count": len(work_orders),
                "records": [w.name for w in work_orders],
                "info": exec_info,
            },
            {
                "id": "stock_entry",
                "label": "Manufactured Stock",
                "doctype": "Stock Entry",
                "icon": "▥",
                "status": stock_status,
                "badge": stock_badge,
                "count": len(stock_entries),
                "records": [s.name for s in stock_entries],
                "info": f"Submitted finished goods: {fg_completed_total:g} units",
            },
        ],
    }


def _resolve_project_boms(project) -> list:
    """Finds all explicit and Work Order linked BOMs for this Project."""
    boms = {}

    # Check custom_sarathi_bom on Project
    if hasattr(project, "custom_sarathi_bom") and project.custom_sarathi_bom:
        info = frappe.db.get_value(
            "BOM",
            project.custom_sarathi_bom,
            ["name", "item", "docstatus", "is_active"],
            as_dict=True,
        )
        if info:
            boms[info.name] = info

    # Check custom_sarathi_project on BOM
    if frappe.db.has_column("BOM", "custom_sarathi_project"):
        for b in frappe.get_all(
            "BOM",
            filters={"custom_sarathi_project": project.name, "docstatus": ["!=", 2]},
            fields=["name", "item", "docstatus", "is_active"],
        ):
            boms[b.name] = b

    # Check BOMs on project Work Orders
    wo_boms = frappe.get_all(
        "Work Order",
        filters={"project": project.name, "docstatus": ["!=", 2]},
        pluck="bom_no",
    )
    for bom_no in set(wo_boms) - {None, ""}:
        if bom_no not in boms and frappe.db.exists("BOM", bom_no):
            info = frappe.db.get_value(
                "BOM", bom_no, ["name", "item", "docstatus", "is_active"], as_dict=True
            )
            if info:
                boms[info.name] = info

    return list(boms.values())


def _resolve_production_plans(project_name: str, so_names: list) -> list:
    """Resolves Production Plans directly linked or linked via Sales Orders."""
    plans = {}

    if frappe.db.has_column("Production Plan", "project"):
        for p in frappe.get_all(
            "Production Plan",
            filters={"project": project_name, "docstatus": ["!=", 2]},
            fields=["name", "docstatus", "status"],
        ):
            plans[p.name] = p

    # Check via Sales Orders
    if so_names and frappe.db.table_exists("Production Plan Sales Order"):
        pp_so = frappe.get_all(
            "Production Plan Sales Order",
            filters={"sales_order": ["in", so_names]},
            pluck="parent",
        )
        for parent in set(pp_so):
            if parent not in plans and frappe.db.exists("Production Plan", parent):
                info = frappe.db.get_value(
                    "Production Plan",
                    parent,
                    ["name", "docstatus", "status"],
                    as_dict=True,
                )
                if info and info.docstatus != 2:
                    plans[info.name] = info

    # In some ERPNext versions child table is Production Plan Item
    if so_names and frappe.db.table_exists("Production Plan Item"):
        if frappe.db.has_column("Production Plan Item", "sales_order"):
            pp_items = frappe.get_all(
                "Production Plan Item",
                filters={"sales_order": ["in", so_names]},
                pluck="parent",
            )
            for parent in set(pp_items):
                if parent not in plans and frappe.db.exists("Production Plan", parent):
                    info = frappe.db.get_value(
                        "Production Plan",
                        parent,
                        ["name", "docstatus", "status"],
                        as_dict=True,
                    )
                    if info and info.docstatus != 2:
                        plans[info.name] = info

    return list(plans.values())
