"""Tests for SarathiAgentGraph 14-Node State Machine and Multi-Turn Lifecycle."""

import unittest

from ERPNext_Agent.core.state import AgentState
from ERPNext_Agent.core.workflow import SarathiAgentGraph
from ERPNext_Agent.tools.client import FrappeClient


class TestSarathiAgentGraph(unittest.TestCase):
	"""Test suite for LangGraph orchestration pipeline."""

	def setUp(self):
		self.client = FrappeClient()
		self.graph = SarathiAgentGraph(self.client)

	def test_turn1_missing_parameters_discovery(self):
		"""Verify Turn 1 asks for missing mandatory slots for Company."""
		s = AgentState(
			session_id="unit_graph_1", user="Administrator", original_request="I want to create a new company"
		)
		r = self.graph.invoke(s)
		self.assertEqual(r.status, "COLLECTING_SLOTS")
		self.assertEqual(r.selected_doctypes, ["Company"])
		self.assertEqual(r.selected_skills, ["Organization"])
		missing_fields = [m["field"] for m in r.missing_parameters]
		self.assertIn("company_name", missing_fields)
		self.assertIn("abbr", missing_fields)

	def test_turn2_slot_intake_and_confirmation_gate(self):
		"""Verify Turn 2 takes slots, verifies uniqueness, and pauses at confirmation gate."""
		s = AgentState(
			session_id="unit_graph_2", user="Administrator", original_request="I want to create a new company"
		)
		r1 = self.graph.invoke(s)

		# Feed slot answers
		r1.original_request = "Unit Test Dynamics, UTD"
		r2 = self.graph.invoke(r1)

		self.assertEqual(r2.status, "AWAITING_CONFIRMATION")
		self.assertEqual(r2.confirmation_status, "AWAITING_CONFIRMATION")
		self.assertEqual(r2.parameters.get("company_name"), "Unit Test Dynamics")
		self.assertEqual(r2.parameters.get("abbr"), "UTD")
		self.assertTrue(r2.confirmation_required)
		self.assertIsNotNone(r2.final_response.get("confirmation_data"))

	def test_key_value_slot_intake_clean_extraction(self):
		"""Verify key: value intake cleanly extracts values without prefixes or corruption."""
		s = AgentState(
			session_id="unit_graph_kv",
			user="Administrator",
			original_request="I want to create a new company",
		)
		r1 = self.graph.invoke(s)
		self.assertEqual(r1.status, "COLLECTING_SLOTS")

		# Submit key-value formatted input
		r1.original_request = "company_name: Meera Manufacturing, abbr: MM"
		r2 = self.graph.invoke(r1)

		self.assertEqual(r2.status, "AWAITING_CONFIRMATION")
		self.assertEqual(r2.parameters.get("company_name"), "Meera Manufacturing")
		self.assertEqual(r2.parameters.get("abbr"), "MM")

		# Verify confirmation card is clean and does NOT contain internal ERPNext flags
		conf_fields = r2.final_response.get("confirmation_data", {}).get("fields", {})
		self.assertNotIn("Is Group", conf_fields)
		self.assertNotIn("Allow Account Creation Against Child Company", conf_fields)
		self.assertNotIn("Enable Perpetual Inventory", conf_fields)
		self.assertNotIn("Valuation Method", conf_fields)
		self.assertIn("Company Name", conf_fields)
		self.assertEqual(conf_fields.get("Company Name"), "Meera Manufacturing")
		self.assertEqual(conf_fields.get("Abbr"), "MM")

	def test_auto_generate_abbr_gmplc(self):
		"""Verify automatic abbreviation generation using initials of each word (GMplc)."""
		s = AgentState(
			session_id="unit_graph_abbr",
			user="Administrator",
			original_request="I want to create a new company",
		)
		r1 = self.graph.invoke(s)
		self.assertEqual(r1.status, "COLLECTING_SLOTS")

		# User provides company name without abbreviation
		r1.original_request = "Gaurav Manufacture private limited company"
		r2 = self.graph.invoke(r1)

		self.assertEqual(r2.status, "AWAITING_CONFIRMATION")
		self.assertEqual(r2.parameters.get("company_name"), "Gaurav Manufacture private limited company")
		self.assertEqual(r2.parameters.get("abbr"), "GMplc")

	def test_company_intake_provides_currency_and_country(self):
		"""Verify Company slot intake contains currency, country, and letterhead options."""
		s = AgentState(
			session_id="unit_graph_co_slots",
			user="Administrator",
			original_request="I want to create a new company",
		)
		r = self.graph.invoke(s)
		self.assertEqual(r.status, "COLLECTING_SLOTS")
		details = r.final_response.get("missing_details", [])
		field_names = [d["field"] for d in details]
		self.assertIn("company_name", field_names)
		self.assertIn("abbr", field_names)
		self.assertIn("default_currency", field_names)
		self.assertIn("country", field_names)
		self.assertIn("default_letter_head", field_names)

	def test_reset_command(self):
		"""Verify user can reset conversational context with cancel/abort."""
		s = AgentState(
			session_id="unit_graph_3",
			user="Administrator",
			status="COLLECTING_SLOTS",
			original_request="cancel",
		)
		r = self.graph.invoke(s)
		self.assertEqual(r.status, "IDLE")
		self.assertEqual(r.parameters, {})

	def test_multi_module_slot_intake(self):
		"""Verify slot intake across Selling (Customer), Stock (Item), Projects (Project), Buying (Supplier)."""
		test_cases = [
			(
				"I want to create a new customer",
				"Customer",
				["customer_name", "customer_type", "customer_group", "territory"],
			),
			(
				"I want to create an item",
				"Item",
				["item_code", "item_name", "item_group", "stock_uom", "is_stock_item"],
			),
			("I want to create a project", "Project", ["project_name", "company", "status"]),
			(
				"I want to create a supplier",
				"Supplier",
				["supplier_name", "supplier_type", "supplier_group", "country"],
			),
		]
		for req, expected_dt, expected_fields in test_cases:
			s = AgentState(session_id=f"test_mod_{expected_dt}", user="Administrator", original_request=req)
			r = self.graph.invoke(s)
			self.assertEqual(r.status, "COLLECTING_SLOTS", f"Failed for {expected_dt}")
			details = r.final_response.get("missing_details", [])
			f_names = [d["field"] for d in details]
			for ef in expected_fields:
				self.assertIn(ef, f_names, f"Expected {ef} in slots for {expected_dt}")

	def test_clean_pending_values_filters_system_flags(self):
		"""Verify internal Frappe schema flags are completely excluded from user presentation."""
		from ERPNext_Agent.core.slot_registry import get_clean_pending_values

		dirty = {
			"company_name": "Gaurav Manufacture private limited company",
			"abbr": "GMplc",
			"default_currency": "INR",
			"country": "India",
			"is_group": 0,
			"enable_perpetual_inventory": 1,
			"reconciliation_takes_effect_on": "Oldest Of Invoice Or Advance",
			"allow_account_creation_against_child_company": 0,
			"auto_exchange_rate_revaluation": 0,
			"submit_err_jv": 0,
			"valuation_method": "FIFO",
		}
		clean = get_clean_pending_values(dirty)
		self.assertIn("company_name", clean)
		self.assertIn("abbr", clean)
		self.assertIn("default_currency", clean)
		self.assertIn("country", clean)
		self.assertNotIn("is_group", clean)
		self.assertNotIn("enable_perpetual_inventory", clean)
		self.assertNotIn("reconciliation_takes_effect_on", clean)
		self.assertNotIn("allow_account_creation_against_child_company", clean)
		self.assertNotIn("valuation_method", clean)


if __name__ == "__main__":
	unittest.main()
