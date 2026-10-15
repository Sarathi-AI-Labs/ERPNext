"""DASH-013: Permission-aware executive business risks, pending approvals, and record drill-downs."""
from collections import defaultdict
from datetime import date, datetime, timedelta
import re

import frappe
from frappe.utils import flt, get_datetime, getdate, now_datetime

from sarathi_visibility.api.access import (
	allowed_fields,
	check_record,
	deny,
	require_capability,
	require_session,
	can_finance,
)
from sarathi_visibility.api.data_helpers import (
	_company,
	_date,
	_extra,
	_parse,
	invalid,
	pagination,
	read_errors,
)

FEATURE_KEYS = {
	"reference_at",
	"review_days",
	"risk_category",
	"risk_severity",
	"risk_start",
	"risk_page_length",
	"approval_start",
	"approval_page_length",
}
BASE_KEYS = {"company", "customer", "project", "from_date", "to_date"}

RISK_CATEGORIES = ("", "All", "Receivables", "Deliveries", "Projects", "Manufacturing")
RISK_SEVERITIES = ("", "All", "Critical", "High", "Medium", "Informational")
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Informational": 3}


def validate_risk_filters(filters):
	"""Strict server-side validation of executive risk filters."""
	values = _parse(filters)
	if set(values) - BASE_KEYS - FEATURE_KEYS:
		invalid("Unsupported executive risk filter.")
	values = {k: v for k, v in values.items() if v is not None and v != ""}
	values["company"] = _company(values.get("company"))

	for key in ("from_date", "to_date"):
		if key in values:
			_date(values[key])
	if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
		invalid("Date bounds must be ordered: from_date must be on or before to_date.")

	# Validate customer link
	if values.get("customer"):
		if not frappe.db.exists("Customer", values["customer"]):
			invalid("Selected customer does not exist.")
		check_record("Customer", values["customer"])

	# Validate project link and company/customer alignment
	if values.get("project"):
		if not frappe.db.exists("Project", values["project"]):
			invalid("Selected project does not exist.")
		project_doc = check_record("Project", values["project"])
		if project_doc.company != values["company"] or (values.get("customer") and project_doc.customer != values["customer"]):
			deny()

	# Validate reference_at
	ref = values.get("reference_at")
	if ref is not None:
		if not isinstance(ref, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", ref):
			invalid("Reference time must be a site-local ISO date and time.")
		try:
			ref_dt = datetime.fromisoformat(ref)
		except ValueError:
			invalid("Invalid reference time.")
	else:
		ref_dt = now_datetime().replace(microsecond=0)

	# Validate review_days
	_, window = pagination(0, values.get("review_days", 7)) if str(values.get("review_days", 7)) != "0" else (0, 0)
	if isinstance(values.get("review_days"), bool) or window > 90:
		invalid("Review window must be an integer from 0 to 90 days.")

	# Validate risk_category and risk_severity
	cat = values.get("risk_category", "")
	if cat not in RISK_CATEGORIES:
		invalid("Unsupported risk category filter.")
	values.setdefault("risk_category", "")

	sev = values.get("risk_severity", "")
	if sev not in RISK_SEVERITIES:
		invalid("Unsupported risk severity filter.")
	values.setdefault("risk_severity", "")

	# Validate pagination
	for prefix in ("risk", "approval"):
		start_k = f"{prefix}_start"
		len_k = f"{prefix}_page_length"
		values[start_k], values[len_k] = pagination(values.get(start_k, 0), values.get(len_k, 25))

	values.update(reference_at=str(ref_dt), review_days=window)
	return values, ref_dt


def _enrich_risk(alert):
	alert["entity_type"] = alert.get("record_type")
	alert["entity_name"] = alert.get("affected_record")
	alert["explanation"] = alert.get("description")
	alert["drilldown"] = {
		"type": "doctype",
		"doctype": alert.get("record_type"),
		"name": alert.get("affected_record"),
		"route": alert.get("drilldown_route", []),
	}
	return alert


def _enrich_approval(approval):
	approval["doctype"] = approval.get("reference_doctype")
	approval["docname"] = approval.get("reference_name")
	approval["status"] = approval.get("workflow_state")
	approval["date"] = approval.get("assigned_date")
	approval["drilldown"] = {
		"type": "doctype",
		"doctype": approval.get("reference_doctype"),
		"name": approval.get("reference_name"),
		"route": approval.get("drilldown_route", []),
	}
	return approval


def get_payment_risks(values, ref_dt):
	"""
	Generate customer receivable exceptions based on verified submitted Sales Invoices.
	Criteria:
	- docstatus = 1 (submitted)
	- outstanding_amount > 0 (strictly unpaid balance, never fully settled invoices)
	- company = values['company']
	- Overdue: due_date < reference_date
	- Due soon: reference_date <= due_date <= reference_date + review_days
	"""
	if not frappe.has_permission("Sales Invoice", "read"):
		return []

	company = values["company"]
	ref_date = ref_dt.date()
	review_days = values["review_days"]
	currency = frappe.get_cached_value("Company", company, "default_currency") or "INR"

	conditions = [
		["company", "=", company],
		["docstatus", "=", 1],
		["outstanding_amount", ">", 0.0],
	]
	if values.get("customer"):
		conditions.append(["customer", "=", values["customer"]])

	# Date bounds if specified
	if values.get("from_date"):
		conditions.append(["due_date", ">=", values["from_date"]])
	if values.get("to_date"):
		conditions.append(["due_date", "<=", values["to_date"]])

	fields = ["name", "customer", "posting_date", "due_date", "grand_total", "outstanding_amount", "currency"]
	invoices = frappe.get_all("Sales Invoice", filters=conditions, fields=fields, order_by="due_date asc", limit_page_length=500)

	alerts = []
	for inv in invoices:
		due = inv.due_date
		if not due:
			continue
		if isinstance(due, datetime):
			due = due.date()
		elif isinstance(due, str):
			try:
				due = date.fromisoformat(due[:10])
			except (ValueError, TypeError):
				continue

		outstanding = flt(inv.outstanding_amount)
		inv_currency = inv.currency or currency
		days_diff = (due - ref_date).days

		if days_diff < 0:
			days_overdue = abs(days_diff)
			severity = "Critical" if days_overdue >= 30 else "High"
			alerts.append({
				"id": f"receivable-{inv.name}",
				"category": "Receivables",
				"severity": severity,
				"title": f"Overdue Customer Receivable ({days_overdue}d past due)",
				"description": f"Outstanding balance of {inv_currency} {outstanding:,.2f} from {inv.customer} is {days_overdue} days past due date ({due}).",
				"trigger_reason": f"Submitted Sales Invoice past due date {due} with {inv_currency} {outstanding:,.2f} remaining unpaid.",
				"affected_record": inv.name,
				"record_type": "Sales Invoice",
				"customer": inv.customer,
				"project": None,
				"due_date": str(due),
				"days_due": days_diff,
				"amount": outstanding,
				"currency": inv_currency,
				"drilldown_route": ["Form", "Sales Invoice", inv.name],
			})
		elif days_diff <= review_days:
			alerts.append({
				"id": f"receivable-{inv.name}",
				"category": "Receivables",
				"severity": "Medium",
				"title": f"Customer Receivable Due Soon ({days_diff}d remaining)",
				"description": f"Payment of {inv_currency} {outstanding:,.2f} from {inv.customer} is due in {days_diff} days on {due}.",
				"trigger_reason": f"Submitted Sales Invoice payment due on {due} within {review_days}-day review window.",
				"affected_record": inv.name,
				"record_type": "Sales Invoice",
				"customer": inv.customer,
				"project": None,
				"due_date": str(due),
				"days_due": days_diff,
				"amount": outstanding,
				"currency": inv_currency,
				"drilldown_route": ["Form", "Sales Invoice", inv.name],
			})

	return [_enrich_risk(a) for a in alerts]


def get_project_delivery_risks(values, ref_dt):
	"""
	Generate Project and customer delivery commitment exceptions.
	- Project risks: Overdue projects, projects on hold, projects approaching deadline, milestone tasks overdue.
	- Delivery risks: Open Sales Orders with remaining quantity past promised delivery date or on hold.
	"""
	company = values["company"]
	ref_date = ref_dt.date()
	review_days = values["review_days"]
	alerts = []

	# --- 1. Project Risks ---
	if frappe.has_permission("Project", "read"):
		proj_conditions = [
			["company", "=", company],
			["docstatus", "<", 2],
			["status", "in", ["Open", "On hold"]],
		]
		if values.get("customer"):
			proj_conditions.append(["customer", "=", values["customer"]])
		if values.get("project"):
			proj_conditions.append(["name", "=", values["project"]])

		fields = ["name", "project_name", "customer", "status", "expected_start_date", "expected_end_date", "percent_complete"]
		projects = frappe.get_all("Project", filters=proj_conditions, fields=fields, order_by="expected_end_date asc", limit_page_length=500)

		for p in projects:
			p_name = p.project_name or p.name
			pct = flt(p.percent_complete)

			# On Hold check
			if p.status == "On hold":
				alerts.append({
					"id": f"project-hold-{p.name}",
					"category": "Projects",
					"severity": "High",
					"title": f"Project On Hold: {p_name}",
					"description": f"Project '{p_name}' for customer {p.customer or 'Internal'} is currently On Hold at {pct:.1f}% progress.",
					"trigger_reason": "Project recorded status is On hold.",
					"affected_record": p.name,
					"record_type": "Project",
					"customer": p.customer,
					"project": p.name,
					"due_date": str(p.expected_end_date) if p.expected_end_date else None,
					"days_due": (p.expected_end_date - ref_date).days if p.expected_end_date else None,
					"amount": None,
					"currency": None,
					"drilldown_route": ["Form", "Project", p.name],
				})

			end = p.expected_end_date
			if end:
				if isinstance(end, datetime):
					end = end.date()
				elif isinstance(end, str):
					try:
						end = date.fromisoformat(end[:10])
					except (ValueError, TypeError):
						end = None

			if end:
				days_diff = (end - ref_date).days
				if days_diff < 0:
					days_overdue = abs(days_diff)
					severity = "Critical" if days_overdue >= 14 else "High"
					alerts.append({
						"id": f"project-overdue-{p.name}",
						"category": "Projects",
						"severity": severity,
						"title": f"Overdue Project Deadline: {p_name}",
						"description": f"Project '{p_name}' expected completion was {end} ({days_overdue} days ago); current progress is {pct:.1f}%.",
						"trigger_reason": f"Expected project deadline {end} passed with status {p.status}.",
						"affected_record": p.name,
						"record_type": "Project",
						"customer": p.customer,
						"project": p.name,
						"due_date": str(end),
						"days_due": days_diff,
						"amount": None,
						"currency": None,
						"drilldown_route": ["Form", "Project", p.name],
					})
				elif days_diff <= review_days and p.status != "On hold":
					alerts.append({
						"id": f"project-duesoon-{p.name}",
						"category": "Projects",
						"severity": "Medium",
						"title": f"Project Deadline Approaching: {p_name}",
						"description": f"Project '{p_name}' expected completion is in {days_diff} days on {end}; current progress is {pct:.1f}%.",
						"trigger_reason": f"Expected completion date within {review_days}-day review window.",
						"affected_record": p.name,
						"record_type": "Project",
						"customer": p.customer,
						"project": p.name,
						"due_date": str(end),
						"days_due": days_diff,
						"amount": None,
						"currency": None,
						"drilldown_route": ["Form", "Project", p.name],
					})

		# Milestone tasks overdue
		if frappe.has_permission("Task", "read"):
			active_proj_ids = [p.name for p in projects]
			if active_proj_ids:
				task_conditions = [
					["project", "in", active_proj_ids],
					["is_milestone", "=", 1],
					["docstatus", "<", 2],
					["status", "not in", ["Completed", "Cancelled", "Template"]],
					["exp_end_date", "<", str(ref_dt)],
				]
				milestones = frappe.get_all(
					"Task",
					filters=task_conditions,
					fields=["name", "subject", "project", "exp_end_date", "status"],
					limit_page_length=200,
				)
				for m in milestones:
					alerts.append({
						"id": f"task-milestone-{m.name}",
						"category": "Projects",
						"severity": "High",
						"title": f"Overdue Milestone Task: {m.subject}",
						"description": f"Milestone task '{m.subject}' in project {m.project} is past its expected deadline ({m.exp_end_date}).",
						"trigger_reason": f"Milestone task incomplete past scheduled deadline {m.exp_end_date}.",
						"affected_record": m.name,
						"record_type": "Task",
						"customer": None,
						"project": m.project,
						"due_date": str(m.exp_end_date)[:10] if m.exp_end_date else None,
						"days_due": -1,
						"amount": None,
						"currency": None,
						"drilldown_route": ["Form", "Task", m.name],
					})

	# --- 2. Customer Delivery Risks ---
	if frappe.has_permission("Sales Order", "read"):
		so_conditions = [
			["company", "=", company],
			["docstatus", "=", 1],
			["status", "in", ["To Deliver and Bill", "To Deliver", "On Hold"]],
		]
		if values.get("customer"):
			so_conditions.append(["customer", "=", values["customer"]])
		if values.get("project"):
			so_conditions.append(["project", "=", values["project"]])

		sos = frappe.get_all("Sales Order", filters=so_conditions, fields=["name", "customer", "project", "status", "delivery_date"], limit_page_length=500)
		so_dict = {s.name: s for s in sos}

		if so_dict:
			items = frappe.get_all(
				"Sales Order Item",
				filters={"parent": ["in", list(so_dict.keys())], "docstatus": 1},
				fields=["parent", "item_code", "qty", "delivered_qty", "stock_uom", "delivery_date"],
				limit_page_length=2000,
			)

			for it in items:
				rem_qty = flt(it.qty) - flt(it.delivered_qty)
				if rem_qty <= 0:
					continue

				so = so_dict.get(it.parent)
				if not so:
					continue

				target = it.delivery_date or so.delivery_date
				if target:
					if isinstance(target, datetime):
						target = target.date()
					elif isinstance(target, str):
						try:
							target = date.fromisoformat(target[:10])
						except (ValueError, TypeError):
							target = None

				uom = it.stock_uom or "Nos"

				# On Hold order
				if so.status == "On Hold":
					alerts.append({
						"id": f"delivery-hold-{it.parent}-{it.item_code}",
						"category": "Deliveries",
						"severity": "High",
						"title": f"Customer Delivery On Hold: {so.name}",
						"description": f"Delivery commitment for {so.customer} ({rem_qty} {uom} of {it.item_code}) is On Hold.",
						"trigger_reason": "Sales Order delivery status is On Hold.",
						"affected_record": so.name,
						"record_type": "Sales Order",
						"customer": so.customer,
						"project": so.project,
						"due_date": str(target) if target else None,
						"days_due": (target - ref_date).days if target else None,
						"amount": rem_qty,
						"currency": uom,
						"drilldown_route": ["Form", "Sales Order", so.name],
					})

				if target:
					days_diff = (target - ref_date).days
					if days_diff < 0:
						days_overdue = abs(days_diff)
						severity = "Critical" if days_overdue >= 14 else "High"
						alerts.append({
							"id": f"delivery-overdue-{it.parent}-{it.item_code}",
							"category": "Deliveries",
							"severity": severity,
							"title": f"Overdue Customer Delivery: {so.customer}",
							"description": f"Delivery of {rem_qty} {uom} of {it.item_code} to {so.customer} was promised by {target} ({days_overdue} days ago).",
							"trigger_reason": f"Promised delivery date {target} passed with {rem_qty} {uom} remaining to deliver.",
							"affected_record": so.name,
							"record_type": "Sales Order",
							"customer": so.customer,
							"project": so.project,
							"due_date": str(target),
							"days_due": days_diff,
							"amount": rem_qty,
							"currency": uom,
							"drilldown_route": ["Form", "Sales Order", so.name],
						})
					elif days_diff <= review_days and so.status != "On Hold":
						alerts.append({
							"id": f"delivery-duesoon-{it.parent}-{it.item_code}",
							"category": "Deliveries",
							"severity": "Medium",
							"title": f"Customer Delivery Due Soon: {so.customer}",
							"description": f"Promised delivery of {rem_qty} {uom} of {it.item_code} to {so.customer} is due in {days_diff} days on {target}.",
							"trigger_reason": f"Delivery commitment due on {target} within {review_days}-day review window.",
							"affected_record": so.name,
							"record_type": "Sales Order",
							"customer": so.customer,
							"project": so.project,
							"due_date": str(target),
							"days_due": days_diff,
							"amount": rem_qty,
							"currency": uom,
							"drilldown_route": ["Form", "Sales Order", so.name],
						})

	return [_enrich_risk(a) for a in alerts]


def get_production_shortage_risks(values, ref_dt):
	"""
	Generate manufacturing delays and material shortage exceptions.
	- Overdue active Work Orders.
	- Work Orders approaching completion.
	- Active Work Orders blocked by raw material shortages.
	"""
	if not frappe.has_permission("Work Order", "read"):
		return []

	company = values["company"]
	ref_date = ref_dt.date()
	review_days = values["review_days"]
	alerts = []

	wo_conditions = [
		["company", "=", company],
		["docstatus", "=", 1],
		["status", "in", ["Not Started", "In Process"]],
	]
	if values.get("project"):
		wo_conditions.append(["project", "=", values["project"]])

	fields = ["name", "production_item", "item_name", "qty", "produced_qty", "stock_uom", "status", "planned_start_date", "planned_end_date", "expected_delivery_date", "project"]
	wos = frappe.get_list("Work Order", filters=wo_conditions, fields=fields, limit_page_length=500)
	wo_dict = {wo.name: wo for wo in wos}

	for wo in wos:
		target = wo.planned_end_date or wo.expected_delivery_date
		if target:
			if isinstance(target, datetime):
				target = target.date()
			elif isinstance(target, str):
				try:
					target = date.fromisoformat(target[:10])
				except (ValueError, TypeError):
					target = None

		prod_name = wo.item_name or wo.production_item
		uom = wo.stock_uom or "Nos"

		if target:
			days_diff = (target - ref_date).days
			if days_diff < 0:
				days_overdue = abs(days_diff)
				alerts.append({
					"id": f"mfg-overdue-{wo.name}",
					"category": "Manufacturing",
					"severity": "High",
					"title": f"Overdue Production Order: {prod_name}",
					"description": f"Work Order {wo.name} for {prod_name} was expected by {target} ({days_overdue} days ago); {flt(wo.produced_qty)}/{flt(wo.qty)} {uom} produced.",
					"trigger_reason": f"Target completion date {target} passed with Work Order in status {wo.status}.",
					"affected_record": wo.name,
					"record_type": "Work Order",
					"customer": None,
					"project": wo.project,
					"due_date": str(target),
					"days_due": days_diff,
					"amount": flt(wo.qty) - flt(wo.produced_qty),
					"currency": uom,
					"drilldown_route": ["Form", "Work Order", wo.name],
				})
			elif days_diff <= review_days:
				alerts.append({
					"id": f"mfg-duesoon-{wo.name}",
					"category": "Manufacturing",
					"severity": "Medium",
					"title": f"Production Order Due Soon: {prod_name}",
					"description": f"Work Order {wo.name} for {prod_name} is due in {days_diff} days on {target}; {flt(wo.produced_qty)}/{flt(wo.qty)} {uom} produced.",
					"trigger_reason": f"Expected completion date within {review_days}-day review window.",
					"affected_record": wo.name,
					"record_type": "Work Order",
					"customer": None,
					"project": wo.project,
					"due_date": str(target),
					"days_due": days_diff,
					"amount": flt(wo.qty) - flt(wo.produced_qty),
					"currency": uom,
					"drilldown_route": ["Form", "Work Order", wo.name],
				})

	# Material shortages affecting active Work Orders
	if wo_dict and frappe.has_permission("Work Order Item", "read") and frappe.has_permission("Bin", "read"):
		wo_items = frappe.get_all(
			"Work Order Item",
			filters={"parent": ["in", list(wo_dict.keys())]},
			fields=["parent", "item_code", "item_name", "source_warehouse", "required_qty", "transferred_qty"],
			limit_page_length=2000,
		)
		bin_keys = list({(it.item_code, it.source_warehouse) for it in wo_items if it.source_warehouse})
		items_needed = list({k[0] for k in bin_keys})
		warehouses_needed = list({k[1] for k in bin_keys})

		bin_map = {}
		if items_needed and warehouses_needed:
			bins = frappe.get_all(
				"Bin",
				filters={"item_code": ["in", items_needed], "warehouse": ["in", warehouses_needed]},
				fields=["item_code", "warehouse", "actual_qty", "reserved_qty"],
				limit_page_length=5000,
			)
			for b in bins:
				bin_map[(b.item_code, b.warehouse)] = b

		for it in wo_items:
			req = flt(it.required_qty)
			trans = flt(it.transferred_qty)
			rem_req = max(0.0, req - trans)
			if rem_req <= 0.0:
				continue

			bin_rec = bin_map.get((it.item_code, it.source_warehouse))
			actual_stock = flt(bin_rec.actual_qty) if bin_rec else 0.0
			reserved_stock = flt(bin_rec.reserved_qty) if bin_rec else 0.0
			available_stock = max(0.0, actual_stock - reserved_stock)

			shortage = max(0.0, rem_req - available_stock)
			if shortage > 0.0:
				wo = wo_dict.get(it.parent)
				target = wo.planned_end_date or wo.expected_delivery_date if wo else None
				days_diff = (target.date() - ref_date).days if isinstance(target, datetime) else (target - ref_date).days if isinstance(target, date) else None

				# Severity is Critical if the affected Work Order is overdue or due soon
				sev = "Critical" if (days_diff is not None and days_diff <= review_days) else "High"
				alerts.append({
					"id": f"shortage-{it.parent}-{it.item_code}",
					"category": "Manufacturing",
					"severity": sev,
					"title": f"Production Material Shortage: {it.item_code}",
					"description": f"Shortage of {shortage:,.2f} of {it.item_code} in warehouse '{it.source_warehouse}' blocks Work Order {it.parent}.",
					"trigger_reason": f"Required raw material ({rem_req:,.2f}) exceeds uncommitted available stock ({available_stock:,.2f}) in source warehouse.",
					"affected_record": it.parent,
					"record_type": "Work Order",
					"customer": None,
					"project": wo.project if wo else None,
					"due_date": str(target) if target else None,
					"days_due": days_diff,
					"amount": shortage,
					"currency": None,
					"drilldown_route": ["Form", "Work Order", it.parent],
				})

	return [_enrich_risk(a) for a in alerts]


def get_pending_approvals(values):
	"""
	Retrieve pending approvals genuinely assigned to or authorized for the logged-in user.
	Sources:
	- Workflow Action: status = 'Open' and (user = current_user OR role in user_roles)
	- ToDo: status = 'Open' and (allocated_to = current_user OR (role and role in user_roles))
	Read-focused: verifies read permission on the reference document.
	"""
	user = frappe.session.user
	if not user or user == "Guest":
		return []

	user_roles = set(frappe.get_roles(user))
	approvals = []

	# --- 1. Workflow Actions ---
	if frappe.has_permission("Workflow Action", "read"):
		# Find permitted workflow actions
		wf_actions = frappe.get_all(
			"Workflow Action",
			filters={"status": "Open"},
			fields=["name", "reference_doctype", "reference_name", "workflow_state", "user", "creation", "modified"],
			limit_page_length=200,
		)
		for wa in wf_actions:
			# Check user assignment or permitted role
			is_assigned = (wa.user == user)
			if not is_assigned:
				roles = frappe.get_all("Workflow Action Permitted Role", filters={"parent": wa.name}, pluck="role")
				if set(roles) & user_roles:
					is_assigned = True

			if is_assigned:
				# Verify permission to read reference document
				ref_dt = wa.reference_doctype
				ref_name = wa.reference_name
				if ref_dt and ref_name and frappe.has_permission(ref_dt, "read", ref_name):
					# If company filter applies, check document company
					doc_company = frappe.db.get_value(ref_dt, ref_name, "company")
					if doc_company and values.get("company") and doc_company != values["company"]:
						continue

					approvals.append({
						"id": f"wf-{wa.name}",
						"source_type": "Workflow",
						"reference_doctype": ref_dt,
						"reference_name": ref_name,
						"title": f"Workflow Approval: {ref_dt} {ref_name}",
						"workflow_state": wa.workflow_state or "Pending Approval",
						"description": f"Document {ref_dt} '{ref_name}' is awaiting your decision in state '{wa.workflow_state}'.",
						"assigned_date": str(wa.creation)[:10] if wa.creation else None,
						"priority": "High",
						"drilldown_route": ["Form", ref_dt, ref_name],
					})

	# --- 2. Assigned ToDo Actions ---
	if frappe.has_permission("ToDo", "read"):
		todo_conditions = [
			["status", "=", "Open"],
			["allocated_to", "=", user],
		]
		todos = frappe.get_all(
			"ToDo",
			filters=todo_conditions,
			fields=["name", "reference_type", "reference_name", "priority", "date", "description", "creation"],
			limit_page_length=200,
		)
		for t in todos:
			ref_dt = t.reference_type
			ref_name = t.reference_name
			if ref_dt and ref_name:
				if frappe.has_permission(ref_dt, "read", ref_name):
					doc_company = frappe.db.get_value(ref_dt, ref_name, "company")
					if doc_company and values.get("company") and doc_company != values["company"]:
						continue
					route = ["Form", ref_dt, ref_name]
				else:
					continue
			else:
				route = ["Form", "ToDo", t.name]

			approvals.append({
				"id": f"todo-{t.name}",
				"source_type": "Assignment",
				"reference_doctype": ref_dt or "Task",
				"reference_name": ref_name or t.name,
				"title": f"Assigned Action: {ref_dt or 'Task'}",
				"workflow_state": "Open",
				"description": t.description or "Action item assigned for your review.",
				"assigned_date": str(t.date or t.creation)[:10] if (t.date or t.creation) else None,
				"priority": t.priority or "Medium",
				"drilldown_route": route,
			})

	return [_enrich_approval(a) for a in approvals]


@frappe.whitelist(methods=["GET"])
@read_errors
def get_executive_risks_and_approvals(filters=None, **extra):
	"""
	Main entry point for Owner & Executive Business Risks, Exceptions, and Pending Approvals.
	Returns:
	- Triage of business-critical exceptions sorted by severity and deadline.
	- Genuinely pending approvals assigned to current user.
	- Bounded pagination and verified record drill-down routes.
	"""
	require_capability("owner")
	_extra(extra)
	values, ref_dt = validate_risk_filters(filters)

	# Fetch risks across categories
	payment_risks = get_payment_risks(values, ref_dt)
	proj_del_risks = get_project_delivery_risks(values, ref_dt)
	mfg_risks = get_production_shortage_risks(values, ref_dt)

	all_risks = payment_risks + proj_del_risks + mfg_risks

	# Deduplicate alerts by unique alert ID
	unique_risks = {}
	for r in all_risks:
		if r["id"] not in unique_risks:
			unique_risks[r["id"]] = r
	deduped_risks = list(unique_risks.values())

	# Calculate summary counts before category/severity filtering
	counts_by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Informational": 0}
	counts_by_category = defaultdict(int)
	for r in deduped_risks:
		counts_by_severity[r["severity"]] += 1
		counts_by_category[r["category"]] += 1

	# Apply category and severity filters if specified
	cat_filter = values.get("risk_category")
	sev_filter = values.get("risk_severity")

	filtered_risks = deduped_risks
	if cat_filter and cat_filter != "All":
		filtered_risks = [r for r in filtered_risks if r["category"] == cat_filter]
	if sev_filter and sev_filter != "All":
		filtered_risks = [r for r in filtered_risks if r["severity"] == sev_filter]

	# Sort risks: Severity first (Critical > High > Medium > Informational), then days_due ascending (most overdue first), then title
	filtered_risks.sort(key=lambda r: (
		SEVERITY_ORDER.get(r["severity"], 9),
		r["days_due"] if r["days_due"] is not None else 9999,
		r["title"]
	))

	# Pagination for risks
	r_start = values["risk_start"]
	r_length = values["risk_page_length"]
	paged_risks = filtered_risks[r_start:r_start + r_length]
	risks_has_next = (r_start + r_length) < len(filtered_risks)

	# Fetch pending approvals assigned to current user
	all_approvals = get_pending_approvals(values)

	# Pagination for approvals
	a_start = values["approval_start"]
	a_length = values["approval_page_length"]
	paged_approvals = all_approvals[a_start:a_start + a_length]
	approvals_has_next = (a_start + a_length) < len(all_approvals)

	currency = frappe.get_cached_value("Company", values["company"], "default_currency") or "INR"

	return {
		"applied_filters": values,
		"reference_at": str(ref_dt),
		"reference_date": str(ref_dt.date()),
		"review_days": values["review_days"],
		"currency": currency,
		"summary": {
			"total_risks": len(deduped_risks),
			"critical": counts_by_severity["Critical"],
			"high": counts_by_severity["High"],
			"medium": counts_by_severity["Medium"],
			"informational": counts_by_severity["Informational"],
			"pending_approvals": len(all_approvals),
			"categories": dict(counts_by_category),
		},
		"risks": {
			"available": True,
			"counts": counts_by_severity,
			"rows": paged_risks,
			"has_next": risks_has_next,
			"total_count": len(deduped_risks),
			"matching_count": len(filtered_risks),
			"basis": "Business exceptions evaluated against submitted invoices, open deliveries, project deadlines, and active manufacturing orders.",
		},
		"approvals": {
			"available": True,
			"count": len(all_approvals),
			"rows": paged_approvals,
			"has_next": approvals_has_next,
			"matching_count": len(all_approvals),
			"basis": "Pending workflow actions and task assignments genuinely allocated to the authorized user according to configured ERPNext workflows and assignments.",
		},
		"generated_at": str(now_datetime()),
	}
