"""Manual read-only DASH-010 reconciliation against native reports/documents."""
from decimal import Decimal
import time

import frappe
from frappe.utils import add_days, get_first_day, today
from erpnext.accounts.utils import get_fiscal_year
from erpnext.selling.report.sales_order_analysis.sales_order_analysis import execute as sales_order_analysis
from sarathi_owner.api.sales_analytics import get_sales_analytics
from sarathi_owner.api.finance_kpis import native_report
from sarathi_owner.tests.reconcile_finance_kpis import batches


def run():
	if frappe.session.user != "Administrator":
		raise frappe.PermissionError("Use the authorized local audit identity.")
	company = frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company
	start = str(get_fiscal_year(today(),company=company)[1])
	output = {"company":company,"verified_at":today(),"periods":[],"differences":[]}
	precision=int(frappe.db.get_default("currency_precision") or 2)
	quantum=Decimal(1).scaleb(-precision)
	for label,begin,end in [("fiscal year to date",start,today()),("month to date",str(get_first_day(today())),today()),("historical empty cohort",start,add_days(start,90))]:
		began=time.monotonic()
		result=get_sales_analytics({"company":company,"from_date":begin,"to_date":end,"page_length":100,"backlog_page_length":100})
		revenue,backlog=result["revenue"],result["backlog"]
		if not revenue["available"] or not backlog["available"]:
			raise AssertionError("Local complete-scope analytics unavailable")
		native=native_report("Profit and Loss Statement",revenue["reference_filters"])
		expected_income=Decimal(str(native[4][0]["value"]))
		trend=sum((Decimal(str(row["amount"])) for row in revenue["trend"]),Decimal(0))
		customers=sum((Decimal(str(row["amount"])) for row in revenue["rows"]),Decimal(0))
		checks=[]
		def compare(name,expected,actual):
			diff=Decimal(str(actual))-Decimal(str(expected))
			entry=dict(check=name,expected=str(expected),actual=str(actual),raw_difference=str(diff),currency_rounded_difference=str(diff.quantize(quantum)),passed=diff.quantize(quantum)==0)
			checks.append(entry)
			if not entry["passed"]:output["differences"].append({"period":label,**entry})
		compare("Included accounting income vs native P&L",expected_income,revenue["included_income"])
		compare("Trend sum vs native P&L",expected_income,trend)
		if revenue["has_next"]:raise AssertionError("Audit must collect all customer pages")
		compare("Customer breakdown plus unattributed vs native P&L",expected_income,customers+Decimal(str(revenue["unattributed"])))
		# Independently read native order documents; no dashboard joins or formula helper.
		expected_value=Decimal(0);held=Decimal(0);line_count=0;quantities={}
		for row in batches("Sales Order",["name","status"],{"company":company,"docstatus":1,"transaction_date":["between",[begin,end]]}):
			if row.status in ("Closed","Stopped","Cancelled","Completed","To Bill"):continue
			order=frappe.get_doc("Sales Order",row.name)
			for item in order.items:
				remaining=max(Decimal(str(item.qty))-Decimal(str(item.delivered_qty)),Decimal(0))
				if not remaining:continue
				line_count+=1
				amount=remaining*Decimal(str(item.base_net_rate))
				if row.status=="On Hold":held+=amount
				else:
					expected_value+=amount
					key=(item.item_code,item.stock_uom)
					quantities[key]=quantities.get(key,Decimal(0))+remaining*Decimal(str(item.conversion_factor))
		compare("Delivery backlog vs source order net rates",expected_value,backlog["remaining_value"])
		compare("Held demand vs source orders",held,backlog["held_value"])
		if backlog["has_next"]:raise AssertionError("Audit must collect all backlog pages")
		compare("Detail sum vs executable plus held commitments",expected_value+held,sum((Decimal(str(row["remaining_value"])) for row in backlog["rows"]),Decimal(0)))
		for row in backlog["quantities"]:compare("Stock quantity "+row["item_code"]+" / "+row["stock_uom"],quantities[(row["item_code"],row["stock_uom"])],row["remaining_qty"])
		# Native report's pending_qty is delivery quantity; pending_amount is UNBILLED.
		report=sales_order_analysis(frappe._dict(company=company,from_date=begin,to_date=end))
		native_lines={row["name"]:row for row in report[1]}
		for row in backlog["rows"]:
			if row["held"]:continue  # Native report intentionally excludes On Hold.
			ref=native_lines[row["line"]]
			compare("Native Sales Order Analysis remaining line "+row["line"],max(Decimal(str(ref["pending_qty"])),Decimal(0)),Decimal(str(row["ordered_qty"]))-Decimal(str(row["delivered_qty"])))
		output["periods"].append({"label":label,"from_date":begin,"to_date":end,"currency":result["currency"],"reference_filters":revenue["reference_filters"],"checks":checks,"top_customers":revenue["top_customers"],"unattributed":revenue["unattributed"],"backlog_lines":line_count,"seconds":round(time.monotonic()-began,3)})
	output["passed"]=not output["differences"]
	return output
