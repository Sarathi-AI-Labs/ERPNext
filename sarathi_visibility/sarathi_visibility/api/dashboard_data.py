"""Permission-aware, explicit document relationships shared by dashboard and reports."""

from collections import defaultdict

import frappe
from frappe.model import get_permitted_fields
from frappe.utils import flt, getdate, today

UNASSIGNED = "__unassigned__"
PROJECT_FIELDS = [
    "name",
    "project_name",
    "company",
    "customer",
    "status",
    "percent_complete",
    "expected_start_date",
    "expected_end_date",
    "sales_order",
    "custom_sarathi_bom",
    "custom_sarathi_manufacturing",
]
WO_FIELDS = [
    "name",
    "project",
    "company",
    "bom_no",
    "sales_order",
    "production_item",
    "stock_uom",
    "qty",
    "produced_qty",
    "status",
    "docstatus",
    "planned_start_date",
    "planned_end_date",
    "actual_start_date",
    "actual_end_date",
    "track_semi_finished_goods",
]


def readable(doctype):
    return frappe.db.exists("DocType", doctype) and frappe.has_permission(
        doctype, "read"
    )


def rows(doctype, fields, filters=None):
    if not readable(doctype):
        return []
    meta = frappe.get_meta(doctype)
    valid = [
        f
        for f in fields
        if f in {"name", "docstatus", "creation", "modified"} or meta.has_field(f)
    ]
    return frappe.get_list(
        doctype,
        fields=valid,
        filters=filters or {},
        order_by="modified desc",
        limit_page_length=0,
    )


def children(doctype, parents, fields):
    """Only called with names returned by permission-filtered parent queries."""
    if not parents:
        return []
    meta = frappe.get_meta(doctype)
    parent_types = {
        "Sales Order Item": "Sales Order",
        "BOM Item": "BOM",
        "BOM Operation": "BOM",
        "Stock Entry Detail": "Stock Entry",
        "Work Order Item": "Work Order",
        "Work Order Operation": "Work Order",
        "Job Card Time Log": "Job Card",
        "Job Card Operation": "Job Card",
        "Material Request Item": "Material Request",
        "Purchase Order Item": "Purchase Order",
        "Purchase Receipt Item": "Purchase Receipt",
        "Purchase Invoice Item": "Purchase Invoice",
        "Delivery Note Item": "Delivery Note",
        "Sales Invoice Item": "Sales Invoice",
    }
    permitted = set(get_permitted_fields(doctype, parenttype=parent_types[doctype]))
    valid = [
        f
        for f in fields
        if f in permitted and (f in {"name", "parent", "idx"} or meta.has_field(f))
    ]
    return frappe.get_all(
        doctype,
        filters={"parent": ["in", list(parents)]},
        fields=valid,
        order_by="idx",
        limit_page_length=0,
    )


def check_link(doctype, name):
    if name:
        frappe.get_doc(doctype, name).check_permission("read")


def parse_filters(filters=None):
    raw = frappe.parse_json(filters) if isinstance(filters, str) else filters
    result = {
        key: (raw or {}).get(key) or ""
        for key in ("company", "customer", "project", "from_date", "to_date", "status")
    }
    if (raw or {}).get("unassigned_customer"):
        result["customer"] = UNASSIGNED
    for key in ("from_date", "to_date"):
        if result[key]:
            result[key] = str(getdate(result[key]))
    if (
        result["from_date"]
        and result["to_date"]
        and result["from_date"] > result["to_date"]
    ):
        frappe.throw("From date must be on or before To date.")
    if result["status"] not in (
        "",
        "Active",
        "Ongoing",
        "Completed",
        "Delayed",
        "Cancelled",
        "On hold",
    ):
        frappe.throw("Unsupported project status filter.")
    check_link("Company", result["company"])
    if result["customer"] != UNASSIGNED:
        check_link("Customer", result["customer"])
    if result["project"]:
        check_link("Project", result["project"])
        project = frappe.get_doc("Project", result["project"])
        if result["company"] and result["company"] != project.company:
            frappe.throw(
                "Project does not belong to the selected organization.",
                frappe.PermissionError,
            )
        customer = project.customer or UNASSIGNED
        if result["customer"] and result["customer"] != customer:
            frappe.throw(
                "Project does not belong to the selected customer.",
                frappe.PermissionError,
            )
        result.update(company=project.company or "", customer=customer)
        check_link("Company", result["company"])
    return result


def delayed(row):
    return bool(
        row.get("expected_end_date")
        and str(row["expected_end_date"])[:10] < today()
        and row.get("status") not in ("Completed", "Cancelled")
    )


def status_matches(project, status):
    if status == "Delayed":
        return delayed(project)
    if status == "Ongoing":
        return project.get("status") == "Open"
    if status == "Active":
        return project.get("status") not in ("Completed", "Cancelled")
    return not status or project.get("status") == status


def in_period(value, filters):
    if not filters["from_date"] and not filters["to_date"]:
        return True
    if not value:
        return False
    date = str(value)[:10]
    return (not filters["from_date"] or date >= filters["from_date"]) and (
        not filters["to_date"] or date <= filters["to_date"]
    )


def load(filters=None):
    f = parse_filters(filters)
    companies = rows("Company", ["name", "company_name", "default_currency"])
    company_names = {r.name for r in companies}
    company_filter = (
        {"company": f["company"]}
        if f["company"]
        else {"company": ["in", list(company_names) or ["__none__"]]}
    )
    customers = rows("Customer", ["name", "customer_name", "disabled"])
    customer_map = {c.name: c for c in customers}
    projects = rows("Project", PROJECT_FIELDS, company_filter)
    # Project access never grants access to unrelated restricted customer records.
    projects = [
        p for p in projects if not p.get("customer") or p.customer in customer_map
    ]
    all_projects = projects
    if f["customer"]:
        projects = [p for p in projects if (p.customer or UNASSIGNED) == f["customer"]]
    if f["project"]:
        projects = [p for p in projects if p.name == f["project"]]
    projects = [p for p in projects if status_matches(p, f["status"])]
    project_map = {p.name: p for p in projects}
    project_names = list(project_map)
    project_filter = {"project": ["in", project_names or ["__none__"]]}
    for p in projects:
        p["customer_name"] = customer_map.get(p.customer, {}).get(
            "customer_name", "Unassigned customer"
        )
        p["delayed"] = delayed(p)

    orders = rows(
        "Sales Order",
        [
            "name",
            "company",
            "customer",
            "project",
            "transaction_date",
            "delivery_date",
            "status",
            "docstatus",
            "currency",
            "grand_total",
            "base_grand_total",
            "per_delivered",
            "per_billed",
        ],
        company_filter,
    )
    orders = [o for o in orders if o.customer in customer_map]
    membership_orders = orders
    if f["customer"] and f["customer"] != UNASSIGNED:
        orders = [o for o in orders if o.customer == f["customer"]]
    orders = [o for o in orders if in_period(o.transaction_date, f)]
    all_order_items = children(
        "Sales Order Item",
        [o.name for o in orders],
        [
            "name",
            "parent",
            "item_code",
            "item_name",
            "qty",
            "stock_qty",
            "uom",
            "stock_uom",
            "delivered_qty",
            "produced_qty",
            "bom_no",
            "project",
            "delivery_date",
            "base_amount",
            "net_amount",
            "billed_amt",
        ],
    )
    order_parent_map = {o.name: o for o in orders}
    for r in all_order_items:
        r.project = r.get("project") or order_parent_map[r.parent].get("project")
    # Project and status views only include orders explicitly tied to matching projects.
    if f["project"] or f["status"] or f["customer"] == UNASSIGNED:
        linked_orders = {p.sales_order for p in projects if p.get("sales_order")}
        item_orders = {
            r.parent for r in all_order_items if r.get("project") in project_map
        }
        orders = [
            o
            for o in orders
            if o.project in project_map
            or o.name in linked_orders
            or o.name in item_orders
        ]
    order_items = [r for r in all_order_items if r.parent in {o.name for o in orders}]
    if f["project"] or f["status"] or f["customer"] == UNASSIGNED:
        order_map = {o.name: o for o in orders}
        order_items = [
            r
            for r in order_items
            if r.get("project") in project_map
            or (
                not r.get("project")
                and order_map[r.parent].get("project") in project_map
            )
            or (
                not r.get("project")
                and r.parent in {p.get("sales_order") for p in projects}
                and len(
                    {p.name for p in all_projects if p.get("sales_order") == r.parent}
                )
                == 1
            )
        ]
        for order in orders:
            selected_items = [r for r in order_items if r.parent == order.name]
            if len(selected_items) != sum(
                r.parent == order.name for r in all_order_items
            ):
                # A mixed-project order must not contribute the other project's value.
                order["grand_total"] = sum(
                    flt(r.get("net_amount")) for r in selected_items
                )
                order["value_scope"] = "Selected project items, net excluding taxes"
                order["per_delivered"] = None
                order["per_billed"] = None
            else:
                order["value_scope"] = "Full order including taxes"
    else:
        for order in orders:
            order["value_scope"] = "Full order including taxes"

    if f["project"]:
        work_orders = rows("Work Order", WO_FIELDS, project_filter)
        work_orders = [
            w
            for w in work_orders
            if w.project in project_map and w.company == project_map[w.project].company
        ]
    else:
        work_orders = rows("Work Order", WO_FIELDS, company_filter)
        for w in work_orders:
            w["project"] = w.get("project") or "—"
    wo_map = {w.name: w for w in work_orders}
    job_cards = rows(
        "Job Card",
        [
            "name",
            "work_order",
            "project",
            "company",
            "production_item",
            "operation",
            "workstation",
            "for_quantity",
            "total_completed_qty",
            "stock_uom",
            "time_required",
            "total_time_in_mins",
            "expected_end_date",
            "posting_date",
            "status",
            "docstatus",
            "operation_id",
            "is_corrective_job_card",
            "modified",
            "process_loss_qty",
            "sequence_id",
            "finished_good",
            "semi_fg_bom",
            "manufactured_qty",
            "track_semi_finished_goods",
            "batch_no",
            "for_job_card",
            "quality_inspection",
            "is_paused",
        ],
        (
            {"work_order": ["in", list(wo_map) or ["__none__"]]}
            if wo_map
            else company_filter
        ),
    )
    if f["project"]:
        job_cards = [j for j in job_cards if j.company == wo_map[j.work_order].company]
    for j in job_cards:
        j["project"] = wo_map.get(j.work_order, {}).get("project") or "—"
        j["planned_hours"] = flt(j.get("time_required")) / 60
        j["actual_hours"] = flt(j.get("total_time_in_mins")) / 60
    for j in job_cards:
        w = wo_map.get(j.work_order)
        if not w:
            continue
        j["production_phase"] = (
            "Cancelled"
            if j.docstatus == 2 or w.docstatus == 2
            else (
                "Planned / draft Work Order"
                if w.docstatus != 1
                else (
                    "Completed"
                    if j.status == "Completed"
                    else (
                        "Stopped / closed Work Order"
                        if w.status in ("Stopped", "Closed", "Completed")
                        else (
                            "On hold"
                            if j.get("is_paused") or j.status in ("On Hold", "On hold")
                            else (
                                "Awaiting stock posting"
                                if j.docstatus == 1
                                else "Executable pending"
                            )
                        )
                    )
                )
            )
        )
    work_orders_period = [
        w for w in work_orders if in_period(w.get("planned_start_date"), f)
    ]

    time_logs = children(
        "Job Card Time Log",
        [j.name for j in job_cards if j.docstatus != 2],
        ["parent", "from_time", "to_time"],
    )
    lifetime_jobs = job_cards
    job_cards = [j for j in lifetime_jobs if in_period(j.posting_date, f)]
    wo_operations = children(
        "Work Order Operation",
        [w.name for w in work_orders if w.docstatus == 1],
        [
            "name",
            "parent",
            "idx",
            "operation",
            "sequence_id",
            "workstation",
            "completed_qty",
            "process_loss_qty",
            "status",
            "actual_start_time",
            "time_in_mins",
            "actual_operation_time",
            "finished_good",
            "fg_warehouse",
        ],
    )

    boms = rows(
        "BOM",
        [
            "name",
            "item",
            "item_name",
            "company",
            "quantity",
            "uom",
            "is_active",
            "docstatus",
            "custom_sarathi_project",
            "amended_from",
            "total_cost",
            "currency",
        ],
        (
            {"custom_sarathi_project": ["in", project_names or ["__none__"]]}
            if f["project"]
            else company_filter
        ),
    )
    # Historical BOM references from accessible Work Orders are displayed as history,
    # never inferred from matching item codes.
    historical = {w.bom_no for w in work_orders if w.bom_no} - {b.name for b in boms}
    if historical:
        boms += rows(
            "BOM",
            [
                "name",
                "item",
                "item_name",
                "company",
                "quantity",
                "uom",
                "is_active",
                "docstatus",
                "custom_sarathi_project",
                "amended_from",
                "total_cost",
                "currency",
            ],
            {"name": ["in", list(historical)]},
        )
    boms = [
        b
        for b in boms
        if (
            not f["project"]
            or (
                b.company in {p.company for p in projects}
                and (
                    not b.get("custom_sarathi_project")
                    or b.custom_sarathi_project in project_map
                )
            )
        )
    ]
    for b in boms:
        b["project"] = (
            b.get("custom_sarathi_project")
            or ", ".join(sorted({w.project for w in work_orders if w.bom_no == b.name}))
            or "—"
        )
        b["assignment"] = (
            "Current main BOM"
            if any(p.get("custom_sarathi_bom") == b.name for p in projects)
            else (
                "Historical / unassigned"
                if not b.get("custom_sarathi_project")
                else "Draft / revision"
            )
        )
    # Walk only explicitly linked, readable subassembly BOMs; no item-code inference.
    known_boms = {b.name for b in boms}
    frontier = list(boms)
    while frontier:
        edges = children("BOM Item", [b.name for b in frontier], ["parent", "bom_no"])
        candidates = {e.get("bom_no") for e in edges if e.get("bom_no")} - known_boms
        if not candidates:
            break
        next_boms = rows(
            "BOM",
            [
                "name",
                "item",
                "item_name",
                "company",
                "quantity",
                "uom",
                "is_active",
                "docstatus",
                "custom_sarathi_project",
                "amended_from",
                "total_cost",
                "currency",
            ],
            {"name": ["in", list(candidates)]},
        )
        next_boms = [
            b
            for b in next_boms
            if (
                b.company in {p.company for p in projects}
                and b.get("custom_sarathi_project") in (None, "")
            )
            or (
                b.get("custom_sarathi_project") in project_map
                and b.company == project_map[b.custom_sarathi_project].company
            )
        ]
        parent_boms = {b.name: b for b in frontier}
        for b in next_boms:
            b.project = b.get("custom_sarathi_project") or ", ".join(
                sorted(
                    {
                        parent_boms[e.parent].project
                        for e in edges
                        if e.get("bom_no") == b.name
                    }
                )
            )
            b.assignment = "Linked subassembly BOM"
        boms += next_boms
        known_boms.update(b.name for b in next_boms)
        if len(known_boms) > 1000:
            frappe.throw("Project BOM tree exceeds supported size")
        frontier = next_boms
    components = children(
        "BOM Item",
        [b.name for b in boms],
        [
            "parent",
            "item_code",
            "item_name",
            "qty",
            "stock_qty",
            "stock_uom",
            "uom",
            "source_warehouse",
            "bom_no",
            "rate",
            "amount",
        ],
    )
    operations = children(
        "BOM Operation",
        [b.name for b in boms],
        [
            "parent",
            "operation",
            "workstation",
            "time_in_mins",
            "hour_rate",
            "operating_cost",
            "idx",
        ],
    )

    stock = rows(
        "Stock Entry",
        [
            "name",
            "company",
            "project",
            "work_order",
            "purpose",
            "posting_date",
            "fg_completed_qty",
            "job_card",
            "docstatus",
        ],
        company_filter,
    )
    stock_parent_map = {s.name: s for s in stock}
    raw_stock_items = children(
        "Stock Entry Detail",
        list(stock_parent_map),
        [
            "name",
            "parent",
            "item_code",
            "item_name",
            "transfer_qty",
            "stock_uom",
            "s_warehouse",
            "t_warehouse",
            "is_finished_item",
            "project",
            "quality_inspection",
            "batch_no",
            "serial_no",
            "secondary_item_type",
        ],
    )
    stock_items = []
    for r in raw_stock_items:
        parent = stock_parent_map[r.parent]
        linked_project = wo_map.get(parent.get("work_order"), {}).get("project")
        project = r.get("project") or linked_project or parent.get("project")
        if f["project"]:
            if project != f["project"]:
                continue
        elif project and project_map and project not in project_map:
            continue
        r.update(
            project=project or "—",
            line_id=r.name,
            posting_date=parent.posting_date,
            work_order=parent.get("work_order"),
            job_card=parent.get("job_card"),
            purpose=parent.purpose,
            quantity_basis="Posted stock movement, not current project allocation",
        )
        stock_items.append(r)
    selected_parents = {r.parent for r in stock_items}
    stock_parent_projects = {
        name: sorted({r.project for r in stock_items if r.parent == name})
        for name in selected_parents
    }
    stock_items = [r for r in stock_items if stock_parent_map[r.parent].docstatus == 1]
    stock = [s for s in stock if s.name in selected_parents]
    stock_map = {s.name: s for s in stock}
    for s in stock:
        s.project = ", ".join(stock_parent_projects[s.name])
    finished = [
        r
        for r in stock_items
        if r.get("is_finished_item") and in_period(r.posting_date, f)
    ]

    required = children(
        "Work Order Item",
        [
            w.name
            for w in work_orders_period
            if w.docstatus == 1 and w.status not in ("Completed", "Stopped", "Closed")
        ],
        [
            "parent",
            "item_code",
            "item_name",
            "required_qty",
            "consumed_qty",
            "transferred_qty",
            "source_warehouse",
        ],
    )
    warehouses = rows("Warehouse", ["name", "company"], company_filter)
    warehouse_names = {w.name for w in warehouses}
    # Bin has no user-level Company field: limit it to already-authorized warehouses.
    bins = rows(
        "Bin",
        [
            "name",
            "item_code",
            "warehouse",
            "actual_qty",
            "reserved_qty",
            "reserved_qty_for_production",
        ],
        {
            "warehouse": ["in", list(warehouse_names) or ["__none__"]],
            "item_code": ["in", list({r.item_code for r in required}) or ["__none__"]],
        },
    )
    available = {(r.item_code, r.warehouse): flt(r.actual_qty) for r in bins}
    material_map = {}
    item_info = {
        r.name: r
        for r in rows(
            "Item",
            ["name", "stock_uom"],
            {"name": ["in", list({r.item_code for r in required}) or ["__none__"]]},
        )
    }
    for r in required:
        wo = wo_map[r.parent]
        key = (r.item_code, r.source_warehouse or "", wo.company)
        entry = material_map.setdefault(
            key,
            {
                "item_code": r.item_code,
                "item_name": r.item_name,
                "warehouse": r.source_warehouse or "",
                "company": wo.company,
                "uom": item_info.get(r.item_code, {}).get("stock_uom", ""),
                "required_qty": 0,
                "remaining_qty": 0,
            },
        )
        entry["required_qty"] += flt(r.required_qty)
        entry["remaining_qty"] += max(
            flt(r.required_qty) - max(flt(r.consumed_qty), flt(r.transferred_qty)), 0
        )
    materials = list(material_map.values())
    for r in materials:
        known = readable("Bin") and r["warehouse"] in warehouse_names
        r["available_qty"] = (
            available.get((r["item_code"], r["warehouse"]), 0) if known else None
        )
        r["shortage_qty"] = (
            max(r["remaining_qty"] - r["available_qty"], 0) if known else None
        )
    from sarathi_visibility.api.production import analyze

    semi_items = {
        o.get("finished_good") for o in wo_operations if o.get("finished_good")
    }
    semi_bins = (
        rows(
            "Bin",
            ["name", "item_code", "warehouse", "actual_qty"],
            {
                "warehouse": ["in", list(warehouse_names) or ["__none__"]],
                "item_code": ["in", list(semi_items) or ["__none__"]],
            },
        )
        if readable("Bin")
        else None
    )
    semi_units = {
        i.name: i.get("stock_uom")
        for i in rows(
            "Item",
            ["name", "stock_uom"],
            {"name": ["in", list(semi_items) or ["__none__"]]},
        )
    }
    operation_balance, production_summary, wip_stock = analyze(
        projects,
        work_orders,
        wo_operations,
        lifetime_jobs,
        warehouse_names,
        semi_bins,
        semi_units,
    )
    from sarathi_visibility.api.production import live_activity

    live_activity_rows = live_activity(
        projects,
        work_orders,
        lifetime_jobs,
        time_logs,
        operation_balance,
        production_summary,
    )
    tasks = rows(
        "Task",
        [
            "name",
            "subject",
            "project",
            "status",
            "progress",
            "exp_end_date",
            "expected_time",
            "actual_time",
        ],
        project_filter,
    )
    integrations = rows(
        "Sarathi Machine Integration Log",
        [
            "name",
            "project",
            "sync_status",
            "machine",
            "source_system",
            "timestamp",
            "planned_qty",
            "completed_qty",
            "rejected_qty",
            "modified",
        ],
        project_filter,
    )

    associations = rows(
        "Sarathi Customer Organization", ["name", "company", "customer"], company_filter
    )
    member_names = (
        {p.customer for p in all_projects if p.customer}
        | {o.customer for o in membership_orders}
        | {a.customer for a in associations}
    )
    if not f["company"]:
        customer_cards = [dict(c) for c in customers if not c.get("disabled")]
    else:
        customer_cards = [dict(c) for c in customers if c.name in member_names]
    customers_catalogue = [dict(c) for c in customers if not c.get("disabled")]
    if any(not p.customer for p in all_projects):
        customer_cards.append(
            {"name": UNASSIGNED, "customer_name": "Unassigned customer"}
        )
    for c in customer_cards:
        scoped = [p for p in projects if (p.customer or UNASSIGNED) == c["name"]]
        c.update(
            project_count=len(scoped),
            active=sum(status_matches(p, "Active") for p in scoped),
            delayed=sum(delayed(p) for p in scoped),
            open_orders=sum(
                o.docstatus == 1 and o.status not in ("Completed", "Closed")
                for o in orders
                if o.customer == c["name"]
            ),
        )
    for p in projects:
        p["main_item"] = next(
            (b.item for b in boms if b.name == p.get("custom_sarathi_bom")), None
        )
        p["work_order_count"] = sum(
            w.project == p.name and w.docstatus != 2 for w in work_orders
        )
        p["job_card_count"] = sum(
            j.project == p.name and j.docstatus != 2 for j in job_cards
        )

    issues = []
    for p in projects:
        for condition, message in (
            (not p.customer, "Assign a customer"),
            (not p.get("custom_sarathi_bom"), "Assign an explicit main BOM"),
        ):
            if condition:
                issues.append(
                    {
                        "name": p.name,
                        "doctype": "Project",
                        "project": p.name,
                        "issue": message,
                    }
                )
    for w in work_orders:
        if w.docstatus != 2 and not any(
            b.name == w.bom_no and b.get("custom_sarathi_project") == w.project
            for b in boms
        ):
            issues.append(
                {
                    "name": w.name,
                    "doctype": "Work Order",
                    "project": w.project,
                    "issue": "Historical BOM needs explicit project ownership; no item-based inference used",
                }
            )
    for j in job_cards:
        if (
            j.docstatus != 2
            and j.status != "Completed"
            and j.get("expected_end_date")
            and str(j.expected_end_date)[:10] < today()
        ):
            issues.append(
                {
                    "name": j.name,
                    "doctype": "Job Card",
                    "project": j.project,
                    "issue": "Operation is past its planned end date",
                }
            )
    for r in production_summary:
        if (
            r["project_status"] == "Completed"
            and r["production_status"] != "Finished"
            and r["work_orders"]
        ):
            issues.append(
                dict(
                    name=r["project"],
                    doctype="Project",
                    project=r["project"],
                    issue="Project is Completed but submitted manufacturing is unfinished",
                )
            )
    for r in operation_balance:
        if (
            r["completed"] is not None
            and r["completed"] + (r["process_loss"] or 0) > r["planned"]
        ):
            issues.append(
                dict(
                    name=r["work_order"],
                    doctype="Work Order",
                    project=r["project"],
                    issue="Operation completion plus process loss exceeds planned quantity: "
                    + (r["operation"] or ""),
                )
            )
    open_log_parents = {
        log.parent
        for log in time_logs
        if log.get("from_time") and not log.get("to_time")
    }
    for j in lifetime_jobs:
        if j.name in open_log_parents and (
            project_map[j.project].status in ("Completed", "Cancelled", "On hold")
            or j.status == "Completed"
            or wo_map[j.work_order].status in ("Completed", "Stopped", "Closed")
        ):
            issues.append(
                dict(
                    name=j.name,
                    doctype="Job Card",
                    project=j.project,
                    issue="Open time log conflicts with completed / held / stopped work; verify and close the time log",
                )
            )
    deadlines = []
    for dt, records, field in (
        ("Project", projects, "expected_end_date"),
        ("Task", tasks, "exp_end_date"),
    ):
        for r in records:
            if r.get(field) and r.status not in ("Completed", "Cancelled"):
                deadlines.append(
                    dict(
                        doctype=dt,
                        name=r.name,
                        project=r.name if dt == "Project" else r.project,
                        due_date=str(r.get(field))[:10],
                        status=r.status,
                        days_remaining=(getdate(r.get(field)) - getdate(today())).days,
                    )
                )
    deadlines.sort(key=lambda r: r["due_date"])
    from sarathi_visibility.api.pipeline import load_pipeline

    pipeline = load_pipeline(
        dict(
            projects=projects, filters=f, order_items=order_items, wip_stock=wip_stock
        ),
        company_filter,
        work_orders,
        lifetime_jobs,
        stock_items,
        stock_map,
    )
    all_items = rows(
        "Item",
        [
            "name",
            "item_name",
            "item_group",
            "stock_uom",
            "is_stock_item",
            "default_warehouse",
            "valuation_rate",
            "standard_rate",
            "disabled",
        ],
    )
    items = [i for i in all_items if not i.get("disabled")]
    item_map = {i.name: i for i in items}

    bins_data = (
        rows(
            "Bin",
            [
                "name",
                "item_code",
                "warehouse",
                "actual_qty",
                "reserved_qty",
                "valuation_rate",
                "stock_value",
            ],
            {"warehouse": ["in", list(warehouse_names) or ["__none__"]]},
        )
        if readable("Bin")
        else []
    )
    inventory = []
    for b in bins_data:
        i_info = item_map.get(b.item_code, {})
        inventory.append(
            frappe._dict(
                name=b.name,
                item_code=b.item_code,
                item_name=i_info.get("item_name") or b.item_code,
                warehouse=b.warehouse,
                actual_qty=flt(b.actual_qty),
                stock_uom=i_info.get("stock_uom", ""),
                valuation_rate=flt(b.valuation_rate),
                stock_value=flt(b.stock_value)
                or (flt(b.actual_qty) * flt(b.valuation_rate)),
                reserved_qty=flt(b.reserved_qty),
            )
        )

    # Master catalogues & workstations
    all_workstations = rows(
        "Workstation",
        [
            "name",
            "workstation_name",
            "workstation_type",
            "status",
            "production_capacity",
            "hour_rate",
            "description",
            "plant_floor",
        ],
    )
    station_stats = {}
    for j in lifetime_jobs:
        if j.docstatus == 2:
            continue
        w_name = j.get("workstation") or ""
        s = station_stats.setdefault(
            w_name,
            {"jobs": 0, "open_jobs": 0, "planned_hours": 0.0, "actual_hours": 0.0},
        )
        s["jobs"] += 1
        s["open_jobs"] += 1 if j.status != "Completed" else 0
        s["planned_hours"] += flt(j.get("planned_hours") or j.get("time_required")) / 60
        s["actual_hours"] += (
            flt(j.get("actual_hours") or j.get("total_time_in_mins")) / 60
        )

    workstation_rows = []
    for w in all_workstations:
        st = station_stats.get(
            w.name,
            {"jobs": 0, "open_jobs": 0, "planned_hours": 0.0, "actual_hours": 0.0},
        )
        workstation_rows.append(
            frappe._dict(
                name=w.name,
                workstation=w.name,
                workstation_name=w.get("workstation_name") or w.name,
                workstation_type=w.get("workstation_type") or "—",
                status=w.get("status") or "Production",
                production_capacity=flt(w.get("production_capacity") or 1),
                jobs=st["jobs"],
                open_jobs=st["open_jobs"],
                planned_hours=st["planned_hours"],
                actual_hours=st["actual_hours"],
                description=w.get("description") or "",
                plant_floor=w.get("plant_floor") or "—",
            )
        )
    for w_name, st in station_stats.items():
        if w_name and not any(w.name == w_name for w in all_workstations):
            workstation_rows.append(
                frappe._dict(
                    name=w_name,
                    workstation=w_name,
                    workstation_name=w_name,
                    workstation_type="—",
                    status="Production",
                    production_capacity=1,
                    jobs=st["jobs"],
                    open_jobs=st["open_jobs"],
                    planned_hours=st["planned_hours"],
                    actual_hours=st["actual_hours"],
                    description="",
                    plant_floor="—",
                )
            )

    operations_catalogue = rows(
        "Operation", ["name", "operation_name", "workstation", "description"]
    )
    warehouses_list = rows(
        "Warehouse",
        [
            "name",
            "warehouse_name",
            "company",
            "is_group",
            "parent_warehouse",
            "disabled",
        ],
        company_filter if f["company"] else None,
    )
    warehouses = [w for w in warehouses_list if not w.get("disabled")]
    suppliers_list = rows(
        "Supplier",
        [
            "name",
            "supplier_name",
            "supplier_group",
            "country",
            "is_transporter",
            "disabled",
        ],
    )
    suppliers = [s for s in suppliers_list if not s.get("disabled")]
    workstation_types = rows(
        "Workstation Type", ["name", "workstation_type", "description"]
    )
    plant_floors = rows("Plant Floor", ["name", "floor_name", "warehouse", "company"])
    routings = rows("Routing", ["name", "routing_name", "disabled"])

    if not readable("Work Order"):
        for r in production_summary:
            if r["project_status"] not in ("Completed", "Cancelled", "On hold"):
                r.update(
                    live_status="Access restricted",
                    production_status="Access restricted",
                    activity_message="Work Order read access is required",
                    note="Manufacturing data unavailable to this viewer",
                )
    return dict(
        **pipeline,
        items=items,
        inventory=inventory,
        workstations=workstation_rows,
        operations_catalogue=operations_catalogue,
        warehouses=warehouses,
        customers_catalogue=customers_catalogue,
        suppliers=suppliers,
        workstation_types=workstation_types,
        plant_floors=plant_floors,
        routings=routings,
        live_activity=live_activity_rows,
        operation_balance=operation_balance,
        production_summary=production_summary,
        wip_stock=wip_stock,
        filters=f,
        companies=companies,
        customers=customer_cards,
        projects=projects,
        orders=orders,
        order_items=order_items,
        work_orders=work_orders_period,
        job_cards=job_cards,
        boms=boms,
        components=components,
        operations=operations,
        stock=stock,
        finished=finished,
        materials=materials,
        tasks=tasks,
        integrations=integrations,
        issues=issues,
        deadlines=deadlines,
    )


def grouped(rows_, key, value=None):
    result = defaultdict(float)
    for r in rows_:
        result[str(r.get(key) or "Unassigned")] += flt(r.get(value)) if value else 1
    return dict(result)
