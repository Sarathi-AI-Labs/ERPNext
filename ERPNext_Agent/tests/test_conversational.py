"""Unit tests for ConversationalAgent and interactive slot filling."""

import unittest

from ERPNext_Agent.core.conversational_agent import ConversationalAgent


class TestConversationalAgent(unittest.TestCase):
	def setUp(self):
		self.conv = ConversationalAgent()

	def test_turn1_missing_slots_questionnaire_project(self):
		res = self.conv.handle_message("I want to create a project", session_id="test_proj")
		self.assertEqual(res["status"], "COLLECTING_SLOTS")
		self.assertEqual(res["target_doctype"], "Project")
		self.assertIn("project_name", res["missing"])
		self.assertIn("Project Name", res["message"])

	def test_turn1_company_slot_intake(self):
		res = self.conv.handle_message("I want to create a new company", session_id="test_co")
		self.assertEqual(res["status"], "COLLECTING_SLOTS")
		self.assertEqual(res["target_doctype"], "Company")
		self.assertIn("company_name", res["missing"])
		self.assertIn("abbr", res["missing"])
		self.assertIn("Company Name", res["message"])
		self.assertIn("Company Abbreviation", res["message"])

	def test_company_confirmation_flow(self):
		sid = "test_co_flow"
		self.conv.handle_message("I want to create a new company", session_id=sid)
		res_conf = self.conv.handle_message("Unit Test Alpha, UTA", session_id=sid)
		self.assertEqual(res_conf["status"], "AWAITING_CONFIRMATION")
		self.assertEqual(res_conf["doctype"], "Company")
		self.assertIn("Unit Test Alpha", res_conf["message"])
		self.assertIn("UTA", res_conf["message"])
		self.assertIn("Organization Skill loaded", res_conf["message"])

		# Cancel flow
		res_cancel = self.conv.handle_message("cancel", session_id=sid)
		self.assertEqual(res_cancel["status"], "IDLE")

	def test_customer_intake_and_confirmation(self):
		sid = "test_cust"
		res = self.conv.handle_message("create customer Zenith Automation", session_id=sid)
		self.assertEqual(res["status"], "AWAITING_CONFIRMATION")
		self.assertEqual(res["doctype"], "Customer")
		self.assertEqual(res["pending_values"]["customer_name"], "Zenith Automation")
		self.assertEqual(res["pending_values"]["customer_group"], "All Customer Groups")

	def test_item_intake(self):
		sid = "test_item"
		res = self.conv.handle_message("create item ITEM-TEST-99 named Industrial Sensor", session_id=sid)
		self.assertEqual(res["status"], "AWAITING_CONFIRMATION")
		self.assertEqual(res["doctype"], "Item")
		self.assertEqual(res["pending_values"]["item_code"], "ITEM-TEST-99")
		self.assertEqual(res["pending_values"]["item_name"], "Industrial Sensor")
		self.assertEqual(res["pending_values"]["stock_uom"], "Nos")

	def test_live_changes_query(self):
		res = self.conv.handle_message("show live changes", session_id="test_live")
		self.assertEqual(res["status"], "LIVE_CHANGES")
		self.assertIn("Live System Activity", res["message"])
		self.assertIsInstance(res.get("changes"), list)

	def test_stock_query(self):
		res = self.conv.handle_message("check stock in Stores", session_id="test_stock")
		self.assertEqual(res["status"], "STOCK_REPORT")
		self.assertIn("Stock", res["message"])

	def test_orchestrated_pipeline_setup(self):
		sid = "test_compound"
		res = self.conv.handle_message(
			"Create company Test Orbit with abbr TO and create a project called Satellite Alpha for that company",
			session_id=sid,
		)
		self.assertEqual(res["status"], "AWAITING_CONFIRMATION")
		self.assertTrue(res.get("is_orchestrated"))
		self.assertIn("Multi-Step Workflow", res["message"])
		self.assertEqual(len(res["pipeline_steps"]), 2)
		# Verify topological order: Company first, Project second
		self.assertEqual(res["pipeline_steps"][0]["doctype"], "Company")
		self.assertEqual(res["pipeline_steps"][1]["doctype"], "Project")
		self.assertEqual(res["pipeline_steps"][0]["values"]["company_name"], "Test Orbit")
		self.assertEqual(res["pipeline_steps"][0]["values"]["abbr"], "TO")
		self.assertEqual(res["pipeline_steps"][1]["values"]["project_name"], "Satellite Alpha")
		self.assertEqual(res["pipeline_steps"][1]["values"]["company"], "Test Orbit")


if __name__ == "__main__":
	unittest.main()
