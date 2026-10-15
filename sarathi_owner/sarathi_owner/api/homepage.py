"""DASH-008: homepage context/previews, not executive KPI calculations."""
import frappe
from frappe.utils import now_datetime
from erpnext.accounts.utils import FiscalYearError
from sarathi_visibility.api.access import require_capability, check_record, deny
from sarathi_visibility.api.data_helpers import (
	get_options, get_records, invalid, read_errors, _parse, _extra,
)


@frappe.whitelist(methods=["GET"])
@read_errors
def options(resource, company=None, customer=None, search="", start=0, **extra):
	require_capability("owner")
	_extra(extra)
	if resource not in ("companies", "customers", "projects", "warehouses"):
		invalid("Unsupported homepage option type.")
	if resource not in ("projects", "warehouses") and (company or customer):
		invalid("Company and Customer scope apply only to Project or Warehouse options.")
	filters = {}
	if resource == "projects":
		if not company:
			invalid("Select a Company first.")
		filters = {"company": company}
		if customer:
			filters["customer"] = customer
	elif resource == "warehouses":
		if not company:
			invalid("Select a Company first.")
		filters = {"company": company, "is_group": 0}
	return get_options(resource, filters, search=search, start=start, page_length=25)


@frappe.whitelist(methods=["GET"])
@read_errors
def get_homepage(filters=None, **extra):
	require_capability("owner")
	_extra(extra)
	values = _parse(filters)
	from sarathi_owner.api.sales_analytics import FEATURE_KEYS, get_sales_analytics
	from sarathi_owner.api.project_health import FEATURE_KEYS as HEALTH_KEYS, get_project_delivery_health
	from sarathi_owner.api.manufacturing_inventory import FEATURE_KEYS as MFG_KEYS, get_manufacturing_inventory_summary
	from sarathi_owner.api.executive_risks import FEATURE_KEYS as RISK_KEYS, get_executive_risks_and_approvals
	if set(values) - {"company", "customer", "project", "from_date", "to_date"} - FEATURE_KEYS - HEALTH_KEYS - MFG_KEYS - RISK_KEYS:
		invalid("Unsupported homepage filter.")
	values = {k: v for k, v in values.items() if v is not None and v != ""}
	health_filters = {k: v for k,v in values.items() if k in HEALTH_KEYS or k in ("company","customer","project","from_date","to_date","order_status","delivery_from","delivery_to")}
	mfg_filters = {k: v for k, v in values.items() if k in MFG_KEYS or k in ("company", "customer", "project", "from_date", "to_date")}
	risk_filters = {k: v for k, v in values.items() if k in RISK_KEYS or k in ("company", "customer", "project", "from_date", "to_date")}
	all_filters = dict(values)
	sales_filters = {k: v for k,v in values.items() if k not in HEALTH_KEYS and k not in MFG_KEYS and k not in RISK_KEYS}
	values = sales_filters.copy()
	values = {k: v for k, v in values.items() if k not in FEATURE_KEYS}
	project_filters = {k: v for k, v in values.items() if k != "project"}
	if values.get("project"):
		project_filters["name"] = values["project"]
	projects = get_records("projects", project_filters, page_length=6)
	company = projects["applied_filters"]["company"]
	values["company"] = company
	if values.get("project"):
		project = check_record("Project", values["project"])
		if project.company != company or (values.get("customer") and project.customer != values["customer"]):
			deny()
	work_orders = {"available": False, "reason": "Select a Project to scope manufacturing for a Customer."}
	if not values.get("customer") or values.get("project"):
		wo_filters = {k: v for k, v in values.items() if k != "customer"}
		if frappe.has_permission("Work Order", "read"):
			work_orders = {"available": True, **get_records("work_orders", wo_filters, page_length=6)}
		else:
			work_orders = {"available": False, "reason": "Work Orders are unavailable for your permissions."}
	from sarathi_owner.api.finance_kpis import get_finance_kpis
	from sarathi_visibility.api.data_helpers import DashboardReadError
	messages = list(getattr(frappe.local, "message_log", []) or [])
	try:
		finance = {"available": True, "data": get_finance_kpis(values)}
	except (frappe.PermissionError, frappe.ValidationError, DashboardReadError):
		frappe.local.message_log = messages
		finance = {"available": False, "reason": "Financial reports are unavailable for this permission scope, period or configuration."}
	try:
		sales = {"available": True, "data": get_sales_analytics({**sales_filters, "company": company})}
	except FiscalYearError:
		frappe.local.message_log = messages
		sales = {"available": False, "reason": "No configured Fiscal Year covers this reporting period."}
	except frappe.ValidationError:
		# Feature-specific invalid filters must be rejected, not silently ignored.
		raise
	except (frappe.PermissionError, DashboardReadError):
		frappe.local.message_log = messages
		sales = {"available": False, "reason": "Customer and sales analytics are unavailable for this permission scope or configuration."}
	try:
		health = {"available": True, "data": get_project_delivery_health({**health_filters, "company": company})}
	except frappe.PermissionError:
		frappe.local.message_log = messages
		health = {"available": False, "reason": "Project and delivery health are unavailable for your permission scope."}
	except DashboardReadError:
		frappe.local.message_log = messages
		health = {"available": False, "reason": "Project and delivery health could not load. Please refresh to try again."}
	try:
		mfg_inv = {"available": True, "data": get_manufacturing_inventory_summary({**mfg_filters, "company": company})}
	except frappe.ValidationError:
		raise
	except frappe.PermissionError:
		frappe.local.message_log = messages
		mfg_inv = {"available": False, "reason": "Manufacturing and inventory summary is unavailable for your permission scope."}
	except DashboardReadError:
		frappe.local.message_log = messages
		mfg_inv = {"available": False, "reason": "Manufacturing and inventory summary could not load. Please refresh to try again."}
	try:
		executive_risks = {"available": True, "data": get_executive_risks_and_approvals({**risk_filters, "company": company})}
	except frappe.ValidationError:
		raise
	except frappe.PermissionError:
		frappe.local.message_log = messages
		executive_risks = {"available": False, "reason": "Executive risks and approvals are unavailable for your permission scope."}
	except DashboardReadError:
		frappe.local.message_log = messages
		executive_risks = {"available": False, "reason": "Executive risks and approvals could not load. Please refresh to try again."}
	return {
		"applied_filters": {**all_filters, **values},
		"generated_at": str(now_datetime()),
		"executive_risks": executive_risks,
		"finance": finance,
		"sales": sales,
		"project_health": health,
		"manufacturing_inventory": mfg_inv,
		"projects": projects,
		"work_orders": work_orders,
		"date_basis": "Project expected start; Work Order planned start. Blank bounds include all dates.",
		"availability": {
			"finance": "Financial indicators are unavailable until accounting reconciliation is complete.",
			"analytics": "Executive risks, approvals, finance, sales, projects, and manufacturing summaries are active.",
		},
	}
