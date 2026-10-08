"""Tests for controlled ToolRegistry, Pydantic schemas, and safety levels."""

import unittest

from ERPNext_Agent.tools.client import FrappeClient
from ERPNext_Agent.tools.tool_registry import ToolRegistry


class TestToolRegistry(unittest.TestCase):
	"""Test suite for controlled Frappe Tool Registry."""

	def setUp(self):
		self.client = FrappeClient()
		self.tool_reg = ToolRegistry(self.client)

	def test_registered_tools_count(self):
		"""Verify all 15 required enterprise tools are registered."""
		tools = self.tool_reg.list_tools()
		tool_names = [t.name for t in tools]
		required = [
			"get_doctype_meta",
			"search_documents",
			"get_document",
			"create_document",
			"update_document",
			"delete_document",
			"submit_document",
			"cancel_document",
			"amend_document",
			"check_permission",
			"validate_document",
			"run_report",
			"get_link_options",
			"check_duplicate",
			"resolve_dependency",
		]
		for req in required:
			self.assertIn(req, tool_names, f"Tool '{req}' missing from ToolRegistry")

	def test_safety_levels(self):
		"""Verify high risk and mutation tools require confirmation."""
		delete_meta = self.tool_reg.get_tool_meta("delete_document")
		self.assertIsNotNone(delete_meta)
		self.assertEqual(delete_meta.safety_level, "HIGH_RISK")
		self.assertTrue(delete_meta.requires_confirmation)

		create_meta = self.tool_reg.get_tool_meta("create_document")
		self.assertIsNotNone(create_meta)
		self.assertEqual(create_meta.safety_level, "CONFIRMATION_REQUIRED")
		self.assertTrue(create_meta.requires_confirmation)

		meta_meta = self.tool_reg.get_tool_meta("get_doctype_meta")
		self.assertIsNotNone(meta_meta)
		self.assertEqual(meta_meta.safety_level, "SAFE")
		self.assertFalse(meta_meta.requires_confirmation)

	def test_permission_check_tool(self):
		"""Verify check_permission tool functions correctly for authenticated user."""
		res = self.tool_reg.execute(
			"check_permission", user="Administrator", doctype="Company", perm_type="read"
		)
		self.assertTrue(res.get("success"))
		self.assertTrue(res.get("has_permission"))


if __name__ == "__main__":
	unittest.main()
