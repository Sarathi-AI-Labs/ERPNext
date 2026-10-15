"""DASH-008 native-permission tests; reuse rollback fixtures and security regressions."""
import unittest
from sarathi_visibility.tests.test_permissions import PermissionTests
import frappe
from sarathi_owner.api.homepage import get_homepage, options


class HomepageTests(PermissionTests):
	def test_homepage_requires_unambiguous_company(self):
		with self.assertRaises(frappe.ValidationError):
			get_homepage()
		self.user("owner")
		result = get_homepage()
		self.assertEqual(result["applied_filters"]["company"], self.companies[0])

	def test_homepage_owner_gate_and_forged_company(self):
		for user in ("manager", "operator", "supervisor", "unrelated"):
			self.user(user)
			with self.assertRaises(frappe.PermissionError):
				get_homepage({"company": self.companies[0]})
			with self.assertRaises(frappe.PermissionError):
				options("companies")
		self.user("owner")
		with self.assertRaises(frappe.PermissionError):
			get_homepage({"company": self.companies[1]})

	def test_customer_project_company_scopes_are_consistent(self):
		self.user("owner")
		result = get_homepage({"company": self.companies[0], "customer": self.customers[0], "project": self.projects[0]})
		self.assertEqual([p["name"] for p in result["projects"]["rows"]], [self.projects[0]])
		self.assertTrue(all(wo["project"] == self.projects[0] for wo in result["work_orders"].get("rows", [])))
		with self.assertRaises(frappe.PermissionError):
			get_homepage({"company": self.companies[0], "project": self.projects[1]})

	def test_customer_only_manufacturing_does_not_claim_unsupported_filter(self):
		result = get_homepage({"company": self.companies[0], "customer": self.customers[0]})
		self.assertFalse(result["work_orders"]["available"])
		self.assertNotIn("rows", result["work_orders"])

	def test_date_validation_and_unsupported_filters(self):
		for extra in [{"from_date": "bad"}, {"from_date": "2026-05-01", "to_date": "2026-04-01"}, {"date_range": "invented"}, {"warehouse": "x"}]:
			with self.assertRaises(frappe.ValidationError):
				get_homepage({"company": self.companies[0], **extra})

	def test_previews_are_bounded_and_do_not_expose_unvalidated_metrics(self):
		result = get_homepage({"company": self.companies[0]})
		self.assertLessEqual(len(result["projects"]["rows"]), 6)
		self.assertLessEqual(len(result["work_orders"].get("rows", [])), 6)
		self.assertNotIn("profit", result)
		self.assertNotIn("revenue", result)
		self.assertIn("accounting reconciliation", result["availability"]["finance"])

	def test_options_are_owner_scoped_searchable_and_bounded(self):
		self.user("owner")
		result = options("projects", company=self.companies[0], customer=self.customers[0], search=self.token)
		self.assertEqual([row["value"] for row in result["options"]], [self.projects[0]])
		with self.assertRaises(frappe.ValidationError):
			options("User")
		with self.assertRaises(frappe.ValidationError):
			options("projects")

	def test_mismatched_readable_customer_project_is_denied(self):
		with self.assertRaises(frappe.PermissionError):
			get_homepage({"company": self.companies[0], "customer": self.customers[1], "project": self.projects[0]})


def run():
	result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HomepageTests))
	frappe.db.rollback()
	if not result.wasSuccessful():
		raise AssertionError("Owner homepage tests failed")
	return {"tests": result.testsRun, "skipped": len(result.skipped), "passed": True}
