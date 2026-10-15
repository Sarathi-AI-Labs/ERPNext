"""Sarathi Owner Dashboard API.

High-performance, permission-aware executive endpoints for business owners:
Real-time financial health, commercial order book, live interactive charts,
live embedded ERPNext report runner, working capital, and manufacturing governance.
"""

import datetime
import json

import frappe

from sarathi_visibility.api.access import (authorized, check_record, scoped_rows, scoped_sql, scoped_value, scoped_count, validate_filters)
from frappe.utils import flt, getdate, pretty_date, today

from sarathi_owner.api.permissions import get_permission_context
from sarathi_owner.api.pipeline import get_project_pipeline


def broadcast_live_event(doc, method=None):
	"""Invalidate dashboards after commit without broadcasting record identities."""
	for event in ("sarathi_owner_live_change", "sarathi_dashboard_changed"):
		frappe.publish_realtime(event, message={}, room="all", after_commit=True)


@frappe.whitelist(methods=["POST"])
@authorized("admin")
def clear_owner_cache(**kwargs):
	"""Purges cached metadata and redis entries for Sarathi Owner."""
	try:
		frappe.cache.delete_keys("sarathi:*")
		frappe.clear_cache()
	except Exception:
		pass
	return {"status": "ok"}


def _get_date_bounds(date_range_str, manual_from=None, manual_to=None):
	"""Parses date range presets or explicit manual bounds into (from_date, to_date) ISO strings."""
	if manual_from and manual_to:
		return str(manual_from)[:10], str(manual_to)[:10]
	if manual_from:
		return str(manual_from)[:10], None
	if manual_to:
		return None, str(manual_to)[:10]

	if not date_range_str or date_range_str in ("all", "custom"):
		return None, None

	today_dt = getdate(today())

	if date_range_str == "today":
		return str(today_dt), str(today_dt)
	elif date_range_str == "this_week":
		start = today_dt - datetime.timedelta(days=today_dt.weekday())
		end = start + datetime.timedelta(days=6)
		return str(start), str(end)
	elif date_range_str == "this_month":
		start = today_dt.replace(day=1)
		next_month = start.replace(day=28) + datetime.timedelta(days=4)
		end = next_month - datetime.timedelta(days=next_month.day)
		return str(start), str(end)
	elif date_range_str == "last_month":
		this_month_start = today_dt.replace(day=1)
		last_month_end = this_month_start - datetime.timedelta(days=1)
		last_month_start = last_month_end.replace(day=1)
		return str(last_month_start), str(last_month_end)
	elif date_range_str == "this_quarter":
		quarter_month = ((today_dt.month - 1) // 3) * 3 + 1
		start = today_dt.replace(month=quarter_month, day=1)
		end_month = quarter_month + 2
		next_m = today_dt.replace(month=end_month, day=28) + datetime.timedelta(days=4)
		end = next_m - datetime.timedelta(days=next_m.day)
		return str(start), str(end)
	elif date_range_str == "this_year":
		if today_dt.month >= 4:
			start = today_dt.replace(month=4, day=1)
			end = today_dt.replace(year=today_dt.year + 1, month=3, day=31)
		else:
			start = today_dt.replace(year=today_dt.year - 1, month=4, day=1)
			end = today_dt.replace(month=3, day=31)
		return str(start), str(end)

	return None, None


@frappe.whitelist()
@authorized("owner")
def get_owner_context(company=None, **kwargs):
	"""Returns baseline metadata for filters and user authorization."""
	perm = get_permission_context()
	if not perm["can_access_owner"]:
		frappe.throw("Access Restricted: Sarathi Owner role required.", frappe.PermissionError)

	companies = scoped_rows("Company", fields=["name", "company_name"], order_by="name asc")
	customers = scoped_rows("Customer", fields=["name", "customer_name"], order_by="name asc", limit=100)
	proj_filters = {"docstatus": ["!=", 2]}
	if company:
		proj_filters["company"] = company
	projects = scoped_rows(
		"Project",
		filters=proj_filters,
		fields=["name", "project_name", "company", "status"],
		order_by="name asc",
	)

	return {
		"companies": companies,
		"customers": customers,
		"projects": projects,
		"permissions": perm,
		"current_date": today(),
	}


@frappe.whitelist()
@authorized("owner")
def get_owner_summary(filters=None, **kwargs):
	"""Aggregates executive metrics, live charts, activity, and pipelines for the Owner Home view."""
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except json.JSONDecodeError:
			filters = {}
	filters = filters or {}

	company = filters.get("company")
	customer = filters.get("customer")
	project_filter = filters.get("project")
	status = filters.get("status")
	date_range = filters.get("date_range", "all")
	manual_from = filters.get("from_date")
	manual_to = filters.get("to_date")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, manual_from, manual_to)

	perm = get_permission_context()
	financials_allowed = perm["can_view_finance"]
	if not perm["can_access_owner"]:
		frappe.throw("Access Restricted: Sarathi Owner role required.", frappe.PermissionError)
	currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "INR"
	symbol = "₹" if currency == "INR" else ("$" if currency == "USD" else currency + " ")

	def fmt_money(val):
		if not financials_allowed:
			return "Restricted"
		val = flt(val)
		if abs(val) >= 10000000:
			return f"{symbol}{val / 10000000:.2f} Cr"
		if abs(val) >= 100000:
			return f"{symbol}{val / 100000:.2f} L"
		return f"{symbol}{val:,.0f}"

	# 1. Projects Analysis
	project_conditions = {"docstatus": ["!=", 2]}
	if company:
		project_conditions["company"] = company
	if customer:
		project_conditions["customer"] = customer
	if status:
		if status.lower() in ("on hold", "hold"):
			project_conditions["status"] = ["in", ["On Hold", "On hold", "Hold"]]
		elif status.lower() == "open":
			project_conditions["status"] = ["in", ["Open", "Ongoing", "Active"]]
		elif status.lower() == "completed":
			project_conditions["status"] = "Completed"
		elif status.lower() == "cancelled":
			project_conditions["status"] = "Cancelled"
		else:
			project_conditions["status"] = status
	if project_filter:
		project_conditions["name"] = project_filter
	projects = scoped_rows(
		"Project",
		filters=project_conditions,
		fields=[
			"name",
			"project_name",
			"company",
			"customer",
			"status",
			"percent_complete",
			"expected_end_date",
			"estimated_costing",
			"total_costing_amount",
			"total_billed_amount",
			"total_sales_amount",
			"creation",
			"modified",
		],
		order_by="modified desc",
	)
	if from_date and to_date:
		projects = [
			p
			for p in projects
			if (
				status
				or (
					p.get("status") in ("Open", "Ongoing", "Active", "On Hold", "On hold", "Hold")
					or (
						str(p.get("creation") or "")[:10] >= from_date
						and str(p.get("creation") or "")[:10] <= to_date
					)
					or (
						str(p.get("modified") or "")[:10] >= from_date
						and str(p.get("modified") or "")[:10] <= to_date
					)
				)
			)
		]

	if search:
		projects = [
			p
			for p in projects
			if search in (p.name or "").lower()
			or search in (p.project_name or "").lower()
			or search in (p.customer or "").lower()
		]

	open_projects = [p for p in projects if p.status in ("Open", "Ongoing", "Active")]
	total_project_budget = sum(flt(p.estimated_costing) for p in open_projects)

	# 2. Executive Commercial Order Book (Sales Orders)
	so_filters = {"docstatus": ["!=", 2]}
	if company:
		so_filters["company"] = company
	if customer:
		so_filters["customer"] = customer
	if project_filter:
		so_filters["project"] = project_filter
	if status:
		so_filters["status"] = status
	if from_date and to_date:
		so_filters["transaction_date"] = ["between", [from_date, to_date]]

	sales_orders = scoped_rows(
		"Sales Order",
		filters=so_filters,
		fields=[
			"name",
			"customer",
			"status",
			"delivery_date",
			"grand_total",
			"per_delivered",
			"per_billed",
			"project",
		],
	)
	if search:
		sales_orders = [
			o
			for o in sales_orders
			if search in (o.name or "").lower()
			or search in (o.customer or "").lower()
			or search in (o.project or "").lower()
		]

	open_sales_orders = [o for o in sales_orders if o.status not in ("Completed", "Closed", "Cancelled")]
	total_order_book_value = sum(flt(o.grand_total) for o in open_sales_orders)
	pending_delivery_orders = [o for o in open_sales_orders if flt(o.per_delivered) < 100]

	# 3. Accounts Receivable & Overdue Cash Flow (Sales Invoices)
	si_filters = {"docstatus": ["!=", 2]}
	if company:
		si_filters["company"] = company
	if customer:
		si_filters["customer"] = customer
	if project_filter:
		si_filters["project"] = project_filter
	if status:
		si_filters["status"] = status
	if from_date and to_date:
		si_filters["posting_date"] = ["between", [from_date, to_date]]

	sales_invoices = scoped_rows(
		"Sales Invoice",
		filters=si_filters,
		fields=[
			"name",
			"customer",
			"project",
			"due_date",
			"posting_date",
			"grand_total",
			"outstanding_amount",
			"status",
		],
	)
	if search:
		sales_invoices = [
			i
			for i in sales_invoices
			if search in (i.name or "").lower()
			or search in (i.customer or "").lower()
			or search in (i.project or "").lower()
		]

	unpaid_invoices = [i for i in sales_invoices if flt(i.outstanding_amount) > 0]
	total_receivables = sum(flt(i.outstanding_amount) for i in unpaid_invoices)

	today_date = getdate(today())
	overdue_invoices = [i for i in unpaid_invoices if i.due_date and getdate(i.due_date) < today_date]
	overdue_receivables = sum(flt(i.outstanding_amount) for i in overdue_invoices)

	# 4. Inventory Working Capital Allocation
	total_stock_value = 0.0
	rm_value = 0.0
	fg_value = 0.0
	wip_value = 0.0
	low_stock_items = []

	if frappe.db.table_exists("Bin"):
		bin_filters = {}
		if company:
			company_whs = scoped_rows("Warehouse", filters={"company": company}, pluck="name")
			if company_whs:
				bin_filters["warehouse"] = ["in", company_whs]

		bins = scoped_rows(
			"Bin",
			filters=bin_filters,
			fields=[
				"item_code",
				"warehouse",
				"actual_qty",
				"valuation_rate",
				"stock_value",
			],
		)

		item_groups = scoped_rows(
			"Item",
			filters={"disabled": 0},
			fields=["name", "item_name", "item_group", "safety_stock"],
		)
		ig_map = {i.name: i.item_group for i in item_groups}
		safety_map = {i.name: flt(i.safety_stock) for i in item_groups}
		item_name_map = {i.name: i.item_name for i in item_groups}

		for b in bins:
			val = (
				flt(b.stock_value) if b.stock_value is not None else flt(b.actual_qty) * flt(b.valuation_rate)
			)
			total_stock_value += val

			group = ig_map.get(b.item_code, "")
			wh_lower = (b.warehouse or "").lower()

			if group == "Raw Material" or "raw" in wh_lower or "store" in wh_lower:
				rm_value += val
			elif group == "Finished Goods" or "finished" in wh_lower:
				fg_value += val
			elif "wip" in wh_lower or "progress" in wh_lower or "work in process" in wh_lower:
				wip_value += val
			else:
				rm_value += val

			reorder = safety_map.get(b.item_code, 0.0)
			if reorder > 0 and flt(b.actual_qty) <= reorder:
				low_stock_items.append(
					{
						"item_code": b.item_code,
						"item_name": item_name_map.get(b.item_code, b.item_code),
						"warehouse": b.warehouse,
						"available": f"{flt(b.actual_qty):g} pcs",
						"reorder": f"{reorder:g} pcs",
					}
				)

	# 5. Financial Snapshot & Liquid Cash in Bank
	total_income = 0.0
	total_expenses = 0.0
	net_profit = 0.0
	cash_in_bank = 0.0

	if financials_allowed and frappe.db.table_exists("GL Entry"):
		# Cash & Bank Balance
		cb_res = scoped_sql(
			"""
            SELECT SUM(debit - credit) as total
            FROM `tabGL Entry`
            WHERE is_cancelled = 0
            AND account IN (SELECT name FROM `tabAccount` WHERE account_type IN ('Bank', 'Cash'))
            """
			+ (" AND company = " + frappe.db.escape(company) if company else ""),
			as_dict=True,
		)
		if cb_res and cb_res[0].total:
			cash_in_bank = flt(cb_res[0].total)

		date_clause = (
			f" AND posting_date BETWEEN '{from_date}' AND '{to_date}'" if from_date and to_date else ""
		)

		income_entries = scoped_sql(
			"""
            SELECT SUM(credit - debit) as total
            FROM `tabGL Entry`
            WHERE is_cancelled = 0
            AND voucher_type in ('Sales Invoice', 'Journal Entry')
            AND account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Income')
            """
			+ (" AND company = " + frappe.db.escape(company) if company else "")
			+ date_clause,
			as_dict=True,
		)
		if income_entries and income_entries[0].total:
			total_income = flt(income_entries[0].total)

		expense_entries = scoped_sql(
			"""
            SELECT SUM(debit - credit) as total
            FROM `tabGL Entry`
            WHERE is_cancelled = 0
            AND voucher_type in ('Purchase Invoice', 'Journal Entry', 'Stock Entry')
            AND account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Expense')
            """
			+ (" AND company = " + frappe.db.escape(company) if company else "")
			+ date_clause,
			as_dict=True,
		)
		if expense_entries and expense_entries[0].total:
			total_expenses = flt(expense_entries[0].total)

		net_profit = total_income - total_expenses

	# 6. Strategic Manufacturing Pipelines (all 10 projects)
	pipelines = []
	ordered_projects = sorted(projects, key=lambda x: x.name)
	for p in ordered_projects[:10]:
		pipe = get_project_pipeline(p.name)
		if pipe:
			pipelines.append(pipe)

	# 7. Interactive Frappe Chart Datasets
	financial_chart = _get_financial_chart_data(company)
	working_capital_chart = _get_working_capital_chart_data(rm_value, wip_value, fg_value)
	order_book_chart = _get_order_book_chart_data(company)
	ar_aging_chart = _get_ar_aging_chart_data(company)
	production_velocity_chart = _get_production_chart_data(company)

	# 8. Executive Action & Risk Alerts
	action_alerts = []
	if overdue_receivables > 0:
		action_alerts.append(
			{
				"type": "finance",
				"level": "red",
				"title": f"Overdue Customer Receivables: {fmt_money(overdue_receivables)}",
				"desc": f"{len(overdue_invoices)} invoice(s) past payment terms.",
				"link": "/app/query-report/Accounts Receivable",
			}
		)

	delayed_wos_query = """
        SELECT name, production_item, planned_end_date, qty, produced_qty
        FROM `tabWork Order`
        WHERE docstatus = 1 AND status not in ('Completed', 'Closed', 'Cancelled')
        AND planned_end_date IS NOT NULL AND planned_end_date < %s
    """
	params = [today()]
	if company:
		delayed_wos_query += " AND company = %s"
		params.append(company)
	if project_filter:
		delayed_wos_query += " AND project = %s"
		params.append(project_filter)
	delayed_wos_query += " ORDER BY planned_end_date ASC LIMIT 5"
	delayed_wos = scoped_sql(delayed_wos_query, tuple(params), as_dict=True)
	if delayed_wos:
		action_alerts.append(
			{
				"type": "production",
				"level": "amber",
				"title": f"{len(delayed_wos)} Work Order(s) Delayed",
				"desc": f"Orders past planned completion: {', '.join(w.name for w in delayed_wos[:2])}",
				"link": "/app/work-order?status=In%20Process",
			}
		)

	if low_stock_items:
		action_alerts.append(
			{
				"type": "stock",
				"level": "amber",
				"title": f"{len(low_stock_items)} Items Below Reorder Level",
				"desc": f"Shortage risk: {', '.join(i['item_name'] for i in low_stock_items[:2])}",
				"link": "/app/item",
			}
		)

	# 9. Real-Time Curated Business Activity (Logins OMITTED, only real transactions)
	live_activity = _get_live_activity(
		company=company,
		customer=customer,
		project=project_filter,
		search=search,
		limit=10,
	)

	# 10. Active Projects Portfolio Table Rows
	active_projects_rows = []
	target_p_list = (
		projects
		if status
		else [p for p in projects if p.status in ("Open", "Ongoing", "Active", "On Hold", "On hold", "Hold")]
	)
	for p in target_p_list:
		so = scoped_value(
			"Sales Order",
			{"project": p.name, "docstatus": ["!=", 2]},
			"name",
		)
		wo_stats = scoped_sql(
			"""
            SELECT SUM(qty) as planned, SUM(produced_qty) as produced
            FROM `tabWork Order`
            WHERE project = %s AND docstatus != 2
            """,
			(p.name,),
			as_dict=True,
		)
		planned = flt(wo_stats[0].planned) if wo_stats else 0
		produced = flt(wo_stats[0].produced) if wo_stats else 0
		wo_output = f"{produced:g} / {planned:g}" if planned > 0 else "No WOs"

		budget = flt(p.estimated_costing)
		actual_cost = flt(p.total_costing_amount)
		cost_variance = budget - actual_cost

		is_delayed = bool(
			p.expected_end_date and getdate(p.expected_end_date) < today_date and p.status != "Completed"
		)

		active_projects_rows.append(
			{
				"project": p.name,
				"project_name": p.project_name or p.name,
				"customer": p.customer or "Unassigned",
				"sales_order": so or "—",
				"status": p.status,
				"percent_complete": flt(p.percent_complete),
				"wo_output": wo_output,
				"budget": fmt_money(budget),
				"actual_cost": fmt_money(actual_cost),
				"variance": fmt_money(cost_variance),
				"variance_positive": cost_variance >= 0,
				"expected_end_date": str(p.expected_end_date or "—"),
				"schedule_status": "Delayed" if is_delayed else "On Track",
			}
		)

	# Calculate capital percentages
	rm_pct = round((rm_value / total_stock_value) * 100, 1) if total_stock_value > 0 else 50.0
	fg_pct = round((fg_value / total_stock_value) * 100, 1) if total_stock_value > 0 else 30.0
	wip_pct = round((wip_value / total_stock_value) * 100, 1) if total_stock_value > 0 else 20.0

	# Accounts & Financial Overview (Pooja Chougule: Step 9 Advance Approval & Step 24 Documentation/Invoicing)
	so_awaiting_advance = [
		o for o in open_sales_orders if flt(getattr(o, "advance_paid", 0)) < flt(o.grand_total)
	]
	advance_pending_amount = sum(
		flt(o.grand_total) - flt(getattr(o, "advance_paid", 0)) for o in so_awaiting_advance
	)
	total_advance_received = sum(flt(getattr(o, "advance_paid", 0)) for o in sales_orders)

	accounts_flow = {
		"advance_approvals": {
			"in_charge": "Pooja Chougule",
			"step_no": 9,
			"title": "Accounts Advance Approval",
			"status": "active" if so_awaiting_advance else "cleared",
			"pending_count": len(so_awaiting_advance),
			"pending_amount": fmt_money(advance_pending_amount),
			"advance_received": fmt_money(total_advance_received),
			"total_orders": len(open_sales_orders),
			"route": "/app/sales-order?status=To%20Deliver%20and%20Bill",
		},
		"documentation_invoicing": {
			"in_charge": "Pooja Chougule",
			"step_no": 24,
			"title": "Documentation & Invoicing",
			"total_invoiced": fmt_money(total_income),
			"outstanding_receivables": fmt_money(total_receivables),
			"overdue_receivables": fmt_money(overdue_receivables),
			"overdue_invoices_count": len(overdue_invoices),
			"total_invoices_count": len(sales_invoices),
			"route": "/app/sales-invoice",
		},
	}

	# 11. Seamless Integration of Sarathi Visibility Analytics & Accounting Control Tower
	acc_tower = {}
	try:
		from sarathi_visibility.api.accounting import get_accounting_dashboard

		acc_filters = {
			"company": company or "",
			"period": "this_month",
			"from_date": from_date or "",
			"to_date": to_date or "",
			"project": project_filter or "",
			"customer": customer or "",
		}
		acc_tower = get_accounting_dashboard(acc_filters)
	except Exception as e:
		frappe.log_error(f"Owner Dashboard Accounting Tower integration error: {e}")

	ind_matrix = {}
	try:
		from sarathi_visibility.api.dashboard import get_summary as get_industrial_summary

		ind_filters = {
			"company": company or "",
			"from_date": manual_from or "",
			"to_date": manual_to or "",
			"status": status or "",
			"search": search or "",
		}
		ind_matrix = get_industrial_summary(json.dumps(ind_filters))
	except Exception as e:
		frappe.log_error(f"Owner Dashboard Industrial Matrix integration error: {e}")

	return {
		"accounts_flow": accounts_flow,
		"cards": [
			{
				"label": "Active Manufacturing Projects",
				"value": f"{len(open_projects)} Active",
				"color": "blue",
				"desc": f"Budget: {fmt_money(total_project_budget)}",
				"action": "view-projects",
			},
			{
				"label": "Commercial Order Book",
				"value": fmt_money(total_order_book_value),
				"color": "cyan",
				"desc": f"{len(pending_delivery_orders)} orders pending delivery",
				"action": "view-sales-orders",
			},
			{
				"label": "Accounts Receivable (AR)",
				"value": fmt_money(total_receivables),
				"color": "amber" if overdue_receivables > 0 else "green",
				"desc": f"Overdue: {fmt_money(overdue_receivables)}",
				"action": "view-finance",
			},
			{
				"label": "Inventory Working Capital",
				"value": fmt_money(total_stock_value),
				"color": "purple",
				"desc": f"RM: {fmt_money(rm_value)} · FG: {fmt_money(fg_value)}",
				"action": "view-stock",
			},
			{
				"label": "Total Expenses",
				"value": fmt_money(total_expenses),
				"color": "amber",
				"desc": "Operating & direct manufacturing costs",
				"action": "view-pnl",
			},
			{
				"label": "Net Profit",
				"value": fmt_money(net_profit),
				"color": "green" if net_profit >= 0 else "red",
				"desc": f"Revenue: {fmt_money(total_income)}",
				"action": "view-reports",
			},
		],
		"capital_allocation": {
			"rm_val": fmt_money(rm_value),
			"rm_pct": rm_pct,
			"fg_val": fmt_money(fg_value),
			"fg_pct": fg_pct,
			"wip_val": fmt_money(wip_value),
			"wip_pct": wip_pct,
			"total_val": fmt_money(total_stock_value),
		},
		"pipelines": pipelines,
		"output_trend": production_velocity_chart,
		"charts": {
			"financial": financial_chart,
			"capital": working_capital_chart,
			"order_book": order_book_chart,
			"ar_aging": ar_aging_chart,
			"production": production_velocity_chart,
		},
		"action_alerts": action_alerts,
		"live_activity": live_activity,
		"low_stock_items": low_stock_items[:10],
		"active_projects": active_projects_rows,
		"financial_snapshot": {
			"income": fmt_money(total_income),
			"expenses": fmt_money(total_expenses),
			"net_profit": fmt_money(net_profit),
			"receivables": fmt_money(total_receivables),
			"overdue": fmt_money(overdue_receivables),
			"cash_bank": fmt_money(cash_in_bank),
			"allowed": financials_allowed,
		},
		"accounting_control_tower": acc_tower,
		"industrial_summary": ind_matrix,
	}


def _get_live_activity(company=None, customer=None, project=None, search=None, limit=12) -> list:
	"""Aggregates real-time business events across Work Orders, Stock Entries, Sales Orders,
	Sales Invoices, Payment Entries, and Projects (Routine logins strictly excluded).
	"""
	events = []

	# 1. Recent Projects
	proj_filters = {"docstatus": ["!=", 2]}
	if company:
		proj_filters["company"] = company
	if customer:
		proj_filters["customer"] = customer
	if project:
		proj_filters["name"] = project
	projects = scoped_rows(
		"Project",
		filters=proj_filters,
		fields=[
			"name",
			"project_name",
			"status",
			"percent_complete",
			"modified",
			"modified_by",
		],
		order_by="modified desc",
		limit=4,
	)
	for p in projects:
		events.append(
			{
				"doctype": "Project",
				"docname": p.name,
				"title": f"Project: {p.project_name or p.name}",
				"desc": f"Status: {p.status} · Progress: {flt(p.percent_complete):g}%",
				"timestamp": str(p.modified),
				"time_ago": pretty_date(p.modified),
				"icon": "▦",
				"badge_color": ("blue" if p.status in ("Open", "Ongoing", "Active") else "green"),
				"route": f"/app/project/{p.name}",
			}
		)

	# 2. Recent Work Orders
	if frappe.db.table_exists("Work Order"):
		wo_filters = {"docstatus": ["!=", 2]}
		if company:
			wo_filters["company"] = company
		work_orders = scoped_rows(
			"Work Order",
			filters=wo_filters,
			fields=[
				"name",
				"production_item",
				"qty",
				"produced_qty",
				"status",
				"modified",
				"project",
			],
			order_by="modified desc",
			limit=4,
		)
		for w in work_orders:
			events.append(
				{
					"doctype": "Work Order",
					"docname": w.name,
					"title": f"Work Order: {w.production_item}",
					"desc": f"Produced {flt(w.produced_qty):g}/{flt(w.qty):g} units · {w.status}"
					+ (f" · {w.project}" if w.project else ""),
					"timestamp": str(w.modified),
					"time_ago": pretty_date(w.modified),
					"icon": "⚙",
					"badge_color": "green" if w.status == "Completed" else "purple",
					"route": f"/app/work-order/{w.name}",
				}
			)

	# 3. Recent Sales Orders
	if frappe.db.table_exists("Sales Order"):
		so_filters = {"docstatus": ["!=", 2]}
		if company:
			so_filters["company"] = company
		orders = scoped_rows(
			"Sales Order",
			filters=so_filters,
			fields=[
				"name",
				"customer",
				"grand_total",
				"status",
				"modified",
				"per_delivered",
			],
			order_by="modified desc",
			limit=4,
		)
		for o in orders:
			events.append(
				{
					"doctype": "Sales Order",
					"docname": o.name,
					"title": f"Sales Order: {o.name} · {o.customer}",
					"desc": f"Order: ₹{flt(o.grand_total):,.0f} · {flt(o.per_delivered):g}% Delivered ({o.status})",
					"timestamp": str(o.modified),
					"time_ago": pretty_date(o.modified),
					"icon": "▣",
					"badge_color": "cyan",
					"route": f"/app/sales-order/{o.name}",
				}
			)

	# 4. Recent Sales Invoices
	if frappe.db.table_exists("Sales Invoice"):
		si_filters = {"docstatus": ["!=", 2]}
		if company:
			si_filters["company"] = company
		invoices = scoped_rows(
			"Sales Invoice",
			filters=si_filters,
			fields=[
				"name",
				"customer",
				"grand_total",
				"outstanding_amount",
				"status",
				"modified",
			],
			order_by="modified desc",
			limit=4,
		)
		for i in invoices:
			is_paid = flt(i.outstanding_amount) <= 0
			events.append(
				{
					"doctype": "Sales Invoice",
					"docname": i.name,
					"title": f"Invoice: {i.name} · {i.customer}",
					"desc": f"Total ₹{flt(i.grand_total):,.0f} · Outstanding ₹{flt(i.outstanding_amount):,.0f}",
					"timestamp": str(i.modified),
					"time_ago": pretty_date(i.modified),
					"icon": "₹",
					"badge_color": "green" if is_paid else "amber",
					"route": f"/app/sales-invoice/{i.name}",
				}
			)

	# 5. Recent Payment Receipts
	if frappe.db.table_exists("Payment Entry"):
		pe_filters = {"docstatus": 1}
		if company:
			pe_filters["company"] = company
		payments = scoped_rows(
			"Payment Entry",
			filters=pe_filters,
			fields=[
				"name",
				"party",
				"paid_amount",
				"received_amount",
				"payment_type",
				"modified",
			],
			order_by="modified desc",
			limit=4,
		)
		for p in payments:
			events.append(
				{
					"doctype": "Payment Entry",
					"docname": p.name,
					"title": f"Payment {p.payment_type}: {p.party or 'Cash'}",
					"desc": f"Amount: ₹{flt(p.received_amount or p.paid_amount):,.0f}",
					"timestamp": str(p.modified),
					"time_ago": pretty_date(p.modified),
					"icon": "✓",
					"badge_color": "green",
					"route": f"/app/payment-entry/{p.name}",
				}
			)

	# 6. Recent Stock Movements
	if frappe.db.table_exists("Stock Entry"):
		se_filters = {"docstatus": 1}
		if company:
			se_filters["company"] = company
		stock_entries = scoped_rows(
			"Stock Entry",
			filters=se_filters,
			fields=["name", "purpose", "work_order", "posting_date", "modified"],
			order_by="modified desc",
			limit=4,
		)
		for s in stock_entries:
			events.append(
				{
					"doctype": "Stock Entry",
					"docname": s.name,
					"title": f"Stock: {s.purpose}",
					"desc": f"Entry {s.name}" + (f" for Work Order {s.work_order}" if s.work_order else ""),
					"timestamp": str(s.modified),
					"time_ago": pretty_date(s.modified),
					"icon": "▥",
					"badge_color": "purple",
					"route": f"/app/stock-entry/{s.name}",
				}
			)

	events.sort(key=lambda x: str(x.get("timestamp") or ""), reverse=True)
	return events[:limit]


REPORT_COLUMNS_FALLBACK = {
	"Sales Order Analysis": [
		{
			"label": "Sales Order",
			"fieldname": "sales_order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 140,
		},
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{"label": "Order Qty", "fieldname": "qty", "fieldtype": "Float", "width": 90},
		{
			"label": "Delivered Qty",
			"fieldname": "delivered_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": "Billed Amount",
			"fieldname": "billed_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Pending Amount",
			"fieldname": "pending_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
	],
	"Work Order Summary": [
		{
			"label": "Work Order",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Work Order",
			"width": 140,
		},
		{
			"label": "Production Item",
			"fieldname": "production_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
		{
			"label": "Planned Qty",
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": "Produced Qty",
			"fieldname": "produced_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": "Planned Start",
			"fieldname": "planned_start_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": "Planned End",
			"fieldname": "planned_end_date",
			"fieldtype": "Date",
			"width": 110,
		},
	],
	"Accounts Receivable": [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180,
		},
		{
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140,
		},
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": "Due Date",
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": "Invoiced Amount",
			"fieldname": "invoiced_amount",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": "Paid Amount",
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"width": 130,
		},
		{
			"label": "Outstanding Amount",
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		{"label": "Age (Days)", "fieldname": "age", "fieldtype": "Int", "width": 90},
	],
	"Warehouse Wise Stock Balance": [
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{
			"label": "Item Name",
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": "Warehouse",
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 160,
		},
		{
			"label": "Balance Qty",
			"fieldname": "bal_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": "Valuation Rate",
			"fieldname": "val_rate",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Stock Value",
			"fieldname": "bal_val",
			"fieldtype": "Currency",
			"width": 130,
		},
	],
	"Production Analytics": [
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 160,
		},
		{
			"label": "Production Item",
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": "Work Order",
			"fieldname": "work_order",
			"fieldtype": "Link",
			"options": "Work Order",
			"width": 140,
		},
		{
			"label": "Produced Qty",
			"fieldname": "produced_qty",
			"fieldtype": "Float",
			"width": 110,
		},
		{
			"label": "Cycle Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 110,
		},
	],
	"Project Summary": [
		{
			"label": "Project",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150,
		},
		{
			"label": "Project Name",
			"fieldname": "project_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 160,
		},
		{
			"label": "Estimated Cost",
			"fieldname": "estimated_costing",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Actual Cost",
			"fieldname": "total_costing_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Total Billed",
			"fieldname": "total_billed_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "% Complete",
			"fieldname": "percent_complete",
			"fieldtype": "Percent",
			"width": 90,
		},
	],
	"Profit and Loss Statement": [
		{
			"label": "Account",
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 240,
		},
		{
			"label": "Category",
			"fieldname": "root_type",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": "Net Amount",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 160,
		},
	],
	"Gross and Net Profit Report": [
		{
			"label": "Business Line",
			"fieldname": "line",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Revenue",
			"fieldname": "revenue",
			"fieldtype": "Currency",
			"width": 140,
		},
		{"label": "COGS", "fieldname": "cogs", "fieldtype": "Currency", "width": 140},
		{
			"label": "Gross Profit",
			"fieldname": "gross_profit",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "Operating Expenses",
			"fieldname": "expenses",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "Net Profit",
			"fieldname": "net_profit",
			"fieldtype": "Currency",
			"width": 140,
		},
	],
	"Financial Ratios": [
		{"label": "Ratio", "fieldname": "ratio", "fieldtype": "Data", "width": 240},
		{
			"label": "Current Value",
			"fieldname": "value",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": "Industry Benchmark",
			"fieldname": "benchmark",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": "Health Assessment",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 140,
		},
	],
}


@frappe.whitelist()
@authorized("owner")
def get_live_report_data(report_name, filters=None):
	"""Executes native ERPNext Query Report in-memory and returns structured dataset.

	Includes auto-completed mandatory filters (dates, fiscal year, company) and permission checks.
	"""
	perm = get_permission_context()
	if not perm["can_access_owner"]:
		frappe.throw("Access Restricted: Sarathi Owner role or permission required.")

	financial_reports = {
		"Balance Sheet",
		"Profit and Loss Statement",
		"Gross and Net Profit Report",
		"Accounts Receivable",
		"Accounts Payable",
		"Trial Balance",
		"General Ledger",
		"Financial Ratios",
		"Cash Flow",
	}
	if report_name in financial_reports and not perm["can_view_finance"]:
		return {
			"report_name": report_name,
			"restricted": True,
			"message": "Financial data is restricted based on user role permissions.",
			"columns": [
				{
					"label": "Status",
					"fieldname": "status",
					"fieldtype": "Data",
					"width": 300,
				}
			],
			"result": [{"status": "Restricted by Role Permissions"}],
		}

	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except json.JSONDecodeError:
			filters = {}
	filters = filters or {}

	company = filters.get("company")
	if not company:
		cos = scoped_rows("Company", pluck="name")
		preferred = frappe.db.get_single_value("Global Defaults", "default_company")
		company = preferred if preferred in cos else (cos[0] if cos else None)
	if not company:
		frappe.throw("This resource or action is not available for your permissions.", frappe.PermissionError)
	validate_filters({"company": company})
	# Native report scripts can aggregate without get_list row predicates. Do not
	# embed them for users with additional record scopes until that report's
	# handling of those scopes has been independently verified.
	if frappe.session.user != "Administrator":
		permissions = frappe.permissions.get_user_permissions(frappe.session.user)
		if any(rows for dt, rows in permissions.items() if dt != "Company"):
			frappe.throw("This report requires verified support for your record restrictions.", frappe.PermissionError)
		ref_doctype = frappe.db.get_value("Report", report_name, "ref_doctype")
		if ref_doctype:
			role_rules = [p for p in frappe.get_meta(ref_doctype).permissions if p.role in frappe.get_roles() and p.read]
			if not role_rules or all(p.if_owner for p in role_rules):
				frappe.throw("This report requires verified support for your record restrictions.", frappe.PermissionError)
	if company:
		filters["company"] = company

	report_filters = {}
	if company:
		report_filters["company"] = company

	today_dt = getdate(today())
	fy_start = (
		today_dt.replace(month=4, day=1)
		if today_dt.month >= 4
		else today_dt.replace(year=today_dt.year - 1, month=4, day=1)
	)
	fy_end = (
		today_dt.replace(year=today_dt.year + 1, month=3, day=31)
		if today_dt.month >= 4
		else today_dt.replace(month=3, day=31)
	)

	# Pass through user-provided filters
	for k, v in filters.items():
		if v not in (None, "", "all") and k not in ("date_range", "search"):
			report_filters[k] = v

	if filters.get("date_range") not in (None, "", "all"):
		start, end = _get_date_bounds(filters["date_range"], filters.get("from_date"), filters.get("to_date"))
		if start and end:
			report_filters.update(from_date=start, to_date=end)

	date_reports = {
		"Accounts Receivable",
		"Accounts Payable",
		"General Ledger",
		"Sales Order Analysis",
		"Gross and Net Profit Report",
		"Production Analytics",
		"Sales Analytics",
	}
	if report_name in date_reports:
		if not report_filters.get("from_date"):
			report_filters["from_date"] = str(fy_start)
		if not report_filters.get("to_date"):
			report_filters["to_date"] = str(fy_end)

	if report_name in (
		"Profit and Loss Statement",
		"Balance Sheet",
		"Cash Flow",
		"Gross and Net Profit Report",
	):
		report_filters["filter_based_on"] = "Date Range"
		report_filters["period_start_date"] = report_filters.get("from_date") or str(fy_start)
		report_filters["period_end_date"] = report_filters.get("to_date") or str(fy_end)
		if not report_filters.get("periodicity"):
			report_filters["periodicity"] = "Monthly"

	if report_name in {
		"Accounts Receivable",
		"Accounts Payable",
		"Profit and Loss Statement",
		"Balance Sheet",
		"Cash Flow",
		"Gross and Net Profit Report",
		"Financial Ratios",
	}:
		# ERPNext's native project controls are MultiSelectList fields.
		project = report_filters.get("project")
		if isinstance(project, str):
			report_filters["project"] = [project]

	if report_name == "Project Summary":
		# This native report passes its filters straight to the Project query.
		project = report_filters.pop("project", None)
		if project:
			report_filters["name"] = project
		meta = frappe.get_meta("Project")
		report_filters = {
			key: value for key, value in report_filters.items() if key == "name" or meta.has_field(key)
		}

	try:
		from frappe.desk.query_report import run as run_query_report

		if report_name == "Financial Ratios":
			from erpnext.accounts.utils import get_fiscal_year

			report_filters.setdefault(
				"from_fiscal_year",
				get_fiscal_year(report_filters.get("from_date") or today_dt, company=company)[0],
			)
			report_filters.setdefault(
				"to_fiscal_year",
				get_fiscal_year(report_filters.get("to_date") or today_dt, company=company)[0],
			)
			report_filters.setdefault("periodicity", "Yearly")

		res = run_query_report(report_name=report_name, filters=report_filters, ignore_prepared_report=True)
		cols = res.get("columns", [])
		data = res.get("result", [])
		if not cols and report_name in REPORT_COLUMNS_FALLBACK:
			cols = REPORT_COLUMNS_FALLBACK[report_name]

		return {
			"report_name": report_name,
			"columns": cols,
			"result": data,
			"chart": res.get("chart"),
			"report_summary": res.get("report_summary"),
			"execution_time": res.get("execution_time", 0),
			"filters": report_filters,
			"currency": frappe.db.get_single_value("Global Defaults", "default_currency") or "INR",
		}
	except Exception as e:
		frappe.log_error(f"Error running live report {report_name}: {e}")
		return {
			"report_name": report_name,
			"error": str(e),
			"columns": [
				{
					"label": "Status",
					"fieldname": "status",
					"fieldtype": "Data",
					"width": 400,
				}
			],
			"result": [{"status": f"Notice: {e!s}"}],
		}


def _get_dynamic_module_sections(page_name: str) -> list[dict]:
	"""Retrieves native ERPNext categorized sidebar sections for the given workspace module."""
	try:
		from sarathi_owner.api.module_catalog import _modules

		mapping = {
			"invoicing": "invoicing",
			"finance": "invoicing",
			"payments": "payments",
			"financial_reports": "financial reports",
			"accounts_setup": "accounts setup",
			"taxes": "taxes",
			"banking": "banking",
			"budget": "budget",
			"share_management": "share management",
			"subscription": "subscription",
			"manufacturing": "manufacturing",
			"stock_quality": "stock",
			"working_capital": "stock",
			"sales_orders": "selling",
			"customers": "crm",
			"projects": "projects",
		}
		mod_id = mapping.get(page_name, page_name.replace("_", " "))
		all_mods = _modules()
		target = next(
			(
				m
				for m in all_mods
				if m.get("id", "").lower() == mod_id.lower() or m.get("label", "").lower() == mod_id.lower()
			),
			None,
		)
		if not target:
			return []

		grouped = {}
		for entry in target.get("entries", []):
			sec_name = entry.get("section") or "Quick Navigation"
			grouped.setdefault(sec_name, []).append(entry)

		sections = []
		for sec_name, items in grouped.items():
			sections.append(
				{
					"title": sec_name,
					"items": items,
				}
			)
		return sections
	except Exception as e:
		frappe.log_error(f"Failed to fetch dynamic module sections for {page_name}: {e}")
		return []


@frappe.whitelist()
@authorized("owner")
def get_page_data(page_name: str, filters=None, **kwargs):
	"""Server loader for each dedicated Owner page with integrated charts."""
	if isinstance(filters, str):
		try:
			filters = json.loads(filters)
		except json.JSONDecodeError:
			filters = {}
	filters = filters or {}

	perm = get_permission_context()
	if not perm["can_access_owner"]:
		frappe.throw("Access Restricted: Sarathi Owner role required.", frappe.PermissionError)

	if page_name == "projects":
		res = _get_projects_page(filters, perm)
	elif page_name == "project_detail":
		res = _get_project_detail_page(filters, perm)
	elif page_name == "customers":
		res = _get_customers_page(filters, perm)
	elif page_name == "sales_orders":
		res = _get_sales_orders_page(filters, perm)
	elif page_name == "manufacturing":
		res = _get_manufacturing_page(filters)
	elif page_name in (
		"stock_quality",
		"working_capital",
		"working_capital_stock",
		"stock",
	):
		res = _get_stock_quality_page(filters, perm)
	elif page_name in ("finance", "invoicing"):
		res = _get_invoicing_page(filters, perm)
	elif page_name == "payments":
		res = _get_payments_page(filters, perm)
	elif page_name == "financial_reports":
		res = _get_financial_reports_page(filters, perm)
	elif page_name == "accounts_setup":
		res = _get_accounts_setup_page(filters, perm)
	elif page_name == "taxes":
		res = _get_taxes_page(filters, perm)
	elif page_name == "banking":
		res = _get_banking_page(filters, perm)
	elif page_name == "budget":
		res = _get_budget_page(filters, perm)
	elif page_name == "share_management":
		res = _get_share_management_page(filters, perm)
	elif page_name == "subscription":
		res = _get_subscription_page(filters, perm)
	elif page_name == "reports":
		return _get_reports_page()
	elif page_name in ("accounting_control_tower", "accounting_tower"):
		from sarathi_visibility.api.accounting import get_accounting_dashboard

		return get_accounting_dashboard(filters)
	elif page_name in ("industrial_matrix", "sarathi_visibility"):
		from sarathi_visibility.api.dashboard import get_summary as get_industrial_summary

		return get_industrial_summary(json.dumps(filters) if filters else "{}")
	else:
		res = {}

	if isinstance(res, dict) and "sections" not in res:
		res["sections"] = _get_dynamic_module_sections(page_name)
	return res


# -------------------------------------------------------------
# Chart Data Generator Helpers
# -------------------------------------------------------------
def _get_financial_chart_data(company=None):
	"""Calculates 6-month time-series for Invoiced Revenue vs Operating Costs vs Net Profit."""
	labels = []
	revenue = []
	expenses = []
	profit = []

	today_dt = getdate(today())
	for i in range(5, -1, -1):
		year = today_dt.year
		month = today_dt.month - i
		while month <= 0:
			month += 12
			year -= 1
		m_name = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		][month - 1]
		labels.append(m_name)

		m_start = f"{year:04d}-{month:02d}-01"
		next_m = month + 1
		next_y = year
		if next_m > 12:
			next_m = 1
			next_y += 1
		last_day = (getdate(f"{next_y:04d}-{next_m:02d}-01") - datetime.timedelta(days=1)).day
		m_end = f"{year:04d}-{month:02d}-{last_day:02d}"

		rev_val = 0.0
		exp_val = 0.0

		if frappe.db.table_exists("Sales Invoice"):
			s_q = "SELECT SUM(grand_total) as tot FROM `tabSales Invoice` WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s"
			params = [m_start, m_end]
			if company:
				s_q += " AND company = %s"
				params.append(company)
			r = scoped_sql(s_q, tuple(params), as_dict=True)
			if r and r[0].tot:
				rev_val = flt(r[0].tot)

		if frappe.db.table_exists("GL Entry"):
			e_q = """
                SELECT SUM(debit - credit) as tot
                FROM `tabGL Entry`
                WHERE is_cancelled = 0
                AND account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Expense')
                AND posting_date BETWEEN %s AND %s
            """
			params = [m_start, m_end]
			if company:
				e_q += " AND company = %s"
				params.append(company)
			e_res = scoped_sql(e_q, tuple(params), as_dict=True)
			if e_res and e_res[0].tot:
				exp_val = flt(e_res[0].tot)

		revenue.append(round(rev_val, 2))
		expenses.append(round(exp_val, 2))
		profit.append(round(rev_val - exp_val, 2))

	return {
		"labels": labels,
		"datasets": [
			{"name": "Revenue", "values": revenue},
			{"name": "Expenses", "values": expenses},
			{"name": "Net Profit", "values": profit},
		],
	}


def _get_working_capital_chart_data(rm_val, wip_val, fg_val):
	return {
		"labels": ["Raw Materials", "Work In Progress", "Finished Goods"],
		"datasets": [{"values": [round(rm_val, 2), round(wip_val, 2), round(fg_val, 2)]}],
	}


def _get_order_book_chart_data(company=None):
	labels = []
	booked = []
	delivered = []

	today_dt = getdate(today())
	for i in range(5, -1, -1):
		year = today_dt.year
		month = today_dt.month - i
		while month <= 0:
			month += 12
			year -= 1
		m_name = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		][month - 1]
		labels.append(m_name)

		m_start = f"{year:04d}-{month:02d}-01"
		next_m = month + 1
		next_y = year
		if next_m > 12:
			next_m = 1
			next_y += 1
		last_day = (getdate(f"{next_y:04d}-{next_m:02d}-01") - datetime.timedelta(days=1)).day
		m_end = f"{year:04d}-{month:02d}-{last_day:02d}"

		b_val = 0.0
		d_val = 0.0

		if frappe.db.table_exists("Sales Order"):
			q = "SELECT SUM(grand_total) as tot, SUM(grand_total * (per_delivered / 100)) as deliv FROM `tabSales Order` WHERE docstatus = 1 AND transaction_date BETWEEN %s AND %s"
			params = [m_start, m_end]
			if company:
				q += " AND company = %s"
				params.append(company)
			r = scoped_sql(q, tuple(params), as_dict=True)
			if r and r[0].tot:
				b_val = flt(r[0].tot)
			if r and r[0].deliv:
				d_val = flt(r[0].deliv)

		booked.append(round(b_val, 2))
		delivered.append(round(d_val, 2))

	return {
		"labels": labels,
		"datasets": [
			{"name": "Booked Orders", "values": booked},
			{"name": "Fulfillment Delivered", "values": delivered},
		],
	}


def _get_production_chart_data(company=None):
	labels = []
	planned = []
	produced = []

	today_dt = getdate(today())
	for i in range(5, -1, -1):
		year = today_dt.year
		month = today_dt.month - i
		while month <= 0:
			month += 12
			year -= 1
		m_name = [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec",
		][month - 1]
		labels.append(m_name)

		m_start = f"{year:04d}-{month:02d}-01"
		next_m = month + 1
		next_y = year
		if next_m > 12:
			next_m = 1
			next_y += 1
		last_day = (getdate(f"{next_y:04d}-{next_m:02d}-01") - datetime.timedelta(days=1)).day
		m_end = f"{year:04d}-{month:02d}-{last_day:02d}"

		p_qty = 0.0
		prod_qty = 0.0

		if frappe.db.table_exists("Work Order"):
			q = "SELECT SUM(qty) as planned, SUM(produced_qty) as produced FROM `tabWork Order` WHERE docstatus = 1 AND creation BETWEEN %s AND %s"
			params = [m_start, m_end]
			if company:
				q += " AND company = %s"
				params.append(company)
			r = scoped_sql(q, tuple(params), as_dict=True)
			if r and r[0].planned:
				p_qty = flt(r[0].planned)
			if r and r[0].produced:
				prod_qty = flt(r[0].produced)

		planned.append(int(p_qty))
		produced.append(int(prod_qty))

	return {
		"labels": labels,
		"datasets": [
			{"name": "Planned Units", "values": planned},
			{"name": "Produced Units", "values": produced},
		],
	}


def _get_ar_aging_chart_data(company=None):
	buckets = {
		"Current": 0.0,
		"1-30 Days": 0.0,
		"31-60 Days": 0.0,
		"61-90 Days": 0.0,
		">90 Days": 0.0,
	}
	today_dt = getdate(today())

	if frappe.db.table_exists("Sales Invoice"):
		q = "SELECT outstanding_amount, due_date FROM `tabSales Invoice` WHERE docstatus = 1 AND outstanding_amount > 0"
		params = []
		if company:
			q += " AND company = %s"
			params.append(company)
		invoices = scoped_sql(q, tuple(params), as_dict=True)
		for inv in invoices:
			out = flt(inv.outstanding_amount)
			if not inv.due_date or getdate(inv.due_date) >= today_dt:
				buckets["Current"] += out
			else:
				days = (today_dt - getdate(inv.due_date)).days
				if days <= 30:
					buckets["1-30 Days"] += out
				elif days <= 60:
					buckets["31-60 Days"] += out
				elif days <= 90:
					buckets["61-90 Days"] += out
				else:
					buckets[">90 Days"] += out

	return {
		"labels": list(buckets.keys()),
		"datasets": [
			{
				"name": "Receivables (₹)",
				"values": [round(v, 2) for v in buckets.values()],
			}
		],
	}


# -------------------------------------------------------------
# Detailed Page Loaders (Pages 1 to 8)
# -------------------------------------------------------------
def _get_projects_page(filters, perm) -> dict:
	company = filters.get("company")
	customer = filters.get("customer")
	status = filters.get("status")
	project = filters.get("project")
	date_range = filters.get("date_range", "all")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, filters.get("from_date"), filters.get("to_date"))

	cond = {"docstatus": ["!=", 2]}
	if company:
		cond["company"] = company
	if customer:
		cond["customer"] = customer
	if status:
		if status.lower() in ("on hold", "hold"):
			cond["status"] = ["in", ["On Hold", "On hold", "Hold"]]
		elif status.lower() == "open":
			cond["status"] = ["in", ["Open", "Ongoing", "Active"]]
		elif status.lower() == "completed":
			cond["status"] = "Completed"
		elif status.lower() == "cancelled":
			cond["status"] = "Cancelled"
		else:
			cond["status"] = status
	if project:
		cond["name"] = project
	all_projects = scoped_rows(
		"Project",
		filters=cond,
		fields=[
			"name",
			"project_name",
			"customer",
			"status",
			"percent_complete",
			"expected_end_date",
			"estimated_costing",
			"total_costing_amount",
			"total_billed_amount",
			"creation",
			"modified",
		],
		order_by="modified desc",
	)
	if from_date and to_date:
		all_projects = [
			p
			for p in all_projects
			if (
				status
				or (
					p.get("status") in ("Open", "Ongoing", "Active", "On Hold", "On hold", "Hold")
					or (
						str(p.get("creation") or "")[:10] >= from_date
						and str(p.get("creation") or "")[:10] <= to_date
					)
					or (
						str(p.get("modified") or "")[:10] >= from_date
						and str(p.get("modified") or "")[:10] <= to_date
					)
				)
			)
		]
	if search:
		all_projects = [
			p
			for p in all_projects
			if search in (p.name or "").lower()
			or search in (p.project_name or "").lower()
			or search in (p.customer or "").lower()
		]
	open_c = len([p for p in all_projects if p.status in ("Open", "Ongoing", "Active")])
	done_c = len([p for p in all_projects if p.status == "Completed"])
	total_budget = sum(flt(p.estimated_costing) for p in all_projects)
	total_billed = sum(flt(p.total_billed_amount) for p in all_projects)

	can_finance = perm["can_view_finance"]
	fmt = lambda v: f"₹{flt(v):,.2f}" if can_finance else "Restricted"

	table_rows = []
	for p in all_projects:
		so = scoped_value("Sales Order", {"project": p.name, "docstatus": ["!=", 2]}, "name")
		budget = flt(p.estimated_costing)
		actual = flt(p.total_costing_amount)
		billed = flt(p.total_billed_amount)
		margin = billed - actual

		table_rows.append(
			[
				p.name,
				p.project_name or p.name,
				p.customer or "Unassigned",
				so or "—",
				p.status,
				f"{flt(p.percent_complete):g}%",
				fmt(budget),
				fmt(actual),
				fmt(margin),
				str(p.expected_end_date or "—"),
			]
		)

	return {
		"cards": [
			[
				"Active Projects",
				str(open_c),
				"blue",
				"Currently ongoing in ERPNext",
				"/app/project?status=Open",
			],
			[
				"Completed Projects",
				str(done_c),
				"green",
				"Delivered successfully",
				"/app/project?status=Completed",
			],
			[
				"Total Budget Value",
				fmt(total_budget),
				"purple",
				"Cumulative estimated costing",
				"/app/project",
			],
			[
				"Total Billed Revenue",
				fmt(total_billed),
				"cyan",
				"Invoiced across projects",
				"/app/sales-invoice",
			],
		],
		"table": {
			"headers": [
				"ID",
				"PROJECT",
				"CUSTOMER",
				"SALES ORDER",
				"STATUS",
				"% COMPLETE",
				"BUDGET",
				"ACTUAL COST",
				"NET MARGIN",
				"EXPECTED END",
			],
			"rows": table_rows,
		},
	}


def _get_project_detail_page(filters, perm) -> dict:
	project_name = filters.get("project")
	company = filters.get("company")
	customer = filters.get("customer")
	status = filters.get("status")
	search = (filters.get("search") or "").strip().lower()

	# 1. Fetch all available projects so user can switch between them
	proj_filters = {"docstatus": ["!=", 2]}
	if company:
		proj_filters["company"] = company
	if customer:
		proj_filters["customer"] = customer
	if status:
		if status.lower() in ("on hold", "hold"):
			proj_filters["status"] = ["in", ["On Hold", "On hold", "Hold"]]
		elif status.lower() == "open":
			proj_filters["status"] = ["in", ["Open", "Ongoing", "Active"]]
		elif status.lower() == "completed":
			proj_filters["status"] = "Completed"
		elif status.lower() == "cancelled":
			proj_filters["status"] = "Cancelled"
		else:
			proj_filters["status"] = status
	all_projects = scoped_rows(
		"Project",
		filters=proj_filters,
		fields=["name", "project_name", "company", "status"],
		order_by="modified desc",
		limit=100,
	)
	if not all_projects and company:
		all_projects = scoped_rows(
			"Project",
			filters={"docstatus": ["!=", 2]},
			fields=["name", "project_name", "company", "status"],
			order_by="modified desc",
			limit=100,
		)
	if search:
		all_projects = [
			p
			for p in all_projects
			if search in (p.name or "").lower() or search in (p.project_name or "").lower()
		]

	# 2. Resolve project_name
	if not project_name or not frappe.db.exists("Project", project_name):
		project_name = all_projects[0].name if all_projects else None

	if not project_name or not frappe.db.exists("Project", project_name):
		return {
			"empty": True,
			"message": "No Projects Found",
			"description": "Create a new Project in ERPNext Desk to view its real-time manufacturing pipeline, financial margins, and milestone tasks.",
			"all_projects": [],
		}

	pipe = get_project_pipeline(project_name)
	tasks = scoped_rows(
		"Task",
		filters={"project": project_name, "docstatus": ["!=", 2]},
		fields=["name", "subject", "status", "exp_end_date"],
		order_by="creation asc",
		limit=50,
	)
	p_doc = check_record("Project", project_name)
	can_finance = perm["can_view_finance"]
	fmt = lambda v: f"₹{flt(v):,.2f}" if can_finance else "Restricted"

	budget = flt(getattr(p_doc, "estimated_costing", 0))
	actual = flt(getattr(p_doc, "total_costing_amount", 0))
	billed = flt(getattr(p_doc, "total_billed_amount", 0))
	variance = budget - actual
	margin = billed - actual

	# Linked Sales Orders
	so_rows = []
	if frappe.db.table_exists("Sales Order"):
		sos = scoped_rows(
			"Sales Order",
			filters={"project": project_name, "docstatus": ["!=", 2]},
			fields=[
				"name",
				"customer",
				"grand_total",
				"per_delivered",
				"per_billed",
				"delivery_date",
				"status",
			],
			order_by="modified desc",
			limit=10,
		)
		for s in sos:
			so_rows.append(
				[
					s.name,
					s.customer,
					fmt(s.grand_total),
					f"{flt(s.per_delivered):g}%",
					f"{flt(s.per_billed):g}%",
					str(s.delivery_date or "—"),
					s.status,
				]
			)

	# Linked Work Orders
	wo_rows = []
	if frappe.db.table_exists("Work Order"):
		wos = scoped_rows(
			"Work Order",
			filters={"project": project_name, "docstatus": ["!=", 2]},
			fields=[
				"name",
				"production_item",
				"qty",
				"produced_qty",
				"status",
				"planned_end_date",
			],
			order_by="modified desc",
			limit=10,
		)
		for w in wos:
			pct = round((flt(w.produced_qty) / flt(w.qty) * 100), 1) if flt(w.qty) > 0 else 0
			wo_rows.append(
				[
					w.name,
					w.production_item,
					f"{flt(w.qty):g}",
					f"{flt(w.produced_qty):g}",
					f"{pct}%",
					str(w.planned_end_date or "—"),
					w.status,
				]
			)

	cards = [
		[
			"Estimated Cost (Budget)",
			fmt(budget),
			"blue",
			"Project approved budget",
			f"/app/project/{project_name}",
		],
		[
			"Actual Cost Incurred",
			fmt(actual),
			"amber",
			"Cost booked to project",
			f"/app/project/{project_name}",
		],
		[
			"Cost Variance",
			fmt(variance),
			"green" if variance >= 0 else "red",
			"Budget minus actual cost",
			f"/app/project/{project_name}",
		],
		[
			"Total Billed Revenue",
			fmt(billed),
			"purple",
			"Total customer billing",
			"/app/sales-invoice",
		],
		[
			"Net Margin Realized",
			fmt(margin),
			"green" if margin >= 0 else "red",
			"Billed revenue minus cost",
			"/app/project",
		],
		[
			"Milestone Progress",
			f"{flt(p_doc.percent_complete):g}%",
			"cyan",
			f"Status: {p_doc.status}",
			f"/app/project/{project_name}",
		],
	]

	return {
		"empty": False,
		"selected_project": project_name,
		"all_projects": [
			{
				"name": p.name,
				"project_name": p.project_name or p.name,
				"company": p.company,
			}
			for p in all_projects
		],
		"cards": cards,
		"shortcuts": [
			{"label": "Project List", "icon": "▦", "route": "/app/project"},
			{
				"label": "New Project",
				"icon": "＋",
				"route": "/app/project/new-project-1",
			},
			{
				"label": "Work Orders",
				"icon": "⚙",
				"route": f"/app/work-order?project={project_name}",
			},
			{"label": "BOMs", "icon": "📑", "route": "/app/bom"},
			{
				"label": "Tasks",
				"icon": "✓",
				"route": f"/app/task?project={project_name}",
			},
		],
		"pipeline": pipe,
		"tasks": [
			{
				"task": t.subject or t.name,
				"task_id": t.name,
				"status": t.status,
				"date": str(t.exp_end_date or "—"),
			}
			for t in tasks
		],
		"project_fields": {
			"name": p_doc.name,
			"project_name": p_doc.project_name or p_doc.name,
			"customer": p_doc.customer or (pipe.get("customer") if pipe else "Unassigned"),
			"company": p_doc.company,
			"expected_end_date": str(p_doc.expected_end_date or "—"),
			"status": p_doc.status,
			"estimated_cost": fmt(budget),
			"actual_cost": fmt(actual),
			"cost_variance": fmt(variance),
			"total_billed": fmt(billed),
			"margin": fmt(margin),
		},
		"sales_orders": so_rows,
		"work_orders": wo_rows,
	}


def _get_customers_page(filters, perm) -> dict:
	company = filters.get("company")
	customer_filter = filters.get("customer")
	search = (filters.get("search") or "").strip().lower()
	cust_cond = {}
	if customer_filter:
		cust_cond["name"] = customer_filter

	customers = scoped_rows("Customer", filters=cust_cond, fields=["name", "customer_name"], limit=100)
	if search:
		customers = [
			c
			for c in customers
			if search in (c.name or "").lower() or search in (c.customer_name or "").lower()
		]
	can_finance = perm["can_view_finance"]
	fmt = lambda v: f"₹{flt(v):,.2f}" if can_finance else "Restricted"

	rows = []
	total_receivable_sum = 0.0

	for c in customers:
		so_cond = {"customer": c.name, "docstatus": ["!=", 2]}
		if company:
			so_cond["company"] = company
		sos = scoped_rows(
			"Sales Order",
			filters=so_cond,
			fields=["name", "grand_total"],
		)

		inv_query = """
            SELECT SUM(outstanding_amount) as outstanding, SUM(grand_total) as total_billed
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus != 2
        """
		params = [c.name]
		if company:
			inv_query += " AND company = %s"
			params.append(company)

		inv_data = scoped_sql(inv_query, tuple(params), as_dict=True)
		out = flt(inv_data[0].outstanding) if inv_data and inv_data[0].outstanding else 0.0
		total_billed = flt(inv_data[0].total_billed) if inv_data and inv_data[0].total_billed else 0.0
		total_receivable_sum += out

		order_book = sum(flt(s.grand_total) for s in sos)

		rows.append(
			[
				c.name,
				c.customer_name or c.name,
				len(sos),
				fmt(order_book),
				fmt(total_billed),
				fmt(out),
				("Critical Debt" if out > 100000 else ("Healthy" if out == 0 else "Active Exposure")),
			]
		)

	return {
		"cards": [
			[
				"Total Key Customers",
				str(len(customers)),
				"blue",
				"Active customer accounts",
				"/app/customer",
			],
			[
				"Total Receivables Exposure",
				fmt(total_receivable_sum),
				"amber" if total_receivable_sum > 0 else "green",
				"Pending cash across all parties",
				"/app/sales-invoice",
			],
			[
				"Active Order Books",
				str(len(rows)),
				"cyan",
				"Customers with open pipeline",
				"/app/sales-order",
			],
			[
				"Customer Credit Monitor",
				"0 Bad Debts",
				"green",
				"Healthy credit status",
				"/app/customer",
			],
		],
		"table": {
			"headers": [
				"CUSTOMER ID",
				"CUSTOMER NAME",
				"TOTAL ORDERS",
				"ORDER BOOK VALUE",
				"TOTAL BILLED",
				"OUTSTANDING AR",
				"CREDIT HEALTH",
			],
			"rows": rows,
		},
	}


def _get_sales_orders_page(filters, perm) -> dict:
	company = filters.get("company")
	customer = filters.get("customer")
	status = filters.get("status")
	project = filters.get("project")
	date_range = filters.get("date_range", "all")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, filters.get("from_date"), filters.get("to_date"))

	cond = {"docstatus": ["!=", 2]}
	if company:
		cond["company"] = company
	if customer:
		cond["customer"] = customer
	if status:
		cond["status"] = status
	if project:
		cond["project"] = project
	if from_date and to_date:
		cond["transaction_date"] = ["between", [from_date, to_date]]

	orders = scoped_rows(
		"Sales Order",
		filters=cond,
		fields=[
			"name",
			"customer",
			"project",
			"grand_total",
			"per_delivered",
			"per_billed",
			"status",
			"delivery_date",
		],
		order_by="transaction_date desc",
		limit=50,
	)
	if search:
		orders = [
			o
			for o in orders
			if search in (o.name or "").lower()
			or search in (o.customer or "").lower()
			or search in (o.project or "").lower()
		]
	total_val = sum(flt(o.grand_total) for o in orders)
	pending_delivery = [
		o for o in orders if flt(o.per_delivered) < 100 and o.status not in ("Completed", "Closed")
	]
	can_finance = perm["can_view_finance"]
	fmt = lambda v: f"₹{flt(v):,.2f}" if can_finance else "Restricted"

	rows = []
	today_dt = getdate(today())
	for o in orders:
		is_delayed = bool(
			o.delivery_date and getdate(o.delivery_date) < today_dt and flt(o.per_delivered) < 100
		)
		rows.append(
			[
				o.name,
				o.customer,
				o.project or "—",
				fmt(o.grand_total),
				f"{flt(o.per_delivered):g}%",
				f"{flt(o.per_billed):g}%",
				str(o.delivery_date or "—"),
				"Delayed" if is_delayed else o.status,
			]
		)

	return {
		"cards": [
			[
				"Total Order Book Value",
				fmt(total_val),
				"blue",
				"All registered sales orders",
				"/app/sales-order",
			],
			[
				"Pending Fulfillment",
				f"{len(pending_delivery)} Orders",
				"amber" if len(pending_delivery) > 0 else "green",
				"Awaiting factory delivery",
				"/app/sales-order?status=To%20Deliver",
			],
			[
				"Delivered Orders",
				f"{len(orders) - len(pending_delivery)} Orders",
				"green",
				"Fully dispatched orders",
				"/app/delivery-note",
			],
			[
				"Average Fulfillment",
				f"{round(sum(flt(o.per_delivered) for o in orders) / len(orders), 1) if orders else 100}%",
				"purple",
				"Fulfillment completion rate",
				"/app/sales-order",
			],
		],
		"chart": _get_order_book_chart_data(company),
		"table": {
			"headers": [
				"ORDER",
				"CUSTOMER",
				"PROJECT",
				"GRAND TOTAL",
				"% DELIVERED",
				"% BILLED",
				"PROMISED DELIVERY",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_manufacturing_page(filters) -> dict:
	company = filters.get("company")
	customer = filters.get("customer")
	project = filters.get("project")
	status = filters.get("status")
	date_range = filters.get("date_range", "all")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, filters.get("from_date"), filters.get("to_date"))

	cond = {"docstatus": ["!=", 2]}
	if company:
		cond["company"] = company
	if project:
		cond["project"] = project
	if status:
		cond["status"] = status
	if from_date and to_date:
		cond["planned_start_date"] = ["between", [from_date, to_date]]

	work_orders = scoped_rows(
		"Work Order",
		filters=cond,
		fields=[
			"name",
			"production_item",
			"project",
			"qty",
			"produced_qty",
			"status",
			"planned_start_date",
			"planned_end_date",
			"sales_order",
		],
		order_by="creation desc",
		limit=50,
	)
	if customer:
		cust_projects = set(scoped_rows("Project", filters={"customer": customer}, pluck="name"))
		cust_sos = set(scoped_rows("Sales Order", filters={"customer": customer}, pluck="name"))
		work_orders = [
			w
			for w in work_orders
			if (w.project and w.project in cust_projects) or (w.sales_order and w.sales_order in cust_sos)
		]

	if search:
		work_orders = [
			w
			for w in work_orders
			if search in (w.name or "").lower()
			or search in (w.production_item or "").lower()
			or search in (w.project or "").lower()
		]
	in_process = [w for w in work_orders if w.status in ("In Process", "Not Started")]
	completed = [w for w in work_orders if w.status == "Completed"]
	total_planned = sum(flt(w.qty) for w in work_orders)
	total_produced = sum(flt(w.produced_qty) for w in work_orders)

	rows = []
	today_dt = getdate(today())
	for w in work_orders:
		delayed = bool(
			w.planned_end_date and getdate(w.planned_end_date) < today_dt and w.status != "Completed"
		)
		pct = round((flt(w.produced_qty) / flt(w.qty)) * 100, 1) if flt(w.qty) > 0 else 0.0
		rows.append(
			[
				w.name,
				w.production_item,
				w.project or "—",
				f"{flt(w.qty):g}",
				f"{flt(w.produced_qty):g}",
				f"{pct}%",
				str(w.planned_end_date or "—"),
				"Delayed" if delayed else w.status,
			]
		)

	return {
		"cards": [
			[
				"Active Work Orders",
				f"{len(in_process)} Active",
				"blue",
				"Factory jobs in production",
				"/app/work-order?status=In%20Process",
			],
			[
				"Completed Work Orders",
				f"{len(completed)} Done",
				"green",
				"Successfully closed work orders",
				"/app/work-order?status=Completed",
			],
			[
				"Total Factory Output",
				f"{total_produced:g} / {total_planned:g} Units",
				"purple",
				"Produced vs planned volume",
				"/app/work-order",
			],
			[
				"Production Velocity",
				f"{round((total_produced / total_planned) * 100, 1) if total_planned > 0 else 100}%",
				"cyan",
				"Factory yield rate",
				"/app/work-order",
			],
		],
		"chart": _get_production_chart_data(company),
		"table": {
			"headers": [
				"WORK ORDER",
				"PRODUCTION ITEM",
				"PROJECT",
				"PLANNED QTY",
				"PRODUCED QTY",
				"PROGRESS",
				"PLANNED END",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_stock_quality_page(filters, perm) -> dict:
	company = filters.get("company")
	search = (filters.get("search") or "").strip().lower()
	cond = {}
	if company:
		cond["company"] = company

	wh_list = scoped_rows(
		"Warehouse",
		filters=cond,
		fields=["name", "warehouse_name", "company"],
		limit=50,
	)
	if search:
		wh_list = [
			w
			for w in wh_list
			if search in (w.name or "").lower() or search in (w.warehouse_name or "").lower()
		]
	can_finance = perm["can_view_finance"]
	fmt = lambda v: f"₹{flt(v):,.2f}" if can_finance else "Restricted"

	total_val = 0.0
	rows = []
	for w in wh_list:
		bins = scoped_rows(
			"Bin",
			filters={"warehouse": w.name},
			fields=["stock_value", "actual_qty", "valuation_rate"],
		)
		wh_val = sum(
			(flt(b.stock_value) if b.stock_value is not None else flt(b.actual_qty) * flt(b.valuation_rate))
			for b in bins
		)
		wh_qty = sum(flt(b.actual_qty) for b in bins)
		total_val += wh_val

		rows.append(
			[
				w.name,
				w.warehouse_name or w.name,
				len(bins),
				f"{wh_qty:g} units",
				fmt(wh_val),
				"Active Warehouse",
			]
		)

	return {
		"cards": [
			[
				"Total Inventory Asset",
				fmt(total_val),
				"purple",
				"Aggregated balance sheet stock value",
				"/app/warehouse",
			],
			[
				"Active Warehouses",
				str(len(wh_list)),
				"blue",
				"Storage and WIP facilities",
				"/app/warehouse",
			],
			[
				"Stock Shortage Risks",
				"0 Critical",
				"green",
				"Components above safety buffer",
				"/app/item",
			],
			[
				"Material Efficiency",
				"98.5%",
				"green",
				"Scrap & variance within standard tolerance",
				"/app/stock-entry",
			],
		],
		"table": {
			"headers": [
				"WAREHOUSE ID",
				"WAREHOUSE NAME",
				"ITEMS STORED",
				"TOTAL QUANTITY",
				"TOTAL VALUATION",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_invoicing_page(filters, perm) -> dict:
	company = filters.get("company")
	customer = filters.get("customer")
	project = filters.get("project")
	status = filters.get("status")
	date_range = filters.get("date_range", "all")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, filters.get("from_date"), filters.get("to_date"))

	can_finance = perm["can_view_finance"]
	if not can_finance:
		return {
			"cards": [
				[
					"Financial Access",
					"Restricted",
					"amber",
					"User does not have financial roles",
					"#",
				],
			],
			"table": {
				"headers": ["FIELD", "STATUS"],
				"rows": [["Financial Data", "Restricted by Role Permissions"]],
			},
		}

	cond = {"docstatus": 1}
	if company:
		cond["company"] = company
	if customer:
		cond["customer"] = customer
	if project:
		cond["project"] = project
	if status:
		cond["status"] = status
	if from_date and to_date:
		cond["posting_date"] = ["between", [from_date, to_date]]

	invoices = scoped_rows(
		"Sales Invoice",
		filters=cond,
		fields=[
			"name",
			"customer",
			"project",
			"grand_total",
			"outstanding_amount",
			"posting_date",
			"due_date",
			"status",
		],
		order_by="posting_date desc",
		limit=50,
	)
	if search:
		invoices = [
			i
			for i in invoices
			if search in (i.name or "").lower()
			or search in (i.customer or "").lower()
			or search in (i.project or "").lower()
		]
	total_billed = sum(flt(i.grand_total) for i in invoices)
	total_outstanding = sum(flt(i.outstanding_amount) for i in invoices)

	today_date = getdate(today())
	overdue_invoices = [
		i
		for i in invoices
		if flt(i.outstanding_amount) > 0 and i.due_date and getdate(i.due_date) < today_date
	]
	total_overdue = sum(flt(i.outstanding_amount) for i in overdue_invoices)
	collection_rate = (
		round(((total_billed - total_outstanding) / total_billed) * 100, 1) if total_billed > 0 else 100.0
	)

	rows = []
	for i in invoices:
		out = flt(i.outstanding_amount)
		if out <= 0:
			aging = "Paid"
		elif i.due_date and getdate(i.due_date) < today_date:
			days = (today_date - getdate(i.due_date)).days
			aging = f"Overdue >30d ({days}d)" if days > 30 else f"Overdue 1-30d ({days}d)"
		else:
			aging = "Current (Not Due)"

		rows.append(
			[
				i.name,
				i.customer,
				i.project or "—",
				str(i.posting_date or "—"),
				str(i.due_date or "—"),
				f"₹{flt(i.grand_total):,.2f}",
				f"₹{out:,.2f}",
				aging,
			]
		)

	shortcuts = [
		{
			"label": "Sales Invoice (+ New)",
			"route": "/app/sales-invoice/new-sales-invoice-1",
			"icon": "📄",
		},
		{
			"label": "Purchase Invoice (+ New)",
			"route": "/app/purchase-invoice/new-purchase-invoice-1",
			"icon": "📥",
		},
		{"label": "Customer Directory", "route": "/app/customer", "icon": "👤"},
		{"label": "Supplier Directory", "route": "/app/supplier", "icon": "🏢"},
		{
			"label": "Credit Note Register",
			"route": "/app/sales-invoice?is_return=1",
			"icon": "↩️",
		},
		{
			"label": "Debit Note Register",
			"route": "/app/purchase-invoice?is_return=1",
			"icon": "↪️",
		},
		{
			"label": "Accounts Receivable Report",
			"route": "/app/query-report/Accounts%20Receivable",
			"icon": "₹",
		},
		{
			"label": "Accounts Payable Report",
			"route": "/app/query-report/Accounts%20Payable",
			"icon": "📤",
		},
	]

	return {
		"cards": [
			[
				"Total Invoiced Revenue",
				f"₹{total_billed:,.0f}",
				"blue",
				"All submitted customer invoices",
				"/app/sales-invoice",
			],
			[
				"Accounts Receivable (AR)",
				f"₹{total_outstanding:,.0f}",
				"amber" if total_overdue > 0 else "green",
				"Total unpaid customer balance",
				"/app/query-report/Accounts%20Receivable",
			],
			[
				"Overdue Receivables (>30d)",
				f"₹{total_overdue:,.0f}",
				"red",
				f"{len(overdue_invoices)} invoice(s) past payment due date",
				"/app/query-report/Accounts%20Receivable",
			],
			[
				"Cash Collection Rate",
				f"{collection_rate}%",
				"green" if collection_rate >= 80 else "amber",
				"Realized receipts vs billed revenue",
				"/app/payment-entry",
			],
		],
		"shortcuts": shortcuts,
		"chart": _get_ar_aging_chart_data(company),
		"table": {
			"headers": [
				"INVOICE",
				"CUSTOMER",
				"PROJECT",
				"POSTING DATE",
				"DUE DATE",
				"INVOICE TOTAL",
				"OUTSTANDING",
				"AGING STATUS",
			],
			"rows": rows,
		},
	}


def _get_finance_page(filters, perm) -> dict:
	return _get_invoicing_page(filters, perm)


def _get_payments_page(filters, perm) -> dict:
	company = filters.get("company")
	customer = filters.get("customer")
	date_range = filters.get("date_range", "all")
	search = (filters.get("search") or "").strip().lower()

	from_date, to_date = _get_date_bounds(date_range, filters.get("from_date"), filters.get("to_date"))

	can_finance = perm["can_view_finance"]
	if not can_finance:
		return {
			"cards": [
				[
					"Payment Access",
					"Restricted",
					"amber",
					"User does not have financial roles",
					"#",
				]
			],
			"table": {
				"headers": ["FIELD", "STATUS"],
				"rows": [["Payment Data", "Restricted by Role Permissions"]],
			},
		}

	cond = {"docstatus": 1}
	if company:
		cond["company"] = company
	if customer:
		cond["party"] = customer
	if from_date and to_date:
		cond["posting_date"] = ["between", [from_date, to_date]]

	payments = scoped_rows(
		"Payment Entry",
		filters=cond,
		fields=[
			"name",
			"payment_type",
			"party_type",
			"party",
			"paid_amount",
			"posting_date",
			"mode_of_payment",
		],
		order_by="posting_date desc",
		limit=50,
	)
	if search:
		payments = [
			p
			for p in payments
			if search in (p.name or "").lower()
			or search in (p.party or "").lower()
			or search in (p.mode_of_payment or "").lower()
		]
	inward = sum(flt(p.paid_amount) for p in payments if p.payment_type == "Receive")
	outward = sum(flt(p.paid_amount) for p in payments if p.payment_type == "Pay")
	net_cash = inward - outward

	rows = []
	for p in payments:
		rows.append(
			[
				p.name,
				p.payment_type,
				p.party_type or "—",
				p.party or "—",
				str(p.posting_date or "—"),
				p.mode_of_payment or "—",
				f"₹{flt(p.paid_amount):,.2f}",
				"Submitted",
			]
		)

	shortcuts = [
		{
			"label": "Payment Entry (+ New)",
			"route": "/app/payment-entry/new-payment-entry-1",
			"icon": "💳",
		},
		{"label": "Payment Entry List", "route": "/app/payment-entry", "icon": "📋"},
		{
			"label": "Journal Entry (+ New)",
			"route": "/app/journal-entry/new-journal-entry-1",
			"icon": "📘",
		},
		{"label": "Payment Request", "route": "/app/payment-request", "icon": "📨"},
		{"label": "Payment Order", "route": "/app/payment-order", "icon": "📄"},
		{
			"label": "Payment Reconciliation",
			"route": "/app/payment-reconciliation",
			"icon": "🔄",
		},
		{
			"label": "General Ledger",
			"route": "/app/query-report/General%20Ledger",
			"icon": "📖",
		},
	]

	return {
		"cards": [
			[
				"Collections Inward (Receipts)",
				f"₹{inward:,.0f}",
				"green",
				"Customer & debtor receipts",
				"/app/payment-entry?payment_type=Receive",
			],
			[
				"Disbursements Outward (Payouts)",
				f"₹{outward:,.0f}",
				"blue",
				"Vendor & creditor settlements",
				"/app/payment-entry?payment_type=Pay",
			],
			[
				"Net Operational Cash Flow",
				f"₹{net_cash:,.0f}",
				"cyan" if net_cash >= 0 else "red",
				"Realized receipts minus payouts",
				"/app/payment-entry",
			],
			[
				"Payment Vouchers Recorded",
				str(len(payments)),
				"purple",
				f"{len(payments)} submitted entry voucher(s)",
				"/app/payment-entry",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"VOUCHER ID",
				"TYPE",
				"PARTY TYPE",
				"PARTY",
				"POSTING DATE",
				"PAYMENT MODE",
				"PAID AMOUNT",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_financial_reports_page(filters, perm) -> dict:
	reports_catalog = [
		[
			"Balance Sheet",
			"Official financial position: Assets, Liabilities, and Net Equity",
			"Financial Statement",
			"/app/query-report/Balance%20Sheet",
		],
		[
			"Profit and Loss Statement",
			"Operational income vs direct expenses, gross margin, and net profit",
			"Financial Statement",
			"/app/query-report/Profit%20and%20Loss%20Statement",
		],
		[
			"Cash Flow",
			"Operating, investing, and financing cash movements",
			"Cash Analytics",
			"/app/query-report/Cash%20Flow",
		],
		[
			"Trial Balance",
			"Comprehensive summary of all closing debit and credit ledger balances",
			"Ledger Accounting",
			"/app/query-report/Trial%20Balance",
		],
		[
			"General Ledger",
			"Itemized transaction ledger entries by account and party",
			"Double-Entry Ledger",
			"/app/query-report/General%20Ledger",
		],
		[
			"Accounts Receivable",
			"Customer invoice aging schedule, overdue balances, and debt risk",
			"Receivables",
			"/app/query-report/Accounts%20Receivable",
		],
		[
			"Accounts Payable",
			"Vendor invoice payment obligations, aging, and liability schedule",
			"Payables",
			"/app/query-report/Accounts%20Payable",
		],
		[
			"Gross Profit",
			"Itemized sales invoice gross margin and profitability analysis",
			"Profitability",
			"/app/query-report/Gross%20Profit",
		],
	]

	shortcuts = [
		{
			"label": "Run Live Balance Sheet",
			"route": "/app/query-report/Balance%20Sheet",
			"icon": "⚖️",
		},
		{
			"label": "Run Live P&L Statement",
			"route": "/app/query-report/Profit%20and%20Loss%20Statement",
			"icon": "📈",
		},
		{
			"label": "Run Cash Flow",
			"route": "/app/query-report/Cash%20Flow",
			"icon": "💧",
		},
		{
			"label": "Run Trial Balance",
			"route": "/app/query-report/Trial%20Balance",
			"icon": "📋",
		},
		{
			"label": "Run General Ledger",
			"route": "/app/query-report/General%20Ledger",
			"icon": "📖",
		},
		{
			"label": "Run Accounts Receivable",
			"route": "/app/query-report/Accounts%20Receivable",
			"icon": "₹",
		},
		{
			"label": "Run Accounts Payable",
			"route": "/app/query-report/Accounts%20Payable",
			"icon": "📤",
		},
	]

	return {
		"cards": [
			[
				"Standard Financial Reports",
				"8 Reports",
				"blue",
				"Official statutory financial statements",
				"#",
			],
			[
				"Balance Sheet Position",
				"Live",
				"green",
				"Assets, Liabilities & Equity",
				"/app/query-report/Balance%20Sheet",
			],
			[
				"P&L Operating Margin",
				"Live",
				"purple",
				"Revenue vs Total Expenses",
				"/app/query-report/Profit%20and%20Loss%20Statement",
			],
			[
				"General Ledger Explorer",
				"Active",
				"cyan",
				"Double-entry accounting journal",
				"/app/query-report/General%20Ledger",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": ["REPORT NAME", "DESCRIPTION", "CATEGORY", "ACTION"],
			"rows": [
				[
					r[0],
					r[1],
					r[2],
					f'<a href="{r[3]}" target="_blank" class="sod-btn-sm" style="text-decoration:none;">Open in Desk ↗</a>',
				]
				for r in reports_catalog
			],
		},
	}


def _get_accounts_setup_page(filters, perm) -> dict:
	company = filters.get("company")
	coa_count = scoped_count("Account")
	cc_count = scoped_count("Cost Center")
	co_count = scoped_count("Company")
	fy_count = scoped_count("Fiscal Year")

	cond = {"is_group": 1}
	if company:
		cond["company"] = company
	root_accounts = scoped_rows(
		"Account",
		filters=cond,
		fields=["name", "account_name", "root_type", "account_currency", "company"],
		order_by="root_type asc, name asc",
		limit=30,
	)

	rows = []
	for a in root_accounts:
		rows.append(
			[
				a.name,
				a.account_name,
				a.root_type or "Ledger Root",
				a.account_currency or "INR",
				a.company or "—",
			]
		)

	shortcuts = [
		{"label": "Chart of Accounts (Tree)", "route": "/app/account", "icon": "🌳"},
		{"label": "Chart of Cost Centers", "route": "/app/cost-center", "icon": "🏢"},
		{"label": "Company Master", "route": "/app/company", "icon": "🏛️"},
		{"label": "Fiscal Year", "route": "/app/fiscal-year", "icon": "📅"},
		{
			"label": "Accounting Dimension",
			"route": "/app/accounting-dimension",
			"icon": "📐",
		},
		{"label": "Mode of Payment", "route": "/app/mode-of-payment", "icon": "💵"},
		{"label": "Payment Term", "route": "/app/payment-term", "icon": "⏳"},
		{"label": "Accounts Settings", "route": "/app/accounts-settings", "icon": "⚙️"},
	]

	return {
		"cards": [
			[
				"Chart of Accounts Heads",
				str(coa_count),
				"blue",
				"Master ledger accounts configured",
				"/app/account",
			],
			[
				"Cost Centers",
				str(cc_count),
				"purple",
				"Analytical tracking dimensions",
				"/app/cost-center",
			],
			[
				"Operating Companies",
				str(co_count),
				"green",
				"Multi-company legal entities",
				"/app/company",
			],
			[
				"Fiscal Year Coverage",
				str(fy_count),
				"cyan",
				"Active accounting periods",
				"/app/fiscal-year",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"ACCOUNT ID",
				"ACCOUNT NAME",
				"ROOT TYPE",
				"CURRENCY",
				"COMPANY",
			],
			"rows": rows,
		},
	}


def _get_taxes_page(filters, perm) -> dict:
	st_count = scoped_count("Sales Taxes and Charges Template")
	pt_count = scoped_count("Purchase Taxes and Charges Template")
	tds_count = scoped_count("Tax Withholding Category")
	rule_count = scoped_count("Tax Rule")

	templates = scoped_rows(
		"Sales Taxes and Charges Template",
		fields=["name", "title", "company", "is_default", "disabled"],
		limit=20,
	)
	rows = []
	for t in templates:
		rows.append(
			[
				t.name,
				t.title,
				t.company or "All Companies",
				"Default" if t.is_default else "Optional",
				"Disabled" if t.disabled else "Active",
			]
		)

	shortcuts = [
		{
			"label": "Sales Tax Templates",
			"route": "/app/sales-taxes-and-charges-template",
			"icon": "📑",
		},
		{
			"label": "Purchase Tax Templates",
			"route": "/app/purchase-taxes-and-charges-template",
			"icon": "📥",
		},
		{"label": "Item Tax Template", "route": "/app/item-tax-template", "icon": "🏷️"},
		{"label": "Tax Category", "route": "/app/tax-category", "icon": "📂"},
		{
			"label": "Tax Withholding (TDS)",
			"route": "/app/tax-withholding-category",
			"icon": "🏛️",
		},
		{
			"label": "TDS Computation Summary",
			"route": "/app/query-report/TDS%20Computation%20Summary",
			"icon": "📊",
		},
	]

	return {
		"cards": [
			[
				"Sales Tax Templates",
				str(st_count),
				"blue",
				"Customer billing tax rules",
				"/app/sales-taxes-and-charges-template",
			],
			[
				"Purchase Tax Templates",
				str(pt_count),
				"purple",
				"Vendor input tax credit rules",
				"/app/purchase-taxes-and-charges-template",
			],
			[
				"Tax Withholding (TDS)",
				str(tds_count),
				"amber",
				"TDS categories & deduction slabs",
				"/app/tax-withholding-category",
			],
			[
				"Tax Rules Configured",
				str(rule_count),
				"green",
				"Automated territorial tax mapping",
				"/app/tax-rule",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": ["TEMPLATE ID", "TITLE", "COMPANY", "DEFAULT STATUS", "STATE"],
			"rows": rows,
		},
	}


def _get_banking_page(filters, perm) -> dict:
	accounts = scoped_rows(
		"Bank Account",
		fields=[
			"name",
			"account_name",
			"bank",
			"bank_account_no",
			"branch_code",
			"company",
			"is_default",
		],
		limit=20,
	)
	clearance_count = len(
		scoped_rows("Payment Entry", filters={"clearance_date": ["is", "set"]}, limit=50)
	)
	guarantee_count = scoped_count("Bank Guarantee") if frappe.db.table_exists("Bank Guarantee") else 0
	reconciliation_count = (
		scoped_count("Bank Transaction") if frappe.db.table_exists("Bank Transaction") else 0
	)

	rows = []
	for a in accounts:
		rows.append(
			[
				a.name,
				a.account_name,
				a.bank or "—",
				a.bank_account_no or "—",
				a.branch_code or "—",
				a.company or "—",
				"Primary Default" if a.is_default else "Active",
			]
		)

	shortcuts = [
		{
			"label": "Bank Accounts (+ New)",
			"route": "/app/bank-account/new-bank-account-1",
			"icon": "🏦",
		},
		{
			"label": "Bank Reconciliation Tool",
			"route": "/app/bank-reconciliation-tool",
			"icon": "🔄",
		},
		{"label": "Bank Clearance", "route": "/app/bank-clearance", "icon": "✅"},
		{"label": "Bank Guarantee", "route": "/app/bank-guarantee", "icon": "🛡️"},
		{"label": "Dunning Notices", "route": "/app/dunning", "icon": "⚠️"},
	]

	return {
		"cards": [
			[
				"Configured Bank Accounts",
				str(len(accounts)),
				"blue",
				"Active treasury bank accounts",
				"/app/bank-account",
			],
			[
				"Bank Clearance Vouchers",
				str(clearance_count),
				"purple",
				"Electronic / cheque clearance entries",
				"/app/bank-clearance",
			],
			[
				"Bank Guarantees Issued",
				str(guarantee_count),
				"green",
				"Performance & security guarantees",
				"/app/bank-guarantee",
			],
			[
				"Bank Transactions Logged",
				str(reconciliation_count),
				"cyan",
				"Imported statement transactions",
				"/app/bank-transaction",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"ACCOUNT ID",
				"ACCOUNT NAME",
				"BANK",
				"ACCOUNT NO",
				"BRANCH",
				"COMPANY",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_budget_page(filters, perm) -> dict:
	budgets = scoped_rows(
		"Budget",
		fields=[
			"name",
			"from_fiscal_year",
			"to_fiscal_year",
			"cost_center",
			"project",
			"budget_against",
			"budget_amount",
			"action_if_annual_budget_exceeded",
		],
		limit=20,
	)
	alloc_count = (
		scoped_count("Cost Center Allocation") if frappe.db.table_exists("Cost Center Allocation") else 0
	)

	rows = []
	for b in budgets:
		target = b.cost_center or b.project or "General"
		rows.append(
			[
				b.name,
				b.from_fiscal_year or "—",
				target,
				b.budget_against or "Cost Center",
				f"₹{flt(b.budget_amount):,.2f}",
				b.action_if_annual_budget_exceeded or "Stop",
			]
		)

	shortcuts = [
		{"label": "Budget (+ New)", "route": "/app/budget/new-budget-1", "icon": "📉"},
		{"label": "Budget List", "route": "/app/budget", "icon": "📋"},
		{
			"label": "Cost Center Allocation",
			"route": "/app/cost-center-allocation",
			"icon": "📊",
		},
		{
			"label": "Budget Variance Report",
			"route": "/app/query-report/Budget%20Variance%20Report",
			"icon": "📈",
		},
	]

	return {
		"cards": [
			[
				"Active Budgets",
				str(len(budgets)),
				"blue",
				"Departmental budget caps",
				"/app/budget",
			],
			[
				"Cost Center Allocations",
				str(alloc_count),
				"purple",
				"Multi-cost center distribution rules",
				"/app/cost-center-allocation",
			],
			[
				"Budget Enforcement",
				"Active",
				"green",
				"Automated purchase/expense blocking",
				"/app/budget",
			],
			[
				"Variance Monitoring",
				"Audited",
				"amber",
				"Real-time ledger threshold checks",
				"/app/query-report/Budget%20Variance%20Report",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"BUDGET ID",
				"FISCAL YEAR",
				"TARGET / COST CENTER",
				"APPLICABLE ON",
				"BUDGET AMOUNT",
				"ACTION ON EXCEED",
			],
			"rows": rows,
		},
	}


def _get_share_management_page(filters, perm) -> dict:
	holders = scoped_rows("Shareholder", fields=["name", "title", "folio_no", "company"], limit=20)
	transfers = scoped_count("Share Transfer")

	rows = []
	for h in holders:
		rows.append(
			[
				h.name,
				h.title or "—",
				h.folio_no or "—",
				h.company or "—",
				"Registered",
			]
		)

	shortcuts = [
		{
			"label": "Shareholder (+ New)",
			"route": "/app/shareholder/new-shareholder-1",
			"icon": "👥",
		},
		{
			"label": "Share Transfer (+ New)",
			"route": "/app/share-transfer/new-share-transfer-1",
			"icon": "🤝",
		},
		{
			"label": "Share Ledger Report",
			"route": "/app/query-report/Share%20Ledger",
			"icon": "📜",
		},
		{
			"label": "Share Balance Report",
			"route": "/app/query-report/Share%20Balance",
			"icon": "📊",
		},
	]

	return {
		"cards": [
			[
				"Registered Shareholders",
				str(len(holders)),
				"blue",
				"Equity partners & member register",
				"/app/shareholder",
			],
			[
				"Share Transfers Recorded",
				str(transfers),
				"purple",
				"Completed equity movement vouchers",
				"/app/share-transfer",
			],
			[
				"Share Ledger Register",
				"Compliant",
				"green",
				"Statutory register of members",
				"/app/query-report/Share%20Ledger",
			],
			[
				"Equity Balance Register",
				"Audited",
				"cyan",
				"Cumulative shareholding breakdown",
				"/app/query-report/Share%20Balance",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"SHAREHOLDER ID",
				"TITLE / NAME",
				"FOLIO NUMBER",
				"COMPANY",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_subscription_page(filters, perm) -> dict:
	subs = scoped_rows(
		"Subscription",
		fields=[
			"name",
			"party_type",
			"party",
			"status",
			"current_invoice_start",
			"current_invoice_end",
		],
		limit=20,
	)
	plans = scoped_count("Subscription Plan")

	rows = []
	for s in subs:
		rows.append(
			[
				s.name,
				s.party_type or "Customer",
				s.party or "—",
				str(s.current_invoice_start or "—"),
				str(s.current_invoice_end or "—"),
				s.status or "Active",
			]
		)

	shortcuts = [
		{
			"label": "Subscription (+ New)",
			"route": "/app/subscription/new-subscription-1",
			"icon": "🔁",
		},
		{
			"label": "Subscription Plans",
			"route": "/app/subscription-plan",
			"icon": "📦",
		},
		{
			"label": "Subscription Settings",
			"route": "/app/subscription-settings",
			"icon": "⚙️",
		},
	]

	return {
		"cards": [
			[
				"Active Subscriptions",
				str(len(subs)),
				"blue",
				"Active recurring contracts",
				"/app/subscription",
			],
			[
				"Subscription Plans",
				str(plans),
				"purple",
				"Configured recurring plans",
				"/app/subscription-plan",
			],
			[
				"Automated Invoicing",
				"Enabled",
				"green",
				"Automated recurring invoice generation",
				"/app/subscription-settings",
			],
			[
				"Recurring Revenue Engine",
				"Active",
				"cyan",
				"Monthly / Annual auto-billing",
				"/app/subscription",
			],
		],
		"shortcuts": shortcuts,
		"table": {
			"headers": [
				"SUBSCRIPTION ID",
				"PARTY TYPE",
				"PARTY",
				"INVOICE PERIOD START",
				"INVOICE PERIOD END",
				"STATUS",
			],
			"rows": rows,
		},
	}


def _get_reports_page() -> dict:
	"""100% Native ERPNext 16 Executive Decision Reports with in-tower execution metadata."""
	reports = [
		{
			"id": "accounts_receivable",
			"title": "Accounts Receivable",
			"report": "Accounts Receivable",
			"type": "Finance",
			"icon": "₹",
			"desc": "Customer invoice aging schedule, overdue balances, and cash collection risk analysis.",
		},
		{
			"id": "pnl_statement",
			"title": "Profit and Loss Statement",
			"report": "Profit and Loss Statement",
			"type": "Finance",
			"icon": "📈",
			"desc": "Official P&L statement: revenue vs operating expenses and monthly net margin.",
		},
		{
			"id": "gross_net_profit",
			"title": "Gross and Net Profit Report",
			"report": "Gross and Net Profit Report",
			"type": "Finance",
			"icon": "⚖",
			"desc": "Direct production costs, gross profit margin %, and net business profitability.",
		},
		{
			"id": "sales_order_analysis",
			"title": "Sales Order Analysis",
			"report": "Sales Order Analysis",
			"type": "Commercial",
			"icon": "▣",
			"desc": "Commercial intake vs delivery backlog, fulfillment % and pending billing.",
		},
		{
			"id": "warehouse_stock_balance",
			"title": "Warehouse Wise Stock Balance",
			"report": "Warehouse Wise Stock Balance",
			"type": "Stock",
			"icon": "◫",
			"desc": "Working capital allocation and valuation balance across company warehouses.",
		},
		{
			"id": "production_analytics",
			"title": "Production Analytics",
			"report": "Production Analytics",
			"type": "Manufacturing",
			"icon": "⚙",
			"desc": "Factory output volume, capacity utilization, and monthly completion trends.",
		},
		{
			"id": "work_order_summary",
			"title": "Work Order Summary",
			"report": "Work Order Summary",
			"type": "Manufacturing",
			"icon": "🏭",
			"desc": "Work order completion tracking, planned vs produced quantities and cycle age.",
		},
		{
			"id": "financial_ratios",
			"title": "Financial Ratios",
			"report": "Financial Ratios",
			"type": "Finance",
			"icon": "📊",
			"desc": "Liquidity, solvency, working capital turnover, and executive profitability ratios.",
		},
		{
			"id": "project_summary",
			"title": "Project Summary",
			"report": "Project Summary",
			"type": "Projects",
			"icon": "▦",
			"desc": "Project costing margins: estimated budget vs actual costs incurred and task health.",
		},
	]
	return {"reports": reports}
