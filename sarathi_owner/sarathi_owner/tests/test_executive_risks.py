"""DASH-013: Executive risks, business exceptions, pending approvals, and drill-downs tests."""
from datetime import date, datetime, timedelta
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate, now_datetime

from sarathi_owner.api.executive_risks import (
	FEATURE_KEYS,
	get_executive_risks_and_approvals,
	get_payment_risks,
	get_project_delivery_risks,
	get_production_shortage_risks,
	get_pending_approvals,
	validate_risk_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class ExecutiveRisksSecurityTests(PermissionTests):
	def setUp(self):
		frappe.db.savepoint("dash013_security_case")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash013_security_case")
		for user in self.users.values():
			frappe.clear_cache(user=user)

	def test_capability_and_company_denial(self):
		"""Only users with owner capability can access executive risks."""
		for user in ("manager", "operator", "supervisor", "unrelated", "finance_only"):
			self.user(user)
			with self.assertRaises(frappe.PermissionError):
				get_executive_risks_and_approvals({"company": self.companies[0]})

		self.user("owner")
		# Mismatched/unauthorized company
		with self.assertRaises(frappe.PermissionError):
			get_executive_risks_and_approvals({"company": self.companies[1]})

	def test_strict_filter_validations(self):
		"""Invalid filters, bad dates, and unauthorized parameters are strictly rejected."""
		self.user("owner")
		for extra in (
			{"from_date": "invalid-date"},
			{"from_date": "2026-10-25", "to_date": "2026-10-10"},
			{"reference_at": "not-a-datetime"},
			{"review_days": 100},
			{"review_days": -5},
			{"review_days": "one_week"},
			{"risk_category": "InventedCategory"},
			{"risk_severity": "InventedSeverity"},
			{"risk_start": -1},
			{"risk_page_length": 0},
			{"risk_page_length": 101},
			{"approval_start": -1},
			{"approval_page_length": 0},
			{"approval_page_length": 101},
			{"customer": "nonexistent_customer_xyz"},
			{"project": "nonexistent_project_xyz"},
			{"unauthorized_extra_param": "foo"},
		):
			with self.assertRaises(frappe.ValidationError, msg=str(extra)):
				get_executive_risks_and_approvals({"company": self.companies[0], **extra})

	def test_read_errors_sanitization(self):
		"""Internal exceptions are sanitized without leaking database internals."""
		from sarathi_visibility.api.data_helpers import DashboardReadError
		self.user("owner")
		with patch("sarathi_owner.api.executive_risks.get_payment_risks", side_effect=RuntimeError("internal db crash")), patch.object(frappe, "log_error"):
			with self.assertRaises(DashboardReadError) as err:
				get_executive_risks_and_approvals({"company": self.companies[0]})
			self.assertNotIn("internal db crash", str(err.exception))


class ExecutiveRisksUnitTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash013_unit_class")
		cls.company = frappe.get_all("Company", pluck="name", limit=1)[0]
		cls.currency = frappe.get_cached_value("Company", cls.company, "default_currency") or "INR"

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash013_unit_class")

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash013_unit_case")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash013_unit_case")

	def test_filter_validation_defaults(self):
		"""Verify filter defaults and normalization."""
		validated, ref_dt = validate_risk_filters({"company": self.company})
		self.assertEqual(validated["company"], self.company)
		self.assertEqual(validated["review_days"], 7)
		self.assertEqual(validated["risk_category"], "")
		self.assertEqual(validated["risk_severity"], "")
		self.assertEqual(validated["risk_start"], 0)
		self.assertEqual(validated["risk_page_length"], 25)
		self.assertEqual(validated["approval_start"], 0)
		self.assertEqual(validated["approval_page_length"], 25)
		self.assertIsInstance(ref_dt, datetime)

	def test_payment_risks_overdue_and_settled(self):
		"""Verify payment risks trigger on outstanding invoices and never on settled invoices."""
		ref_dt = datetime(2026, 10, 14, 12, 0, 0)
		values = {
			"company": self.company,
			"review_days": 7,
			"risk_category": "",
			"risk_severity": "",
		}
		risks = get_payment_risks(values, ref_dt)
		for r in risks:
			self.assertEqual(r["category"], "Receivables")
			self.assertEqual(r["entity_type"], "Sales Invoice")
			self.assertIsNotNone(r["amount"])
			self.assertGreater(r["amount"], 0)
			# Fully settled invoices must NEVER appear
			doc = frappe.get_doc("Sales Invoice", r["entity_name"])
			self.assertEqual(doc.docstatus, 1)
			self.assertGreater(doc.outstanding_amount, 0)
			# Drill-down must be valid route array
			self.assertEqual(r["drilldown"]["route"], ["Form", "Sales Invoice", r["entity_name"]])

	def test_project_risks_active_and_completed(self):
		"""Verify project risks trigger for active overdue/approaching projects and not completed ones."""
		ref_dt = datetime(2026, 10, 14, 12, 0, 0)
		values = {
			"company": self.company,
			"review_days": 14,
			"risk_category": "",
			"risk_severity": "",
		}
		risks = get_project_delivery_risks(values, ref_dt)
		for r in risks:
			if r["entity_type"] == "Project":
				proj = frappe.get_doc("Project", r["entity_name"])
				# Completed or Cancelled projects must never be flagged as overdue
				if proj.status in ("Completed", "Cancelled"):
					self.fail(f"Project {proj.name} with status {proj.status} should not generate an overdue alert.")
				self.assertIn(r["severity"], ("Critical", "High", "Medium"))
				self.assertEqual(r["drilldown"]["route"], ["Form", "Project", r["entity_name"]])

	def test_production_and_shortage_risks(self):
		"""Verify production alerts only trigger for active Work Orders and material shortages."""
		ref_dt = datetime(2026, 10, 14, 12, 0, 0)
		values = {
			"company": self.company,
			"review_days": 14,
			"risk_category": "",
			"risk_severity": "",
		}
		risks = get_production_shortage_risks(values, ref_dt)
		for r in risks:
			self.assertEqual(r["category"], "Manufacturing")
			if r["entity_type"] == "Work Order":
				wo = frappe.get_doc("Work Order", r["entity_name"])
				self.assertEqual(wo.docstatus, 1)
				self.assertNotIn(wo.status, ("Completed", "Cancelled", "Stopped"))
				self.assertEqual(r["drilldown"]["route"], ["Form", "Work Order", r["entity_name"]])

	def test_approval_visibility_and_scoping(self):
		"""Verify pending approvals are scoped to current user or permitted role."""
		values = {"company": self.company}
		approvals = get_pending_approvals(values)
		user = frappe.session.user
		user_roles = set(frappe.get_roles(user))

		for a in approvals:
			self.assertIn(a["source_type"], ("Workflow Action", "ToDo Assignment"))
			# If assigned directly
			if a["assigned_to"]:
				self.assertEqual(a["assigned_to"], user)
			# Document must exist and be readable
			self.assertTrue(frappe.has_permission(a["doctype"], "read", a["docname"], user=user))
			self.assertEqual(a["drilldown"]["route"], ["Form", a["doctype"], a["docname"]])

	def test_deduplication_and_sorting(self):
		"""Verify alerts are deduplicated and sorted by severity (Critical > High > Medium > Informational)."""
		payload = get_executive_risks_and_approvals({
			"company": self.company,
			"review_days": 14,
		})
		self.assertTrue(payload["risks"]["available"])
		self.assertTrue(payload["approvals"]["available"])

		rows = payload["risks"]["rows"]
		# Check deduplication
		seen_keys = set()
		for r in rows:
			key = (r["category"], r["entity_type"], r["entity_name"], r["title"])
			self.assertNotIn(key, seen_keys, f"Duplicate alert found: {key}")
			seen_keys.add(key)

		# Check severity ordering
		order = {"Critical": 0, "High": 1, "Medium": 2, "Informational": 3}
		for i in range(len(rows) - 1):
			curr_sev = order.get(rows[i]["severity"], 99)
			next_sev = order.get(rows[i + 1]["severity"], 99)
			self.assertLessEqual(curr_sev, next_sev, f"Severity ordering violated: {rows[i]['severity']} before {rows[i + 1]['severity']}")

	def test_category_and_severity_filtering(self):
		"""Verify risk_category and risk_severity filters isolate the correct records."""
		# Filter by Receivables
		rec_payload = get_executive_risks_and_approvals({
			"company": self.company,
			"risk_category": "Receivables",
			"review_days": 30,
		})
		for r in rec_payload["risks"]["rows"]:
			self.assertEqual(r["category"], "Receivables")

		# Filter by High severity
		high_payload = get_executive_risks_and_approvals({
			"company": self.company,
			"risk_severity": "High",
			"review_days": 30,
		})
		for r in high_payload["risks"]["rows"]:
			self.assertEqual(r["severity"], "High")

	def test_homepage_integration(self):
		"""Verify homepage endpoint returns executive_risks alongside all dashboard sections."""
		from sarathi_owner.api.homepage import get_homepage
		res = get_homepage({"company": self.company})
		self.assertIn("executive_risks", res)
		self.assertTrue(res["executive_risks"]["available"])
		data = res["executive_risks"]["data"]
		self.assertIn("summary", data)
		self.assertIn("risks", data)
		self.assertIn("approvals", data)
		self.assertEqual(data["currency"], self.currency)
