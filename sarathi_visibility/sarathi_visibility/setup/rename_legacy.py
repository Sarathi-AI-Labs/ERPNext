"""One-time, data-preserving upgrade from the former app name."""

import json

import frappe
from frappe.model.rename_doc import rename_doc


def execute():
    previous_patch = frappe.flags.in_patch
    previous_developer = frappe.conf.developer_mode
    frappe.flags.in_patch = True
    frappe.conf.developer_mode = 1
    try:
        for suffix in ("Project Controller", "Material Requirement", "Production Tracker", "Machine Integration Log"):
            _rename("DocType", f"Proflex {suffix}", f"Sarathi {suffix}")
        _rename("Role", "Proflex Super Admin", "Sarathi Super Admin", merge=True)
        _rename("Workspace", "Proflex Visibility", "Sarathi Visibility")
        if frappe.db.exists("Module Def", "Proflex Visibility"):
            frappe.db.set_value("Module Def", "Proflex Visibility", "custom", 1)
        _rename("Module Def", "Proflex Visibility", "Sarathi Visibility")
        if frappe.db.exists("Module Def", "Sarathi Visibility"):
            frappe.db.set_value("Module Def", "Sarathi Visibility", {"app_name": "sarathi_visibility", "custom": 0})
        apps = frappe.get_installed_apps()
        if "proflex_visibility" in apps:
            apps = list(dict.fromkeys("sarathi_visibility" if app == "proflex_visibility" else app for app in apps))
            frappe.db.set_global("installed_apps", json.dumps(apps))
        frappe.db.commit()
        frappe.clear_cache()
        frappe.cache.delete_value("app_modules")
        frappe.cache.delete_value("all_apps")
        frappe.setup_module_map()
    finally:
        frappe.flags.in_patch = previous_patch
        frappe.conf.developer_mode = previous_developer


def _rename(doctype, old, new, merge=False):
    if not frappe.db.exists(doctype, old):
        return
    exists = frappe.db.exists(doctype, new)
    if exists and not merge:
        frappe.throw(f"Both {old} and {new} exist; resolve the duplicate before migrating.")
    rename_doc(doctype, old, new, force=True, merge=bool(exists and merge), ignore_permissions=True)
