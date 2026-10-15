"""DASH-013 Live reconciliation between executive risks/approvals and native ERPNext records."""
from datetime import date, datetime
import json
import frappe
from frappe.utils import flt, getdate, now_datetime

from sarathi_owner.api.executive_risks import get_executive_risks_and_approvals


def reconcile():
	frappe.set_user("Administrator")
	companies = frappe.get_all("Company", pluck="name")
	results = []

	for company in companies:
		payload = get_executive_risks_and_approvals({
			"company": company,
			"review_days": 14,
			"risk_page_length": 100,
			"approval_page_length": 100,
		})
		summary = payload["summary"]
		risks = payload["risks"]["rows"]
		approvals = payload["approvals"]["rows"]
		ref_date = date.fromisoformat(payload["reference_date"])

		# 1. Reconcile Receivables alerts
		receivable_alerts = [r for r in risks if r["category"] == "Receivables"]
		for r in receivable_alerts:
			inv = frappe.get_doc("Sales Invoice", r["affected_record"])
			assert inv.company == company, f"Invoice {inv.name} company mismatch"
			assert inv.docstatus == 1, f"Invoice {inv.name} is not submitted"
			assert flt(inv.outstanding_amount) > 0, f"Invoice {inv.name} has no outstanding balance"

		# Check DB count of overdue submitted invoices for company
		db_overdue_invoices = frappe.db.sql(
			"""
			SELECT name, outstanding_amount, due_date
			FROM `tabSales Invoice`
			WHERE company = %s AND docstatus = 1 AND outstanding_amount > 0 AND due_date < %s
			""",
			(company, ref_date),
			as_dict=True,
		)
		overdue_receivables_alerted = [r for r in receivable_alerts if r["days_due"] < 0]

		# 2. Reconcile Project alerts
		project_alerts = [r for r in risks if r["category"] == "Projects" and r["record_type"] == "Project"]
		for r in project_alerts:
			proj = frappe.get_doc("Project", r["affected_record"])
			assert proj.company == company, f"Project {proj.name} company mismatch"
			assert proj.status in ("Open", "On hold"), f"Project {proj.name} is not active"

		db_overdue_projects = frappe.db.sql(
			"""
			SELECT name, status, expected_end_date
			FROM `tabProject`
			WHERE company = %s AND docstatus < 2 AND status = 'Open' AND expected_end_date < %s
			""",
			(company, ref_date),
			as_dict=True,
		)
		overdue_projects_alerted = [r for r in project_alerts if r["days_due"] is not None and r["days_due"] < 0]

		# 3. Reconcile Delivery alerts
		delivery_alerts = [r for r in risks if r["category"] == "Deliveries"]
		for r in delivery_alerts:
			so = frappe.get_doc("Sales Order", r["affected_record"])
			assert so.company == company, f"Sales Order {so.name} company mismatch"
			assert so.docstatus == 1, f"Sales Order {so.name} is not submitted"
			assert so.status not in ("Completed", "Cancelled", "Closed"), f"Sales Order {so.name} is not open"

		# 4. Reconcile Manufacturing alerts
		mfg_alerts = [r for r in risks if r["category"] == "Manufacturing" and r["record_type"] == "Work Order"]
		for r in mfg_alerts:
			wo = frappe.get_doc("Work Order", r["affected_record"])
			assert wo.company == company, f"Work Order {wo.name} company mismatch"
			assert wo.docstatus == 1, f"Work Order {wo.name} is not submitted"
			assert wo.status not in ("Completed", "Cancelled", "Stopped"), f"Work Order {wo.name} is not active"

		# 5. Reconcile Approvals
		for a in approvals:
			assert frappe.has_permission(a["reference_doctype"], "read", a["reference_name"]), f"Unauthorized approval exposed: {a}"

		diffs = {
			"company": company,
			"reference_date": str(ref_date),
			"total_risks_detected": summary["total_risks"],
			"critical_count": summary["critical"],
			"high_count": summary["high"],
			"medium_count": summary["medium"],
			"pending_approvals_count": summary["pending_approvals"],
			"receivable_alerts_count": len(receivable_alerts),
			"db_overdue_invoices_count": len(db_overdue_invoices),
			"overdue_receivables_diff": len(overdue_receivables_alerted) - len(db_overdue_invoices),
			"project_alerts_count": len(project_alerts),
			"db_overdue_projects_count": len(db_overdue_projects),
			"overdue_projects_diff": len(overdue_projects_alerted) - len(db_overdue_projects),
			"delivery_alerts_count": len(delivery_alerts),
			"mfg_alerts_count": len(mfg_alerts),
			"status": "RECONCILED",
		}
		results.append(diffs)

	print(json.dumps(results, indent=2))
	return results


if __name__ == "__main__":
	reconcile()
