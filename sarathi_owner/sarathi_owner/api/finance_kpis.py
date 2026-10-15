"""DASH-009: report-derived finance, with fail-closed complete-scope authorization."""
from decimal import Decimal

import frappe
from frappe.desk.query_report import get_report_doc
from frappe.utils import getdate, now_datetime, today

from erpnext.accounts.utils import get_fiscal_year, FiscalYearError
from sarathi_visibility.api.access import allowed_fields, check_record, deny, require_capability
from sarathi_visibility.api.data_helpers import _company, _date, _extra, _parse, invalid, read_errors


SOURCES = {
	"Profit and Loss Statement": {"GL Entry": {"company", "posting_date", "account", "debit", "credit", "is_cancelled", "is_opening", "voucher_type", "finance_book", "project", "cost_center"}, "Account": {"name", "root_type", "is_group"}},
	"Gross Profit": {"Sales Invoice": {"company", "posting_date", "base_net_total"}, "Sales Invoice Item": {"base_net_amount", "qty", "item_code"}, "Stock Ledger Entry": {"stock_value_difference", "actual_qty", "valuation_rate"}, "Item": {"name"}, "Purchase Invoice": {"name"}, "Purchase Invoice Item": {"base_rate", "qty", "item_code"}},
	"Accounts Receivable": {"Sales Invoice": {"company", "outstanding_amount"}, "Customer": {"name"}, "GL Entry": {"debit", "credit"}, "Account": {"name"}, "Payment Entry": {"name"}, "Journal Entry": {"name"}},
	"Accounts Payable": {"Purchase Invoice": {"company", "outstanding_amount"}, "Supplier": {"name"}, "GL Entry": {"debit", "credit"}, "Account": {"name"}, "Payment Entry": {"name"}, "Journal Entry": {"name"}},
}


def decimal(value):
	if value is None:
		raise ValueError("Missing native financial amount")
	return Decimal(str(value))


def ratio(numerator, denominator):
	return float(decimal(numerator) / decimal(denominator) * 100) if decimal(denominator) else None


def _complete_scope(company, source):
	"""Native scripts use internal queries; row-limited users must never see full totals."""
	if frappe.session.user != "Administrator":
		permissions = frappe.permissions.get_user_permissions(frappe.session.user)
		if any(rows for dt, rows in permissions.items() if dt != "Company"):
			deny()
		for dt in SOURCES[source]:
			if frappe.get_meta(dt).istable:
				continue  # Child ownership is controlled by its authorized invoice parent.
			role = frappe.permissions.get_role_permissions(frappe.get_meta(dt))
			if not role.get("read"):
				deny()
			if any(frappe.get_hooks(hook, {}).get(dt) for hook in ("has_permission", "permission_query_conditions")):
				deny()
			restrictions = [row for row in permissions.get("Company", []) if row.get("applicable_for") in (None, "", dt)]
			if restrictions and company not in {row.get("doc") for row in restrictions}:
				deny()
	for dt, fields in SOURCES[source].items():
		if fields and not fields <= allowed_fields(dt):
			deny()


def native_report(source, filters):
	messages = list(getattr(frappe.local, "message_log", []) or [])
	try:
		_complete_scope(filters["company"], source)
		report = get_report_doc(source)  # Native Report roles AND ref-DocType report permission.
		if report.report_type != "Script Report" or report.is_standard != "Yes" or report.module != "Accounts" or report.snapshot_report:
			deny()
		# execute_script_report can enable prepared reports after 15s. Use its supported
		# native module executor after the same permission checks, without that write watcher.
		return report.execute_module(frappe._dict(filters))
	except frappe.PermissionError:
		frappe.local.message_log = messages
		raise


def normalize(filters):
	values = _parse(filters)
	if set(values) - {"company", "from_date", "to_date", "as_of_date", "customer", "project", "cost_center", "finance_book"}:
		invalid("Unsupported finance filter.")
	values = {k: v for k, v in values.items() if v is not None and v != ""}
	values["company"] = _company(values.get("company"))
	for key in ("from_date", "to_date", "as_of_date"):
		if key in values:
			_date(values[key])
	end = values.get("to_date") or today()
	start = values.get("from_date") or str(get_fiscal_year(end, company=values["company"])[1])
	if getdate(start) > getdate(end) or (getdate(end) - getdate(start)).days > 366 * 5:
		invalid("Use an ordered finance period of at most five years.")
	values.update(from_date=start, to_date=end, as_of_date=values.get("as_of_date") or end)
	for key, dt in (("customer", "Customer"), ("project", "Project"), ("cost_center", "Cost Center"), ("finance_book", "Finance Book")):
		if key not in values:
			continue
		doc = check_record(dt, values[key])
		if doc.meta.has_field("company") and doc.get("company") != values["company"]:
			deny()
	if values.get("project") and values.get("customer"):
		if check_record("Project", values["project"]).get("customer") != values["customer"]:
			deny()
	return values


def _metric(key, label, value, source, filters, unit="currency", reason=None):
	return {"key": key, "label": label, "value": float(value) if value is not None else None,
		"unit": unit, "available": reason is None and value is not None, "reason": reason,
		"source": source, "report_filters": filters}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_finance_kpis(filters=None, **extra):
	require_capability("owner")
	require_capability("finance")
	_extra(extra)
	values = normalize(filters)
	company = values["company"]
	currency = check_record("Company", company).default_currency
	if "default_currency" not in allowed_fields("Company"):
		deny()
	metrics = []
	pnl_filters = dict(company=company, filter_based_on="Date Range", period_start_date=values["from_date"], period_end_date=values["to_date"], periodicity="Monthly", accumulated_values=0, include_default_book_entries=1)
	if values.get("finance_book"):
		pnl_filters["include_default_book_entries"] = 0
	for key in ("project", "cost_center", "finance_book"):
		if values.get(key):
			pnl_filters[key] = [values[key]] if key in ("project", "cost_center") else values[key]
	messages = list(getattr(frappe.local, "message_log", []) or [])
	try:
		if values.get("customer"):
			raise NotImplementedError("Customer attribution is not supported for P&L accounting income and profit.")
		pnl = native_report("Profit and Loss Statement", pnl_filters)
		summary = pnl[4]
		if len(summary) != 3:
			raise ValueError("Unexpected native P&L summary")
		income, expense, profit = [decimal(row["value"]) for row in summary]
		for key, label, value in (("income", "Accounting income (P&L)", income), ("expense", "Accounting expense (P&L)", expense), ("net_profit", "Net profit / loss", profit)):
			metrics.append(_metric(key, label, value, "Profit and Loss Statement", pnl_filters))
		metrics.append(_metric("net_margin", "Net profit margin", ratio(profit, income), "Profit and Loss Statement", pnl_filters, "%", "Undefined when accounting income is zero." if income == 0 else None))
	except (frappe.PermissionError, NotImplementedError, FiscalYearError) as error:
		frappe.local.message_log = messages
		reason = str(error) if isinstance(error, NotImplementedError) else "No configured Fiscal Year covers this accounting period." if isinstance(error, FiscalYearError) else "Finance is unavailable for this permission scope."
		for key, label in (("income", "Accounting income (P&L)"), ("expense", "Accounting expense (P&L)"), ("net_profit", "Net profit / loss"), ("net_margin", "Net profit margin")):
			metrics.append(_metric(key, label, None, "Profit and Loss Statement", pnl_filters, "%" if key == "net_margin" else "currency", reason))

	gross_filters = dict(company=company, from_date=values["from_date"], to_date=values["to_date"], group_by="Invoice")
	try:
		if any(values.get(key) for key in ("customer", "project", "cost_center", "finance_book")):
			raise NotImplementedError("Gross profit currently supports Company and invoice dates only.")
		gross = native_report("Gross Profit", gross_filters)
		totals = [row for row in gross[1] if row.get("sales_invoice") == "Total" and row.get("indent") is None]
		if len(totals) != 1:
			raise ValueError("Missing or ambiguous native Gross Profit total")
		amount, selling = decimal(totals[0]["gross_profit"]), decimal(totals[0]["selling_amount"])
		metrics.append(_metric("gross_profit", "Gross profit (invoice cost basis)", amount, "Gross Profit", gross_filters))
		metrics.append(_metric("gross_margin", "Gross profit margin", ratio(amount, selling), "Gross Profit", gross_filters, "%", "Undefined when native selling amount is zero." if selling == 0 else None))
	except (frappe.PermissionError, NotImplementedError) as error:
		reason = str(error) if isinstance(error, NotImplementedError) else "Gross profit is unavailable for this permission scope."
		metrics.extend([_metric("gross_profit", "Gross profit (invoice cost basis)", None, "Gross Profit", gross_filters, reason=reason), _metric("gross_margin", "Gross profit margin", None, "Gross Profit", gross_filters, "%", reason)])

	for source, key, label in (("Accounts Receivable", "receivables", "Net receivables including credits"), ("Accounts Payable", "payables", "Net supplier payables")):
		balance_filters = dict(company=company, report_date=values["as_of_date"], party_type="Customer" if key == "receivables" else "Supplier", ageing_based_on="Due Date", range="30,60,90,120", in_party_currency=0, group_by_party=0)
		try:
			if any(values.get(dim) for dim in ("project", "cost_center", "finance_book")) or (key == "payables" and values.get("customer")):
				raise NotImplementedError("This balance does not support the selected financial dimensions.")
			if values.get("customer"):
				balance_filters["party"] = [values["customer"]]
			report = native_report(source, balance_filters)
			amount = sum((decimal(row["outstanding"]) for row in report[1] if row.get("voucher_type") and row.get("voucher_no")), Decimal(0))
			metrics.append(_metric(key, label, amount, source, balance_filters))
		except (frappe.PermissionError, NotImplementedError) as error:
			reason = str(error) if isinstance(error, NotImplementedError) else "This balance is unavailable for this permission scope."
			metrics.append(_metric(key, label, None, source, balance_filters, reason=reason))
	warnings = ["Gross profit follows the native invoice/valuation report, independently of P&L net profit."]
	if any(metric["key"] == "income" and metric["value"] is not None and metric["value"] < 0 for metric in metrics):
		warnings.append("Accounting income is negative; margin retains the signed denominator.")
	if any(metric["key"] == "expense" and metric["value"] is not None and metric["value"] < 0 for metric in metrics):
		warnings.append("Accounting expenses have a net credit balance; review the matching Profit and Loss report.")
	if any(metric["key"] == "receivables" and metric["value"] is not None and metric["value"] < 0 for metric in metrics):
		warnings.append("Net receivables are a credit balance; review Accounts Receivable for its allocation details.")
	return {"metrics": metrics, "currency": currency, "applied_filters": values,
		"generated_at": str(now_datetime()), "as_of_date": values["as_of_date"],
		"period": {"from_date": values["from_date"], "to_date": values["to_date"]},
		"warnings": warnings}
