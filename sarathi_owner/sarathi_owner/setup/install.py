import frappe


def before_install():
	ensure_role("Sarathi Owner")


def after_install():
	ensure_role("Sarathi Owner")
	_ensure_owner_page("sarathiownertower")
	ensure_manufacturing_sidebar_link()


def after_migrate():
	ensure_role("Sarathi Owner")
	_ensure_owner_page("sarathiownertower")
	ensure_manufacturing_sidebar_link()


def ensure_role(role_name: str):
	if frappe.db.exists("Role", role_name):
		return
	role = frappe.new_doc("Role")
	role.role_name = role_name
	role.desk_access = 1
	role.save(ignore_permissions=True)


def _ensure_owner_page(page_name: str):
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

		page.module = "Sarathi Owner"
		page.title = "Sarathi Owner Dashboard"
		page.set("roles", [])
		for role in (
			"Sarathi Owner",
			"System Manager",
			"Manufacturing Manager",
		):
			if frappe.db.exists("Role", role):
				page.append("roles", {"role": role})
		page.flags.do_not_update_json = True
		page.save(ignore_permissions=True)
	finally:
		frappe.conf.developer_mode = developer_mode


def ensure_manufacturing_sidebar_link():
	if not frappe.db.exists("Workspace Sidebar", "Manufacturing"):
		return

	sidebar = frappe.get_doc("Workspace Sidebar", "Manufacturing")
	label = "Sarathi Owner Dashboard"
	new_item = {
		"type": "Link",
		"label": label,
		"link_type": "Page",
		"link_to": "sarathiownertower",
		"icon": "dashboard",
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

	# Find Sarathi Industrial Dashboard position to put Owner Dashboard right above or next to it
	sarathi_index = next(
		(
			index
			for index, row in enumerate(item_rows)
			if row.get("type") == "Link" and "Sarathi Industrial Dashboard" in (row.get("label") or "")
		),
		None,
	)
	insert_index = sarathi_index if sarathi_index is not None else len(item_rows)

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
	for index, row in enumerate(item_rows, start=1):
		row["idx"] = index

	sidebar.set("items", item_rows)
	sidebar.save(ignore_permissions=True)
