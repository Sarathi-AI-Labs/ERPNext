"""Exact, permission-aware in-dashboard details for native accounting entries."""
from urllib.parse import parse_qs, unquote, urlsplit

import frappe

from sarathi_owner.api.detail_analytics import describe
from sarathi_owner.api.owner_dashboard import _get_date_bounds
from sarathi_owner.api.permissions import get_permission_context

DOCTYPES = {
	name.lower().replace(" ", "-"): name
	for name in (
		"Account",
		"Accounting Dimension",
		"Accounts Settings",
		"Bank Account",
		"Bank Guarantee",
		"BOM",
		"Budget",
		"Company",
		"Cost Center",
		"Cost Center Allocation",
		"Customer",
		"Dunning",
		"Fiscal Year",
		"Item",
		"Item Tax Template",
		"Journal Entry",
		"Mode of Payment",
		"Payment Entry",
		"Payment Order",
		"Payment Request",
		"Payment Term",
		"Project",
		"Purchase Invoice",
		"Purchase Taxes and Charges Template",
		"Sales Invoice",
		"Sales Taxes and Charges Template",
		"Share Transfer",
		"Shareholder",
		"Subscription",
		"Subscription Plan",
		"Subscription Settings",
		"Supplier",
		"Task",
		"Tax Category",
		"Tax Withholding Category",
		"Warehouse",
		"Work Order",
	)
}
DOCTYPES.update(
	{
		"bank-reconciliation-tool": "Bank Transaction",
		"bank-clearance": "Payment Entry",
		"payment-reconciliation": "Payment Entry",
		"credit-note": "Sales Invoice",
		"debit-note": "Purchase Invoice",
		"chart-of-accounts": "Account",
		"accounts": "Account",
	}
)

REPORTS = {
	"Accounts Receivable",
	"Accounts Payable",
	"Balance Sheet",
	"Profit and Loss Statement",
	"Cash Flow",
	"Trial Balance",
	"General Ledger",
	"TDS Computation Summary",
	"Budget Variance Report",
	"Share Ledger",
	"Share Balance",
}

# These Desk pages are operational tools or reports rather than record types.  The
# owner dashboard deliberately presents their relevant, permission-scoped source
# records instead of embedding the ERPNext Desk page (which exposes navigation and
# create actions that do not belong in this read-only dashboard).
ANALYSIS_SOURCES = {
	"Accounts Receivable": "Sales Invoice",
	"Accounts Payable": "Purchase Invoice",
	"Balance Sheet": "Journal Entry",
	"Profit and Loss Statement": "Journal Entry",
	"Profit and Loss": "Journal Entry",
	"Consolidated Report": "Journal Entry",
	"Custom Financial Statement": "Journal Entry",
	"Customer Ledger": "Sales Invoice",
	"Supplier Ledger": "Purchase Invoice",
	"AR Summary": "Sales Invoice",
	"AP Summary": "Purchase Invoice",
	"Sales Register": "Sales Invoice",
	"Purchase Register": "Purchase Invoice",
	"Item-wise sales Register": "Sales Invoice",
	"Item-wise Purchase Register": "Purchase Invoice",
	"Gross Profit": "Sales Invoice",
	"Profitability Analysis": "Sales Invoice",
	"Sales Invoice Trends": "Sales Invoice",
	"Purchase Invoice Trends": "Purchase Invoice",
	"Trial Balance for Party": "Journal Entry",
	"Payment Period Based On Invoice Date": "Payment Entry",
	"Sales Partners Commission": "Sales Invoice",
	"Customer Credit Balance": "Sales Invoice",
	"Sales Payment Summary": "Payment Entry",
	"Address And Contacts": "Customer",
	"UAE VAT 201": "Sales Invoice",
	"Cash Flow": "Payment Entry",
	"Trial Balance": "Journal Entry",
	"General Ledger": "Journal Entry",
	"Financial Reports": "Journal Entry",
	"TDS Computation Summary": "Purchase Invoice",
	"Budget Variance Report": "Budget",
	"Share Ledger": "Share Transfer",
	"Share Balance": "Shareholder",
	"Payment Reconciliation": "Payment Entry",
	"Process Payment Reconciliation": "Payment Entry",
	"Unreconcile Payment": "Payment Entry",
	"Repost Accounting Ledger": "Journal Entry",
	"Repost Payment Ledger": "Payment Entry",
	"Bank Reconciliation Tool": "Bank Transaction",
	"Bank Reconciliation": "Bank Transaction",
	"Reconciliation Statement": "Bank Transaction",
	"Bank Clearance": "Payment Entry",
	"Tax Withholding Details": "Purchase Invoice",
}

SAFE_TYPES = {
	"Data",
	"Link",
	"Select",
	"Date",
	"Datetime",
	"Currency",
	"Float",
	"Int",
	"Percent",
	"Check",
	"Small Text",
	"Text",
	"Time",
	"Duration",
}


@frappe.whitelist()
def get_details(
	route=None, filters=None, search="", start=0, name=None, label=None, kind=None, target=None, entry_id=None
):
	if not get_permission_context().get("can_access_owner"):
		frappe.throw("You do not have access to this dashboard.", frappe.PermissionError)
	filters = frappe.parse_json(filters) if isinstance(filters, str) else (filters or {})
	url = urlsplit(route or "")
	if url.scheme or url.netloc or "\\" in (route or ""):
		frappe.throw("Unsupported dashboard action.")
	item = None
	if entry_id:
		from sarathi_owner.api.module_catalog import _modules

		item = next((e for m in _modules() for e in m["entries"] if e["id"] == entry_id), None)
		if not item:
			frappe.throw("This entry is no longer available for your permissions.", frappe.PermissionError)
		route, kind, target, label = (item.get(k) for k in ("route", "kind", "target", "label"))
		if kind in ("Workspace", "Dashboard"):
			module_target = {"Accounts": "Invoicing"}.get(target, target)
			module = next(
				(
					m
					for m in _modules()
					if m["label"] == module_target or m["id"] == str(module_target).lower()
				),
				None,
			)
			response = {
				"kind": "workspace",
				"label": target,
				"entries": [
					e
					for e in (module or {}).get("entries", [])
					if e["kind"] != "Dashboard" and not (e["kind"] == "Workspace" and e["target"] == target)
				],
				"scope_note": "Choose an entry to view its own records, analysis or report.",
			}
			if kind == "Dashboard":
				response.update(calculations=[], charts=[])
				sources = (
					("Payment Entry",) if target == "Payments" else ("Sales Invoice", "Purchase Invoice")
				)
				for source in sources:
					if not frappe.has_permission(source, "read"):
						continue
					details = get_details("/app/" + source.lower().replace(" ", "-"), filters=filters)
					response["calculations"].extend(
						{**card, "label": source + " · " + card["label"]} for card in details["calculations"]
					)
					response["charts"].extend(
						{**chart, "title": source + " · " + chart["title"]} for chart in details["charts"]
					)
			return response
		analysis_doctype = ANALYSIS_SOURCES.get(target) or ANALYSIS_SOURCES.get(label)
		if kind in ("Report", "Page") or analysis_doctype:
			doctype = analysis_doctype
			if not doctype:
				return {
					"kind": "workspace",
					"label": label,
					"entries": [],
					"calculations": [],
					"charts": [],
					"scope_note": "No dashboard analysis is available for this entry yet.",
				}
			# Keep the heading meaningful while querying the relevant underlying
			# records.  This ensures tools and reports have a rich dashboard view.
			label = label or target
			route = "/app/" + doctype.lower().replace(" ", "-")
		elif kind != "DocType":
			return {
				"kind": "workspace",
				"label": label,
				"entries": [],
				"calculations": [],
				"charts": [],
				"scope_note": "No dashboard analysis is available for this entry yet.",
			}
		else:
			doctype = target
		url = urlsplit(route or "")
	else:
		parts = [unquote(p) for p in url.path.strip("/").split("/")]
		if len(parts) < 2 or parts[0] not in ("app", "desk"):
			frappe.throw("Unsupported dashboard action.")
		if parts[1] == "query-report" and len(parts) > 2 and parts[2] in REPORTS:
			if not get_permission_context().get("can_view_finance"):
				frappe.throw("Financial reports are restricted.", frappe.PermissionError)
			doctype = ANALYSIS_SOURCES.get(parts[2])
			if not doctype:
				frappe.throw("Unsupported dashboard action.")
			label = parts[2]
		else:
			doctype = DOCTYPES.get(parts[1])
			if not doctype:
				frappe.throw("Unsupported dashboard action.")
	if not frappe.has_permission(doctype, "read"):
		frappe.throw("You do not have permission to read these records.", frappe.PermissionError)
	meta = frappe.get_meta(doctype)
	from sarathi_owner.api.module_catalog import _fields

	readable_fields = _fields(meta)
	permitted = {f.fieldname for f in readable_fields}
	fields = [f for f in readable_fields if f.fieldtype in SAFE_TYPES]
	query_filters = dict((item or {}).get("filters") or {})
	for key in ("company", "customer", "supplier", "project"):
		if filters.get(key):
			frappe.get_doc(key.title(), filters[key]).check_permission("read")
			if meta.has_field(key):
				query_filters[key] = filters[key]
	for key, values in parse_qs(url.query).items():
		if key in ("project", "is_return") and meta.has_field(key):
			query_filters[key] = values[0]
	if label in ("Credit Note", "Debit Note") and meta.has_field("is_return"):
		query_filters["is_return"] = 1
	lower, upper = _get_date_bounds(
		filters.get("date_range"), filters.get("from_date"), filters.get("to_date")
	)
	date_field = next((k for k in ("posting_date", "transaction_date") if meta.has_field(k)), None)
	if date_field and lower and upper:
		query_filters[date_field] = ["between", [lower, upper]]
	if name or meta.issingle:
		doc = frappe.get_doc(doctype, name or doctype)
		doc.check_permission("read")
		if (
			name
			and not meta.issingle
			and not frappe.get_list(doctype, filters={**query_filters, "name": name}, limit_page_length=1)
		):
			frappe.throw("Record is outside the selected filters.", frappe.PermissionError)
		doc.apply_fieldlevel_read_permissions()
		tables = []
		for field in meta.fields:
			if (
				field.fieldtype not in ("Table", "Table MultiSelect")
				or field.hidden
				or field.fieldname not in permitted
			):
				continue
			child_meta = frappe.get_meta(field.options)
			child_fields = [f for f in _fields(child_meta, parenttype=doctype) if f.fieldtype in SAFE_TYPES]
			rows = doc.get(field.fieldname) or []
			tables.append(
				{
					"label": field.label,
					"columns": [
						{"fieldname": f.fieldname, "label": f.label, "fieldtype": f.fieldtype}
						for f in child_fields
					],
					"rows": [{f.fieldname: r.get(f.fieldname) for f in child_fields} for r in rows],
					"total": len(rows),
				}
			)
		return {
			"kind": "record",
			"doctype": doctype,
			"name": doc.name,
			"fields": [
				{
					"label": f.label,
					"fieldname": f.fieldname,
					"value": doc.get(f.fieldname),
					"fieldtype": f.fieldtype,
				}
				for f in fields
			],
			"tables": tables,
		}
	return describe(doctype, meta, fields, query_filters, search, start)
