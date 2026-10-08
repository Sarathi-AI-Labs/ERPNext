"""Scoped, permission-aware summaries of the records shown in a detail dialog."""
from collections import Counter, defaultdict

import frappe
from frappe.utils import cint, flt


def describe(doctype, meta, fields, filters, search, start):
	allowed = {f.fieldname: f for f in fields}
	preferred = [
		meta.title_field,
		"status",
		"company",
		"customer",
		"supplier",
		"posting_date",
		"transaction_date",
		"grand_total",
		"outstanding_amount",
		"payment_type",
		"root_type",
		"account_type",
		"modified",
	]
	selected = ["name"]
	for key in preferred:
		if key and key not in selected and (key in allowed or key == "modified"):
			selected.append(key)
	selected = selected[:8]
	metric_fields = [
		k
		for k in (
			"docstatus",
			"status",
			"root_type",
			"payment_type",
			"currency",
			"company",
			"grand_total",
			"outstanding_amount",
			"posting_date",
			"transaction_date",
			"base_paid_amount",
			"total_debit",
			"total_credit",
			"budget_amount",
		)
		if k in allowed or k == "docstatus"
	]
	query_fields = list(dict.fromkeys(selected + metric_fields))
	or_filters = (
		[
			[doctype, key, "like", "%" + str(search)[:100] + "%"]
			for key in dict.fromkeys(["name", meta.title_field or "name"])
		]
		if search
		else None
	)
	# get_list applies user permissions to both rows and all derived metrics.
	rows = frappe.get_list(
		doctype,
		fields=query_fields,
		filters=filters,
		or_filters=or_filters,
		order_by="modified desc",
		limit_page_length=0,
	)
	cards = [
		{
			"label": "Matching records",
			"value": len(rows),
			"desc": "All accessible records matching these filters",
		}
	]
	charts = []
	group = next((key for key in ("status", "root_type", "payment_type") if key in allowed), "docstatus")
	counts = Counter(
		str(row.get(group) or ("Draft" if group == "docstatus" else "Unspecified")) for row in rows
	)
	if group == "docstatus":
		counts = Counter(
			{{"0": "Draft", "1": "Submitted", "2": "Cancelled"}.get(k, k): v for k, v in counts.items()}
		)
	if counts:
		charts.append(
			{
				"title": "Record distribution",
				"type": "donut",
				"labels": list(counts),
				"datasets": [{"name": "Records", "values": list(counts.values())}],
			}
		)
	date_field = next((k for k in ("posting_date", "transaction_date") if k in allowed), "modified")
	periods = Counter(str(row.get(date_field))[:7] for row in rows if row.get(date_field))
	if periods:
		labels = sorted(periods)[-12:]
		charts.append(
			{
				"title": ("Last modified" if date_field == "modified" else "Document date") + " by month",
				"type": "bar",
				"labels": labels,
				"datasets": [{"name": "Records", "values": [periods[k] for k in labels]}],
			}
		)
	if doctype in ("Sales Invoice", "Purchase Invoice") and "grand_total" in allowed:
		groups = defaultdict(list)
		for row in rows:
			if row.get("docstatus") == 1:
				groups[row.get("currency") or "Currency unspecified"].append(row)
		for currency, invoices in groups.items():
			billed = sum(flt(r.grand_total) for r in invoices)
			cards.append(
				{
					"label": f"Submitted invoice total · {currency}",
					"value": billed,
					"fieldtype": "Currency",
					"desc": "Signed total including taxes; returns remain negative",
				}
			)
			if "outstanding_amount" in allowed:
				outstanding = sum(flt(r.outstanding_amount) for r in invoices)
				cards.append(
					{
						"label": f"Outstanding · {currency}",
						"value": outstanding,
						"fieldtype": "Currency",
						"desc": "Signed outstanding balance of the matching invoices",
					}
				)
			if "posting_date" in allowed:
				months = sorted({str(r.get("posting_date"))[:7] for r in invoices if r.get("posting_date")})[
					-12:
				]
				charts.append(
					{
						"title": f"Submitted billing by invoice month · {currency}",
						"type": "bar",
						"labels": months,
						"datasets": [
							{
								"name": "Invoice total",
								"values": [
									sum(
										flt(r.get("grand_total"))
										for r in invoices
										if str(r.get("posting_date"))[:7] == month
									)
									for month in months
								],
							}
						],
					}
				)
	if doctype in ("Payment Entry", "Journal Entry", "Budget") and "company" in allowed:
		companies = defaultdict(list)
		for row in rows:
			if row.get("docstatus") == 1:
				companies[row.get("company")].append(row)
		for company, submitted in companies.items():
			currency = frappe.get_cached_value("Company", company, "default_currency")
			if doctype == "Payment Entry" and "base_paid_amount" in allowed:
				for payment_type in ("Receive", "Pay", "Internal Transfer"):
					total = sum(
						flt(r.get("base_paid_amount"))
						for r in submitted
						if r.get("payment_type") == payment_type
					)
					cards.append(
						{
							"label": f"{payment_type} · {currency}",
							"value": total,
							"fieldtype": "Currency",
							"desc": f"{company} · submitted base paid amounts",
						}
					)
			else:
				for field, title in (
					("total_debit", "Debits"),
					("total_credit", "Credits"),
					("budget_amount", "Approved budget"),
				):
					if field in allowed:
						cards.append(
							{
								"label": f"{title} · {currency}",
								"value": sum(flt(r.get(field)) for r in submitted),
								"fieldtype": "Currency",
								"desc": f"{company} · matching submitted records",
							}
						)
	offset = max(0, cint(start))
	return {
		"kind": "list",
		"doctype": doctype,
		"columns": [
			{
				"fieldname": k,
				"label": allowed[k].label if k in allowed else k.title(),
				"fieldtype": allowed[k].fieldtype if k in allowed else "Data",
			}
			for k in selected
		],
		"result": rows[offset : offset + 25],
		"start": offset,
		"has_more": len(rows) > offset + 25,
		"total_count": len(rows),
		"calculations": cards,
		"charts": charts,
		"scope_note": "Charts and calculations use all matching accessible records, not just this page. Different currencies are kept separate.",
	}
