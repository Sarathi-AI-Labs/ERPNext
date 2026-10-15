import frappe


def before_install():
	ensure_role("Sarathi Owner")


def after_install():
	ensure_role("Sarathi Owner")
	_ensure_owner_page("sarathiownertower")
	remove_manufacturing_sidebar_links()
	try:
		from sarathi_visibility.setup.install import ensure_desk_icons

		ensure_desk_icons()
	except Exception:
		pass


def after_migrate():
	ensure_role("Sarathi Owner")
	_ensure_owner_page("sarathiownertower")
	remove_manufacturing_sidebar_links()
	try:
		from sarathi_visibility.setup.install import ensure_desk_icons

		ensure_desk_icons()
	except Exception:
		pass


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
		):
			if frappe.db.exists("Role", role):
				page.append("roles", {"role": role})
		page.flags.do_not_update_json = True
		page.save(ignore_permissions=True)
	finally:
		frappe.conf.developer_mode = developer_mode


def remove_manufacturing_sidebar_links():
	if not frappe.db.exists("Workspace Sidebar", "Manufacturing"):
		return

	sidebar = frappe.get_doc("Workspace Sidebar", "Manufacturing")
	labels_to_remove = {
		"Sarathi Industrial Dashboard",
		"Sarathi Owner Dashboard",
	}

	item_rows = []
	changed = False
	for row in sidebar.items:
		if row.label in labels_to_remove or row.link_to in ("sarathicontroltower", "sarathiownertower"):
			changed = True
			continue
		item_rows.append(row.as_dict())

	if changed:
		for index, row in enumerate(item_rows, start=1):
			row["idx"] = index
		sidebar.set("items", item_rows)
		sidebar.save(ignore_permissions=True)
