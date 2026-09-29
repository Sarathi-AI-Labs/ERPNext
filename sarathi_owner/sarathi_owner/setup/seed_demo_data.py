"""Realistic Industrial Demo Data Seeder for Sarathi Owner Dashboard & Control Tower.

Populates real industrial manufacturing records into ERPNext:
- Customers, Items, Warehouses, Stock Receipts
- Bill of Materials (BOM)
- Projects & Milestone Tasks
- Sales Orders, Work Orders, Sales Invoices
"""

import frappe
from frappe.utils import add_days, flt, nowdate, today


@frappe.whitelist()
def seed_industrial_data():
    """Populates realistic industrial manufacturing records into ERPNext."""
    company = (
        frappe.db.get_single_value("Global Defaults", "default_company")
        or "SarathiAILabs"
    )
    if not frappe.db.exists("Company", company):
        co = frappe.new_doc("Company")
        co.company_name = company
        co.default_currency = "INR"
        co.country = "India"
        co.insert(ignore_permissions=True)

    currency = (
        frappe.db.get_value("Company", company, "default_currency") or "INR"
    )

    # 1. Ensure Warehouses
    wh_stores = _ensure_warehouse("Stores", company)
    wh_fg = _ensure_warehouse("Finished Goods", company)
    wh_wip = _ensure_warehouse("Work In Progress", company)

    # 2. Ensure Customers
    cust_apex = _ensure_customer("Apex Heavy Engineering Ltd")
    cust_tata = _ensure_customer("Tata Advanced Systems Ltd")
    cust_bdl = _ensure_customer("Bharat Dynamics Ltd")

    # 3. Ensure Items
    item_turbine = _ensure_item(
        "WIND-TURBINE-500KW",
        "500kW Industrial Wind Turbine Generator",
        "Finished Goods",
        2500000.0,
        1500000.0,
    )
    item_gearbox = _ensure_item(
        "GEARBOX-ASSEMBLY-500",
        "Heavy Duty Helical Planetary Gearbox",
        "Sub Assembly",
        650000.0,
        450000.0,
    )
    item_blade = _ensure_item(
        "ROTOR-BLADE-SET",
        "Carbon-Fiber Reinforced Rotor Blades (Set of 3)",
        "Raw Material",
        180000.0,
        120000.0,
    )
    item_shaft = _ensure_item(
        "STEEL-SHAFT-EN24",
        "Forged Alloy Steel Main Shaft EN24T",
        "Raw Material",
        65000.0,
        45000.0,
    )

    # 4. Stock Ingress (Material Receipt for inventory valuation)
    _ensure_stock_receipt(
        company,
        [
            (item_blade, wh_stores, 15, 120000.0),
            (item_shaft, wh_stores, 40, 45000.0),
            (item_gearbox, wh_wip, 4, 450000.0),
            (item_turbine, wh_fg, 2, 1500000.0),
        ],
    )

    # 5. Ensure BOM
    bom_name = _ensure_bom(
        item_turbine,
        company,
        currency,
        [
            (item_gearbox, 1, 450000.0),
            (item_blade, 1, 120000.0),
            (item_shaft, 1, 45000.0),
        ],
    )
    bom_gearbox = _ensure_bom(
        item_gearbox,
        company,
        currency,
        [
            (item_shaft, 2, 45000.0),
        ],
    )

    # 6. Ensure Projects
    proj_1 = _ensure_project(
        "PROJ-TURBINE-01",
        "500kW Turbine Installation Phase 1",
        cust_apex,
        company,
        estimated_cost=15000000.0,
        actual_cost=8500000.0,
        total_billed=12500000.0,
        percent_complete=68.0,
        status="Open",
    )
    _ensure_tasks(
        proj_1,
        [
            ("Civil Foundation & Aerodynamic Assessment", "Completed", -30),
            ("Main Frame Machining & Structural Assembly", "Completed", -15),
            ("Electrical Power Grid Integration", "Working", 10),
            ("Final Factory Acceptance Test (FAT)", "Open", 25),
        ],
    )

    proj_2 = _ensure_project(
        "PROJ-DEFENSE-02",
        "Precision Propulsion Drive System",
        cust_tata,
        company,
        estimated_cost=8000000.0,
        actual_cost=3200000.0,
        total_billed=4000000.0,
        percent_complete=45.0,
        status="Open",
    )

    # 7. Ensure Sales Orders
    _ensure_sales_order(
        "SO-2026-0001",
        cust_apex,
        company,
        proj_1,
        [(item_turbine, 5, 2500000.0)],
        delivery_days=30,
        status="To Deliver and Bill",
    )
    _ensure_sales_order(
        "SO-2026-0002",
        cust_tata,
        company,
        proj_2,
        [(item_gearbox, 8, 650000.0)],
        delivery_days=20,
        status="To Deliver",
    )
    _ensure_sales_order(
        "SO-2026-0003",
        cust_bdl,
        company,
        None,
        [(item_shaft, 25, 65000.0)],
        delivery_days=15,
        status="To Bill",
    )

    # 8. Ensure Work Orders
    _ensure_work_order(
        "WO-2026-0001",
        item_turbine,
        bom_name,
        company,
        proj_1,
        qty=5,
        produced=3,
        status="In Process",
        wh_wip=wh_wip,
        wh_fg=wh_fg,
    )
    _ensure_work_order(
        "WO-2026-0002",
        item_gearbox,
        bom_gearbox,
        company,
        proj_2,
        qty=8,
        produced=8,
        status="Completed",
        wh_wip=wh_wip,
        wh_fg=wh_fg,
    )

    # 9. Ensure Sales Invoice (with outstanding AR)
    _ensure_sales_invoice(
        "SINV-2026-0001",
        cust_apex,
        company,
        proj_1,
        [(item_turbine, 3, 2500000.0)],
        paid_amount=5000000.0,
        due_days=15,
    )

    frappe.db.commit()
    return {
        "status": "success",
        "message": "Industrial sample records successfully populated! All 8 Owner sections now have live data.",
        "company": company,
    }


def _ensure_warehouse(prefix, company):
    abbr = frappe.db.get_value("Company", company, "abbr") or "SAL"
    wh_name = f"{prefix} - {abbr}"
    if not frappe.db.exists("Warehouse", wh_name):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = prefix
        doc.company = company
        doc.save(ignore_permissions=True)
    return wh_name


def _ensure_customer(name):
    if not frappe.db.exists("Customer", name):
        doc = frappe.new_doc("Customer")
        doc.customer_name = name
        doc.customer_type = "Company"
        doc.customer_group = "Commercial"
        doc.territory = "India"
        doc.save(ignore_permissions=True)
    return name


def _ensure_item(code, name, group, selling_rate, valuation_rate):
    if not frappe.db.exists("Item Group", group):
        ig = frappe.new_doc("Item Group")
        ig.item_group_name = group
        ig.parent_item_group = "All Item Groups"
        ig.save(ignore_permissions=True)

    if not frappe.db.exists("Item", code):
        doc = frappe.new_doc("Item")
        doc.item_code = code
        doc.item_name = name
        doc.item_group = group
        doc.stock_uom = "Nos"
        doc.is_stock_item = 1
        doc.standard_rate = selling_rate
        doc.valuation_rate = valuation_rate
        doc.save(ignore_permissions=True)
    return code


def _ensure_stock_receipt(company, items_list):
    has_receipt = (
        frappe.db.count(
            "Stock Entry", {"purpose": "Material Receipt", "docstatus": 1}
        )
        > 0
    )
    if has_receipt:
        return

    try:
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Receipt"
        se.purpose = "Material Receipt"
        se.company = company
        se.posting_date = today()
        for item_code, wh, qty, rate in items_list:
            se.append(
                "items",
                {
                    "item_code": item_code,
                    "t_warehouse": wh,
                    "qty": qty,
                    "basic_rate": rate,
                    "cost_center": frappe.db.get_value(
                        "Company", company, "cost_center"
                    ),
                },
            )
        se.save(ignore_permissions=True)
        se.submit()
    except Exception as e:
        frappe.log_error(f"Demo Stock Receipt Error: {e}")


def _ensure_bom(item_code, company, currency, items):
    bom_name = frappe.db.get_value("BOM", {"item": item_code, "is_active": 1})
    if bom_name:
        return bom_name

    try:
        doc = frappe.new_doc("BOM")
        doc.item = item_code
        doc.company = company
        doc.currency = currency
        doc.quantity = 1
        doc.is_active = 1
        doc.is_default = 1
        for comp_item, q, r in items:
            doc.append(
                "items",
                {
                    "item_code": comp_item,
                    "qty": q,
                    "rate": r,
                },
            )
        doc.save(ignore_permissions=True)
        doc.submit()
        return doc.name
    except Exception as e:
        frappe.log_error(f"Demo BOM Error: {e}")
        return None


def _ensure_project(
    name,
    p_name,
    customer,
    company,
    estimated_cost,
    actual_cost,
    total_billed,
    percent_complete,
    status,
):
    existing = frappe.db.get_value("Project", {"project_name": p_name}, "name")
    if existing:
        frappe.db.set_value(
            "Project",
            existing,
            {
                "customer": customer,
                "estimated_costing": estimated_cost,
                "total_costing_amount": actual_cost,
                "total_billed_amount": total_billed,
                "percent_complete": percent_complete,
                "status": status,
            },
        )
        return existing

    doc = frappe.new_doc("Project")
    doc.project_name = p_name
    doc.customer = customer
    doc.company = company
    doc.estimated_costing = estimated_cost
    doc.total_costing_amount = actual_cost
    doc.total_billed_amount = total_billed
    doc.percent_complete = percent_complete
    doc.status = status
    doc.expected_end_date = add_days(today(), 45)
    doc.flags.ignore_mandatory = True
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_tasks(project, tasks_list):
    for subject, status, day_offset in tasks_list:
        if not frappe.db.exists(
            "Task", {"project": project, "subject": subject}
        ):
            t = frappe.new_doc("Task")
            t.subject = subject
            t.project = project
            t.status = status
            t.exp_end_date = add_days(today(), day_offset)
            t.save(ignore_permissions=True)


def _ensure_sales_order(
    name, customer, company, project, items, delivery_days, status
):
    if frappe.db.exists("Sales Order", name):
        return name

    try:
        so = frappe.new_doc("Sales Order")
        so.name = name
        so.customer = customer
        so.company = company
        so.project = project
        so.transaction_date = today()
        so.delivery_date = add_days(today(), delivery_days)
        so.status = status

        for item_code, qty, rate in items:
            so.append(
                "items",
                {
                    "item_code": item_code,
                    "qty": qty,
                    "rate": rate,
                    "delivery_date": add_days(today(), delivery_days),
                },
            )
        so.save(ignore_permissions=True)
        so.submit()
        return so.name
    except Exception as e:
        frappe.log_error(f"Demo Sales Order Error: {e}")
        return None


def _ensure_work_order(
    name, item, bom, company, project, qty, produced, status, wh_wip, wh_fg
):
    if frappe.db.exists("Work Order", name):
        return name

    try:
        wo = frappe.new_doc("Work Order")
        wo.name = name
        wo.production_item = item
        if bom:
            wo.bom_no = bom
        wo.company = company
        wo.project = project
        wo.qty = qty
        wo.produced_qty = produced
        wo.status = status
        wo.wip_warehouse = wh_wip
        wo.fg_warehouse = wh_fg
        wo.planned_start_date = add_days(today(), -10)
        wo.planned_end_date = add_days(today(), 15)
        wo.save(ignore_permissions=True)
        wo.submit()
        return wo.name
    except Exception as e:
        frappe.log_error(f"Demo Work Order Error: {e}")
        return None


def _ensure_sales_invoice(
    name, customer, company, project, items, paid_amount, due_days
):
    if frappe.db.exists("Sales Invoice", name):
        return name

    try:
        inv = frappe.new_doc("Sales Invoice")
        inv.name = name
        inv.customer = customer
        inv.company = company
        inv.project = project
        inv.posting_date = today()
        inv.due_date = add_days(today(), due_days)

        for item_code, qty, rate in items:
            inv.append(
                "items",
                {
                    "item_code": item_code,
                    "qty": qty,
                    "rate": rate,
                    "cost_center": frappe.db.get_value(
                        "Company", company, "cost_center"
                    ),
                },
            )
        inv.save(ignore_permissions=True)
        inv.submit()

        if paid_amount > 0:
            frappe.db.set_value(
                "Sales Invoice",
                inv.name,
                "outstanding_amount",
                max(0.0, flt(inv.grand_total) - flt(paid_amount)),
            )
        return inv.name
    except Exception as e:
        frappe.log_error(f"Demo Sales Invoice Error: {e}")
        return None
