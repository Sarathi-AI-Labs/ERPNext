"""Unit tests for DependencyResolver."""

import unittest
from unittest.mock import MagicMock

from ERPNext_Agent.core.resolver import DependencyResolver


class TestDependencyResolver(unittest.TestCase):
	def setUp(self):
		self.mock_client = MagicMock()
		self.resolver = DependencyResolver(self.mock_client)

	def test_prerequisites_lookup(self):
		prereqs = self.resolver.get_prerequisites("Work Order")
		self.assertIn("Item", prereqs)
		self.assertIn("BOM", prereqs)
		self.assertIn("Company", prereqs)
		self.assertIn("Warehouse", prereqs)

	def test_topological_plan_ordering(self):
		order = self.resolver.plan_creation_order(["Work Order", "BOM", "Item", "Company"])
		# Company and Item must come before BOM, BOM before Work Order
		self.assertLess(order.index("Company"), order.index("Work Order"))
		self.assertLess(order.index("Item"), order.index("BOM"))
		self.assertLess(order.index("BOM"), order.index("Work Order"))


if __name__ == "__main__":
	unittest.main()
