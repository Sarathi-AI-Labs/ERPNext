"""Read-only DASH-004 source/report comparisons. Not a dashboard API.

Run inside an initialized bench site as Administrator. No fixtures or transactions
are created; callers must rollback/destroy their read session after collecting.
"""

import hashlib
import importlib
from collections import Counter, defaultdict

import frappe
from frappe.utils import flt, getdate, now_datetime, today


def collect(company=None, from_date=None, to_date=None):
	if frappe.session.user != "Administrator":
		frappe.throw("Run the KPI source audit in an administrator bench session.", frappe.PermissionError)
	from frappe.desk.query_report import run

	if not company:
		invoices = frappe.get_list(
			"Sales Invoice", fields=["company"], filters={"docstatus": 1}, limit_page_length=0
		)
		counts = defaultdict(int)
		for row in invoices:
			counts[row.company] += 1
		company = (
			max(counts, key=counts.get)
			if counts
			else frappe.get_list("Company", pluck="name", limit_page_length=1)[0]
		)
	frappe.get_doc("Company", company).check_permission("read")
	end = getdate(to_date or today())
	start = getdate(from_date or f"{end.year if end.month >= 4 else end.year - 1}-04-01")
	currency = frappe.get_cached_value("Company", company, "default_currency")
	output = {
		"versions": {
			a: getattr(importlib.import_module(a), "__version__", "unknown") for a in ("frappe", "erpnext")
		},
		"captured_at": str(now_datetime()),
		"scope": {
			"company_alias": "C1",
			"company_fingerprint": hashlib.sha256(company.encode()).hexdigest()[:16],
			"currency": currency,
			"from_date": str(start),
			"as_of": str(end),
			"actor": "Administrator (audit only)",
		},
		"checks": [],
	}

	def compare(identifier, kpis, source, expected, actual, rows, note=""):
		difference = flt(actual - expected, 6)
		output["checks"].append(
			dict(
				id=identifier,
				kpi_ids=kpis,
				source=source,
				expected=flt(expected, 6),
				actual=flt(actual, 6),
				difference=difference,
				records=rows,
				status="verified" if abs(difference) <= 0.01 else "mismatch",
				limitation=note,
			)
		)

	def report(name, filters):
		result = run(report_name=name, filters=filters, ignore_prepared_report=True)
		return [r for r in result.get("result", []) if isinstance(r, dict)]

	sales = frappe.get_list(
		"Sales Invoice",
		fields=[
			"name",
			"base_net_total",
			"base_grand_total",
			"customer",
			"currency",
			"conversion_rate",
			"is_return",
			"is_internal_customer",
			"represents_company",
			"outstanding_amount",
		],
		filters={"company": company, "docstatus": 1, "posting_date": ["between", [start, end]]},
		limit_page_length=0,
	)
	sales_rows = report("Sales Register", dict(company=company, from_date=str(start), to_date=str(end)))
	invoice_rows = [r for r in sales_rows if r.get("voucher_type") == "Sales Invoice" and r.get("voucher_no")]
	expected = sum(
		flt(r.base_net_total)
		for r in sales
		if not (r.is_internal_customer and r.represents_company == company)
	)
	compare(
		"invoice_net_vs_sales_register",
		["FIN-001", "SALES-001", "SALES-002", "SALES-003"],
		"Sales Invoice.base_net_total versus Sales Register.net_total",
		expected,
		sum(flt(r.get("net_total")) for r in invoice_rows),
		len(sales),
		"External net invoiced sales, not P&L total income. No submitted return or foreign-currency fixture exists on this site.",
	)
	output["observed_invoice_basis"] = {
		"submitted_invoices": len(sales),
		"returns": sum(bool(r.is_return) for r in sales),
		"invoice_currencies": sorted({r.currency for r in sales}),
		"partially_outstanding_current_invoices": sum(
			0 < flt(r.outstanding_amount) < flt(r.base_grand_total) for r in sales if r.currency == currency
		),
		"base_net_total": expected,
		"base_grand_total": sum(flt(r.base_grand_total) for r in sales),
	}

	pnl = run(
		report_name="Profit and Loss Statement",
		filters=dict(
			company=company,
			filter_based_on="Date Range",
			period_start_date=str(start),
			period_end_date=str(end),
			periodicity="Monthly",
			accumulated_values=0,
			include_default_book_entries=1,
		),
		ignore_prepared_report=True,
	)
	summaries = pnl.get("report_summary", [])
	if len(summaries) < 3:
		raise AssertionError("Expected native income, expense and net-profit report summaries")
	accounts = {
		r.name: r.root_type
		for r in frappe.get_list(
			"Account", fields=["name", "root_type"], filters={"company": company}, limit_page_length=0
		)
	}
	default_book = frappe.get_cached_value("Company", company, "default_finance_book")
	entries = frappe.get_list(
		"GL Entry",
		fields=["account", "debit", "credit", "voucher_type", "is_opening", "finance_book"],
		filters={"company": company, "is_cancelled": 0, "posting_date": ["between", [start, end]]},
		limit_page_length=0,
	)
	ignore_opening = frappe.db.get_single_value("Accounts Settings", "ignore_is_opening_check_for_reporting")
	eligible = [
		r
		for r in entries
		if r.voucher_type != "Period Closing Voucher"
		and (ignore_opening or r.is_opening == "No")
		and (r.finance_book or "") in {"", default_book or ""}
	]
	income = sum(flt(r.credit) - flt(r.debit) for r in eligible if accounts.get(r.account) == "Income")
	expense = sum(flt(r.debit) - flt(r.credit) for r in eligible if accounts.get(r.account) == "Expense")
	compare(
		"pnl_income_vs_gl",
		["FIN-002"],
		"Profit and Loss Statement income summary versus eligible Income GL credit-debit",
		income,
		flt(summaries[0].get("value")),
		len(eligible),
	)
	compare(
		"pnl_expense_vs_gl",
		["FIN-003"],
		"Profit and Loss Statement expense summary versus eligible Expense GL debit-credit",
		expense,
		flt(summaries[1].get("value")),
		len(eligible),
	)
	compare(
		"pnl_profit_vs_gl",
		["FIN-004", "FIN-005"],
		"Profit and Loss Statement net profit versus eligible income-expense",
		income - expense,
		flt(summaries[2].get("value")),
		len(eligible),
		"Default finance book, non-consolidated company currency; alternative books/dimensions and fiscal-year boundaries not exercised.",
	)
	output["pnl_net_margin_pct"] = (income - expense) / income * 100 if income else None

	for dt, name, prefix in (
		("Sales Invoice", "Accounts Receivable", "AR"),
		("Purchase Invoice", "Accounts Payable", "AP"),
	):
		data = report(
			name,
			dict(
				company=company,
				report_date=str(end),
				ageing_based_on="Due Date",
				range="30,60,90,120",
				in_party_currency=0,
				group_by_party=0,
			),
		)
		eligible_rows = [r for r in data if r.get("voucher_type") == dt and r.get("voucher_no")]
		ids = list({r["voucher_no"] for r in eligible_rows})
		headers = (
			frappe.get_list(
				dt,
				fields=["outstanding_amount", "party_account_currency"],
				filters={"name": ["in", ids]},
				limit_page_length=0,
			)
			if ids
			else []
		)
		if any((r.party_account_currency or currency) != currency for r in headers):
			output["checks"].append(
				dict(
					id=prefix.lower() + "_current_snapshot",
					kpi_ids=[prefix + "-001"],
					status="blocked",
					limitation="Party account currency differs; current header sum is not a base-currency control.",
				)
			)
		else:
			compare(
				prefix.lower() + "_current_snapshot",
				[prefix + "-001"],
				name + " invoice-voucher outstanding versus matching current invoice headers",
				sum(flt(r.outstanding_amount) for r in headers),
				sum(flt(r.get("outstanding")) for r in eligible_rows),
				len(headers),
				"Invoice-voucher subset at current audit date only. Historical allocations, advances and Journal Entry balances are not reconciled by this comparison.",
			)
		output[prefix.lower() + "_report_total"] = sum(
			flt(r.get("outstanding")) for r in data if r.get("voucher_no")
		)
		output[prefix.lower() + "_voucher_rows"] = len([r for r in data if r.get("voucher_no")])
		payment_ledger = frappe.get_list(
			"Payment Ledger Entry",
			fields=["amount"],
			filters={
				"company": company,
				"account_type": "Receivable" if prefix == "AR" else "Payable",
				"delinked": 0,
				"posting_date": ["<=", end],
			},
			limit_page_length=0,
		)
		compare(
			prefix.lower() + "_net_vs_payment_ledger",
			[prefix + "-001"],
			name + " all voucher balances versus current eligible Payment Ledger Entry amounts",
			sum(flt(r.amount) for r in payment_ledger),
			output[prefix.lower() + "_report_total"],
			len(payment_ledger),
			"Current base-currency all-party balance only. Historical delinking/reallocation and party/finance-book filters require separate report fixtures.",
		)

	balance = report("Stock Balance", dict(company=company, from_date=str(start), to_date=str(end)))
	warehouse_names = frappe.get_list(
		"Warehouse", filters={"company": company, "is_group": 0}, pluck="name", limit_page_length=0
	)
	bins = frappe.get_list(
		"Bin",
		fields=["item_code", "warehouse", "stock_value", "actual_qty"],
		filters={"warehouse": ["in", warehouse_names]},
		limit_page_length=0,
	)
	compare(
		"stock_value_current_vs_report",
		["INV-001"],
		"Current Bin.stock_value versus native Stock Balance.bal_val at audit date",
		sum(flt(b.stock_value) for b in bins),
		sum(flt(r.get("bal_val")) for r in balance if r.get("item_code") and r.get("warehouse")),
		len(bins),
		"Current snapshot only, no stock-closing/repost/foreign-company or historical valuation fixture. A difference must be investigated, never replaced with purchase-price valuation.",
	)

	source_bins = {(r.item_code, r.warehouse): (flt(r.actual_qty), flt(r.stock_value)) for r in bins}
	ledger_balances = {
		(r["item_code"], r["warehouse"]): (flt(r.get("bal_qty")), flt(r.get("bal_val")))
		for r in balance
		if r.get("item_code") and r.get("warehouse")
	}
	keys = set(source_bins) | set(ledger_balances)
	mismatches = sum(
		any(abs(a - b) > 0.01 for a, b in zip(source_bins.get(key, (0, 0)), ledger_balances.get(key, (0, 0))))
		for key in keys
	)
	compare(
		"stock_item_warehouse_balances",
		["INV-001", "INV-002"],
		"Current Bin quantity/value versus native Stock Balance by exact item and warehouse",
		0,
		mismatches,
		len(keys),
		"Counts mismatched item/warehouse pairs; missing zero-balance rows treated as zero.",
	)

	work_orders = frappe.get_list(
		"Work Order",
		fields=[
			"name",
			"production_item",
			"stock_uom",
			"qty",
			"produced_qty",
			"process_loss_qty",
			"status",
			"docstatus",
			"planned_end_date",
			"creation",
		],
		filters={"company": company},
		limit_page_length=0,
	)
	submitted = [w for w in work_orders if w.docstatus == 1 and getdate(w.creation) <= end]
	native = report(
		"Work Order Summary",
		dict(
			company=company, based_on="Creation Date", from_date="1900-01-01", to_date=str(end), age=-100000
		),
	)
	# Native report does not necessarily emit docstatus; compare unique work_order/name IDs to source map instead.
	by_name = {w.name: w for w in submitted}
	native_submitted = [r for r in native if (r.get("name") or r.get("work_order")) in by_name]
	compare(
		"work_order_qty_vs_report",
		["MFG-001", "MFG-002"],
		"Submitted Work Order quantity versus corresponding Work Order Summary rows",
		sum(flt(w.qty) for w in submitted),
		sum(flt(r.get("qty")) for r in native_submitted),
		len(submitted),
		"Source-to-report total check only: quantities must be split by item/UOM in dashboard output, never expose this cross-item audit checksum as a KPI.",
	)
	compare(
		"work_order_produced_vs_report",
		["MFG-002"],
		"Submitted Work Order produced_qty versus corresponding Work Order Summary rows",
		sum(flt(w.produced_qty) for w in submitted),
		sum(flt(r.get("produced_qty")) for r in native_submitted),
		len(submitted),
		"Same exact submitted IDs and creation-date cohort; group dashboard quantities by item/UOM.",
	)
	groups = defaultdict(lambda: dict(planned=0.0, produced=0.0, work_orders=0))
	for w in submitted:
		group = groups[(w.production_item, w.stock_uom)]
		group["planned"] += flt(w.qty)
		group["produced"] += flt(w.produced_qty)
		group["work_orders"] += 1
	output["production_groups"] = [
		{
			"group_alias": f"item_group_{i + 1}",
			"uom": key[1],
			**v,
			"achievement_pct": v["produced"] / v["planned"] * 100 if v["planned"] else None,
		}
		for i, (key, v) in enumerate(groups.items())
	]
	output["work_order_status_counts"] = dict(Counter(w.status for w in submitted))
	jobs = frappe.get_list(
		"Job Card",
		fields=["name", "docstatus", "for_quantity", "total_completed_qty", "process_loss_qty", "status"],
		filters={"company": company, "docstatus": ["!=", 2]},
		limit_page_length=0,
	)
	output["job_cards"] = dict(
		records=len(jobs),
		submitted=sum(j.docstatus == 1 for j in jobs),
		statuses=dict(Counter(j.status for j in jobs)),
		remaining_sum_audit_only=sum(
			max(flt(j.for_quantity) - flt(j.total_completed_qty) - flt(j.process_loss_qty), 0) for j in jobs
		),
	)
	output["configuration_gaps"] = {
		dt: frappe.db.count(dt) if frappe.db.exists("DocType", dt) else None
		for dt in (
			"Work Order Operation",
			"Job Card Time Log",
			"Stock Reservation Entry",
			"Downtime Entry",
			"Subcontracting Order",
			"Subcontracting Receipt",
			"Workflow",
			"Workflow Action",
			"ToDo",
			"Shift Type",
			"Issue",
		)
	}
	output["not_exercised"] = [
		"native submitted credit note",
		"partial-payment allocation history",
		"foreign invoice/account currencies",
		"reservation allocation",
		"cancel/amend controller lifecycle",
		"live machine telemetry",
		"assigned operator jobs",
		"multi-item scalar production KPI (prohibited)",
	]
	return output


def describe_sources(doctype_fields):
	"""Record installed schema evidence, not business records or credentials."""
	if frappe.session.user != "Administrator":
		frappe.throw("Administrator audit session required.", frappe.PermissionError)
	output = {}
	for doctype, fields in sorted(doctype_fields.items()):
		if not frappe.db.exists("DocType", doctype):
			output[doctype] = {"exists": False, "missing_fields": fields}
			continue
		meta = frappe.get_meta(doctype)
		valid = set(meta.get_valid_columns()) | {f.fieldname for f in meta.fields}
		output[doctype] = {
			"exists": True,
			"records": frappe.db.count(doctype),
			"is_submittable": bool(meta.is_submittable),
			"missing_fields": sorted(set(fields) - valid),
			"fields": {
				field: {
					"type": meta.get_field(field).fieldtype if meta.get_field(field) else "System",
					"options": meta.get_field(field).options if meta.get_field(field) else None,
				}
				for field in sorted(set(fields) & valid)
			},
		}
	return output
