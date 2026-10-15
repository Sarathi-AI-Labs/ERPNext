"""DASH-011: permission-aware recorded Project, Task and delivery health reads."""
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
import math
import re

import frappe
from frappe.query_builder import Case
from frappe.utils import get_datetime, getdate, now_datetime

from sarathi_owner.api.sales_analytics import EXCLUDED, full_read
from sarathi_visibility.api.access import allowed_fields, check_record, deny, require_capability
from sarathi_visibility.api.data_helpers import _company, _date, _extra, _parse, invalid, pagination, read_errors

FEATURE_KEYS = {"reference_at", "review_days", "project_health", "project_status", "project_start", "project_page_length", "task_view", "task_start", "task_page_length", "delivery_view", "health_delivery_start", "health_delivery_page_length"}
BASE_KEYS = {"company", "customer", "project", "from_date", "to_date", "order_status", "delivery_from", "delivery_to"}
PROJECT_FIELDS = ("name", "project_name", "company", "customer", "status", "percent_complete", "percent_complete_method", "expected_start_date", "expected_end_date", "actual_start_date", "actual_end_date", "modified", "docstatus")
TASK_FIELDS = ("name", "subject", "project", "company", "status", "exp_end_date", "is_milestone", "task_weight", "modified", "docstatus")
DELIVERY_FIELDS = {
	"Sales Order": {"name", "company", "customer", "project", "transaction_date", "status", "docstatus", "per_delivered"},
	"Sales Order Item": {"name", "parent", "parenttype", "parentfield", "project", "item_code", "qty", "delivered_qty", "stock_uom", "conversion_factor", "delivery_date"},
}
MAX_PROJECTS = 2000
MAX_GROUPS = 10000
PROJECT_STATES = ("Open", "On hold", "Completed", "Cancelled")
HEALTH_STATES = ("Overdue", "At risk", "Due soon", "Unknown", "Not overdue", "Completed", "Cancelled")
TASK_VIEWS = ("Attention", "All incomplete", "Overdue", "Due soon", "Milestones")
DELIVERY_VIEWS = ("All open", "Overdue", "Due soon", "Held", "Unknown")


def readable(doctype, fields):
	if not set(fields) <= allowed_fields(doctype):
		deny()
	# Native list queries apply permission_query_conditions, but arbitrary
	# document has_permission hooks cannot safely be approximated in aggregates.
	if frappe.get_hooks("has_permission", {}).get(doctype):
		deny()


def validate(filters):
	values = _parse(filters)
	if set(values) - BASE_KEYS - FEATURE_KEYS:
		invalid("Unsupported project/delivery health filter.")
	values = {key: value for key,value in values.items() if value is not None and value != ""}
	values["company"] = _company(values.get("company"))
	for key in ("from_date", "to_date", "delivery_from", "delivery_to"):
		if key in values:
			_date(values[key])
	for start,end in (("from_date","to_date"),("delivery_from","delivery_to")):
		if values.get(start) and values.get(end) and values[start] > values[end]:
			invalid("Health date bounds must be ordered.")
	for key,dt in (("customer","Customer"),("project","Project")):
		if key not in values:
			continue
		doc=check_record(dt,values[key])
		if dt=="Project" and (doc.company != values["company"] or (values.get("customer") and doc.customer != values["customer"])):
			deny()
	ref=values.get("reference_at")
	if ref is not None:
		if not isinstance(ref,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?",ref):
			invalid("Reference time must be a site-local ISO date and time.")
		try:
			ref=datetime.fromisoformat(ref)
		except ValueError:
			invalid("Invalid reference time.")
	else:
		ref=now_datetime().replace(microsecond=0)
	_,window=pagination(0, values.get("review_days",7)) if str(values.get("review_days",7)) != "0" else (0,0)
	if isinstance(values.get("review_days"),bool) or window>90:
		invalid("Review window must be an integer from 0 to 90 days.")
	for key,choices,default in (("project_health",HEALTH_STATES,""),("project_status",PROJECT_STATES,""),("task_view",TASK_VIEWS,"Attention"),("delivery_view",DELIVERY_VIEWS,"All open")):
		if key in values and values[key] not in choices:
			invalid("Unsupported health or status selection.")
		values.setdefault(key,default)
	if values.get("order_status"):
		statuses=(frappe.get_meta("Sales Order").get_field("status").options or "").splitlines()
		if values["order_status"] not in statuses or values["order_status"] in EXCLUDED:
			invalid("Select an open Sales Order status.")
	for prefix in ("project", "task", "health_delivery"):
		values[prefix+"_start"], values[prefix+"_page_length"] = pagination(values.get(prefix+"_start",0),values.get(prefix+"_page_length",25))
	values.update(reference_at=str(ref),review_days=window)
	return values,ref


def portfolio_filters(values):
	conditions=[["company","=",values["company"]],["docstatus","<",2]]
	for key in ("customer", "project", "project_status"):
		if values.get(key):
			conditions.append([{"project":"name","project_status":"status"}.get(key,key),"=",values[key]])
	for key,operator in (("from_date",">="),("to_date","<=")):
		if values.get(key):
			conditions.append(["expected_start_date",operator,values[key]])
	return conditions


def task_filters(ids, values, ref, detail=False):
	conditions=[["project","in",ids],["docstatus","<",2]]
	if detail:
		conditions.append(["status","not in",["Completed","Cancelled","Template"]])
		view=values["task_view"]
		if view in ("Attention","Milestones"):
			conditions.append(["exp_end_date","<=",str(ref+timedelta(days=values["review_days"]))])
		if view=="Milestones":
			conditions.append(["is_milestone","=",1])
		if view=="Overdue":
			conditions.append(["exp_end_date","<",str(ref)])
		if view=="Due soon":
			conditions.extend([["exp_end_date",">=",str(ref)],["exp_end_date","<=",str(ref+timedelta(days=values["review_days"]))]])
	return conditions


def task_health(deadline, ref, window):
	if not deadline:
		return "Unknown"
	try:
		end=datetime.fromisoformat(str(deadline))
	except (TypeError,ValueError):
		return "Unknown"
	return "Overdue" if end<ref else "Due soon" if end<=ref+timedelta(days=window) else "Not overdue"


def delivery_health(row, ref, window):
	if row.status=="On Hold":return "Held"
	if not row.delivery_date:return "Unknown"
	try:end=date.fromisoformat(str(row.delivery_date)[:10])
	except (TypeError,ValueError):return "Unknown"
	return "Overdue" if end<ref.date() else "Due soon" if end<=ref.date()+timedelta(days=window) else "Not overdue"


def tasks(projects, values, ref):
	readable("Task",TASK_FIELDS)
	ids=[row.name for row in projects]
	active=[row.name for row in projects if row.status in ("Open","On hold")]
	coverage=defaultdict(lambda:dict(visible_tasks=0,visible_weight=0,overdue_tasks=0,due_soon_tasks=0,overdue_milestones=0,due_soon_milestones=0,unknown_dates=0))
	if not ids:
		return {"available":True,"rows":[],"has_next":False,"counts":{},"coverage":"Visible Tasks only."},coverage
	# Explicit readable Project IDs enforce the parent boundary in addition to Task's native permissions.
	or_company=[["company","=",values["company"]],["company","is","not set"]]
	groups=frappe.get_list("Task",fields=["project","status","exp_end_date","is_milestone",{"COUNT":"name","as":"task_count"},{"SUM":"task_weight","as":"weight"}],
		filters=task_filters(ids,values,ref),or_filters=or_company,group_by="project,status,exp_end_date,is_milestone",order_by="project asc",page_length=MAX_GROUPS+1)
	if len(groups)>MAX_GROUPS:
		raise NotImplementedError("Too many Task groups; narrow the Project scope.")
	for row in groups:
		count=int(row.task_count); info=coverage[row.project]
		info["visible_tasks"]+=count;info["visible_weight"]+=float(row.weight or 0)
		if row.project not in active or row.status in ("Completed","Cancelled","Template"):
			continue
		health=task_health(row.exp_end_date,ref,values["review_days"])
		if health=="Overdue":
			info["overdue_tasks"]+=count
			if row.is_milestone:info["overdue_milestones"]+=count
		elif health=="Due soon":
			info["due_soon_tasks"]+=count
			if row.is_milestone:info["due_soon_milestones"]+=count
		elif health=="Unknown":info["unknown_dates"]+=count
	start,length=values["task_start"],values["task_page_length"]
	# Direct permission-aware QB avoids legacy get_list's IFNULL(Datetime,...)
	# string comparison, which drops exact inclusive microsecond boundaries and
	# can include undated rows in an overdue filter. Native permissions stay on.
	rows=frappe.qb.get_query("Task",fields=list(TASK_FIELDS),filters=task_filters(active,values,ref,True),or_filters=or_company,
		order_by="exp_end_date asc,name asc",offset=start,limit=length+1,ignore_permissions=False).run(as_dict=True) if active else []
	for row in rows:
		row["health"]=task_health(row.exp_end_date,ref,values["review_days"])
	counts={key:sum(info[key] for info in coverage.values()) for key in ("overdue_tasks","due_soon_tasks","overdue_milestones","due_soon_milestones","unknown_dates")}
	return {"available":True,"rows":rows[:length],"has_next":len(rows)>length,"counts":counts,"coverage":"Visible Tasks only; zero visible Tasks does not prove there are none."},coverage


def classify_project(row, ref, window, coverage):
	status=row.status; end=row.expected_end_date; reason=""
	try:
		end=date.fromisoformat(str(end)[:10]) if end else None
		if end and row.expected_start_date and date.fromisoformat(str(row.expected_start_date)[:10])>end:
			end=None;reason="Expected start is after expected end."
	except (TypeError,ValueError):
		end=None;reason="Invalid expected schedule dates."
	overdue=status in ("Open","On hold") and end is not None and end<ref.date()
	due_soon=status=="Open" and end is not None and ref.date()<=end<=ref.date()+timedelta(days=window)
	if status not in PROJECT_STATES:
		health="Unknown";reason="This recorded Project status has no verified health rule."
	elif status in ("Completed","Cancelled"):
		health=status;reason="Recorded terminal Project status; excluded from deadline alerts."
	elif overdue:
		health="Overdue";reason="Expected Project end date has passed."
	elif status=="On hold":
		health="At risk";reason="Project is recorded On hold."
	elif coverage and coverage["overdue_tasks"]:
		health="At risk";reason="An accessible incomplete Task deadline has passed."
	elif not end:
		health="Unknown";reason=reason or "No recorded expected Project end date."
	elif due_soon:
		health="Due soon";reason="Expected Project end is within the selected review window."
	else:
		health="Not overdue";reason="Date has not passed; this is not a forecast or guarantee of On track."
	value=row.percent_complete
	try:
		value=float(value) if value is not None else None
		if value is not None and (not math.isfinite(value) or not 0<=value<=100):value=None
	except (TypeError,ValueError):value=None
	warnings=[]
	if value is None:warnings.append("Recorded progress is unavailable or invalid.")
	if coverage is None:warnings.append("Task coverage unavailable; recorded progress is not recalculated.")
	elif not coverage["visible_tasks"] and row.percent_complete_method!="Manual":warnings.append("No accessible Tasks; native no-Task progress can be zero. This is not proof of execution.")
	elif row.percent_complete_method=="Task Weight" and not coverage["visible_weight"]:warnings.append("Accessible Tasks have zero total weight; native progress may be zero.")
	return {**dict(row),"progress":value,"health":health,"reason":reason,"overdue":overdue,"due_soon":due_soon,
		"days_to_end":(end-ref.date()).days if end else None,"task_coverage":coverage,"progress_warnings":warnings,
		"progress_method":row.percent_complete_method or "Task Completion (native default)"}


def projects(values, ref):
	readable("Project",PROJECT_FIELDS)
	rows=frappe.get_list("Project",fields=list(PROJECT_FIELDS),filters=portfolio_filters(values),order_by="name asc",page_length=MAX_PROJECTS+1)
	if len(rows)>MAX_PROJECTS:
		raise NotImplementedError("More than 2000 Projects match; narrow the portfolio filters.")
	messages=list(getattr(frappe.local,"message_log",[]) or [])
	try:
		task_data,coverage=tasks(rows,values,ref)
	except (frappe.PermissionError,NotImplementedError) as error:
		frappe.local.message_log=messages
		task_data={"available":False,"reason":str(error) if isinstance(error,NotImplementedError) else "Tasks are unavailable for this permission scope."};coverage=None
	classified=[classify_project(row,ref,values["review_days"],coverage[row.name] if coverage is not None else None) for row in rows]
	counts=dict(total=len(rows),active=sum(row.status in ("Open","On hold") for row in rows),completed=sum(row.status=="Completed" for row in rows),cancelled=sum(row.status=="Cancelled" for row in rows),
		overdue=sum(row["overdue"] for row in classified),due_soon=sum(row["due_soon"] for row in classified),held=sum(row.status=="On hold" for row in rows))
	counts["at_risk"]=sum(row["health"]=="At risk" for row in classified)
	counts["unknown"]=sum(row["health"]=="Unknown" for row in classified)
	partition=dict(Counter(row["health"] for row in classified))
	selected=[row for row in classified if not values["project_health"] or row["health"]==values["project_health"]]
	selected.sort(key=lambda row:(HEALTH_STATES.index(row["health"]),row["name"]))
	start,length=values["project_start"],values["project_page_length"]
	return {"available":True,"rows":selected[start:start+length],"has_next":start+length<len(selected),"matching_count":len(selected),"counts":counts,"health_partition":partition,"tasks":task_data,
		"basis":"Current recorded Project progress/status. Global dates select expected-start cohort. Health filters select detail rows; portfolio totals retain the same cohort.",
		"forecast":"Unavailable: no approved critical-path or required-production mapping. Not overdue does not guarantee On track."}


def delivery(values, ref):
	# Child-link restrictions cannot be approximated from a parent list alone.
	# Reuse DASH-010's conservative full-scope gate with NON-financial fields only.
	full_read(values["company"],DELIVERY_FIELDS)
	parent_filters=[["company","=",values["company"]],["docstatus","=",1],["status","not in",list(EXCLUDED)]]
	if values.get("customer"):parent_filters.append(["customer","=",values["customer"]])
	if values.get("order_status"):parent_filters.append(["status","=",values["order_status"]])
	for key,operator in (("from_date",">="),("to_date","<=")):
		if values.get(key):parent_filters.append(["transaction_date",operator,values[key]])
	parents=frappe.get_list("Sales Order",fields=["name"],filters=parent_filters,page_length=MAX_PROJECTS+1)
	if len(parents)>MAX_PROJECTS:raise NotImplementedError("More than 2000 orders match; narrow delivery filters.")
	order,item=[frappe.qb.DocType(dt) for dt in ("Sales Order","Sales Order Item")]
	project=Case().when(item.project.isnull() | (item.project==""),order.project).else_(item.project)
	query=(frappe.qb.from_(order).join(item).on((item.parent==order.name)&(item.parenttype=="Sales Order")&(item.parentfield=="items"))
		.where(order.name.isin([row.name for row in parents])).where((item.qty>0)&(item.delivered_qty<item.qty)))
	if values.get("project"):query=query.where(project==values["project"])
	for key,operator in (("delivery_from",">="),("delivery_to","<=")):
		if values.get(key):query=query.where(item.delivery_date>=values[key]) if operator==">=" else query.where(item.delivery_date<=values[key])
	fields=(order.name.as_("sales_order"),order.customer,order.status,order.per_delivered,order.transaction_date,item.name.as_("line"),project.as_("project"),item.item_code,item.stock_uom,item.conversion_factor,item.qty,item.delivered_qty,item.delivery_date)
	all_rows=query.select(*fields).limit(MAX_GROUPS+1).run(as_dict=True) if parents else []
	if len(all_rows)>MAX_GROUPS:raise NotImplementedError("More than 10000 delivery lines match; narrow delivery filters.")
	sets={key:set() for key in ("open_orders","overdue_orders","due_soon_orders","held_orders","partially_delivered_orders","unknown_date_orders")}
	line_counts=Counter();quantities=defaultdict(lambda:Decimal(0))
	for row in all_rows:
		if not row.stock_uom or row.conversion_factor is None or float(row.conversion_factor)<=0:
			raise NotImplementedError("Delivery lines have missing stock UOM or invalid conversion factors.")
		health=delivery_health(row,ref,values["review_days"]);line_counts[health]+=1
		if health=="Held":sets["held_orders"].add(row.sales_order);continue
		sets["open_orders"].add(row.sales_order)
		if health in ("Overdue","Due soon","Unknown"):sets[{"Overdue":"overdue_orders","Due soon":"due_soon_orders","Unknown":"unknown_date_orders"}[health]].add(row.sales_order)
		if 0<float(row.per_delivered or 0)<100:sets["partially_delivered_orders"].add(row.sales_order)
		quantities[(row.item_code,row.stock_uom)]+=(Decimal(str(row.qty))-Decimal(str(row.delivered_qty)))*Decimal(str(row.conversion_factor))
	view=values["delivery_view"]
	filtered=query
	if view=="Held":filtered=filtered.where(order.status=="On Hold")
	elif view!="All open":
		filtered=filtered.where(order.status!="On Hold")
		if view=="Overdue":filtered=filtered.where(item.delivery_date<str(ref.date()))
		elif view=="Due soon":filtered=filtered.where(item.delivery_date[str(ref.date()):str(ref.date()+timedelta(days=values["review_days"]))])
		elif view=="Unknown":filtered=filtered.where(item.delivery_date.isnull())
	start,length=values["health_delivery_start"],values["health_delivery_page_length"]
	rows=filtered.select(*fields).orderby(order.name).orderby(item.name).offset(start).limit(length+1).run(as_dict=True) if parents else []
	for row in rows:
		row["health"]=delivery_health(row,ref,values["review_days"])
		row["remaining_qty"]=float((Decimal(str(row.qty))-Decimal(str(row.delivered_qty)))*Decimal(str(row.conversion_factor)))
		row["days_to_delivery"]=(getdate(row.delivery_date)-ref.date()).days if row.delivery_date else None
	return {"available":True,"rows":rows[:length],"has_next":len(rows)>length,"counts":{key:len(ids) for key,ids in sets.items()},"line_counts":dict(line_counts),
		"quantities":[{"item_code":key[0],"stock_uom":key[1],"remaining_qty":float(qty)} for key,qty in sorted(quantities.items())[:100]],"quantity_group_count":len(quantities),
		"basis":"Current submitted undelivered order lines, excluding terminal orders; held demand separate. Global dates select order transaction dates. Remaining stock quantity uses native delivered counters and conversion factor, not invoices subtracted from order value.",
		"coverage":"Orders may have both overdue and upcoming lines; order buckets overlap, line classifications do not. No delivery value or recognized revenue is returned."}


@frappe.whitelist(methods=["GET"])
@read_errors
def get_project_delivery_health(filters=None, **extra):
	require_capability("owner")
	_extra(extra)
	values,ref=validate(filters)
	result={"applied_filters":values,"generated_at":str(now_datetime()),"reference_at":str(ref),"reference_date":str(ref.date()),"review_days":values["review_days"]}
	for key,compute in (("projects",projects),("deliveries",delivery)):
		messages=list(getattr(frappe.local,"message_log",[]) or [])
		try:
			result[key]=compute(values,ref)
		except (frappe.PermissionError,NotImplementedError) as error:
			frappe.local.message_log=messages
			result[key]={"available":False,"reason":str(error) if isinstance(error,NotImplementedError) else "This health section is unavailable for your permission scope."}
	return result
