"""Unit tests for SkillRouter and Intent Classifier."""

import unittest

from ERPNext_Agent.core.router import SkillRouter


class TestSkillRouter(unittest.TestCase):
	def setUp(self):
		self.router = SkillRouter()

	def test_route_organization(self):
		res = self.router.route("What is the default currency of company SarathiAILabs?")
		self.assertEqual(res["primary_module"], "Organization")
		self.assertIn("Company", res["detected_doctypes"])
		self.assertEqual(res["action"], "QUERY")

	def test_route_stock_mutation(self):
		res = self.router.route("Create a Material Receipt stock entry for 50 units of ITEM-001 in Stores")
		self.assertEqual(res["primary_module"], "Stock")
		self.assertTrue(res["is_mutation"])
		self.assertEqual(res["action"], "CREATE")

	def test_route_manufacturing(self):
		res = self.router.route("Submit Work Order for 20 units using BOM-001")
		self.assertEqual(res["primary_module"], "Manufacturing")
		self.assertTrue(res["is_workflow"])
		self.assertEqual(res["action"], "SUBMIT")

	def test_route_buying(self):
		res = self.router.route("Create a Purchase Order to supplier Acme Corp")
		self.assertEqual(res["primary_module"], "Buying")
		self.assertIn("Purchase Order", res["detected_doctypes"])

	def test_route_selling(self):
		res = self.router.route("List all open Sales Orders for Customer Global Motors")
		self.assertEqual(res["primary_module"], "Selling")
		self.assertIn("Sales Order", res["detected_doctypes"])

	def test_route_accounting(self):
		res = self.router.route("Make a new Journal Entry debiting Cash and crediting Bank")
		self.assertEqual(res["primary_module"], "Accounting")
		self.assertIn("Journal Entry", res["detected_doctypes"])

	def test_route_projects(self):
		res = self.router.route("Show all tasks in Project Factory Automation")
		self.assertEqual(res["primary_module"], "Projects")

	def test_route_assets(self):
		res = self.router.route("Check status of Asset CNC Lathe Machine")
		self.assertEqual(res["primary_module"], "Assets")

	def test_route_quality(self):
		res = self.router.route("Submit Quality Inspection for incoming batch")
		self.assertEqual(res["primary_module"], "Quality")


if __name__ == "__main__":
	unittest.main()
