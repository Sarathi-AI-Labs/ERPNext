"""DASH-010: accounting-income attribution and current delivery commitments.

Read-only, fixed queries. Native accounting filters are used only after a
complete-scope gate; row-limited report scopes fail closed, never widen.
"""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

import frappe
from frappe.query_builder import Case
from frappe.query_builder.functions import Coalesce, Count, Sum
from frappe.utils import getdate, now_datetime, today
from erpnext.accounts.report.financial_statements import apply_additional_conditions, get_account_filter_query
from erpnext.accounts.utils import FiscalYearError
from pypika.terms import ExistsCriterion

from sarathi_owner.api.finance_kpis import _complete_scope, decimal, native_report, normalize, ratio
from sarathi_visibility.api.access import allowed_fields, check_record, deny, require_capability
from sarathi_visibility.api.data_helpers import _date, _extra, _parse, invalid, pagination, read_errors


INCOME_FIELDS = {
	"GL Entry": {"name", "company", "posting_date", "account", "credit", "debit", "is_cancelled", "is_opening", "voucher_type", "voucher_no", "party_type", "party", "project", "cost_center", "finance_book"},
	"Sales Invoice": {"name", "company", "customer", "docstatus"},
	"Customer": {"name", "customer_name"},
}
BACKLOG_FIELDS = {
	"Sales Order": {"name", "company", "customer", "docstatus", "status", "transaction_date", "project"},
	"Sales Order Item": {"name", "parent", "parenttype", "parentfield", "item_code", "uom", "stock_uom", "qty", "delivered_qty", "conversion_factor", "base_net_rate", "delivery_date", "project"},
	"Customer": {"name", "customer_name"},
}
FEATURE_KEYS = {"interval", "top_limit", "start", "page_length", "backlog_start", "backlog_page_length", "order_status", "delivery_from", "delivery_to"}
BASE_KEYS = {"company", "from_date", "to_date", "customer", "project", "cost_center", "finance_book"}
EXCLUDED = ("Closed", "Stopped", "Cancelled", "Completed", "To Bill")
MAX_GROUPS = 20_000


def full_read(company, sources):
	"""Additional one-to-one attribution/child sources must also be wholly readable."""
	permissions = frappe.permissions.get_user_permissions(frappe.session.user)
	if frappe.session.user != "Administrator" and any(rows for dt, rows in permissions.items() if dt != "Company"):
		deny()
	for dt, fields in sources.items():
		meta = frappe.get_meta(dt)
		if not fields <= allowed_fields(dt):
			deny()
		if meta.istable or frappe.session.user == "Administrator":
			continue
		if not frappe.permissions.get_role_permissions(meta).get("read"):
			deny()
		if any(frappe.get_hooks(hook, {}).get(dt) for hook in ("has_permission", "permission_query_conditions")):
			deny()
		restrictions = [row for row in permissions.get("Company", []) if row.get("applicable_for") in (None, "", dt)]
		if restrictions and company not in {row.get("doc") for row in restrictions}:
			deny()


def validated(filters):
	values = _parse(filters)
	if set(values) - BASE_KEYS - FEATURE_KEYS:
		invalid("Unsupported customer/sales filter.")
	base = normalize({key: value for key, value in values.items() if key in BASE_KEYS})
	interval = values.get("interval") or "Monthly"
	if interval not in ("Daily", "Monthly"):
		invalid("Reporting interval must be Daily or Monthly.")
	if interval == "Daily" and (getdate(base["to_date"]) - getdate(base["from_date"])).days > 92:
		invalid("Daily reporting supports at most 93 calendar days.")
	start, length = pagination(values.get("start", 0), values.get("page_length", 25))
	backlog_start, backlog_length = pagination(values.get("backlog_start", 0), values.get("backlog_page_length", 25))
	_, top = pagination(0, values.get("top_limit", 5))
	if top > 20:
		invalid("Top Customers supports at most 20 results.")
	status = values.get("order_status") or ""
	statuses = (frappe.get_meta("Sales Order").get_field("status").options or "").splitlines()
	if status and (not isinstance(status, str) or status not in statuses or status in EXCLUDED):
		invalid("Select an open Sales Order status.")
	features = dict(interval=interval, top_limit=top, start=start, page_length=length,
		backlog_start=backlog_start, backlog_page_length=backlog_length, order_status=status)
	for key in ("delivery_from", "delivery_to"):
		if values.get(key):
			features[key] = _date(values[key])
	if features.get("delivery_from") and features.get("delivery_to") and features["delivery_from"] > features["delivery_to"]:
		invalid("Delivery dates must be ordered.")
	return base, features


def pnl_filters(base):
	filters = frappe._dict(company=base["company"], filter_based_on="Date Range", period_start_date=base["from_date"],
		period_end_date=base["to_date"], periodicity="Monthly", accumulated_values=0, include_default_book_entries=1)
	for key in ("project", "cost_center", "finance_book"):
		if base.get(key):
			filters[key] = [base[key]] if key != "finance_book" else base[key]
	if base.get("finance_book"):
		filters.include_default_book_entries = 0
	return filters


def income_groups(base):
	_complete_scope(base["company"], "Profit and Loss Statement")
	full_read(base["company"], INCOME_FIELDS)
	filters = pnl_filters(base)
	# Validate the same report configuration and permission contract as DASH-009.
	reference = native_report("Profit and Loss Statement", dict(filters))
	gl, invoice, customer = [frappe.qb.DocType(dt) for dt in ("GL Entry", "Sales Invoice", "Customer")]
	attribution = Case().when(gl.voucher_type == "Sales Invoice", invoice.customer).when(gl.party_type == "Customer", gl.party).else_("")
	query = (frappe.qb.from_(gl).left_join(invoice).on((gl.voucher_type == "Sales Invoice") & (gl.voucher_no == invoice.name) & (invoice.docstatus == 1) & (invoice.company == gl.company))
		.left_join(customer).on(customer.name == attribution)
		.select(Coalesce(customer.name, "").as_("customer"), Coalesce(customer.customer_name, "").as_("customer_name"), gl.posting_date,
			Sum(gl.credit - gl.debit).as_("amount"))
		.where((gl.company == base["company"]) & (gl.is_cancelled == 0) & (gl.posting_date <= base["to_date"]))
		.where(ExistsCriterion(get_account_filter_query(None, None, "Income", gl))))
	query = apply_additional_conditions("GL Entry", query, base["from_date"], True, filters)
	# Match installed P&L's opening-entry behavior: it calls get_data with
	# ignore_opening_entries=False. Do not impose an extra exclusion here.
	rows = query.groupby(customer.name, customer.customer_name, gl.posting_date).limit(MAX_GROUPS + 1).run(as_dict=True)
	if len(rows) > MAX_GROUPS:
		raise NotImplementedError("Too many customer/date groups; narrow the reporting period.")
	actual = sum((decimal(row.amount) for row in rows), Decimal(0))
	expected = decimal(reference[4][0]["value"])
	precision = int(frappe.db.get_default("currency_precision") or 2)
	if actual.quantize(Decimal(1).scaleb(-precision)) != expected.quantize(Decimal(1).scaleb(-precision)):
		raise NotImplementedError("Income attribution does not reconcile to native P&L for this configuration.")
	return rows, expected, dict(filters)


def periods(base, interval):
	current, end = getdate(base["from_date"]), getdate(base["to_date"])
	result = []
	while current <= end:
		key = str(current) if interval == "Daily" else current.strftime("%Y-%m")
		result.append({"period": key, "amount": Decimal(0)})
		current = current + timedelta(days=1) if interval == "Daily" else current.replace(year=current.year + (current.month == 12), month=current.month % 12 + 1, day=1)
	return result


def revenue(base, features):
	groups, accounting_total, reference_filters = income_groups(base)
	series = periods(base, features["interval"])
	by_period = {row["period"]: row for row in series}
	customers = {}
	unattributed = Decimal(0)
	for row in groups:
		if base.get("customer") and row.customer != base["customer"]:
			continue
		amount = decimal(row.amount)
		key = str(row.posting_date) if features["interval"] == "Daily" else str(row.posting_date)[:7]
		by_period[key]["amount"] += amount
		if not row.customer:
			unattributed += amount
		else:
			entry = customers.setdefault(row.customer, {"customer": row.customer, "customer_name": row.customer_name, "amount": Decimal(0)})
			entry["amount"] += amount
	rows = sorted(customers.values(), key=lambda row: (-row["amount"], row["customer"]))
	included = sum((row["amount"] for row in rows), Decimal(0))
	for rank, row in enumerate(rows, 1):
		row.update(rank=rank, share=ratio(row["amount"], included), amount=float(row["amount"]))
	for row in series:
		row["amount"] = float(row["amount"])
	start, length = features["start"], features["page_length"]
	return {"available": True, "rows": rows[start:start+length], "top_customers": rows[:features["top_limit"]],
		"has_next": start + length < len(rows), "customer_count": len(rows), "customer_total": float(included),
		"unattributed": float(unattributed), "included_income": float(included + unattributed), "company_accounting_income": float(accounting_total),
		"trend": series, "reference_filters": reference_filters,
		"basis": "P&L accounting income; submitted Sales Invoice customer, explicit GL Customer party, otherwise unattributed.",
		"share_basis": "Signed included customer income, excluding unattributed income; not limited to Top Customers."}


def backlog_query(base, features):
	full_read(base["company"], BACKLOG_FIELDS)
	if base.get("cost_center") or base.get("finance_book"):
		raise NotImplementedError("Delivery backlog does not support Cost Center or Finance Book.")
	order, item = [frappe.qb.DocType(dt) for dt in ("Sales Order", "Sales Order Item")]
	query = (frappe.qb.from_(order).join(item).on((item.parent == order.name) & (item.parenttype == "Sales Order") & (item.parentfield == "items"))
		.where((order.company == base["company"]) & (order.docstatus == 1) & order.status.notin(EXCLUDED))
		.where((item.qty > 0) & (item.delivered_qty < item.qty))
		.where(order.transaction_date[base["from_date"]:base["to_date"]]))
	if base.get("customer"):
		query = query.where(order.customer == base["customer"])
	if base.get("project"):
		project = Case().when((item.project.isnull()) | (item.project == ""), order.project).else_(item.project)
		query = query.where(project == base["project"])
	if features.get("order_status"):
		query = query.where(order.status == features["order_status"])
	if features.get("delivery_from"):
		query = query.where(item.delivery_date >= features["delivery_from"])
	if features.get("delivery_to"):
		query = query.where(item.delivery_date <= features["delivery_to"])
	remaining = item.qty - item.delivered_qty
	return query, order, item, remaining


def backlog(base, features):
	query, order, item, remaining = backlog_query(base, features)
	# Aggregate before pagination at item+stock-UOM+hold+due-state grain; never sum mixed quantities.
	held = Case().when(order.status == "On Hold", 1).else_(0)
	due = Case().when(item.delivery_date.isnull(), "Unknown").when(item.delivery_date < today(), "Overdue").else_("Upcoming")
	groups = (query.select(item.item_code, item.stock_uom, held.as_("held"), due.as_("due_state"),
		Sum(remaining * item.conversion_factor).as_("remaining_qty"), Sum(remaining * item.base_net_rate).as_("remaining_value"))
		.groupby(item.item_code, item.stock_uom, held, due).limit(MAX_GROUPS+1).run(as_dict=True))
	if len(groups) > MAX_GROUPS:
		raise NotImplementedError("Too many backlog item groups; narrow the filters.")
	invalid_lines = query.where((item.conversion_factor <= 0) | item.conversion_factor.isnull() | item.base_net_rate.isnull() | item.stock_uom.isnull() | (item.stock_uom == "")).select(item.name).limit(1).run()
	if invalid_lines:
		raise NotImplementedError("Backlog has missing quantity conversion, stock UOM or net base rate.")
	start, length = features["backlog_start"], features["backlog_page_length"]
	rows = (query.select(order.name.as_("sales_order"), order.customer, order.transaction_date, order.status,
		item.name.as_("line"), item.item_code, item.uom, item.stock_uom, item.conversion_factor, item.delivery_date, item.qty.as_("ordered_qty"), item.delivered_qty,
		(remaining * item.conversion_factor).as_("remaining_qty"), (remaining * item.base_net_rate).as_("remaining_value"))
		.orderby(order.name).orderby(item.name).offset(start).limit(length+1).run(as_dict=True))
	counts = query.select(order.status, Count(order.name).distinct().as_("order_count")).groupby(order.status).run(as_dict=True)
	value = held_value = overdue = Decimal(0)
	quantities = defaultdict(lambda: Decimal(0))
	for group in groups:
		amount = decimal(group.remaining_value)
		if group.held:
			held_value += amount
		else:
			value += amount
			quantities[(group.item_code, group.stock_uom)] += decimal(group.remaining_qty)
			if group.due_state == "Overdue":
				overdue += amount
	for row in rows:
		for key in ("remaining_qty", "remaining_value", "ordered_qty", "delivered_qty", "conversion_factor"):
			row[key] = float(decimal(row[key]))
		row["due_state"] = "Unknown" if not row.delivery_date else "Overdue" if str(row.delivery_date) < today() else "Upcoming"
		row["held"] = row.status == "On Hold"
	return {"available": True, "rows": rows[:length], "has_next": len(rows)>length,
		"remaining_value": float(value), "held_value": float(held_value), "overdue_value": float(overdue),
		"orders_by_status": [dict(row) for row in counts],
		"open_order_count": sum(row.order_count for row in counts if row.status != "On Hold"),
		"held_order_count": sum(row.order_count for row in counts if row.status == "On Hold"),
		"quantity_group_count": len(quantities), "quantities_has_next": len(quantities)>100,
		"quantities": [{"item_code": item_code, "stock_uom": uom, "remaining_qty": float(qty)} for (item_code,uom),qty in sorted(quantities.items())[:100]],
		"basis": "Current undelivered quantity × net base rate; excludes tax and held demand. Dates select order-date cohort; not historical revenue.",
		"source_as_of": str(now_datetime())}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_sales_analytics(filters=None, **extra):
	require_capability("owner")
	require_capability("finance")
	_extra(extra)
	base, features = validated(filters)
	company = check_record("Company", base["company"])
	if not {"default_currency", "default_finance_book"} <= allowed_fields("Company"):
		deny()
	result = {"applied_filters": {**base, **features}, "currency": company.default_currency, "generated_at": str(now_datetime())}
	for key, compute in (("revenue", revenue), ("backlog", backlog)):
		messages = list(getattr(frappe.local, "message_log", []) or [])
		try:
			result[key] = compute(base, features)
		except (frappe.PermissionError, NotImplementedError, FiscalYearError) as error:
			frappe.local.message_log = messages
			reason = str(error) if isinstance(error, NotImplementedError) else "This analytics section is unavailable for the selected permissions, fiscal period or configuration."
			result[key] = {"available": False, "reason": reason}
	return result
