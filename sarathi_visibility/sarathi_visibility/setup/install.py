import json

import frappe


def before_install():
    ensure_role("Sarathi Super Admin")


def after_install():
    from sarathi_visibility.setup.dashboard import install
    install()
    ensure_role("Sarathi Super Admin")
    ensure_module_profile_page()
    ensure_workspace_shortcuts()
    ensure_no_desk_icon()
    ensure_manufacturing_sidebar_link()


def after_migrate():
    from sarathi_visibility.setup.dashboard import install
    install()
    ensure_module_profile_page()
    ensure_workspace_shortcuts()
    ensure_no_desk_icon()
    ensure_manufacturing_sidebar_link()


def ensure_no_desk_icon():
    if frappe.db.exists("Desktop Icon", "Sarathi Visibility"):
        frappe.delete_doc("Desktop Icon", "Sarathi Visibility", ignore_permissions=True, force=True)
    elif frappe.db.table_exists("Desktop Icon"):
        for icon in frappe.get_all("Desktop Icon", filters={"label": "Sarathi Visibility"}, pluck="name"):
            frappe.delete_doc("Desktop Icon", icon, ignore_permissions=True, force=True)

    if frappe.db.exists("Workspace Sidebar", "Sarathi Visibility"):
        frappe.delete_doc("Workspace Sidebar", "Sarathi Visibility", ignore_permissions=True, force=True)
    elif frappe.db.table_exists("Workspace Sidebar"):
        for sb in frappe.get_all("Workspace Sidebar", filters={"title": "Sarathi Visibility"}, pluck="name"):
            frappe.delete_doc("Workspace Sidebar", sb, ignore_permissions=True, force=True)

    try:
        from frappe.desk.doctype.desktop_icon.desktop_icon import clear_desktop_icons_cache
        clear_desktop_icons_cache()
    except Exception:
        pass


def filter_bootinfo_desktop_icons(bootinfo):
    if not bootinfo:
        return
    desktop_icons = bootinfo.get("desktop_icons")
    if isinstance(desktop_icons, list):
        bootinfo["desktop_icons"] = [
            icon for icon in desktop_icons
            if not (
                isinstance(icon, dict) and (
                    icon.get("name") == "Sarathi Visibility" or
                    icon.get("label") == "Sarathi Visibility" or
                    icon.get("link_to") == "Sarathi Visibility"
                )
            )
        ]


def ensure_role(role_name: str):
    if frappe.db.exists("Role", role_name):
        return

    role = frappe.new_doc("Role")
    role.role_name = role_name
    role.desk_access = 1
    role.save(ignore_permissions=True)


def ensure_module_profile_page():
    _ensure_control_tower_page("sarathicontroltower")


def _ensure_control_tower_page(page_name: str):
    developer_mode = getattr(frappe.conf, "developer_mode", 0)
    try:
        frappe.conf.developer_mode = 1
        if frappe.db.exists("Page", page_name):
            page = frappe.get_doc("Page", page_name)
        else:
            page = frappe.new_doc("Page")
            page.page_name = page_name
            page.name = page_name
            page.standard = "Yes"
            page.system_page = 0

        page.module = "Sarathi Visibility"
        page.title = "Sarathi Industrial Dashboard"
        page.set("roles", [])
        for role in ("Manufacturing User", "Manufacturing Manager", "System Manager", "Sarathi Super Admin"):
            if frappe.db.exists("Role", role):
                page.append("roles", {"role": role})
        page.flags.do_not_update_json = True
        page.save(ignore_permissions=True)
    finally:
        frappe.conf.developer_mode = developer_mode


def ensure_workspace_shortcuts():
    workspace_name = "Sarathi Visibility"
    if not frappe.db.exists("Workspace", workspace_name):
        return

    workspace = frappe.get_doc("Workspace", workspace_name)
    workspace.public = 0
    workspace.is_hidden = 1
    workspace.set(
        "shortcuts",
        [shortcut.as_dict() for shortcut in workspace.shortcuts if shortcut.label not in ("Sarathi Control Tower", "Website View")],
    )
    _remove_content_shortcut(workspace, "Sarathi Control Tower")
    _remove_content_shortcut(workspace, "Website View")
    _ensure_shortcut(
        workspace,
        label="Sarathi Industrial Dashboard",
        link_to="sarathicontroltower",
        shortcut_type="Page",
        color="Blue",
    )
    _ensure_content_shortcut(workspace, "Sarathi Industrial Dashboard", "sarathi-control-tower-shortcut")
    workspace.save(ignore_permissions=True)


def _ensure_shortcut(
    workspace,
    *,
    label: str,
    link_to: str,
    shortcut_type: str,
    color: str,
    url: str = "",
):
    for shortcut in workspace.shortcuts:
        if shortcut.label == label:
            shortcut.link_to = link_to
            shortcut.type = shortcut_type
            shortcut.color = color
            shortcut.doc_view = ""
            shortcut.url = url
            return

    workspace.append(
        "shortcuts",
        {
            "label": label,
            "link_to": link_to,
            "type": shortcut_type,
            "color": color,
            "doc_view": "",
            "url": url,
        },
    )


def _ensure_content_shortcut(workspace, shortcut_name: str, block_id: str):
    try:
        content = json.loads(workspace.content or "[]")
    except json.JSONDecodeError:
        content = []

    if any(block.get("data", {}).get("shortcut_name") == shortcut_name for block in content):
        return

    content.insert(
        0,
        {
            "id": block_id,
            "type": "shortcut",
            "data": {"shortcut_name": shortcut_name, "col": 3},
        },
    )
    workspace.content = json.dumps(content, separators=(",", ":"))


def _remove_content_shortcut(workspace, shortcut_name: str):
    try:
        content = json.loads(workspace.content or "[]")
    except json.JSONDecodeError:
        return

    cleaned = [block for block in content if block.get("data", {}).get("shortcut_name") != shortcut_name]
    if len(cleaned) != len(content):
        workspace.content = json.dumps(cleaned, separators=(",", ":"))


def ensure_manufacturing_sidebar_link():
    _remove_manufacturing_workspace_card_link()

    if not frappe.db.exists("Workspace Sidebar", "Manufacturing"):
        return

    sidebar = frappe.get_doc("Workspace Sidebar", "Manufacturing")
    label = "Sarathi Industrial Dashboard"
    new_item = {
        "type": "Link",
        "label": label,
        "link_type": "Page",
        "link_to": "sarathicontroltower",
        "icon": "chart",
        "indent": 0,
        "child": 0,
        "collapsible": 1,
        "keep_closed": 0,
        "show_arrow": 0,
    }

    item_rows = []
    existing_row = None
    for row in sidebar.items:
        if row.label == label:
            existing_row = row
            continue
        item_rows.append(row.as_dict())

    settings_index = next(
        (
            index
            for index, row in enumerate(item_rows)
            if row.get("type") == "Link" and row.get("label") == "Settings"
        ),
        None,
    )
    insert_index = settings_index + 1 if settings_index is not None else len(item_rows)

    if existing_row:
        new_item.update(
            {
                "name": existing_row.name,
                "parent": existing_row.parent,
                "parentfield": existing_row.parentfield,
                "parenttype": existing_row.parenttype,
            }
        )

    item_rows.insert(insert_index, new_item)
    _reindex_rows(item_rows)
    sidebar.set("items", item_rows)
    sidebar.save(ignore_permissions=True)


def _remove_manufacturing_workspace_card_link():
    if not frappe.db.exists("Workspace", "Manufacturing"):
        return

    workspace = frappe.get_doc("Workspace", "Manufacturing")
    label = "Sarathi Industrial Dashboard"
    link_rows = [row.as_dict() for row in workspace.links if row.label != label and row.label != "Sarathi Industrial Dashboard"]
    if len(link_rows) == len(workspace.links):
        return

    _reindex_rows(link_rows)
    _refresh_card_break_counts(link_rows)
    workspace.set("links", link_rows)
    workspace.save(ignore_permissions=True)


def _reindex_rows(rows):
    for index, row in enumerate(rows, start=1):
        row["idx"] = index


def _refresh_card_break_counts(rows):
    for index, row in enumerate(rows):
        if row.get("type") != "Card Break":
            continue

        link_count = 0
        for following_row in rows[index + 1 :]:
            if following_row.get("type") == "Card Break":
                break
            if following_row.get("type") == "Link":
                link_count += 1
        row["link_count"] = link_count
