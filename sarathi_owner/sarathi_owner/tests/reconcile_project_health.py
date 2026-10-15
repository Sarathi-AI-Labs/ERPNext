"""Read-only local DASH-011 comparisons with native Projects, Tasks and orders."""
from collections import Counter, defaultdict
from datetime import timedelta
from decimal import Decimal

import frappe
from frappe.utils import getdate, get_datetime, now_datetime
from sarathi_owner.api.project_health import get_project_delivery_health
from sarathi_owner.tests.reconcile_finance_kpis import batches


def run():
	if frappe.session.user!="Administrator":raise frappe.PermissionError("Use the authorized local audit identity.")
	company=frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company
	ref=now_datetime().replace(microsecond=0);window=7
	output={"company":company,"reference_at":str(ref),"review_days":window,"scopes":[],"differences":[]}
	customers=frappe.get_all("Project",filters={"company":company,"customer":["is","set"]},pluck="customer",limit=2)
	for label,extra in [("whole company",{}),("selected Customer",{"customer":customers[0]}),("zero-day review window",{"review_days":0})]:
		window=extra.get("review_days",7)
		result=get_project_delivery_health({"company":company,"reference_at":str(ref),"project_page_length":100,"task_page_length":100,"health_delivery_page_length":100,**extra})
		projects,deliveries=result["projects"],result["deliveries"]
		if not projects["available"] or not deliveries["available"]:raise AssertionError("Complete audit scope unavailable")
		conditions={"company":company,"docstatus":["<",2]}
		if extra.get("customer"):conditions["customer"]=extra["customer"]
		docs=list(batches("Project",["name","status","percent_complete","percent_complete_method","expected_end_date"],conditions))
		expected=dict(total=len(docs),active=sum(row.status in ("Open","On hold") for row in docs),completed=sum(row.status=="Completed" for row in docs),cancelled=sum(row.status=="Cancelled" for row in docs),
			overdue=sum(row.status in ("Open","On hold") and bool(row.expected_end_date) and getdate(row.expected_end_date)<ref.date() for row in docs),
			due_soon=sum(row.status=="Open" and bool(row.expected_end_date) and ref.date()<=getdate(row.expected_end_date)<=ref.date()+timedelta(days=window) for row in docs),held=sum(row.status=="On hold" for row in docs))
		checks=[]
		def compare(check,expected,actual):
			entry={"check":check,"expected":expected,"actual":actual,"passed":expected==actual}
			checks.append(entry)
			if not entry["passed"]:output["differences"].append({"scope":label,**entry})
		for key,value in expected.items():compare("Project "+key,value,projects["counts"][key])
		if projects["has_next"] or deliveries["has_next"]:raise AssertionError("Collect all audit pages before certifying")
		stored={row.name:row for row in docs}
		for row in projects["rows"]:
			compare("Stored progress "+row["name"],float(stored[row["name"]].percent_complete),row["progress"])
			compare("Stored method "+row["name"],stored[row["name"]].percent_complete_method,row["percent_complete_method"])
		active=[row.name for row in docs if row.status in ("Open","On hold")]
		tasks=list(batches("Task",["name","status","exp_end_date","is_milestone"],{"project":["in",active],"docstatus":["<",2]})) if active else []
		overdue_tasks=sum(row.status not in ("Completed","Cancelled","Template") and bool(row.exp_end_date) and get_datetime(row.exp_end_date)<ref for row in tasks)
		compare("Visible overdue Tasks",overdue_tasks,projects["tasks"]["counts"].get("overdue_tasks",0))
		# Independently inspect source order documents. Read-only; native delivered
		# counters are compared to the returned remaining stock quantity per line.
		order_filters={"company":company,"docstatus":1}
		if extra.get("customer"):order_filters["customer"]=extra["customer"]
		sets={key:set() for key in ("open_orders","overdue_orders","due_soon_orders","held_orders","partially_delivered_orders","unknown_date_orders")}
		line_values={};quantities=defaultdict(lambda:Decimal(0));line_counts=Counter()
		for entry in batches("Sales Order",["name","status"],order_filters):
			if entry.status in ("Closed","Stopped","Cancelled","Completed","To Bill"):continue
			order=frappe.get_doc("Sales Order",entry.name)
			for line in order.items:
				remaining=max(Decimal(str(line.qty))-Decimal(str(line.delivered_qty)),Decimal(0))
				if line.qty<=0 or not remaining:continue
				stock=remaining*Decimal(str(line.conversion_factor));line_values[line.name]=float(stock)
				if order.status=="On Hold":sets["held_orders"].add(order.name);line_counts["Held"]+=1;continue
				sets["open_orders"].add(order.name);quantities[(line.item_code,line.stock_uom)]+=stock
				if 0<order.per_delivered<100:sets["partially_delivered_orders"].add(order.name)
				if not line.delivery_date:sets["unknown_date_orders"].add(order.name);line_counts["Unknown"]+=1
				elif getdate(line.delivery_date)<ref.date():sets["overdue_orders"].add(order.name);line_counts["Overdue"]+=1
				elif getdate(line.delivery_date)<=ref.date()+timedelta(days=window):sets["due_soon_orders"].add(order.name);line_counts["Due soon"]+=1
				else:line_counts["Not overdue"]+=1
		for key,ids in sets.items():compare("Delivery "+key,len(ids),deliveries["counts"][key])
		compare("Delivery line partition",dict(line_counts),deliveries["line_counts"])
		for row in deliveries["rows"]:compare("Source line stock qty "+row["line"],line_values[row["line"]],row["remaining_qty"])
		for row in deliveries["quantities"]:compare("Item / UOM qty "+row["item_code"]+" / "+row["stock_uom"],float(quantities[(row["item_code"],row["stock_uom"])]),row["remaining_qty"])
		output["scopes"].append({"label":label,"filters":result["applied_filters"],"project_counts":projects["counts"],"delivery_counts":deliveries["counts"],"task_records":len(tasks),"checks":checks})
	output["passed"]=not output["differences"]
	return output
