"""Read-only local reconciliation evidence. Run through bench execute; no fixtures."""
from decimal import Decimal
import time

import frappe
from frappe.utils import add_days, get_first_day, today
from erpnext.accounts.utils import get_fiscal_year, get_party_types_from_account_type
from sarathi_owner.api.finance_kpis import get_finance_kpis, native_report


def batches(doctype, fields, filters):
	start = 0
	while True:
		rows = frappe.get_list(doctype, fields=fields, filters=filters, order_by="name asc", start=start, page_length=250)
		yield from rows
		if len(rows) < 250:
			break
		start += 250


def run():
	# This audit deliberately requires full authorized scope; it is not a public endpoint.
	if frappe.session.user != "Administrator":
		raise frappe.PermissionError("Run local reconciliation with the authorized audit identity.")
	company = frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company
	start = str(get_fiscal_year(today(),company=company)[1])
	precision = int(frappe.db.get_default("currency_precision") or 2)
	quantum = Decimal(1).scaleb(-precision)
	output = {"company":company,"currency":frappe.get_cached_value("Company",company,"default_currency"),"currency_precision":precision,"periods":[],"differences":[]}
	for label, from_date, to_date in [("fiscal year to date",start,today()),("month to date",str(get_first_day(today())),today()),("historical cutoff",start,add_days(start,90))]:
		began=time.monotonic()
		result=get_finance_kpis({"company":company,"from_date":from_date,"to_date":to_date})
		period={"label":label,"from_date":from_date,"to_date":to_date,"comparisons":[],"seconds":round(time.monotonic()-began,3)}
		output["periods"].append(period)
		cache={}
		for metric in result["metrics"]:
			if not metric["available"]:
				period["comparisons"].append({"metric":metric["key"],"status":"unavailable","reason":metric["reason"]})
				continue
			key=metric["source"]
			cache.setdefault(key,None)
			if cache[key] is None:
				cache[key]=native_report(key,metric["report_filters"])
			native=cache[key]
			if key=="Profit and Loss Statement":
				income,expense,profit=[Decimal(str(row["value"])) for row in native[4]]
				expected={"income":income,"expense":expense,"net_profit":profit,"net_margin":profit/income*100 if income else None}[metric["key"]]
			elif key=="Gross Profit":
				total=[row for row in native[1] if row.get("sales_invoice")=="Total" and row.get("indent") is None][0]
				selling=Decimal(str(total["selling_amount"]));gross=Decimal(str(total["gross_profit"]))
				expected=gross if metric["key"]=="gross_profit" else gross/selling*100
			else:
				expected=sum((Decimal(str(row["outstanding"])) for row in native[1] if row.get("voucher_type") and row.get("voucher_no")),Decimal(0))
			actual=Decimal(str(metric["value"]))
			difference=actual-expected
			comparison={"metric":metric["key"],"reference":key,"reference_filters":metric["report_filters"],"expected":str(expected),"actual":str(actual),"raw_difference":str(difference),"currency_rounded_difference":str(difference.quantize(quantum)),"comparison_precision":2 if metric["unit"]=="%" else precision,"status":"matched" if actual.quantize(Decimal("0.01") if metric["unit"]=="%" else quantum)==expected.quantize(Decimal("0.01") if metric["unit"]=="%" else quantum) else "mismatch"}
			period["comparisons"].append(comparison)
			if comparison["status"]=="mismatch":output["differences"].append(comparison)

		# Independent native GL arithmetic for default-book P&L, not the dashboard extractor.
		accounts={row.name:row.root_type for row in batches("Account",["name","root_type"],{"company":company,"is_group":0})}
		book=frappe.get_cached_value("Company",company,"default_finance_book") or ""
		ignore_opening=frappe.db.get_single_value("Accounts Settings","ignore_is_opening_check_for_reporting")
		income=Decimal(0);expense=Decimal(0);count=0
		for row in batches("GL Entry",["account","debit","credit","voucher_type","is_opening","finance_book"],{"company":company,"is_cancelled":0,"posting_date":["between",[from_date,to_date]]}):
			if row.voucher_type=="Period Closing Voucher" or (not ignore_opening and row.is_opening!="No") or (row.finance_book or "") not in ("",book):continue
			count+=1
			if accounts.get(row.account)=="Income":income+=Decimal(str(row.credit))-Decimal(str(row.debit))
			if accounts.get(row.account)=="Expense":expense+=Decimal(str(row.debit))-Decimal(str(row.credit))
		period["independent_gl"]={"income":str(income),"expense":str(expense),"net_profit":str(income-expense),"eligible_entries":count}
		for key,expected in [("income",income),("expense",expense),("net_profit",income-expense)]:
			actual=next(metric["value"] for metric in result["metrics"] if metric["key"]==key)
			if actual is not None and (Decimal(str(actual))-expected).quantize(quantum)!=0:
				output["differences"].append({"metric":key,"reference":"independent GL","period":label,"expected":str(expected),"actual":str(actual)})
		period["independent_payment_ledger"]={}
		for account_type,key in [("Receivable","receivables"),("Payable","payables")]:
			rows=list(batches("Payment Ledger Entry",["amount"],{"company":company,"account_type":account_type,"party_type":"Customer" if key=="receivables" else "Supplier","posting_date":["<=",to_date],"delinked":0}))
			expected=sum((Decimal(str(row.amount)) for row in rows),Decimal(0))
			actual=next(metric["value"] for metric in result["metrics"] if metric["key"]==key)
			difference=Decimal(str(actual))-expected if actual is not None else None
			period["independent_payment_ledger"][key]={"expected_signed_balance":str(expected),"actual":str(actual),"difference":str(difference),"entries":len(rows)}
			if difference is not None and difference.quantize(quantum)!=0:
				output["differences"].append({"metric":key,"reference":"independent Payment Ledger","period":label,"expected":str(expected),"actual":str(actual)})
	output["passed"]=not output["differences"]
	return output
