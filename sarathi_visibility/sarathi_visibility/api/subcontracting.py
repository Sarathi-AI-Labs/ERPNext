"""Subcontracting Analytics and Reporting API for Sarathi Industrial Control Tower."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

import frappe
from frappe.utils import (
    cint,
    date_diff,
    flt,
    formatdate,
    getdate,
    now_datetime,
    today,
)


def _check_read(doctype: str) -> bool:
    return bool(frappe.db.exists("DocType", doctype) and frappe.has_permission(doctype, "read"))


def _parse_filters(filters: Any = None) -> Dict[str, str]:
    if isinstance(filters, str):
        try:
            filters = frappe.parse_json(filters)
        except Exception:
            filters = {}
    filters = filters or {}
    return {
        "company": str(filters.get("company") or "").strip(),
        "supplier": str(filters.get("supplier") or "").strip(),
        "project": str(filters.get("project") or "").strip(),
        "status": str(filters.get("status") or "").strip(),
        "from_date": str(filters.get("from_date") or "").strip(),
        "to_date": str(filters.get("to_date") or "").strip(),
        "cost_granularity": str(filters.get("cost_granularity") or "monthly").lower(),
    }


def get_subcontracting_card_summary(filters: Any = None) -> Dict[str, Any]:
    """Lightweight summary metrics specifically for the main dashboard card."""
    f = _parse_filters(filters)
    if not _check_read("Subcontracting Order"):
        return {
            "active_subcontracts": 0,
            "material_with_suppliers": 0.0,
            "pending_subcontracts": 0,
            "currency": "INR",
        }

    company_currency = "INR"
    if f["company"]:
        company_currency = frappe.db.get_value("Company", f["company"], "default_currency") or "INR"
    else:
        first_comp = frappe.db.get_value("Company", {}, "default_currency")
        if first_comp:
            company_currency = first_comp

    # Build filter conditions
    order_filters: Dict[str, Any] = {"docstatus": ["!=", 2]}
    if f["company"]:
        order_filters["company"] = f["company"]
    if f["project"]:
        order_filters["project"] = f["project"]
    if f["supplier"]:
        order_filters["supplier"] = f["supplier"]
    if f["from_date"]:
        order_filters["transaction_date"] = [">=", f["from_date"]]
    if f["to_date"]:
        order_filters.setdefault("transaction_date", [])
        if isinstance(order_filters["transaction_date"], list) and len(order_filters["transaction_date"]) == 2:
            order_filters["transaction_date"] = ["between", [f["from_date"] or "1900-01-01", f["to_date"]]]
        else:
            order_filters["transaction_date"] = ["<=", f["to_date"]]

    orders = frappe.get_all(
        "Subcontracting Order",
        fields=["name", "status", "docstatus", "total", "schedule_date"],
        filters=order_filters,
        limit_page_length=0,
    )

    active_statuses = {"Open", "Material Transferred", "Partial Material Transferred", "Partially Received"}
    active_count = sum(1 for o in orders if o.docstatus == 1 and o.status in active_statuses)
    pending_count = sum(1 for o in orders if o.docstatus == 1 and o.status in ("Open", "Material Transferred", "Partial Material Transferred"))

    # Material with suppliers: sum remaining supplied items on submitted orders
    material_val = 0.0
    submitted_order_names = [o.name for o in orders if o.docstatus == 1 and o.status != "Cancelled"]
    if submitted_order_names and _check_read("Subcontracting Order Supplied Item"):
        supplied_items = frappe.get_all(
            "Subcontracting Order Supplied Item",
            fields=["parent", "total_supplied_qty", "supplied_qty", "consumed_qty", "returned_qty", "rate"],
            filters={"parent": ["in", submitted_order_names]},
            limit_page_length=0,
        )
        for s in supplied_items:
            sent = flt(s.total_supplied_qty or s.supplied_qty)
            consumed = flt(s.consumed_qty)
            returned = flt(s.returned_qty)
            remaining = max(0.0, sent - consumed - returned)
            material_val += remaining * flt(s.rate)

    return {
        "active_subcontracts": active_count,
        "material_with_suppliers": flt(material_val, 2),
        "pending_subcontracts": pending_count,
        "currency": company_currency,
    }


@frappe.whitelist()
def get_subcontracting_dashboard(filters: Any = None) -> Dict[str, Any]:
    """Detailed data payload for the Subcontracting Detail View."""
    f = _parse_filters(filters)
    has_sco = _check_read("Subcontracting Order")
    has_scr = _check_read("Subcontracting Receipt")
    has_po = _check_read("Purchase Order")
    has_se = _check_read("Stock Entry")

    currency = "INR"
    if f["company"]:
        currency = frappe.db.get_value("Company", f["company"], "default_currency") or "INR"
    else:
        default_comp = frappe.db.get_value("Company", {}, "default_currency")
        if default_comp:
            currency = default_comp

    suppliers_list = []
    if _check_read("Supplier"):
        suppliers_list = frappe.get_all(
            "Supplier",
            fields=["name", "supplier_name"],
            filters={"disabled": 0},
            order_by="supplier_name asc",
            limit_page_length=0,
        )

    projects_list = []
    if _check_read("Project"):
        proj_filter = {"company": f["company"]} if f["company"] else {}
        projects_list = frappe.get_all(
            "Project",
            fields=["name", "project_name"],
            filters=proj_filter,
            order_by="project_name asc",
            limit_page_length=0,
        )

    if not has_sco:
        return {
            "currency": currency,
            "filters": f,
            "suppliers": suppliers_list,
            "projects": projects_list,
            "kpis": {},
            "pipeline": [],
            "status_distribution": {"labels": [], "values": []},
            "cost_trends": {"labels": [], "material": [], "service": [], "total": []},
            "supplier_analysis": [],
            "project_analysis": [],
            "materials_with_subcontractors": [],
            "orders": [],
            "attention_required": [],
            "supplier_performance": [],
            "live_activity": [],
        }

    # Fetch Subcontracting Orders
    order_filter: Dict[str, Any] = {"docstatus": ["!=", 2]}
    if f["company"]:
        order_filter["company"] = f["company"]
    if f["supplier"]:
        order_filter["supplier"] = f["supplier"]
    if f["project"]:
        order_filter["project"] = f["project"]
    if f["status"]:
        order_filter["status"] = f["status"]
    if f["from_date"]:
        order_filter["transaction_date"] = [">=", f["from_date"]]
    if f["to_date"]:
        if "transaction_date" in order_filter:
            order_filter["transaction_date"] = ["between", [f["from_date"], f["to_date"]]]
        else:
            order_filter["transaction_date"] = ["<=", f["to_date"]]

    sco_fields = [
        "name", "title", "purchase_order", "supplier", "supplier_name",
        "company", "transaction_date", "schedule_date", "status", "docstatus",
        "total_qty", "total", "per_received", "project", "creation", "modified"
    ]
    orders = frappe.get_all("Subcontracting Order", fields=sco_fields, filters=order_filter, order_by="transaction_date desc, modified desc", limit_page_length=0)
    order_names = [o.name for o in orders]

    # Fetch SCO Items
    sco_items_map = defaultdict(list)
    if order_names and _check_read("Subcontracting Order Item"):
        items = frappe.get_all(
            "Subcontracting Order Item",
            fields=["parent", "item_code", "item_name", "qty", "received_qty", "returned_qty", "rate", "amount", "service_cost_per_qty", "schedule_date", "expected_delivery_date"],
            filters={"parent": ["in", order_names]},
            order_by="idx asc",
            limit_page_length=0,
        )
        for itm in items:
            sco_items_map[itm.parent].append(itm)

    # Fetch Supplied Items
    supplied_items_map = defaultdict(list)
    all_supplied_items = []
    if order_names and _check_read("Subcontracting Order Supplied Item"):
        supplied = frappe.get_all(
            "Subcontracting Order Supplied Item",
            fields=["parent", "main_item_code", "rm_item_code", "stock_uom", "reserve_warehouse", "rate", "amount", "required_qty", "supplied_qty", "consumed_qty", "returned_qty", "total_supplied_qty"],
            filters={"parent": ["in", order_names]},
            order_by="idx asc",
            limit_page_length=0,
        )
        for s in supplied:
            supplied_items_map[s.parent].append(s)
            all_supplied_items.append(s)

    # Fetch Subcontracting Receipts
    scr_filters: Dict[str, Any] = {"docstatus": ["!=", 2]}
    if f["company"]:
        scr_filters["company"] = f["company"]
    if f["supplier"]:
        scr_filters["supplier"] = f["supplier"]
    if f["project"]:
        scr_filters["project"] = f["project"]
    if f["from_date"]:
        scr_filters["posting_date"] = [">=", f["from_date"]]
    if f["to_date"]:
        if "posting_date" in scr_filters:
            scr_filters["posting_date"] = ["between", [f["from_date"], f["to_date"]]]
        else:
            scr_filters["posting_date"] = ["<=", f["to_date"]]

    receipts = []
    if has_scr:
        receipts = frappe.get_all(
            "Subcontracting Receipt",
            fields=["name", "supplier", "supplier_name", "company", "posting_date", "status", "docstatus", "total_qty", "total", "project", "creation"],
            filters=scr_filters,
            order_by="posting_date desc",
            limit_page_length=0,
        )

    # Fetch Subcontracting Receipt Items
    scr_items_map = defaultdict(list)
    scr_names = [r.name for r in receipts]
    if scr_names and _check_read("Subcontracting Receipt Item"):
        r_items = frappe.get_all(
            "Subcontracting Receipt Item",
            fields=["parent", "subcontracting_order", "item_code", "item_name", "qty", "received_qty", "rate", "amount", "rm_cost_per_qty", "service_cost_per_qty", "warehouse", "project"],
            filters={"parent": ["in", scr_names]},
            limit_page_length=0,
        )
        for ri in r_items:
            scr_items_map[ri.parent].append(ri)

    # Calculate Subcontracting Detail KPIs
    active_statuses = {"Open", "Material Transferred", "Partial Material Transferred", "Partially Received"}
    active_subcontracts = sum(1 for o in orders if o.docstatus == 1 and o.status in active_statuses)
    open_subcontract_orders = sum(1 for o in orders if o.docstatus == 1 and o.status == "Open")
    completed_subcontracts = sum(1 for o in orders if o.status == "Completed")

    cur_today = today()
    overdue_count = sum(1 for o in orders if o.docstatus == 1 and o.schedule_date and str(o.schedule_date) < cur_today and o.status not in ("Completed", "Cancelled", "Closed"))

    total_service_cost = 0.0
    for o in orders:
        if o.docstatus == 1 and o.status != "Cancelled":
            total_service_cost += flt(o.total)

    total_material_with_subcontractors = 0.0
    consumed_material_cost = 0.0
    for s in all_supplied_items:
        sent = flt(s.total_supplied_qty or s.supplied_qty)
        consumed = flt(s.consumed_qty)
        returned = flt(s.returned_qty)
        remaining = max(0.0, sent - consumed - returned)
        rate = flt(s.rate)
        total_material_with_subcontractors += remaining * rate
        consumed_material_cost += consumed * rate

    total_subcontracting_cost = total_service_cost + consumed_material_cost

    total_fg_received = 0.0
    for r in receipts:
        if r.docstatus == 1 and r.status != "Cancelled":
            total_fg_received += flt(r.total_qty)

    # 1. Total Subcontract Orders
    total_orders_count = len(orders)
    # 2. Active / In-Progress Orders
    active_orders_count = active_subcontracts
    # 3. Material Value at Subcontractors
    material_val = flt(total_material_with_subcontractors, 2)
    # 4. Pending Scrap / Reconciliation
    pending_scrap_count = 0
    if all_supplied_items:
        for s in all_supplied_items:
            consumed = flt(s.consumed_qty)
            returned = flt(s.returned_qty)
            sent = flt(s.total_supplied_qty or s.supplied_qty)
            if sent > (consumed + returned) and (sent - consumed - returned) > 0:
                pending_scrap_count += 1

    # 5. Orders Pending Delivery
    orders_pending_delivery = sum(
        1 for o in orders
        if o.docstatus == 1 and flt(o.per_received) < 100 and o.status not in ("Completed", "Cancelled", "Closed")
    )

    # 6. On-Time Delivery Rate
    completed_orders = [o for o in orders if o.status == "Completed"]
    on_time_count = 0
    for o in completed_orders:
        if not o.schedule_date or str(o.modified)[:10] <= str(o.schedule_date):
            on_time_count += 1
    on_time_delivery_rate = round((on_time_count / len(completed_orders) * 100), 1) if completed_orders else 100.0

    # 7. Total Subcontracting Spend
    total_spend_val = flt(total_subcontracting_cost, 2)

    # 8. Rejected / Rework Quantity
    rejected_qty_val = 0.0
    if scr_names and _check_read("Subcontracting Receipt Item"):
        for items_list in scr_items_map.values():
            for itm in items_list:
                rejected_qty_val += flt(itm.get("rejected_qty") or 0.0)

    kpis = {
        # Exact 8 KPI cards from specification
        "total_subcontract_orders": total_orders_count,
        "active_orders": active_orders_count,
        "material_value_at_subcontractors": material_val,
        "pending_scrap_reconciliation": pending_scrap_count,
        "orders_pending_delivery": orders_pending_delivery,
        "on_time_delivery_rate": f"{on_time_delivery_rate}%",
        "on_time_delivery_rate_num": on_time_delivery_rate,
        "total_subcontracting_spend": total_spend_val,
        "rejected_rework_quantity": rejected_qty_val,

        # Additional summary helpers
        "active_subcontracts": active_subcontracts,
        "open_subcontract_orders": open_subcontract_orders,
        "material_with_subcontractors": material_val,
        "completed": completed_subcontracts,
        "service_cost": flt(total_service_cost, 2),
        "total_subcontracting_cost": total_spend_val,
        "overdue": overdue_count,
        "finished_goods_received": flt(total_fg_received, 2),
    }

    # Pipeline Counts (7 interactive lifecycle stages):
    # 1. Purchase Order
    po_count = 0
    if has_po:
        po_filters = {"is_subcontracted": 1, "docstatus": 1}
        if f["company"]:
            po_filters["company"] = f["company"]
        if f["supplier"]:
            po_filters["supplier"] = f["supplier"]
        if f["project"]:
            po_filters["project"] = f["project"]
        po_count = frappe.db.count("Purchase Order", filters=po_filters)

    # 2. Stock Transfer
    stock_transfer_count = 0
    if has_se:
        se_filt = {"purpose": ["in", ["Send to Subcontractor", "Subcontracting Delivery"]], "docstatus": 1}
        if f["company"]:
            se_filt["company"] = f["company"]
        if f["project"]:
            se_filt["project"] = f["project"]
        stock_transfer_count = frappe.db.count("Stock Entry", filters=se_filt)
    if stock_transfer_count == 0:
        stock_transfer_count = sum(1 for o in orders if o.docstatus == 1 and o.status in ("Material Transferred", "Partial Material Transferred", "Partially Received", "Completed"))

    # 3. Subcontract Order
    sco_count = sum(1 for o in orders if o.docstatus == 1)

    # 4. Material In Production
    in_prod_count = sum(1 for o in orders if o.docstatus == 1 and (o.status in ("Material Transferred", "Partial Material Transferred", "Partially Received") or (flt(o.per_received) > 0 and flt(o.per_received) < 100)))

    # 5. Quality Inspection
    qi_count = 0
    if _check_read("Quality Inspection"):
        qi_filt = {"docstatus": 1}
        if f["company"]:
            qi_filt["company"] = f["company"]
        qi_count = frappe.db.count("Quality Inspection", filters=qi_filt)

    # 6. Subcontract Receipt
    receipt_count = sum(1 for r in receipts if r.docstatus == 1)

    # 7. Billing & Payment
    billing_count = 0
    if _check_read("Purchase Invoice"):
        pi_filt = {"docstatus": 1, "is_subcontracted": 1}
        if f["company"]:
            pi_filt["company"] = f["company"]
        if f["supplier"]:
            pi_filt["supplier"] = f["supplier"]
        if f["project"]:
            pi_filt["project"] = f["project"]
        billing_count = frappe.db.count("Purchase Invoice", filters=pi_filt)
    if billing_count == 0:
        billing_count = completed_subcontracts

    pipeline = [
        {"key": "po", "label": "Purchase Order", "count": po_count, "description": "Subcontracted Purchase Orders"},
        {"key": "stock_transfer", "label": "Stock Transfer", "count": stock_transfer_count, "description": "Raw Material Dispatched to Subcontractor"},
        {"key": "sco", "label": "Subcontract Order", "count": sco_count, "description": "Submitted Subcontracting Orders"},
        {"key": "in_production", "label": "Material In Production", "count": in_prod_count, "description": "Work In Progress at Supplier"},
        {"key": "quality_inspection", "label": "Quality Inspection", "count": qi_count, "description": "Quality Inspections Recorded"},
        {"key": "receipt", "label": "Subcontract Receipt", "count": receipt_count, "description": "Finished Goods Received"},
        {"key": "billing", "label": "Billing & Payment", "count": billing_count, "description": "Invoiced & Completed Orders"},
    ]

    # Status Distribution (Donut Chart)
    status_counts = defaultdict(int)
    for o in orders:
        st = o.status or ("Draft" if o.docstatus == 0 else "Open")
        status_counts[st] += 1
    status_labels = sorted(status_counts.keys())
    status_distribution = {
        "labels": status_labels,
        "values": [status_counts[st] for st in status_labels],
    }

    # Subcontracting Cost Trends (Daily / Monthly / Yearly)
    granularity = f.get("cost_granularity", "monthly")
    daily_buckets = defaultdict(lambda: {"material": 0.0, "service": 0.0})

    for o in orders:
        if o.docstatus == 1 and o.transaction_date:
            d_str = str(o.transaction_date)[:10]
            if granularity == "daily":
                bucket = d_str
            elif granularity == "yearly":
                bucket = d_str[:4]
            else:  # monthly
                bucket = d_str[:7]
            daily_buckets[bucket]["service"] += flt(o.total)

    # Add material costs by receipt or order date
    for r in receipts:
        if r.docstatus == 1 and r.posting_date:
            d_str = str(r.posting_date)[:10]
            if granularity == "daily":
                bucket = d_str
            elif granularity == "yearly":
                bucket = d_str[:4]
            else:
                bucket = d_str[:7]
            for ri in scr_items_map.get(r.name, []):
                daily_buckets[bucket]["material"] += flt(ri.rm_cost_per_qty) * flt(ri.qty)

    sorted_cost_buckets = sorted(daily_buckets.keys())[-15:]
    cost_trends = {
        "labels": sorted_cost_buckets,
        "material": [flt(daily_buckets[b]["material"], 2) for b in sorted_cost_buckets],
        "service": [flt(daily_buckets[b]["service"], 2) for b in sorted_cost_buckets],
        "total": [flt(daily_buckets[b]["material"] + daily_buckets[b]["service"], 2) for b in sorted_cost_buckets],
    }

    # Supplier Analysis Table & Chart
    supplier_data = defaultdict(lambda: {
        "supplier": "",
        "orders": 0,
        "completed": 0,
        "pending": 0,
        "overdue": 0,
        "material_value": 0.0,
        "service_cost": 0.0,
        "total_cost": 0.0,
        "receipt_dates": [],
        "processing_days_list": [],
    })

    for o in orders:
        s_name = o.supplier or "Unassigned"
        rec = supplier_data[s_name]
        rec["supplier"] = o.supplier_name or s_name
        rec["orders"] += 1
        if o.status == "Completed":
            rec["completed"] += 1
        elif o.status in ("Open", "Material Transferred", "Partial Material Transferred", "Partially Received"):
            rec["pending"] += 1

        if o.docstatus == 1 and o.schedule_date and str(o.schedule_date) < cur_today and o.status not in ("Completed", "Cancelled", "Closed"):
            rec["overdue"] += 1

        rec["service_cost"] += flt(o.total)

    for s in all_supplied_items:
        parent_order = next((o for o in orders if o.name == s.parent), None)
        if parent_order:
            s_name = parent_order.supplier or "Unassigned"
            sent = flt(s.total_supplied_qty or s.supplied_qty)
            consumed = flt(s.consumed_qty)
            returned = flt(s.returned_qty)
            rem = max(0.0, sent - consumed - returned)
            supplier_data[s_name]["material_value"] += rem * flt(s.rate)

    for r in receipts:
        s_name = r.supplier or "Unassigned"
        rec = supplier_data[s_name]
        if r.posting_date:
            rec["receipt_dates"].append(str(r.posting_date))

    supplier_analysis = []
    supplier_performance = []
    for s_name, data in sorted(supplier_data.items(), key=lambda x: x[1]["orders"], reverse=True):
        total_cost = data["service_cost"] + data["material_value"]
        supplier_analysis.append({
            "supplier": data["supplier"],
            "orders": data["orders"],
            "completed": data["completed"],
            "pending": data["pending"],
            "overdue": data["overdue"],
            "material_value": flt(data["material_value"], 2),
            "service_cost": flt(data["service_cost"], 2),
            "total_cost": flt(total_cost, 2),
        })

        last_receipt = max(data["receipt_dates"]) if data["receipt_dates"] else "—"
        avg_processing_days = 0.0
        if data["processing_days_list"]:
            avg_processing_days = sum(data["processing_days_list"]) / len(data["processing_days_list"])

        supplier_performance.append({
            "supplier": data["supplier"],
            "total_orders": data["orders"],
            "completed": data["completed"],
            "pending": data["pending"],
            "overdue": data["overdue"],
            "average_processing_time": f"{flt(avg_processing_days, 1)} days" if avg_processing_days > 0 else "—",
            "material_value": flt(data["material_value"], 2),
            "service_cost": flt(data["service_cost"], 2),
            "total_cost": flt(total_cost, 2),
            "last_receipt": last_receipt,
        })

    # Project Analysis
    project_data = defaultdict(lambda: {
        "project": "",
        "suppliers": set(),
        "orders": 0,
        "material_cost": 0.0,
        "service_cost": 0.0,
        "total_cost": 0.0,
        "received": 0.0,
        "pending": 0.0,
    })

    for o in orders:
        p_name = o.project or "No Project Linked"
        p_rec = project_data[p_name]
        p_rec["project"] = p_name
        if o.supplier:
            p_rec["suppliers"].add(o.supplier_name or o.supplier)
        p_rec["orders"] += 1
        p_rec["service_cost"] += flt(o.total)

        tot_qty = flt(o.total_qty)
        rec_pct = flt(o.per_received)
        rec_qty = tot_qty * (rec_pct / 100.0)
        p_rec["received"] += rec_qty
        p_rec["pending"] += max(0.0, tot_qty - rec_qty)

    for s in all_supplied_items:
        parent_order = next((o for o in orders if o.name == s.parent), None)
        if parent_order:
            p_name = parent_order.project or "No Project Linked"
            sent = flt(s.total_supplied_qty or s.supplied_qty)
            consumed = flt(s.consumed_qty)
            project_data[p_name]["material_cost"] += (sent or consumed) * flt(s.rate)

    project_analysis = []
    for p_name, data in sorted(project_data.items(), key=lambda x: x[1]["orders"], reverse=True):
        t_cost = data["material_cost"] + data["service_cost"]
        project_analysis.append({
            "project": data["project"],
            "supplier": ", ".join(sorted(data["suppliers"])) if data["suppliers"] else "—",
            "orders": data["orders"],
            "material_cost": flt(data["material_cost"], 2),
            "service_cost": flt(data["service_cost"], 2),
            "total_cost": flt(t_cost, 2),
            "received": flt(data["received"], 2),
            "pending": flt(data["pending"], 2),
        })

    # Material With Subcontractors Table
    materials_with_subcontractors = []
    for s in all_supplied_items:
        parent_order = next((o for o in orders if o.name == s.parent), None)
        if not parent_order:
            continue
        sent = flt(s.total_supplied_qty or s.supplied_qty)
        consumed = flt(s.consumed_qty)
        returned = flt(s.returned_qty)
        rem = max(0.0, sent - consumed - returned)
        if rem <= 0 and sent <= 0:
            continue

        item_name = frappe.db.get_value("Item", s.rm_item_code, "item_name") or s.rm_item_code
        rate = flt(s.rate)
        m_val = rem * rate

        materials_with_subcontractors.append({
            "supplier": parent_order.supplier_name or parent_order.supplier,
            "item": item_name,
            "item_code": s.rm_item_code,
            "warehouse": s.reserve_warehouse or "—",
            "sent_quantity": sent,
            "consumed_quantity": consumed,
            "remaining_quantity": rem,
            "uom": s.stock_uom or "Nos",
            "rate": rate,
            "material_value": flt(m_val, 2),
            "project": parent_order.project or "—",
            "subcontracting_order": parent_order.name,
            "last_movement": str(parent_order.transaction_date or ""),
            "status": "With Supplier" if rem > 0 else "Consumed",
        })

    # Subcontracting Orders Table
    orders_table = []
    for o in orders:
        o_items = sco_items_map.get(o.name, [])
        item_names = [it.item_name or it.item_code for it in o_items]
        item_summary = ", ".join(item_names[:2])
        if len(item_names) > 2:
            item_summary += f" +{len(item_names)-2} more"

        ord_qty = flt(o.total_qty)
        per_rec = flt(o.per_received)
        rec_qty = ord_qty * (per_rec / 100.0)
        pending_qty = max(0.0, ord_qty - rec_qty)

        # Check material sent status
        o_supplied = supplied_items_map.get(o.name, [])
        tot_req = sum(flt(si.required_qty) for si in o_supplied)
        tot_sent = sum(flt(si.total_supplied_qty or si.supplied_qty) for si in o_supplied)
        mat_sent_str = "No Raw Material Needed" if not tot_req else (
            "Fully Sent" if tot_sent >= tot_req else (
                f"Partially Sent ({round(tot_sent/tot_req*100)}%)" if tot_sent > 0 else "Pending Dispatch"
            )
        )

        orders_table.append({
            "subcontracting_order": o.name,
            "purchase_order": o.purchase_order or "—",
            "supplier": o.supplier_name or o.supplier,
            "project": o.project or "—",
            "item": item_summary or "—",
            "ordered_qty": ord_qty,
            "received_qty": flt(rec_qty, 2),
            "pending_qty": flt(pending_qty, 2),
            "material_sent": mat_sent_str,
            "service_cost": flt(o.total, 2),
            "order_date": str(o.transaction_date or ""),
            "expected_date": str(o.schedule_date or ""),
            "status": o.status or ("Draft" if o.docstatus == 0 else "Open"),
        })

    # Attention Required / Overdue Table
    attention_required = []
    for o in orders:
        if o.docstatus == 2 or o.status in ("Completed", "Cancelled", "Closed"):
            continue

        exp_date = str(o.schedule_date or "")
        days_pending = 0
        if exp_date:
            days_pending = date_diff(cur_today, exp_date)

        issue = ""
        if exp_date and exp_date < cur_today:
            issue = f"Overdue by {days_pending} days"
        elif flt(o.per_received) == 0 and o.status in ("Material Transferred", "Partial Material Transferred"):
            issue = "Material sent; finished goods pending receipt"
        elif o.status == "Open":
            issue = "Pending material dispatch or initial processing"

        if issue:
            attention_required.append({
                "supplier": o.supplier_name or o.supplier,
                "subcontracting_order": o.name,
                "project": o.project or "—",
                "expected_date": exp_date or "—",
                "days_pending": max(0, days_pending),
                "issue": issue,
                "status": o.status or "Open",
            })

    # Live Subcontracting Activity
    live_activity = []
    # 1. SCO activities
    for o in orders[:15]:
        ts = o.modified or o.creation
        act = "Subcontracting Order Submitted" if o.docstatus == 1 else "Subcontracting Order Created"
        if o.status == "Completed":
            act = "Subcontracting Order Completed"
        elif o.status == "Material Transferred":
            act = "Raw Material Dispatched"
        elif o.status == "Partially Received":
            act = "Partial Finished Goods Received"

        live_activity.append({
            "timestamp": str(ts),
            "activity": act,
            "doctype": "Subcontracting Order",
            "name": o.name,
            "supplier": o.supplier_name or o.supplier,
            "project": o.project or "—",
        })

    # 2. Subcontracting Receipt activities
    for r in receipts[:10]:
        live_activity.append({
            "timestamp": str(r.creation or r.posting_date),
            "activity": "Finished Goods Received" if r.docstatus == 1 else "Subcontracting Receipt Drafted",
            "doctype": "Subcontracting Receipt",
            "name": r.name,
            "supplier": r.supplier_name or r.supplier,
            "project": r.project or "—",
        })

    # 3. Stock Entry transfers
    if has_se:
        se_entries = frappe.get_all(
            "Stock Entry",
            fields=["name", "creation", "posting_date", "purpose", "subcontracting_order", "project"],
            filters={"purpose": ["in", ["Send to Subcontractor", "Subcontracting Delivery", "Subcontracting Return"]], "docstatus": 1},
            order_by="creation desc",
            limit_page_length=10,
        )
        for se in se_entries:
            live_activity.append({
                "timestamp": str(se.creation or se.posting_date),
                "activity": f"Stock Movement: {se.purpose}",
                "doctype": "Stock Entry",
                "name": se.name,
                "supplier": "Subcontractor Warehouse",
                "project": se.project or "—",
            })

    live_activity.sort(key=lambda x: str(x["timestamp"]), reverse=True)
    live_activity = live_activity[:25]

    return {
        "currency": currency,
        "filters": f,
        "suppliers": suppliers_list,
        "projects": projects_list,
        "kpis": kpis,
        "pipeline": pipeline,
        "status_distribution": status_distribution,
        "cost_trends": cost_trends,
        "supplier_analysis": supplier_analysis,
        "project_analysis": project_analysis,
        "materials_with_subcontractors": materials_with_subcontractors,
        "orders": orders_table,
        "attention_required": attention_required,
        "supplier_performance": supplier_performance,
        "live_activity": live_activity,
    }
