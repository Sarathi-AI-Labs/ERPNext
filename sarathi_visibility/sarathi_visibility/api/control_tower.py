from __future__ import annotations

from typing import Any
from urllib.parse import quote

import frappe
from frappe.utils import flt, getdate, now_datetime, today

from sarathi_visibility.api.data import (
    BOP_ITEMS,
    DEFAULT_PROJECT_CODE,
    DEFAULT_PROJECT_DOC,
    ENGINEERING_COMPONENTS,
    PIPELINE_WEIGHTS,
    PROJECT_TASKS,
    RAW_STOCK_PLAN,
)
from sarathi_visibility.api.permissions import permission_payload, require_super_admin


MANUFACTURING_PROCESS_STEPS = [
    {
        "key": "item",
        "phase": "Master Setup",
        "label": "Create Product / Item",
        "doctype": "Item",
        "summary": "Raw materials, fabricated components, BOP and finished Mezzanine items.",
        "tone": "blue",
        "filters": None,
    },
    {
        "key": "warehouse",
        "phase": "Master Setup",
        "label": "Warehouse",
        "doctype": "Warehouse",
        "summary": "Raw Material, WIP, Finished Goods, Scrap, Painting and Welding stores.",
        "tone": "teal",
        "filters": None,
    },
    {
        "key": "operation",
        "phase": "Manufacturing Setup",
        "label": "Operation",
        "doctype": "Operation",
        "summary": "Cutting, Drilling, Welding, Grinding, Painting and Inspection steps.",
        "tone": "violet",
        "filters": None,
    },
    {
        "key": "workstation_type",
        "phase": "Manufacturing Setup",
        "label": "Workstation Type",
        "doctype": "Workstation Type",
        "summary": "Machine and station categories used by routing and capacity planning.",
        "tone": "orange",
        "filters": None,
    },
    {
        "key": "workstation",
        "phase": "Manufacturing Setup",
        "label": "Workstation",
        "doctype": "Workstation",
        "summary": "Shop-floor stations with live operation and work order context.",
        "tone": "green",
        "filters": None,
    },
    {
        "key": "plant_floor",
        "phase": "Manufacturing Setup",
        "label": "Plant Floor",
        "doctype": "Plant Floor",
        "summary": "Factory-floor structure for grouping production work areas.",
        "tone": "cyan",
        "filters": None,
    },
    {
        "key": "routing",
        "phase": "Engineering",
        "label": "Routing",
        "doctype": "Routing",
        "summary": "Standard operation sequence that flows into BOMs and Work Orders.",
        "tone": "blue",
        "filters": None,
    },
    {
        "key": "bom",
        "phase": "Engineering",
        "label": "BOM",
        "doctype": "BOM",
        "summary": "Material, operation and cost structure for manufactured products.",
        "tone": "teal",
        "filters": "bom_names",
    },
    {
        "key": "sales_order",
        "phase": "Planning",
        "label": "Create Order",
        "doctype": "Sales Order",
        "summary": "Customer order reference connected to the Mezzanine project.",
        "tone": "violet",
        "filters": "project",
    },
    {
        "key": "production_plan",
        "phase": "Planning",
        "label": "Production Plan",
        "doctype": "Production Plan",
        "summary": "Material and production planning before Work Orders.",
        "tone": "orange",
        "filters": None,
    },
    {
        "key": "material_request",
        "phase": "Planning",
        "label": "Material Request",
        "doctype": "Material Request",
        "summary": "Purchase or transfer demand generated for shortages.",
        "tone": "red",
        "filters": None,
    },
    {
        "key": "work_order",
        "phase": "Execution",
        "label": "Work Order",
        "doctype": "Work Order",
        "summary": "Manufacturing controller for product quantity, BOM and warehouses.",
        "tone": "green",
        "filters": "project",
    },
    {
        "key": "pick_list",
        "phase": "Execution",
        "label": "Pick List",
        "doctype": "Pick List",
        "summary": "Pick raw material from warehouse for manufacturing transfer.",
        "tone": "cyan",
        "filters": None,
    },
    {
        "key": "stock_entry",
        "phase": "Inventory Flow",
        "label": "Stock Entry",
        "doctype": "Stock Entry",
        "summary": "Receipt, transfer to WIP, manufacture, scrap and final stock movement.",
        "tone": "blue",
        "filters": "work_order",
    },
    {
        "key": "job_card",
        "phase": "Execution",
        "label": "Job Card",
        "doctype": "Job Card",
        "summary": "Live operation progress, workstation time and completed quantity.",
        "tone": "teal",
        "filters": "work_order",
    },
]


def envelope(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "permission": permission_payload(),
        "generated_at": now_datetime().isoformat(),
    }


def doctype_exists(doctype: str) -> bool:
    return bool(frappe.db.exists("DocType", doctype))


def has_field(doctype: str, fieldname: str) -> bool:
    if fieldname in {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parenttype", "parentfield"}:
        return True
    if not doctype_exists(doctype):
        return False
    return bool(frappe.get_meta(doctype).has_field(fieldname))


def safe_fields(doctype: str, fields: list[str]) -> list[str]:
    return [field for field in fields if has_field(doctype, field)]


def get_all_safe(
    doctype: str,
    fields: list[str],
    filters: dict | list | None = None,
    order_by: str | None = None,
    limit_page_length: int = 50,
) -> list[dict[str, Any]]:
    if not doctype_exists(doctype):
        return []
    return frappe.get_all(
        doctype,
        fields=safe_fields(doctype, fields) or ["name"],
        filters=filters,
        order_by=order_by,
        limit_page_length=limit_page_length,
    )


def count_safe(doctype: str, filters: dict | list | None = None) -> int:
    if not doctype_exists(doctype):
        return 0
    return frappe.db.count(doctype, filters=filters)


FORM_WRAPPER_DOCTYPES = {"Project", "Company"}
FORM_LAYOUT_FIELDS = {"Tab Break", "Section Break", "Column Break"}
FORM_UNSUPPORTED_FIELDS = {"Button", "HTML", "Image", "Fold"}
FORM_LINK_OPTION_LIMIT = 200


def split_select_options(options: str | None) -> list[str]:
    return [row.strip() for row in (options or "").splitlines() if row.strip()]


def get_link_options(doctype: str | None) -> list[dict[str, Any]]:
    if not doctype or not doctype_exists(doctype):
        return []
    if not frappe.has_permission(doctype, "read"):
        return []

    title_field = frappe.get_meta(doctype).title_field
    fields = ["name"]
    if title_field and title_field != "name" and has_field(doctype, title_field):
        fields.append(title_field)

    try:
        rows = frappe.get_all(
            doctype,
            fields=fields,
            order_by="modified desc",
            limit_page_length=FORM_LINK_OPTION_LIMIT,
        )
    except Exception:
        return []

    options = []
    for row in rows:
        label = row.get(title_field) if title_field and title_field in row else row.get("name")
        options.append({"value": row.get("name"), "label": label or row.get("name")})
    return options


def form_field_payload(field: Any) -> dict[str, Any] | None:
    fieldtype = field.fieldtype
    if field.hidden or fieldtype in FORM_UNSUPPORTED_FIELDS:
        return None

    payload = {
        "fieldname": field.fieldname,
        "label": field.label or field.fieldname or fieldtype,
        "fieldtype": fieldtype,
        "options": field.options,
        "reqd": bool(field.reqd),
        "read_only": bool(field.read_only),
        "description": field.description,
        "default": field.default,
        "depends_on": field.depends_on,
        "mandatory_depends_on": field.mandatory_depends_on,
        "collapsible": bool(field.collapsible),
        "collapsible_depends_on": field.collapsible_depends_on,
    }

    if fieldtype == "Select":
        payload["select_options"] = split_select_options(field.options)
    elif fieldtype == "Link":
        payload["link_doctype"] = field.options
        payload["link_options"] = get_link_options(field.options)
    elif fieldtype == "Table":
        payload["child_doctype"] = field.options

    return payload


def form_wrapper_schema(doctype: str) -> dict[str, Any]:
    if doctype not in FORM_WRAPPER_DOCTYPES:
        frappe.throw("This wrapper only supports Project and Company forms.")
    if not doctype_exists(doctype):
        frappe.throw(f"{doctype} is not available in ERPNext.")

    meta = frappe.get_meta(doctype)
    fields = []
    for field in meta.fields:
        payload = form_field_payload(field)
        if payload:
            fields.append(payload)

    return {
        "doctype": doctype,
        "title": meta.name,
        "fields": fields,
        "layout_fields": list(FORM_LAYOUT_FIELDS),
    }


def route_slug(doctype: str) -> str:
    return doctype.lower().replace(" ", "-")


def resolve_project(project: str | None = None, company: str | None = None) -> dict[str, Any]:
    if project and doctype_exists("Project") and frappe.db.exists("Project", project):
        return project_payload(project)

    if project and doctype_exists("Project") and has_field("Project", "project_name"):
        project_name = frappe.db.get_value("Project", {"project_name": project}, "name")
        if project_name:
            return project_payload(project_name)

    if doctype_exists("Project") and frappe.db.exists("Project", DEFAULT_PROJECT_DOC):
        return project_payload(DEFAULT_PROJECT_DOC)

    filters = {"company": company} if company and has_field("Project", "company") else None
    latest = get_all_safe(
        "Project",
        ["name", "modified"],
        filters=filters,
        order_by="modified desc",
        limit_page_length=1,
    )
    if latest:
        return project_payload(latest[0]["name"])

    candidates = get_all_safe(
        "Project",
        ["name", "project_name", "status", "percent_complete", "customer"],
        filters=[["Project", "project_name", "like", f"%{DEFAULT_PROJECT_CODE}%"]],
        limit_page_length=1,
    )
    if candidates:
        return project_payload(candidates[0]["name"])

    return {
        "name": DEFAULT_PROJECT_DOC,
        "project_name": DEFAULT_PROJECT_CODE,
        "display_name": DEFAULT_PROJECT_CODE,
        "status": "Not configured",
        "percent_complete": 0,
        "customer": None,
        "sales_order": "",
        "exists": False,
        "source": "Blueprint default",
    }


def project_payload(project_name: str) -> dict[str, Any]:
    fields = [
        "name",
        "project_name",
        "status",
        "percent_complete",
        "customer",
        "expected_start_date",
        "expected_end_date",
        "company",
        "production_item",
        "item_code",
        "item",
        "custom_production_item",
        "custom_item_code",
        "custom_item",
    ]
    values = frappe.db.get_value("Project", project_name, safe_fields("Project", fields), as_dict=True) or {}
    return {
        "name": values.get("name", project_name),
        "project_name": values.get("project_name") or DEFAULT_PROJECT_CODE,
        "display_name": values.get("project_name") or values.get("name") or DEFAULT_PROJECT_CODE,
        "status": values.get("status") or "Open",
        "percent_complete": flt(values.get("percent_complete")),
        "customer": values.get("customer"),
        "company": values.get("company"),
        "expected_start_date": values.get("expected_start_date"),
        "expected_end_date": values.get("expected_end_date"),
        "sales_order": find_sales_order(project_name),
        "exists": True,
        "source": "ERPNext Project",
        "production_item": values.get("production_item"),
        "item_code": values.get("item_code"),
        "item": values.get("item"),
        "custom_production_item": values.get("custom_production_item"),
        "custom_item_code": values.get("custom_item_code"),
        "custom_item": values.get("custom_item"),
    }


def apply_production_completion(
    project_doc: dict[str, Any],
    work_orders: list[dict[str, Any]],
    job_cards: list[dict[str, Any]],
    finished_goods: list[dict[str, Any]],
) -> dict[str, Any]:
    project_doc = dict(project_doc)
    project_doc["erp_status"] = project_doc.get("status") or "Open"
    project_doc["erp_percent_complete"] = flt(project_doc.get("percent_complete"))

    has_work_orders = bool(work_orders)
    all_work_orders_completed = has_work_orders and all(row.get("status") == "Completed" for row in work_orders)
    all_job_cards_completed = bool(job_cards) and all(row.get("status") == "Completed" for row in job_cards)
    finished_qty = sum(flt(row.get("balance_qty")) for row in finished_goods)

    if all_work_orders_completed and all_job_cards_completed and finished_qty > 0:
        project_doc["status"] = "Completed"
        project_doc["percent_complete"] = 100
        project_doc["status_source"] = "Computed from completed Work Order, Job Cards and Finished Goods"
    else:
        project_doc["status_source"] = "ERPNext Project"

    return project_doc


def get_project_cards(company: str | None = None) -> list[dict[str, Any]]:
    if not doctype_exists("Project"):
        return []

    filters = {"company": company} if company and has_field("Project", "company") else None
    rows = get_all_safe(
        "Project",
        ["name", "project_name", "status", "percent_complete", "customer", "company", "expected_start_date", "expected_end_date", "modified"],
        filters=filters,
        order_by="modified desc",
        limit_page_length=200,
    )

    projects = []
    for row in rows:
        project_doc = project_payload(row["name"])
        work_orders = get_work_orders_for_project(project_doc["name"])
        job_cards = get_job_cards_for_work_orders(work_orders)
        finished_goods = get_finished_goods_rows(work_orders)
        boms = get_bom_rows(project_doc, work_orders)
        materials = get_material_rows(project_doc["name"], work_orders, boms)
        project_doc = apply_production_completion(project_doc, work_orders, job_cards, finished_goods)
        project_doc.update(
            {
                "bom_count": len(boms),
                "work_order_count": len(work_orders),
                "job_card_count": len(job_cards),
                "completed_job_cards": len([card for card in job_cards if card.get("status") == "Completed"]),
                "finished_goods_qty": sum(flt(item.get("balance_qty")) for item in finished_goods),
                "material_count": len(materials),
                "shortage_qty": sum(flt(item.get("shortage_qty")) for item in materials),
                "modified": row.get("modified"),
                "url": f"/desk/sarathicontroltower?project={quote(str(project_doc['name']))}",
            }
        )
        projects.append(project_doc)

    return projects


def get_company_options(selected_company: str | None = None) -> list[dict[str, Any]]:
    companies: dict[str, dict[str, Any]] = {}

    company_rows = get_all_safe(
        "Company",
        ["name", "company_name", "abbr"],
        order_by="name asc",
        limit_page_length=500,
    )
    for row in company_rows:
        name = row.get("name")
        if name:
            companies[name] = {
                "name": name,
                "company_name": row.get("company_name") or name,
                "abbr": row.get("abbr"),
                "project_count": 0,
                "selected": name == selected_company,
            }

    if companies and doctype_exists("Project") and has_field("Project", "company"):
        rows = frappe.db.sql(
            """
            select company, count(name) as project_count
            from `tabProject`
            where ifnull(company, '') != ''
            group by company
            order by company asc
            """,
            as_dict=True,
        )
        for row in rows:
            name = row.get("company")
            if not name:
                continue
            if name in companies:
                companies[name]["project_count"] = row.get("project_count") or 0
                companies[name]["selected"] = name == selected_company

    for company in companies.values():
        projects = get_project_cards(company.get("name"))
        summary = organization_summary(company.get("name"), projects)
        company.update(
            {
                "project_count": len(projects),
                "active_projects": summary.get("active_projects"),
                "completed_projects": summary.get("completed_projects"),
                "active_work_orders": summary.get("active_work_orders"),
                "open_job_cards": summary.get("open_job_cards"),
                "shortages": summary.get("shortages"),
                "finished_goods": summary.get("finished_goods"),
            }
        )

    return sorted(companies.values(), key=lambda row: row.get("company_name") or row.get("name") or "")


def get_default_company_from_erp() -> str | None:
    companies = get_company_options()
    if not companies:
        return None

    if doctype_exists("Project") and has_field("Project", "company"):
        project_company = frappe.db.get_value("Project", {"name": DEFAULT_PROJECT_DOC}, "company")
        if project_company and any(row.get("name") == project_company for row in companies):
            return project_company

    with_projects = [row for row in companies if flt(row.get("project_count")) > 0]
    if with_projects:
        return with_projects[0].get("name")

    return companies[0].get("name")


def find_sales_order(project_name: str) -> str:
    if not doctype_exists("Sales Order") or not has_field("Sales Order", "project"):
        return ""

    sales_order = frappe.db.get_value("Sales Order", {"project": project_name}, "name")
    return sales_order or ""


def get_project_tasks(project_name: str) -> list[dict[str, Any]]:
    if not doctype_exists("Task") or not has_field("Task", "project"):
        return [{**task, "status": "Not configured", "progress": 0, "source": "Blueprint"} for task in PROJECT_TASKS]

    tasks = get_all_safe(
        "Task",
        ["name", "subject", "status", "progress", "exp_start_date", "exp_end_date", "project"],
        filters={"project": project_name},
        order_by="exp_start_date asc, creation asc",
        limit_page_length=200,
    )
    if tasks:
        for task in tasks:
            task["source"] = "ERPNext Task"
            task["is_delayed"] = is_delayed(task.get("exp_end_date"), task.get("status"))
        return tasks

    return [{**task, "status": "No ERP task", "progress": 0, "source": "Blueprint"} for task in PROJECT_TASKS]


def is_delayed(end_date: Any, status: str | None) -> bool:
    if not end_date:
        return False
    if status in {"Completed", "Cancelled"}:
        return False
    return getdate(end_date) < getdate(today())


def get_pipeline(tasks: list[dict[str, Any]], project: dict[str, Any]) -> list[dict[str, Any]]:
    by_subject = {task.get("subject"): task for task in tasks}
    complete_from_project = flt(project.get("percent_complete"))
    project_completed = project.get("status") == "Completed" or complete_from_project >= 100
    pipeline = []

    for stage in get_pipeline_weights(project.get("name")):
        task = by_subject.get(stage["task"])
        if task:
            status = task.get("status") or "Open"
            progress = 100 if status == "Completed" or project_completed else flt(task.get("progress"))
            if project_completed and status != "Completed":
                status = "Completed"
        else:
            status = "Completed" if project_completed else "No ERP task"
            progress = 100 if project_completed else complete_from_project if stage["stage"] == "Completion" else 0
        pipeline.append(
            {
                **stage,
                "status": status,
                "progress": min(max(progress, 0), 100),
                "task": task,
            }
        )

    return pipeline


def get_pipeline_weights(project_name: str | None) -> list[dict[str, Any]]:
    if not project_name or not doctype_exists("Sarathi Project Controller"):
        return PIPELINE_WEIGHTS

    controller = frappe.db.get_value(
        "Sarathi Project Controller",
        {"project": project_name},
        ["pipeline_weights_json"],
        as_dict=True,
    )
    if not controller or not controller.get("pipeline_weights_json"):
        return PIPELINE_WEIGHTS

    try:
        weights = frappe.parse_json(controller.pipeline_weights_json)
    except Exception:
        return PIPELINE_WEIGHTS

    if not isinstance(weights, list):
        return PIPELINE_WEIGHTS

    normalized = []
    for row in weights:
        if not isinstance(row, dict) or not row.get("stage"):
            continue
        normalized.append(
            {
                "stage": row.get("stage"),
                "weight": flt(row.get("weight")),
                "task": row.get("task") or row.get("stage"),
            }
        )
    return normalized or PIPELINE_WEIGHTS


def get_work_orders_for_project(project_name: str) -> list[dict[str, Any]]:
    if not doctype_exists("Work Order") or not has_field("Work Order", "project"):
        return []

    fields = [
        "name",
        "project",
        "production_item",
        "item_name",
        "bom_no",
        "qty",
        "stock_uom",
        "produced_qty",
        "material_transferred_for_manufacturing",
        "status",
        "wip_warehouse",
        "fg_warehouse",
        "source_warehouse",
        "scrap_warehouse",
        "planned_start_date",
        "planned_end_date",
        "modified",
    ]
    work_orders = get_all_safe(
        "Work Order",
        fields,
        filters={"project": project_name},
        order_by="modified desc",
        limit_page_length=100,
    )
    for row in work_orders:
        qty = flt(row.get("qty"))
        row["completion_percent"] = round((flt(row.get("produced_qty")) / qty) * 100, 2) if qty else 0
    return work_orders


def get_job_cards_for_work_orders(work_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not work_orders or not doctype_exists("Job Card") or not has_field("Job Card", "work_order"):
        return []

    names = [wo["name"] for wo in work_orders]
    fields = [
        "name",
        "work_order",
        "operation",
        "workstation",
        "status",
        "for_quantity",
        "total_completed_qty",
        "total_time_in_mins",
        "actual_start_date",
        "actual_end_date",
        "modified",
    ]
    cards = get_all_safe(
        "Job Card",
        fields,
        filters=[["Job Card", "work_order", "in", names]],
        order_by="modified desc",
        limit_page_length=300,
    )
    for card in cards:
        qty = flt(card.get("for_quantity"))
        completed = flt(card.get("total_completed_qty"))
        card["completion_percent"] = round((completed / qty) * 100, 2) if qty else (100 if card.get("status") == "Completed" else 0)
    return cards


def get_material_rows(project_name: str, work_orders: list[dict[str, Any]], boms: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    custom_rows = get_all_safe(
        "Sarathi Material Requirement",
        [
            "name",
            "item_code",
            "item_name",
            "bom",
            "required_qty",
            "available_qty",
            "reserved_qty",
            "transferred_qty",
            "consumed_qty",
            "returned_qty",
            "shortage_qty",
            "warehouse",
            "purchase_status",
            "status",
        ],
        filters={"project": project_name},
        order_by="idx asc, modified desc",
        limit_page_length=300,
    )
    if custom_rows:
        for row in custom_rows:
            row["source"] = "Sarathi Material Requirement"
        return custom_rows

    bom_items = get_bom_material_rows(work_orders, boms)
    if bom_items:
        return bom_items

    return [
        {
            "item_code": None,
            "item_name": row["material"],
            "cutting_size": row["cutting_size"],
            "required_qty": row["qty"],
            "available_qty": None,
            "reserved_qty": None,
            "transferred_qty": None,
            "consumed_qty": None,
            "returned_qty": None,
            "shortage_qty": None,
            "warehouse": None,
            "purchase_status": "Not configured",
            "source": "Mezzanine engineering source",
        }
        for row in ENGINEERING_COMPONENTS
    ]


def get_bom_material_rows(work_orders: list[dict[str, Any]], boms: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if not doctype_exists("BOM Item"):
        return []

    bom_qty = {wo.get("bom_no"): flt(wo.get("qty")) or 1 for wo in work_orders if wo.get("bom_no")}
    for bom in boms or []:
        if bom.get("name") and bom.get("name") not in bom_qty:
            bom_qty[bom.get("name")] = flt(bom.get("quantity")) or 1
    if not bom_qty:
        return []

    items = get_all_safe(
        "BOM Item",
        ["parent", "item_code", "item_name", "qty", "stock_uom", "source_warehouse"],
        filters=[["BOM Item", "parent", "in", list(bom_qty)]],
        limit_page_length=500,
    )
    totals: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in items:
        parent = row.get("parent")
        item_code = row.get("item_code")
        warehouse = row.get("source_warehouse")
        key = (parent, item_code, warehouse)
        if key not in totals:
            totals[key] = {
                "item_code": item_code,
                "item_name": row.get("item_name"),
                "bom": parent,
                "parent": parent,
                "required_qty": 0,
                "available_qty": get_available_qty(item_code, warehouse),
                "reserved_qty": None,
                "transferred_qty": None,
                "consumed_qty": None,
                "returned_qty": None,
                "warehouse": warehouse,
                "purchase_status": "Check shortage",
                "source": "BOM Item",
            }
        totals[key]["required_qty"] += flt(row.get("qty")) * bom_qty.get(parent, 1)

    for row in totals.values():
        available = flt(row.get("available_qty"))
        required = flt(row.get("required_qty"))
        row["shortage_qty"] = max(required - available, 0)
        if not row["shortage_qty"]:
            row["purchase_status"] = "Not Required"
    return list(totals.values())


def get_available_qty(item_code: str | None, warehouse: str | None = None) -> float | None:
    if not item_code or not doctype_exists("Bin"):
        return None
    conditions = ["item_code = %(item_code)s"]
    values: dict[str, Any] = {"item_code": item_code}
    if warehouse:
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = warehouse

    result = frappe.db.sql(
        f"""
        select sum(actual_qty)
        from `tabBin`
        where {" and ".join(conditions)}
        """,
        values,
    )
    return flt(result[0][0]) if result else 0


def get_project_item_codes(project_doc: dict[str, Any], work_orders: list[dict[str, Any]]) -> list[str]:
    item_codes: set[str] = {
        row.get("production_item")
        for row in work_orders
        if row.get("production_item")
    }

    for fieldname in ["production_item", "item_code", "item", "custom_production_item", "custom_item_code", "custom_item"]:
        if project_doc.get(fieldname):
            item_codes.add(project_doc.get(fieldname))

    sales_orders = []
    if project_doc.get("sales_order"):
        sales_orders.append(project_doc.get("sales_order"))
    if doctype_exists("Sales Order") and has_field("Sales Order", "project"):
        sales_orders.extend(
            row.get("name")
            for row in get_all_safe(
                "Sales Order",
                ["name"],
                filters={"project": project_doc.get("name")},
                limit_page_length=100,
            )
            if row.get("name")
        )

    if sales_orders and doctype_exists("Sales Order Item") and has_field("Sales Order Item", "item_code"):
        item_codes.update(
            row.get("item_code")
            for row in get_all_safe(
                "Sales Order Item",
                ["item_code"],
                filters=[["Sales Order Item", "parent", "in", list(set(sales_orders))]],
                limit_page_length=500,
            )
            if row.get("item_code")
        )

    return sorted(item_codes)


def append_linked_bom_names(
    names: set[str],
    doctype: str,
    project_name: str,
    bom_field: str = "bom",
    project_field: str = "project",
) -> None:
    if not doctype_exists(doctype) or not has_field(doctype, bom_field) or not has_field(doctype, project_field):
        return

    rows = get_all_safe(
        doctype,
        [bom_field],
        filters={project_field: project_name},
        order_by="modified desc",
        limit_page_length=300,
    )
    names.update(row.get(bom_field) for row in rows if row.get(bom_field))


def get_project_bom_names(project_doc: dict[str, Any], work_orders: list[dict[str, Any]]) -> list[str]:
    names: set[str] = {wo.get("bom_no") for wo in work_orders if wo.get("bom_no")}
    if not doctype_exists("BOM"):
        return sorted(names)

    project_refs = {
        project_doc.get("name"),
        project_doc.get("project_name"),
        project_doc.get("display_name"),
    }
    project_refs = {row for row in project_refs if row}
    for fieldname in ["project", "custom_project", "sarathi_project", "project_name"]:
        if has_field("BOM", fieldname) and project_refs:
            rows = get_all_safe(
                "BOM",
                ["name"],
                filters=[["BOM", fieldname, "in", list(project_refs)]],
                order_by="modified desc",
                limit_page_length=300,
            )
            names.update(row.get("name") for row in rows if row.get("name"))

    append_linked_bom_names(names, "Sarathi Material Requirement", project_doc.get("name"))
    append_linked_bom_names(names, "Sarathi Production Tracker", project_doc.get("name"))

    item_codes = get_project_item_codes(project_doc, work_orders)
    if item_codes and has_field("BOM", "item"):
        filters: list[list[Any]] = [["BOM", "item", "in", item_codes]]
        if project_doc.get("company") and has_field("BOM", "company"):
            filters.append(["BOM", "company", "=", project_doc.get("company")])
        rows = get_all_safe(
            "BOM",
            ["name"],
            filters=filters,
            order_by="modified desc",
            limit_page_length=300,
        )
        names.update(row.get("name") for row in rows if row.get("name"))

    return sorted(names)


def get_all_work_orders(company: str | None = None) -> list[dict[str, Any]]:
    if not doctype_exists("Work Order"):
        return []
    filters = [["Work Order", "company", "=", company]] if company and has_field("Work Order", "company") else None
    fields = [
        "name",
        "production_item",
        "item_name",
        "status",
        "qty",
        "produced_qty",
        "bom_no",
        "project",
        "company",
        "planned_start_date",
        "planned_end_date",
        "actual_start_date",
        "actual_end_date",
        "docstatus",
        "modified",
    ]
    return get_all_safe("Work Order", fields, filters=filters, order_by="modified desc", limit_page_length=200)


def get_all_bom_rows(
    company: str | None = None,
    project_doc: dict[str, Any] | None = None,
    work_orders: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if not doctype_exists("BOM"):
        return []

    fields = [
        "name",
        "item",
        "item_name",
        "company",
        "quantity",
        "uom",
        "routing",
        "with_operations",
        "total_cost",
        "is_active",
        "is_default",
        "docstatus",
        "modified",
    ]
    for opt in ["project", "custom_project", "sarathi_project", "project_name", "product_name", "custom_product_name"]:
        if has_field("BOM", opt) and opt not in fields:
            fields.append(opt)

    filters: list[list[Any]] = []
    if company and has_field("BOM", "company"):
        filters.append(["BOM", "company", "=", company])

    boms = get_all_safe(
        "BOM",
        fields,
        filters=filters if filters else None,
        order_by="modified desc",
        limit_page_length=200,
    )

    wo_map: dict[str, str] = {}
    if doctype_exists("Work Order") and has_field("Work Order", "bom_no") and has_field("Work Order", "project"):
        wo_rows = get_all_safe("Work Order", ["bom_no", "project"], limit_page_length=500)
        for wo in wo_rows:
            if wo.get("bom_no") and wo.get("project") and wo.get("bom_no") not in wo_map:
                wo_map[wo.get("bom_no")] = wo.get("project")

    bom_names = [row.get("name") for row in boms if row.get("name")]
    component_counts = get_component_counts(bom_names)

    project_name = project_doc.get("name") if project_doc else None
    linked_boms = set(get_project_bom_names(project_doc, work_orders or [])) if project_doc else set()

    for bom in boms:
        bom["component_count"] = component_counts.get(bom["name"], 0)
        bom["source"] = "ERPNext BOM"
        if not bom.get("project"):
            bom["project"] = (
                bom.get("custom_project")
                or bom.get("sarathi_project")
                or bom.get("project_name")
                or wo_map.get(bom.get("name"), "")
            )
        bom["is_current_project"] = bool(
            project_name
            and (
                bom.get("project") == project_name
                or bom.get("name") in linked_boms
            )
        )

    boms.sort(key=lambda b: (not b.get("is_current_project", False), b.get("modified") or ""), reverse=False)
    return boms


def get_bom_rows(project_doc: dict[str, Any], work_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bom_names = get_project_bom_names(project_doc, work_orders)
    if not bom_names or not doctype_exists("BOM"):
        return []

    fields = [
        "name",
        "item",
        "item_name",
        "company",
        "quantity",
        "uom",
        "routing",
        "with_operations",
        "total_cost",
        "is_active",
        "is_default",
        "docstatus",
        "modified",
    ]
    for opt in ["project", "custom_project", "sarathi_project", "project_name", "product_name", "custom_product_name"]:
        if has_field("BOM", opt) and opt not in fields:
            fields.append(opt)

    boms = get_all_safe(
        "BOM",
        fields,
        filters=[["BOM", "name", "in", bom_names]],
        order_by="modified desc",
        limit_page_length=100,
    )
    component_counts = get_component_counts(bom_names)
    for bom in boms:
        bom["component_count"] = component_counts.get(bom["name"], 0)
        bom["source"] = "ERPNext BOM"
        if not bom.get("project"):
            bom["project"] = project_doc.get("name") or ""
        bom["is_current_project"] = True
    return boms


def get_bom_operation_rows(boms: list[dict[str, Any]], job_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bom_names = [row.get("name") for row in boms if row.get("name")]
    rows = []
    if bom_names and doctype_exists("BOM Operation"):
        rows = get_all_safe(
            "BOM Operation",
            ["parent", "operation", "workstation", "workstation_type", "time_in_mins", "hour_rate", "operating_cost", "idx"],
            filters=[["BOM Operation", "parent", "in", bom_names]],
            order_by="idx asc",
            limit_page_length=300,
        )

    if not rows and job_cards:
        rows = [
            {
                "parent": row.get("work_order"),
                "operation": row.get("operation"),
                "workstation": row.get("workstation"),
                "workstation_type": row.get("workstation_type"),
                "time_in_mins": row.get("total_time_in_mins"),
                "status": row.get("status"),
                "source": "Job Card",
            }
            for row in job_cards
        ]

    for row in rows:
        row["source"] = row.get("source") or "BOM Operation"
    return rows


def get_component_counts(bom_names: list[str]) -> dict[str, int]:
    if not bom_names or not doctype_exists("BOM Item"):
        return {}
    rows = frappe.db.sql(
        """
        select parent, count(name)
        from `tabBOM Item`
        where parent in %(bom_names)s
        group by parent
        """,
        {"bom_names": tuple(bom_names)},
    )
    return {row[0]: row[1] for row in rows}


def get_workstation_rows(project_name: str, job_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_station = {}
    for card in job_cards:
        station = card.get("workstation")
        if station and station not in latest_by_station:
            latest_by_station[station] = card

    rows = get_all_safe(
        "Workstation",
        ["name", "workstation_name", "workstation_type", "production_capacity", "warehouse", "status", "disabled"],
        limit_page_length=200,
    )

    if not rows:
        return [
            {"name": name, "workstation_type": kind, "status": "Not configured", "source": "Blueprint"}
            for name, kind in [
                ("Cutting Workstation", "Cutting Machine"),
                ("Drilling Workstation", "Drilling Machine"),
                ("Welding Workstation", "Welding Station"),
                ("Grinding Workstation", "Grinding Station"),
                ("Painting Workstation", "Painting Machine"),
                ("Inspection Workstation", "Inspection Station"),
            ]
        ]

    if latest_by_station:
        rows = [row for row in rows if row.get("name") in latest_by_station]

    for row in rows:
        current = latest_by_station.get(row.get("name"))
        row["current_work_order"] = current.get("work_order") if current else None
        row["current_operation"] = current.get("operation") if current else None
        row["live_status"] = "Running" if current and current.get("status") == "Work In Progress" else status_from_workstation(row)
        row["source"] = "ERPNext Workstation"
    return rows


def status_from_workstation(row: dict[str, Any]) -> str:
    if row.get("disabled"):
        return "Disabled"
    return row.get("status") or "Available"


def get_stock_entry_rows(project_name: str, work_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not doctype_exists("Stock Entry"):
        return []

    filters: dict | list | None = None
    if has_field("Stock Entry", "project"):
        filters = {"project": project_name}
    elif work_orders and has_field("Stock Entry", "work_order"):
        filters = [["Stock Entry", "work_order", "in", [wo["name"] for wo in work_orders]]]
    else:
        return []

    return get_all_safe(
        "Stock Entry",
        ["name", "purpose", "work_order", "from_warehouse", "to_warehouse", "total_outgoing_value", "total_incoming_value", "docstatus", "posting_date", "posting_time", "modified"],
        filters=filters,
        order_by="posting_date desc, posting_time desc",
        limit_page_length=100,
    )


def get_finished_goods_rows(work_orders: list[dict[str, Any]]) -> list[dict[str, Any]]:
    finished_items = sorted({wo.get("production_item") for wo in work_orders if wo.get("production_item")})
    if not finished_items:
        return []

    rows = []
    for item_code in finished_items:
        rows.append(
            {
                "item_code": item_code,
                "warehouse": "Finished Goods - PMPL",
                "balance_qty": get_available_qty(item_code, "Finished Goods - PMPL"),
                "source": "Bin",
            }
        )
    return rows


def get_live_analysis(
    project_doc: dict[str, Any],
    boms: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    job_cards: list[dict[str, Any]],
    materials: list[dict[str, Any]],
    finished_goods: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not project_doc.get("name"):
        project_doc = resolve_project(DEFAULT_PROJECT_DOC)
        if not work_orders:
            work_orders = get_work_orders_for_project(project_doc["name"])
        if not job_cards:
            job_cards = get_job_cards_for_work_orders(work_orders)
        if not boms:
            boms = get_bom_rows(project_doc, work_orders)
        if not materials:
            materials = get_material_rows(project_doc["name"], work_orders, boms)
        if not finished_goods:
            finished_goods = get_finished_goods_rows(work_orders)

    primary_bom = boms[0] if boms else {}
    primary_work_order = work_orders[0] if work_orders else {}
    primary_finished_good = finished_goods[0] if finished_goods else {}
    completed_job_cards = len([row for row in job_cards if row.get("status") == "Completed"])
    total_job_cards = len(job_cards)
    shortage = next((row for row in materials if flt(row.get("shortage_qty")) > 0), None)
    primary_alert = next((row for row in alerts if row.get("severity") == "Critical"), alerts[0] if alerts else None)

    operations_list = [row.get("operation") for row in job_cards if row.get("operation")]
    seen_ops = set()
    unique_ops = []
    for op in operations_list:
        if op not in seen_ops:
            seen_ops.add(op)
            unique_ops.append(op)
    job_ops_str = ", ".join(unique_ops) if unique_ops else "Cutting, Drilling, Welding, Grinding, Painting, Inspection"

    shortage_bom = (shortage.get("bom") if shortage else None) or (primary_bom.get("name") if primary_bom else "")
    shortage_detail = (
        f"Short by {flt(shortage.get('shortage_qty'))}" + (f" ({shortage_bom})" if shortage_bom else "")
        if shortage
        else (primary_alert.get("detail") if primary_alert else "No critical alerts")
    )

    return [
        {
            "label": "Project",
            "title": f"{project_doc.get('name')} / {project_doc.get('project_name')}",
            "value": project_doc.get("status") or "Open",
            "detail": f"Sales Reference: {project_doc.get('sales_order') or 'No sales order linked'}",
            "doctype": "Project" if project_doc.get("exists") else None,
            "name": project_doc.get("name") if project_doc.get("exists") else None,
            "status": project_doc.get("status") or "Open",
        },
        {
            "label": "BOM",
            "title": primary_bom.get("name") or "BOM not configured",
            "value": primary_bom.get("item") or "No linked BOM",
            "detail": f"{primary_bom.get('component_count', 0)} components",
            "doctype": "BOM" if primary_bom.get("name") else None,
            "name": primary_bom.get("name"),
            "status": "Submitted" if primary_bom.get("docstatus") == 1 else "Not configured",
        },
        {
            "label": "Work Order",
            "title": primary_work_order.get("name") or "Work Order not configured",
            "value": primary_work_order.get("status") or "No Work Order",
            "detail": f"{flt(primary_work_order.get('produced_qty'))} produced of {flt(primary_work_order.get('qty'))}",
            "doctype": "Work Order" if primary_work_order.get("name") else None,
            "name": primary_work_order.get("name"),
            "status": primary_work_order.get("status") or "Not configured",
        },
        {
            "label": "Job Cards",
            "title": f"{completed_job_cards} completed",
            "value": f"{completed_job_cards} / {total_job_cards}",
            "detail": job_ops_str,
            "doctype": "Job Card" if total_job_cards else None,
            "work_order": primary_work_order.get("name") if primary_work_order else (job_cards[0].get("work_order") if job_cards else None),
            "url": f"/desk/job-card?work_order={primary_work_order.get('name') or job_cards[0].get('work_order')}" if (primary_work_order.get("name") or (job_cards and job_cards[0].get("work_order"))) else "/desk/job-card",
            "status": "Completed" if total_job_cards and completed_job_cards == total_job_cards else "In Progress",
        },
        {
            "label": "Finished Goods",
            "title": primary_finished_good.get("item_code") or "Finished item not configured",
            "value": f"{flt(primary_finished_good.get('balance_qty'))} Nos",
            "detail": primary_finished_good.get("warehouse") or "Finished Goods - PMPL",
            "doctype": "Item" if primary_finished_good.get("item_code") else None,
            "name": primary_finished_good.get("item_code"),
            "status": "Available" if flt(primary_finished_good.get("balance_qty")) > 0 else "No stock",
        },
        {
            "label": "Alert",
            "title": f"{shortage.get('item_name') or shortage.get('item_code')} shortage" if shortage else "No critical shortage",
            "value": f"Short by {flt(shortage.get('shortage_qty'))}" if shortage else "0",
            "detail": shortage_detail,
            "doctype": "Item" if shortage and shortage.get("item_code") else None,
            "name": shortage.get("item_code") if shortage else None,
            "status": primary_alert.get("severity") if primary_alert else ("Critical" if shortage else "Clear"),
        },
    ]


def get_alert_rows(
    materials: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    workstations: list[dict[str, Any]],
    work_orders: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    alerts = []
    for row in materials:
        shortage = row.get("shortage_qty")
        if shortage is not None and flt(shortage) > 0:
            item_code = row.get("item_code") or ""
            item_title = (row.get("item_name") or item_code or "").strip()
            detail = f"Short by {flt(shortage)}"
            extra = []
            if row.get("bom"):
                extra.append(str(row.get("bom")))
            if row.get("project"):
                extra.append(str(row.get("project")))
            if extra:
                detail += f" ({' • '.join(extra)})"
            alerts.append({
                "type": "Shortage",
                "severity": "Critical",
                "title": item_title or item_code,
                "detail": detail,
                "doctype": "Item" if item_code else None,
                "name": item_code if item_code else None,
                "project": row.get("project"),
                "bom": row.get("bom"),
            })

    for task in tasks:
        if task.get("is_delayed"):
            detail = f"Due {task.get('exp_end_date')}"
            if task.get("project"):
                detail += f" • {task.get('project')}"
            alerts.append({
                "type": "Delay",
                "severity": "Warning",
                "title": task.get("subject"),
                "detail": detail,
                "doctype": "Task",
                "name": task.get("name"),
                "project": task.get("project"),
            })

    for wo in work_orders or []:
        if (
            wo.get("planned_end_date")
            and str(wo.get("planned_end_date"))[:10] < today()
            and wo.get("status") not in ["Completed", "Cancelled", "Closed"]
        ):
            detail = f"Due {str(wo.get('planned_end_date'))[:10]}"
            if wo.get("project"):
                detail += f" • {wo.get('project')}"
            alerts.append({
                "type": "Delay",
                "severity": "Warning",
                "title": f"WO {wo.get('name')}: {wo.get('production_item') or wo.get('item_name')}",
                "detail": detail,
                "doctype": "Work Order",
                "name": wo.get("name"),
                "project": wo.get("project"),
            })

    for station in workstations:
        if station.get("live_status") in {"Down", "Disabled"}:
            alerts.append({
                "type": "Workstation",
                "severity": "Warning",
                "title": station.get("name"),
                "detail": station.get("live_status"),
                "doctype": "Workstation",
                "name": station.get("name"),
            })

    return alerts[:25]


def get_manufacturing_process(
    project_name: str,
    work_orders: list[dict[str, Any]],
    boms: list[dict[str, Any]],
    materials: list[dict[str, Any]] | None = None,
    job_cards: list[dict[str, Any]] | None = None,
    workstations: list[dict[str, Any]] | None = None,
    stock_entries: list[dict[str, Any]] | None = None,
    bom_operations: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    materials = materials or []
    job_cards = job_cards or []
    workstations = workstations or []
    stock_entries = stock_entries or []
    bom_operations = bom_operations or []
    bom_names = [row.get("name") for row in boms if row.get("name")]
    work_order_names = [row.get("name") for row in work_orders if row.get("name")]
    project_process_rows = project_process_records(
        boms,
        materials,
        work_orders,
        job_cards,
        workstations,
        stock_entries,
        bom_operations,
    )
    steps = []

    for index, step in enumerate(MANUFACTURING_PROCESS_STEPS, start=1):
        doctype = step["doctype"]
        filters = process_filters(doctype, step.get("filters"), project_name, bom_names, work_order_names)
        installed = doctype_exists(doctype)
        count = count_safe(doctype, filters) if installed else 0
        recent = process_recent_records(doctype, filters) if installed else []
        if step["key"] in project_process_rows:
            recent = project_process_rows[step["key"]]
            count = len(recent)
        progress = process_progress(doctype, count, recent, work_orders, bom_names, work_order_names)
        status = process_status(installed, count, progress, step.get("filters"))

        steps.append(
            {
                "index": index,
                "key": step["key"],
                "phase": step["phase"],
                "label": step["label"],
                "doctype": doctype,
                "summary": step["summary"],
                "tone": step["tone"],
                "installed": installed,
                "count": count,
                "status": status,
                "progress": progress,
                "list_url": f"/app/{route_slug(doctype)}",
                "create_url": (
                    f"/app/{route_slug(doctype)}/new?sarathi_prefill=1&project={quote(str(project_name))}"
                    if step["key"] == "bom"
                    else f"/app/{route_slug(doctype)}/new"
                ),
                "recent": recent,
            }
        )

    return steps


def project_process_records(
    boms: list[dict[str, Any]],
    materials: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    job_cards: list[dict[str, Any]],
    workstations: list[dict[str, Any]],
    stock_entries: list[dict[str, Any]],
    bom_operations: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    records: dict[str, list[dict[str, Any]]] = {}

    item_rows = []
    seen_items = set()
    for row in [*materials, *work_orders, *boms]:
        item_code = row.get("item_code") or row.get("production_item") or row.get("item")
        if item_code and item_code not in seen_items:
            seen_items.add(item_code)
            item_rows.append(project_process_row("Item", item_code, row.get("item_name") or row.get("production_item") or item_code, row.get("status")))
    if item_rows:
        records["item"] = item_rows

    warehouse_rows = []
    seen_warehouses = set()
    for row in [*materials, *work_orders, *stock_entries]:
        for fieldname in ["warehouse", "wip_warehouse", "fg_warehouse", "source_warehouse", "scrap_warehouse", "from_warehouse", "to_warehouse"]:
            warehouse = row.get(fieldname)
            if warehouse and warehouse not in seen_warehouses:
                seen_warehouses.add(warehouse)
                warehouse_rows.append(project_process_row("Warehouse", warehouse, warehouse, row.get("status")))
    if warehouse_rows:
        records["warehouse"] = warehouse_rows

    operation_rows = []
    seen_operations = set()
    for row in [*bom_operations, *job_cards]:
        operation = row.get("operation")
        if operation and operation not in seen_operations:
            seen_operations.add(operation)
            operation_rows.append(project_process_row("Operation", operation, operation, row.get("status"), row.get("parent") or row.get("work_order")))
    if operation_rows:
        records["operation"] = operation_rows

    workstation_type_rows = []
    seen_workstation_types = set()
    for row in [*workstations, *bom_operations]:
        workstation_type = row.get("workstation_type")
        if workstation_type and workstation_type not in seen_workstation_types:
            seen_workstation_types.add(workstation_type)
            workstation_type_rows.append(project_process_row("Workstation Type", workstation_type, workstation_type, row.get("status") or row.get("live_status")))
    if workstation_type_rows:
        records["workstation_type"] = workstation_type_rows

    workstation_rows = []
    seen_workstations = set()
    for row in [*job_cards, *workstations, *bom_operations]:
        workstation = row.get("workstation") or row.get("name")
        if workstation and workstation not in seen_workstations:
            seen_workstations.add(workstation)
            workstation_rows.append(project_process_row("Workstation", workstation, row.get("workstation_name") or workstation, row.get("status") or row.get("live_status"), row.get("current_operation") or row.get("operation")))
    if workstation_rows:
        records["workstation"] = workstation_rows

    routing_rows = []
    seen_routing = set()
    for row in boms:
        routing = row.get("routing")
        if routing and routing not in seen_routing:
            seen_routing.add(routing)
            routing_rows.append(project_process_row("Routing", routing, routing, "Ready", row.get("name")))
    if routing_rows:
        records["routing"] = routing_rows

    if boms:
        records["bom"] = [project_process_row("BOM", row.get("name"), row.get("item_name") or row.get("item"), "Submitted" if row.get("docstatus") == 1 else "Draft") for row in boms if row.get("name")]
    if work_orders:
        records["work_order"] = [project_process_row("Work Order", row.get("name"), row.get("item_name") or row.get("production_item"), row.get("status"), row.get("bom_no")) for row in work_orders if row.get("name")]
    if stock_entries:
        records["stock_entry"] = [project_process_row("Stock Entry", row.get("name"), row.get("purpose"), ["Draft", "Submitted", "Cancelled"][int(row.get("docstatus") or 0)] if row.get("docstatus") is not None else "Open", row.get("work_order")) for row in stock_entries if row.get("name")]
    if job_cards:
        records["job_card"] = [project_process_row("Job Card", row.get("name"), row.get("operation"), row.get("status"), row.get("workstation")) for row in job_cards if row.get("name")]

    return records


def project_process_row(doctype: str, name: str | None, title: str | None, status: str | None = None, detail: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "title": title or name,
        "status": status or "Ready",
        "detail": detail,
        "docstatus": None,
        "modified": "",
        "url": f"/app/{route_slug(doctype)}/{name}" if name else f"/app/{route_slug(doctype)}",
    }


def process_filters(
    doctype: str,
    filter_mode: str | None,
    project_name: str,
    bom_names: list[str],
    work_order_names: list[str],
) -> dict | list | None:
    if not filter_mode:
        return None
    if filter_mode == "project" and has_field(doctype, "project"):
        return {"project": project_name}
    if filter_mode == "bom_names" and bom_names and has_field(doctype, "name"):
        return [[doctype, "name", "in", bom_names]]
    if filter_mode == "work_order" and work_order_names and has_field(doctype, "work_order"):
        return [[doctype, "work_order", "in", work_order_names]]
    return None


def process_recent_records(doctype: str, filters: dict | list | None) -> list[dict[str, Any]]:
    fields = ["name", "modified", "docstatus"]
    for fieldname in [
        "item_name",
        "warehouse_name",
        "operation",
        "workstation_name",
        "workstation_type",
        "plant_floor_name",
        "routing_name",
        "production_item",
        "purpose",
        "status",
        "project",
    ]:
        if has_field(doctype, fieldname):
            fields.append(fieldname)

    rows = get_all_safe(
        doctype,
        fields,
        filters=filters,
        order_by="modified desc",
        limit_page_length=8,
    )
    for row in rows:
        row["title"] = (
            row.get("item_name")
            or row.get("warehouse_name")
            or row.get("operation")
            or row.get("workstation_name")
            or row.get("routing_name")
            or row.get("production_item")
            or row.get("purpose")
            or row.get("name")
        )
        row["url"] = f"/app/{route_slug(doctype)}/{row.get('name')}"
    return rows


def process_progress(
    doctype: str,
    count: int,
    recent: list[dict[str, Any]],
    work_orders: list[dict[str, Any]],
    bom_names: list[str],
    work_order_names: list[str],
) -> float:
    if doctype in {"Item", "Warehouse", "Operation", "Workstation Type", "Workstation", "Plant Floor", "Routing"}:
        return 100 if count else 0
    if doctype == "BOM":
        return 100 if bom_names else 0
    if doctype == "Work Order":
        if not work_orders:
            return 0
        total = sum(flt(row.get("qty")) for row in work_orders)
        produced = sum(flt(row.get("produced_qty")) for row in work_orders)
        return round((produced / total) * 100, 2) if total else 0
    if doctype == "Job Card":
        if not recent and not work_order_names:
            return 0
        completed = len([row for row in recent if row.get("status") == "Completed"])
        return round((completed / len(recent)) * 100, 2) if recent else 0
    if doctype == "Stock Entry":
        submitted = len([row for row in recent if int(row.get("docstatus") or 0) == 1 or row.get("status") == "Submitted"])
        return round((submitted / len(recent)) * 100, 2) if recent else 0
    return 100 if count else 0


def process_status(installed: bool, count: int, progress: float, filter_mode: str | None) -> str:
    if not installed:
        return "Not installed"
    if not count:
        return "Not configured" if filter_mode else "No records"
    if progress >= 100:
        return "Ready"
    if progress > 0:
        return "In Progress"
    return "Open"


def get_integration_rows(project_name: str) -> list[dict[str, Any]]:
    rows = get_all_safe(
        "Sarathi Machine Integration Log",
        ["name", "project", "source_system", "machine", "program", "planned_qty", "completed_qty", "rejected_qty", "sync_status", "timestamp", "modified"],
        filters={"project": project_name},
        order_by="modified desc",
        limit_page_length=50,
    )
    if rows:
        return rows

    return [
        {"source_system": "TubePro P1", "sync_status": "Not configured", "pending_syncs": 0},
        {"source_system": "CypCut", "sync_status": "Not configured", "pending_syncs": 0},
        {"source_system": "Tally", "sync_status": "Not configured", "pending_syncs": 0},
    ]


def organization_summary(company: str | None, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    projects = projects if projects is not None else get_project_cards(company)
    project_names = [row["name"] for row in projects if row.get("name")]
    completed_projects = len([row for row in projects if row.get("status") == "Completed"])
    active_projects = len([row for row in projects if row.get("status") not in {"Completed", "Cancelled"}])

    wo_filters: dict | list | None = {}
    if project_names and has_field("Work Order", "project"):
        wo_filters = [["Work Order", "project", "in", project_names]]
    if has_field("Work Order", "status"):
        if isinstance(wo_filters, list):
            wo_filters.append(["Work Order", "status", "not in", ["Completed", "Cancelled", "Stopped"]])
        else:
            wo_filters["status"] = ["not in", ["Completed", "Cancelled", "Stopped"]]
    active_wos = count_safe("Work Order", wo_filters)

    work_order_names = []
    if project_names and doctype_exists("Work Order") and has_field("Work Order", "project"):
        work_order_names = [
            row["name"]
            for row in get_all_safe(
                "Work Order",
                ["name"],
                filters=[["Work Order", "project", "in", project_names]],
                limit_page_length=1000,
            )
        ]

    job_card_filters: dict | list | None = {}
    if work_order_names and has_field("Job Card", "work_order"):
        job_card_filters = [["Job Card", "work_order", "in", work_order_names]]
    if has_field("Job Card", "status"):
        if isinstance(job_card_filters, list):
            job_card_filters.append(["Job Card", "status", "not in", ["Completed", "Cancelled"]])
        else:
            job_card_filters["status"] = ["not in", ["Completed", "Cancelled"]]
    open_job_cards = count_safe("Job Card", job_card_filters)

    production_today = 0
    if doctype_exists("Stock Entry") and has_field("Stock Entry", "purpose"):
        production_today = count_safe("Stock Entry", {"purpose": "Manufacture", "posting_date": today(), "docstatus": 1})

    computed_shortages = len([row for row in projects if flt(row.get("shortage_qty")) > 0])
    finished_goods_qty = sum(flt(row.get("finished_goods_qty")) for row in projects)

    return {
        "company": company or "All Organizations",
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "delayed_projects": count_delayed_projects(),
        "active_work_orders": active_wos,
        "open_job_cards": open_job_cards,
        "shortages": computed_shortages or count_safe("Sarathi Material Requirement", {"shortage_qty": [">", 0]}),
        "production_today": production_today,
        "finished_goods": finished_goods_qty or count_safe("Bin", {"warehouse": "Finished Goods - PMPL"}),
    }


def count_delayed_projects() -> int:
    if not doctype_exists("Task") or not all(has_field("Task", field) for field in ["project", "exp_end_date", "status"]):
        return 0
    rows = get_all_safe(
        "Task",
        ["project"],
        filters=[
            ["Task", "exp_end_date", "<", today()],
            ["Task", "status", "not in", ["Completed", "Cancelled"]],
        ],
        limit_page_length=1000,
    )
    return len({row.get("project") for row in rows if row.get("project")})


@frappe.whitelist()
def get_dashboard(company: str | None = None, project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project, company)
    project_name = project_doc["name"]
    tasks = get_project_tasks(project_name)
    work_orders = get_work_orders_for_project(project_name)
    job_cards = get_job_cards_for_work_orders(work_orders)
    selected_company = company or project_doc.get("company") or get_default_company_from_erp()
    projects = get_project_cards(selected_company)
    boms = get_bom_rows(project_doc, work_orders)
    materials = get_material_rows(project_name, work_orders, boms)
    workstations = get_workstation_rows(project_name, job_cards)
    stock_entries = get_stock_entry_rows(project_name, work_orders)
    finished_goods = get_finished_goods_rows(work_orders)
    project_doc = apply_production_completion(project_doc, work_orders, job_cards, finished_goods)
    bom_operations = get_bom_operation_rows(boms, job_cards)
    alerts = get_alert_rows(materials, tasks, workstations, work_orders)

    active_wos = len([wo for wo in work_orders if wo.get("status") not in {"Completed", "Cancelled", "Stopped"}])
    open_job_cards = len([jc for jc in job_cards if jc.get("status") not in {"Completed", "Cancelled"}])
    computed_shortages = len([m for m in materials if flt(m.get("shortage_qty")) > 0])
    finished_goods_qty = sum(flt(fg.get("balance_qty")) for fg in finished_goods)
    production_today = 0
    if doctype_exists("Stock Entry") and has_field("Stock Entry", "purpose"):
        se_filters: dict[str, Any] = {"purpose": "Manufacture", "posting_date": today(), "docstatus": 1}
        if has_field("Stock Entry", "project"):
            se_filters["project"] = project_name
        production_today = count_safe("Stock Entry", se_filters)

    project_kpis = {
        "company": selected_company or "All Organizations",
        "active_projects": 1,
        "completed_projects": 1 if project_doc.get("status") == "Completed" else 0,
        "delayed_projects": 1 if any(t.get("is_delayed") for t in tasks) else 0,
        "active_work_orders": active_wos,
        "open_job_cards": open_job_cards,
        "shortages": computed_shortages,
        "production_today": production_today,
        "finished_goods": finished_goods_qty,
    }

    return envelope(
        {
            "organization": project_kpis,
            "companies": get_company_options(selected_company),
            "projects": projects,
            "project": project_doc,
            "tasks": tasks,
            "pipeline": get_pipeline(tasks, project_doc),
            "live_analysis": get_live_analysis(
                project_doc,
                boms,
                work_orders,
                job_cards,
                materials,
                finished_goods,
                alerts,
            ),
            "manufacturing_process": get_manufacturing_process(
                project_name,
                work_orders,
                boms,
                materials,
                job_cards,
                workstations,
                stock_entries,
                bom_operations,
            ),
            "boms": boms,
            "bom_operations": bom_operations,
            "materials": materials,
            "engineering_components": ENGINEERING_COMPONENTS,
            "bop_items": BOP_ITEMS,
            "raw_stock_plan": RAW_STOCK_PLAN,
            "work_orders": work_orders,
            "job_cards": job_cards,
            "workstations": workstations,
            "stock_entries": stock_entries,
            "finished_goods": finished_goods,
            "alerts": alerts,
            "integrations": get_integration_rows(project_name),
        }
    )


@frappe.whitelist()
def get_organization_summary(company: str | None = None) -> dict[str, Any]:
    company_names = {row.get("name") for row in get_company_options()}
    selected_company = company if company in company_names else None
    projects = get_project_cards(selected_company)
    boms = get_all_bom_rows(selected_company)
    work_orders = get_all_work_orders(selected_company)
    job_cards = get_job_cards_for_work_orders(work_orders)
    workstations = get_workstation_rows("", job_cards)
    bom_operations = get_bom_operation_rows(boms, job_cards)
    materials = get_bom_material_rows(work_orders, boms)
    stock_entries = get_stock_entry_rows("", work_orders)
    finished_goods = get_finished_goods_rows(work_orders)

    task_filters = []
    if selected_company:
        project_names = [p["name"] for p in projects if p.get("name")]
        if project_names:
            task_filters = [["Task", "project", "in", project_names]]
        else:
            task_filters = [["Task", "project", "=", "__NONE__"]]
    tasks = get_all_safe(
        "Task",
        ["name", "subject", "exp_end_date", "status", "project"],
        filters=task_filters or None,
        limit_page_length=500,
    )
    for t in tasks:
        t["is_delayed"] = bool(
            t.get("exp_end_date")
            and str(t.get("exp_end_date")) < today()
            and t.get("status") not in ["Completed", "Cancelled"]
        )

    alerts = get_alert_rows(materials, tasks, workstations, work_orders)

    org_project_doc = {
        "name": "",
        "project_name": "All Projects",
        "status": "Organization View",
        "company": selected_company or "All Organizations",
        "percent_complete": 0,
    }

    return envelope(
        {
            "organization": organization_summary(selected_company, projects),
            "companies": get_company_options(selected_company),
            "projects": projects,
            "project": org_project_doc,
            "tasks": tasks,
            "pipeline": get_pipeline(tasks, org_project_doc),
            "live_analysis": get_live_analysis(
                org_project_doc,
                boms,
                work_orders,
                job_cards,
                materials,
                finished_goods,
                alerts,
            ),
            "manufacturing_process": get_manufacturing_process(
                "",
                work_orders,
                boms,
                materials,
                job_cards,
                workstations,
                stock_entries,
                bom_operations,
            ),
            "boms": boms,
            "bom_operations": bom_operations,
            "materials": materials,
            "engineering_components": ENGINEERING_COMPONENTS,
            "bop_items": BOP_ITEMS,
            "raw_stock_plan": RAW_STOCK_PLAN,
            "work_orders": work_orders,
            "job_cards": job_cards,
            "workstations": workstations,
            "stock_entries": stock_entries,
            "finished_goods": finished_goods,
            "alerts": alerts,
            "integrations": get_integration_rows(""),
        }
    )


@frappe.whitelist()
def get_project_summary(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    tasks = get_project_tasks(project_doc["name"])
    return envelope({"project": project_doc, "tasks": tasks, "pipeline": get_pipeline(tasks, project_doc)})


@frappe.whitelist()
def get_project_boms(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    return envelope({"boms": get_bom_rows(project_doc, work_orders)})


@frappe.whitelist()
def get_project_materials(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    boms = get_bom_rows(project_doc, work_orders)
    return envelope({"materials": get_material_rows(project_doc["name"], work_orders, boms)})


@frappe.whitelist()
def get_project_production(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    return envelope({"work_orders": work_orders, "job_cards": get_job_cards_for_work_orders(work_orders)})


@frappe.whitelist()
def get_workstations(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    job_cards = get_job_cards_for_work_orders(work_orders)
    return envelope({"workstations": get_workstation_rows(project_doc["name"], job_cards)})


@frappe.whitelist()
def get_stock_entries(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    return envelope({"stock_entries": get_stock_entry_rows(project_doc["name"], work_orders)})


@frappe.whitelist()
def get_finished_goods(project: str | None = None) -> dict[str, Any]:
    project_doc = resolve_project(project)
    work_orders = get_work_orders_for_project(project_doc["name"])
    return envelope({"finished_goods": get_finished_goods_rows(work_orders)})


@frappe.whitelist()
def get_form_schema(doctype: str = "Project") -> dict[str, Any]:
    return envelope({"schema": form_wrapper_schema(doctype)})


@frappe.whitelist()
def update_project(project: str, changes: dict[str, Any]) -> dict[str, Any]:
    require_super_admin()
    doc = frappe.get_doc("Project", project)
    for field, value in (changes or {}).items():
        if has_field("Project", field):
            doc.set(field, value)
    doc.save()
    return envelope({"project": project_payload(project)})


@frappe.whitelist()
def update_task(task: str, changes: dict[str, Any]) -> dict[str, Any]:
    require_super_admin()
    doc = frappe.get_doc("Task", task)
    for field, value in (changes or {}).items():
        if has_field("Task", field):
            doc.set(field, value)
    doc.save()
    return envelope({"task": doc.as_dict()})


@frappe.whitelist()
def recalculate_progress(project: str | None = None) -> dict[str, Any]:
    require_super_admin()
    project_doc = resolve_project(project)
    tasks = get_project_tasks(project_doc["name"])
    if not project_doc.get("exists"):
        return envelope({"project": project_doc, "progress": 0})

    total = len(tasks)
    completed = len([task for task in tasks if task.get("status") == "Completed"])
    progress = round((completed / total) * 100, 2) if total else 0

    doc = frappe.get_doc("Project", project_doc["name"])
    if has_field("Project", "percent_complete"):
        doc.percent_complete = progress
        doc.save()

    return envelope({"project": project_payload(project_doc["name"]), "progress": progress})


def sync_integration(source_system: str, payload: dict[str, Any]) -> dict[str, Any]:
    require_super_admin()
    if not doctype_exists("Sarathi Machine Integration Log"):
        frappe.throw("Sarathi Machine Integration Log DocType is not installed.")

    payload = payload or {}
    doc = frappe.new_doc("Sarathi Machine Integration Log")
    doc.source_system = source_system
    doc.project = payload.get("project") or DEFAULT_PROJECT_DOC
    doc.machine = payload.get("machine")
    doc.program = payload.get("program")
    doc.drawing = payload.get("drawing")
    doc.planned_qty = flt(payload.get("planned_qty"))
    doc.completed_qty = flt(payload.get("completed_qty"))
    doc.rejected_qty = flt(payload.get("rejected_qty"))
    doc.sync_status = payload.get("sync_status") or "Pending"
    doc.raw_payload = frappe.as_json(payload)
    doc.insert()
    return envelope({"integration_log": doc.name})


@frappe.whitelist()
def sync_tubepro(payload: dict[str, Any]) -> dict[str, Any]:
    return sync_integration("TubePro P1", payload)


@frappe.whitelist()
def sync_cypcut(payload: dict[str, Any]) -> dict[str, Any]:
    return sync_integration("CypCut", payload)


@frappe.whitelist()
def sync_tally(payload: dict[str, Any]) -> dict[str, Any]:
    return sync_integration("Tally", payload)
