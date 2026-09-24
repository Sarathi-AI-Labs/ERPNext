"""Install explicit dashboard relationships without rewriting historical documents."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def install():
    create_custom_fields(
        {
            "Project": [
                {
                    "fieldname": "custom_sarathi_manufacturing",
                    "label": "Sarathi Manufacturing Project",
                    "fieldtype": "Check",
                    "insert_after": "project_type",
                },
                {
                    "fieldname": "custom_sarathi_bom",
                    "label": "Main BOM",
                    "fieldtype": "Link",
                    "options": "BOM",
                    "insert_after": "customer",
                    "description": "One current main BOM. Historical Work Orders retain their original BOM.",
                },
            ],
            "BOM": [
                {
                    "fieldname": "custom_sarathi_project",
                    "label": "Sarathi Project",
                    "fieldtype": "Link",
                    "options": "Project",
                    "insert_after": "company",
                    "allow_on_submit": 1,
                }
            ],
        },
        update=True,
    )
    # Only assign customers supported by an explicit Sales Order → Project link.
    for project in frappe.get_all(
        "Project", fields=["name", "company", "customer", "custom_sarathi_bom"]
    ):
        orders = frappe.get_all(
            "Sales Order",
            filters={
                "project": project.name,
                "docstatus": ["!=", 2],
                "company": project.company,
            },
            fields=["customer"],
        )
        customers = {r.customer for r in orders if r.customer}
        if not project.customer and len(customers) == 1:
            frappe.db.set_value(
                "Project",
                project.name,
                "customer",
                customers.pop(),
                update_modified=False,
            )
        if project.custom_sarathi_bom:
            continue
        names = set(
            frappe.get_all(
                "Work Order",
                filters={"project": project.name, "docstatus": ["!=", 2]},
                pluck="bom_no",
            )
        ) - {None, ""}
        if len(names) != 1:
            continue
        bom = next(iter(names))
        info = frappe.db.get_value(
            "BOM",
            bom,
            ["company", "custom_sarathi_project", "docstatus", "is_active"],
            as_dict=True,
        )
        other_projects = [
            p
            for p in frappe.get_all(
                "Work Order",
                filters={"bom_no": bom, "docstatus": ["!=", 2]},
                pluck="project",
            )
            if p != project.name
        ]
        if (
            info
            and info.company == project.company
            and info.docstatus == 1
            and info.is_active
            and not other_projects
            and info.custom_sarathi_project in (None, "", project.name)
        ):
            frappe.db.set_value(
                "BOM",
                bom,
                "custom_sarathi_project",
                project.name,
                update_modified=False,
            )
            frappe.db.set_value(
                "Project",
                project.name,
                "custom_sarathi_bom",
                bom,
                update_modified=False,
            )


def validate_project(doc, method=None):
    if doc.get("custom_sarathi_manufacturing") and (
        not doc.company or not doc.customer
    ):
        frappe.throw(
            "A Sarathi manufacturing project requires an organization and customer."
        )
    if doc.get("sales_order"):
        order = frappe.get_doc("Sales Order", doc.sales_order)
        if order.company != doc.company or (
            doc.customer and order.customer != doc.customer
        ):
            frappe.throw(
                "The Sales Order must belong to this project's organization and customer."
            )
    if not doc.get("custom_sarathi_bom"):
        return
    bom = frappe.get_doc("BOM", doc.custom_sarathi_bom)
    if bom.company != doc.company or bom.get("custom_sarathi_project") != doc.name:
        frappe.throw(
            "The main BOM must be explicitly assigned to this project and organization."
        )
    if bom.docstatus != 1 or not bom.is_active:
        frappe.throw("Select an active, submitted main BOM.")


def validate_bom(doc, method=None):
    project_name = doc.get("custom_sarathi_project")
    if not project_name:
        return
    project = frappe.get_doc("Project", project_name)
    if doc.company != project.company:
        frappe.throw("The BOM and project must belong to the same organization.")
    before = doc.get_doc_before_save()
    if (
        before
        and before.get("custom_sarathi_project")
        and before.custom_sarathi_project != project_name
    ):
        frappe.throw(
            "A project BOM cannot be reassigned. Create a separate BOM for the new project."
        )
    if doc.docstatus == 2 and project.get("custom_sarathi_bom") == doc.name:
        frappe.throw(
            "Select a replacement main BOM on the Project before cancelling its current BOM."
        )


def on_bom_submit(doc, method=None):
    if doc.get("custom_sarathi_project"):
        # Serialize concurrent BOM submissions for the same project.
        frappe.db.get_value(
            "Project", doc.custom_sarathi_project, "name", for_update=True
        )
        if not frappe.db.get_value(
            "Project", doc.custom_sarathi_project, "custom_sarathi_bom"
        ):
            frappe.db.set_value(
                "Project", doc.custom_sarathi_project, "custom_sarathi_bom", doc.name
            )
    notify_dashboard(doc)


def allowed_project_bom(candidate, main_bom, project):
    """Allow structurally linked subassemblies; never another project's BOM."""
    queue, visited = [main_bom], set()
    while queue:
        name = queue.pop()
        if not name or name in visited:
            continue
        visited.add(name)
        if len(visited) > 1000:
            frappe.throw("BOM tree exceeds supported validation size")
        bom = frappe.db.get_value(
            "BOM",
            name,
            ["custom_sarathi_project", "docstatus", "is_active"],
            as_dict=True,
        )
        if not bom or bom.custom_sarathi_project not in (None, "", project):
            continue
        if name == candidate:
            return bom.docstatus == 1 and bool(bom.is_active)
        queue += frappe.get_all("BOM Item", filters={"parent": name}, pluck="bom_no")
        if frappe.get_meta("BOM Operation").has_field("bom_no"):
            queue += frappe.get_all(
                "BOM Operation", filters={"parent": name}, pluck="bom_no"
            )
    return False


def validate_item_projects(doc):
    header_project = doc.get("project")
    for row in doc.get("items") or []:
        if header_project and not row.get("project") and hasattr(row, "project"):
            row.project = header_project
        name = row.get("project") or header_project
        if not name:
            continue
        project = frappe.get_doc("Project", name)
        if doc.get("company") and project.company != doc.company:
            frappe.throw("Every project item must match the document organization")
        if (
            doc.doctype in ("Sales Order", "Delivery Note", "Sales Invoice")
            and project.customer
            and project.customer != doc.get("customer")
        ):
            frappe.throw("Every project item must match the document customer")
        if (
            doc.get("work_order")
            and frappe.db.get_value("Work Order", doc.work_order, "project") != name
        ):
            frappe.throw("Stock item Project must match the linked Work Order")


def validate_transaction(doc, method=None):
    validate_item_projects(doc)
    project_name = doc.get("project")
    if doc.get("work_order"):
        wo = frappe.get_doc("Work Order", doc.work_order)
        if project_name and project_name != wo.project:
            frappe.throw("Project does not match the linked Work Order.")
        if doc.get("company") and wo.company != doc.company:
            frappe.throw("Organization does not match the linked Work Order.")
        project_name = wo.project
        if doc.meta.has_field("project"):
            doc.project = project_name
    if not project_name:
        return
    project = frappe.get_doc("Project", project_name)
    if doc.get("company") and doc.company != project.company:
        frappe.throw("The document and project must belong to the same organization.")
    if (
        doc.doctype == "Sales Order"
        and project.customer
        and doc.customer != project.customer
    ):
        frappe.throw("The Sales Order customer must match the Project customer.")
    if doc.doctype == "Work Order":
        if doc.sales_order:
            order = frappe.get_doc("Sales Order", doc.sales_order)
            if order.company != project.company or (
                project.customer and order.customer != project.customer
            ):
                frappe.throw(
                    "The Work Order's Sales Order must match the project's organization and customer."
                )
        bom_project = (
            frappe.db.get_value("BOM", doc.bom_no, "custom_sarathi_project")
            if doc.bom_no
            else None
        )
        if bom_project and bom_project != project.name:
            frappe.throw("This BOM belongs to another project.")
        before = doc.get_doc_before_save()
        changing_plan = (
            doc.is_new()
            or not before
            or before.bom_no != doc.bom_no
            or before.project != doc.project
        )
        if project.get("custom_sarathi_manufacturing") and changing_plan:
            if not allowed_project_bom(
                doc.bom_no, project.get("custom_sarathi_bom"), project.name
            ):
                frappe.throw(
                    "Use the project's current main BOM or an active linked subassembly BOM for a new Work Order."
                )


def notify_dashboard(doc=None, method=None):
    # Send an invalidation signal so every viewer fetches live data immediately.
    try:
        doctype = getattr(doc, "doctype", "") if doc else ""
        docname = getattr(doc, "name", "") if doc else ""
        payload = {"doctype": doctype, "name": docname}

        # 1. Standard frappe realtime publication (immediate and after commit to room 'all')
        try:
            frappe.publish_realtime(
                "sarathi_dashboard_changed",
                message=payload,
                room="all",
                after_commit=False,
            )
            frappe.publish_realtime(
                "sarathi_dashboard_changed",
                message=payload,
                room="all",
                after_commit=True,
            )
        except Exception:
            pass

        # 2. Publish directly via Redis pub-sub with room="all" so node socketio emits to all connected Desk clients
        try:
            from frappe.utils.background_jobs import get_redis_connection_without_auth

            r = get_redis_connection_without_auth()
            site = (
                getattr(getattr(frappe, "local", None), "site", "frontend")
                or "frontend"
            )
            r.publish(
                "events",
                frappe.as_json(
                    {
                        "event": "sarathi_dashboard_changed",
                        "message": payload,
                        "room": "all",
                        "namespace": site,
                    }
                ),
            )
        except Exception:
            pass
    except Exception:
        pass
