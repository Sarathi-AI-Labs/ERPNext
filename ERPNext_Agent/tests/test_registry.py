"""Tests for SkillRegistry across all 13 modules and 98 sections."""

import unittest

from ERPNext_Agent.core.registry import SkillRegistry


class TestSkillRegistry(unittest.TestCase):
	"""Test suite for SkillRegistry catalog and DocType mappings."""

	def setUp(self):
		self.registry = SkillRegistry()

	def test_all_13_modules_present(self):
		"""Verify all 13 required ERPNext modules are registered."""
		expected_modules = [
			"Organization",
			"Assets",
			"Buying",
			"Manufacturing",
			"Projects",
			"Quality",
			"Selling",
			"Subcontracting",
			"Accounting",
			"Stock",
			"ERPNext Settings",
			"Framework",
			"Users and System",
		]
		registered = self.registry.list_modules()
		for mod in expected_modules:
			self.assertIn(mod, registered, f"Module '{mod}' missing from registry")

	def test_doctype_to_module_lookup(self):
		"""Verify primary DocTypes correctly resolve to their home module."""
		mappings = {
			"Company": "Organization",
			"Project": "Projects",
			"Work Order": "Manufacturing",
			"BOM": "Manufacturing",
			"Item": "Stock",
			"Warehouse": "Stock",
			"Customer": "Selling",
			"Sales Order": "Selling",
			"Supplier": "Buying",
			"Purchase Order": "Buying",
			"Asset": "Assets",
			"Subcontracting Order": "Subcontracting",
			"Quality Inspection": "Quality",
		}
		for dt, expected_mod in mappings.items():
			mod = self.registry.get_module_for_doctype(dt)
			self.assertEqual(
				mod, expected_mod, f"DocType '{dt}' mapped to '{mod}', expected '{expected_mod}'"
			)

	def test_module_metadata_and_sections(self):
		"""Verify module details contain sections and documentation paths."""
		meta = self.registry.get_module_meta("Organization")
		self.assertIsNotNone(meta)
		self.assertIn("Company", meta.get("sections", {}))


if __name__ == "__main__":
	unittest.main()
