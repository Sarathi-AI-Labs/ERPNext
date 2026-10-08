import frappe
from frappe import _

SUPER_ADMIN_ROLES = {"Sarathi Super Admin"}
SETUP_EDIT_ROLES = {"Manufacturing Manager", "System Manager", *SUPER_ADMIN_ROLES}


def is_super_admin(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Administrator":
		return True
	user_roles = set(frappe.get_roles(user))
	return bool(SUPER_ADMIN_ROLES.intersection(user_roles))


def require_super_admin():
	if not is_super_admin():
		frappe.throw(
			_("Only Sarathi Super Admin can modify Sarathi project data."),
			frappe.PermissionError,
		)


def permission_payload() -> dict:
	user = frappe.session.user
	roles = frappe.get_roles(user)
	can_edit_setup = user == "Administrator" or bool(SETUP_EDIT_ROLES.intersection(roles))
	return {
		"user": user,
		"roles": roles,
		"is_super_admin": is_super_admin(user),
		"can_edit_setup": can_edit_setup,
		"view_mode": "admin" if can_edit_setup else "employee",
	}
