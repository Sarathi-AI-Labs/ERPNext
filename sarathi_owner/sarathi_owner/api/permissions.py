import frappe

from sarathi_visibility.api.access import has_capability

OWNER_ROLES = {
	"Sarathi Owner",
	"System Manager",
	"Administrator",
}
FINANCE_ROLES = {
	"Accounts Manager",
	"Accounts User",
	"Auditor",
	"Sarathi Owner",
	"System Manager",
	"Administrator",
}


def can_access_owner(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Administrator":
		return True
	return has_capability("owner", user)


def can_view_finance(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	if user == "Administrator":
		return True
	return has_capability("finance", user) and frappe.has_permission("GL Entry", "read", user=user) and frappe.has_permission(
		"Sales Invoice", "read", user=user
	)


def get_permission_context() -> dict:
	user = frappe.session.user
	roles = frappe.get_roles(user)
	return {
		"user": user,
		"is_admin": user == "Administrator",
		"can_access_owner": can_access_owner(user),
		"can_view_finance": can_view_finance(user),
		"roles": roles,
	}
