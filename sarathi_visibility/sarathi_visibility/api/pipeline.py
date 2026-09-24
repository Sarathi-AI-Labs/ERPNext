"""Explicit, item-level project attribution across procurement and fulfillment."""

from collections import defaultdict

import frappe
from frappe.utils import flt

DOCUMENTS = {
    "requests": ("Material Request", "Material Request Item"),
    "purchases": ("Purchase Order", "Purchase Order Item"),
    "receipts": ("Purchase Receipt", "Purchase Receipt Item"),
    "purchase_invoices": ("Purchase Invoice", "Purchase Invoice Item"),
    "deliveries": ("Delivery Note", "Delivery Note Item"),
    "sales_invoices": ("Sales Invoice", "Sales Invoice Item"),
}
LINK_ROWS = (
    "material_request_item",
    "purchase_order_item",
    "purchase_receipt_item",
    "sales_order_item",
    "so_detail",
    "dn_detail",
)
LINE_FIELDS = [
    "name",
    "parent",
    "project",
    "item_code",
    "item_name",
    "qty",
    "stock_qty",
    "uom",
    "stock_uom",
    "conversion_factor",
    "ordered_qty",
    "received_qty",
    "returned_qty",
    "rejected_qty",
    "delivered_qty",
    "schedule_date",
    "warehouse",
    "rejected_warehouse",
    "net_amount",
    "quality_inspection",
    "batch_no",
    "serial_no",
    "material_request",
    "purchase_order",
    "purchase_receipt",
    "sales_order",
    "delivery_note",
    "job_card",
] + list(LINK_ROWS)


def resolve_project(line, parent, references):
    """An explicit line wins; conflicting references are flagged, never guessed."""
    linked = {
        references[k] for f in LINK_ROWS for k in [line.get(f)] if k in references
    }
    explicit = line.get("project")
    if explicit:
        return explicit, (
            "Explicit item Project"
            if not linked or linked == {explicit}
            else "Conflicting linked Project"
        )
    if len(linked) == 1:
        project = next(iter(linked))
        if parent.get("project") and parent.project != project:
            return None, "Conflicting header / linked Project"
        return project, "Linked document item"
    if len(linked) > 1:
        return None, "Ambiguous linked Projects"
    return parent.get("project"), (
        "Document Project"
        if parent.get("project")
        else "Assign item Project / document link"
    )


def load_pipeline(data, company_filter, work_orders, jobs, stock_items, stock_map):
    from sarathi_visibility.api.dashboard_data import children, readable, rows

    projects = {p.name: p for p in data["projects"]}
    references = {
        r.name: r.project
        for r in data.get("order_items", [])
        if r.get("name") and r.get("project") in projects
    }
    # Lifetime procurement links must not disappear under an activity date filter.
    sales = rows(
        "Sales Order", ["name", "project", "company", "customer"], company_filter
    )
    sales_map = {s.name: s for s in sales}
    for line in children(
        "Sales Order Item", list(sales_map), ["name", "parent", "project"]
    ):
        parent = sales_map[line.parent]
        project = line.get("project") or parent.get("project")
        if not project:
            linked = {
                p.name for p in projects.values() if p.get("sales_order") == parent.name
            }
            project = next(iter(linked)) if len(linked) == 1 else None
        if (
            project in projects
            and parent.company == projects[project].company
            and parent.customer == projects[project].customer
        ):
            references[line.name] = project
    result, parent_maps, line_maps = {}, {}, {}
    exceptions = []
    unrestricted = not any(
        data["filters"].get(k) for k in ("project", "customer", "status")
    )
    for key, (doctype, childtype) in DOCUMENTS.items():
        parents = rows(
            doctype,
            [
                "name",
                "company",
                "project",
                "supplier",
                "customer",
                "status",
                "docstatus",
                "transaction_date",
                "posting_date",
                "currency",
                "is_return",
                "update_stock",
                "outstanding_amount",
            ],
            company_filter,
        )
        parent_map = {p.name: p for p in parents}
        lines = children(childtype, list(parent_map), LINE_FIELDS)
        selected = []
        for line in lines:
            parent = parent_map[line.parent]
            project, basis = resolve_project(line, parent, references)
            if basis.startswith(("Conflicting", "Ambiguous")):
                if (
                    project in projects
                    or parent.get("project") in projects
                    or unrestricted
                ):
                    exceptions.append(
                        dict(
                            doctype=doctype,
                            name=parent.name,
                            line_id=line.name,
                            item_code=line.get("item_code"),
                            project=project if project in projects else None,
                            issue=basis,
                        )
                    )
                continue
            if not project:
                if unrestricted:
                    exceptions.append(
                        dict(
                            doctype=doctype,
                            name=parent.name,
                            line_id=line.name,
                            item_code=line.get("item_code"),
                            project=None,
                            issue=basis,
                        )
                    )
                if not data["filters"].get("project"):
                    project = "—"
                    basis = "Company document"
                else:
                    continue
            if project != "—":
                if (
                    project not in projects
                    or parent.company != projects[project].company
                ):
                    continue
                if (
                    parent.get("customer")
                    and parent.customer != projects[project].customer
                ):
                    continue
            row = frappe._dict(line)
            row.update(
                line_id=line.name,
                name=parent.name,
                project=project,
                company=parent.company,
                doctype=doctype,
                supplier=parent.get("supplier"),
                customer=parent.get("customer"),
                status=parent.status,
                docstatus=parent.docstatus,
                date=parent.get("posting_date") or parent.get("transaction_date"),
                currency=parent.get("currency"),
                is_return=parent.get("is_return"),
                update_stock=parent.get("update_stock"),
                basis=basis,
                value_basis="Item net amount excluding document taxes",
                outstanding_amount=None,
            )
            row["remaining_qty"] = (
                max(
                    flt(line.qty)
                    - flt(
                        line.get("received_qty")
                        if key == "purchases"
                        else line.get("ordered_qty")
                    ),
                    0,
                )
                if key in ("requests", "purchases")
                else None
            )
            selected.append(row)
            references[line.name] = project

        # Outstanding is meaningful only when every document item belongs to this selection.
        for row in selected:
            parent = parent_map[row.name]
            if key in ("purchase_invoices", "sales_invoices") and len(
                [r for r in selected if r.name == row.name]
            ) == len([r for r in lines if r.parent == row.name]):
                row.outstanding_amount = parent.get("outstanding_amount")
                row.value_basis += (
                    "; outstanding is whole-document amount (do not sum repeated rows)"
                )
        result[key] = selected
        parent_maps[doctype] = parent_map
        line_maps[doctype] = {r.line_id: r for r in selected}

    # Material history includes completed submitted Work Orders and their native consumption.
    wo_map = {w.name: w for w in work_orders if w.docstatus == 1}
    required = children(
        "Work Order Item",
        list(wo_map),
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
    result["material_history"] = [
        frappe._dict(
            dict(
                r,
                project=wo_map[r.parent].project,
                work_order=r.parent,
                work_order_status=wo_map[r.parent].status,
                unit=wo_map[r.parent].get("stock_uom"),
            )
        )
        for r in required
    ]
    units = {
        r.name: r.get("stock_uom")
        for r in rows(
            "Item",
            ["name", "stock_uom"],
            {"name": ["in", list({r.item_code for r in required}) or ["__none__"]]},
        )
    }
    for r in result["material_history"]:
        r.unit = units.get(r.item_code)

    result["stock_details"] = stock_items
    result["part_production"] = []
    jobs_by_name = {j.name: j for j in jobs if j.docstatus != 2}
    for r in stock_items:
        j = jobs_by_name.get(r.get("job_card"))
        if (
            j
            and r.get("is_finished_item")
            and r.get("purpose") == "Manufacture"
            and r.get("t_warehouse")
        ):
            row = frappe._dict(r)
            row.update(operation=j.operation, workstation=j.get("workstation"))
            result["part_production"].append(row)
    job_map = {j.name: j for j in jobs if j.docstatus != 2}
    voucher_projects = defaultdict(set)
    for doctype, lines in line_maps.items():
        for r in lines.values():
            if r.docstatus == 1:
                voucher_projects[(doctype, r.name)].add(r.project)
    for s in stock_map.values():
        if s.docstatus == 1 and s.project in projects:
            voucher_projects[("Stock Entry", s.name)].add(s.project)
    allowed_details = {
        (dt, r.name, r.line_id)
        for dt, selected in line_maps.items()
        for r in selected.values()
        if r.docstatus == 1
    }
    allowed_details |= {("Stock Entry", r.parent, r.line_id) for r in stock_items}
    detail_projects = {
        (dt, r.name, r.line_id): r.project
        for dt, selected in line_maps.items()
        for r in selected.values()
        if r.docstatus == 1
    }
    detail_projects.update(
        {("Stock Entry", r.parent, r.line_id): r.project for r in stock_items}
    )
    result["stock_ledger"] = []
    for r in rows(
        "Stock Ledger Entry",
        [
            "name",
            "company",
            "voucher_type",
            "voucher_no",
            "voucher_detail_no",
            "warehouse",
            "item_code",
            "stock_uom",
            "actual_qty",
            "posting_date",
            "posting_time",
            "is_cancelled",
        ],
        company_filter,
    ):
        key = (r.voucher_type, r.voucher_no, r.voucher_detail_no)
        if key in allowed_details and not r.get("is_cancelled"):
            r.project = detail_projects[key]
            result["stock_ledger"].append(r)
    result["reservations"] = []
    for r in rows(
        "Stock Reservation Entry",
        [
            "name",
            "project",
            "company",
            "voucher_type",
            "voucher_no",
            "item_code",
            "warehouse",
            "stock_uom",
            "reserved_qty",
            "consumed_qty",
            "delivered_qty",
            "transferred_qty",
            "status",
            "docstatus",
        ],
        company_filter,
    ):
        project = r.get("project") or (
            wo_map.get(r.get("voucher_no"), {}).get("project")
            if r.get("voucher_type") == "Work Order"
            else references.get(r.get("voucher_detail_no"))
        )
        if project in projects and r.company == projects[project].company:
            r.project = project
            result["reservations"].append(r)

    result["quality"] = []
    for q in rows(
        "Quality Inspection",
        [
            "name",
            "company",
            "reference_type",
            "reference_name",
            "child_row_reference",
            "item_code",
            "status",
            "inspection_type",
            "sample_size",
            "report_date",
            "docstatus",
        ],
        company_filter,
    ):
        project = (
            job_map.get(q.reference_name, {}).get("project")
            if q.reference_type == "Job Card"
            else None
        )
        line = line_maps.get(q.reference_type, {}).get(q.get("child_row_reference"))
        if line:
            project = line.project
        if not project:
            explicit = {
                r.project
                for r in line_maps.get(q.reference_type, {}).values()
                if r.name == q.reference_name and r.get("quality_inspection") == q.name
            }
            if len(explicit) == 1:
                project = next(iter(explicit))
        if q.reference_type == "Stock Entry":
            selected = [
                r
                for r in stock_items
                if r.parent == q.reference_name
                and (
                    r.get("quality_inspection") == q.name
                    or r.get("line_id") == q.get("child_row_reference")
                )
            ]
            if len({r.project for r in selected}) == 1:
                project = selected[0].project
        if project in projects and q.company == projects[project].company:
            q.project = project
            result["quality"].append(q)

    result["job_logs"] = []
    for r in children(
        "Job Card Time Log",
        list(job_map),
        [
            "parent",
            "from_time",
            "to_time",
            "employee",
            "completed_qty",
            "time_in_mins",
            "operation",
        ],
    ):
        r.update(
            project=job_map[r.parent].project,
            job_card=r.parent,
            operation=r.get("operation") or job_map[r.parent].operation,
        )
        result["job_logs"].append(r)
    result["job_suboperations"] = []
    for r in children(
        "Job Card Operation",
        list(job_map),
        ["parent", "operation", "status", "completed_qty", "time_in_mins"],
    ):
        r.update(project=job_map[r.parent].project, job_card=r.parent)
        result["job_suboperations"].append(r)
    result["procurement_exceptions"] = exceptions
    result["tracking_setup"] = []
    for p in projects.values():
        result["tracking_setup"].append(
            dict(
                project=p.name,
                customer=p.customer,
                main_bom=p.get("custom_sarathi_bom"),
                validation=(
                    "Enabled"
                    if p.get("custom_sarathi_manufacturing")
                    else "Review / enable manufacturing validation"
                ),
                physical_parts=(
                    "Configured outputs"
                    if any(
                        p.name in r.get("projects", "").split(", ")
                        for r in data.get("wip_stock", [])
                    )
                    else "Configure operation output Items, BOMs and warehouses; no physical counts inferred"
                ),
            )
        )

    result["pipeline_summary"] = []
    for p in projects.values():
        metrics = {
            key: (
                len(
                    {
                        r.name
                        for r in result[key]
                        if r.project == p.name and r.docstatus == 1
                    }
                )
                if readable(dt)
                else None
            )
            for key, (dt, child) in DOCUMENTS.items()
        }
        metrics.update(
            project=p.name,
            customer=p.customer,
            work_orders=(
                len([w for w in wo_map.values() if w.project == p.name])
                if readable("Work Order")
                else None
            ),
            running_jobs=(
                len(
                    [
                        j
                        for j in jobs
                        if j.project == p.name
                        and j.get("production_phase") == "Executable pending"
                    ]
                )
                if readable("Job Card")
                else None
            ),
            inspections=(
                len([q for q in result["quality"] if q.project == p.name])
                if readable("Quality Inspection")
                else None
            ),
        )
        result["pipeline_summary"].append(metrics)
    if not projects and not data["filters"].get("project"):
        comp_name = data["filters"].get("company") or "Organization Overview"
        metrics = {
            key: (
                len({r.name for r in result[key] if r.docstatus == 1})
                if readable(dt)
                else None
            )
            for key, (dt, child) in DOCUMENTS.items()
        }
        metrics.update(
            project=comp_name,
            customer="—",
            work_orders=(
                len([w for w in wo_map.values() if w.docstatus == 1])
                if readable("Work Order")
                else None
            ),
            running_jobs=(
                len(
                    [
                        j
                        for j in jobs
                        if j.get("production_phase") == "Executable pending"
                    ]
                )
                if readable("Job Card")
                else None
            ),
            inspections=(
                len([q for q in result["quality"] if q.docstatus == 1])
                if readable("Quality Inspection")
                else None
            ),
        )
        result["pipeline_summary"].append(metrics)
    return result
