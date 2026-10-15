"""DASH-012 manufacturing overview, production output, inventory valuation, stock risk and shortage tests."""
from datetime import date, datetime, timedelta
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate, now_datetime, today

from sarathi_owner.api.manufacturing_inventory import (
	classify_work_order,
	get_inventory_valuation,
	get_manufacturing_inventory_summary,
	get_material_shortages,
	get_stock_risk_summary,
	get_target_completion_date,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class ManufacturingInventorySecurityTests(PermissionTests):
	def setUp(self):
		frappe.db.savepoint("dash012_security_case")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash012_security_case")
		for user in self.users.values():
			frappe.clear_cache(user=user)

	def test_capability_and_company_denial(self):
		"""Only users with owner capability can access manufacturing & inventory summary."""
		for user in ("manager", "operator", "supervisor", "unrelated", "finance_only"):
			self.user(user)
			with self.assertRaises(frappe.PermissionError):
				get_manufacturing_inventory_summary({"company": self.companies[0]})

		self.user("owner")
		# Mismatched/unauthorized company
		with self.assertRaises(frappe.PermissionError):
			get_manufacturing_inventory_summary({"company": self.companies[1]})

	def test_strict_filter_validations(self):
		"""Invalid filters, bad dates, and unauthorized parameters are strictly rejected."""
		self.user("owner")
		for extra in (
			{"from_date": "bad_date"},
			{"from_date": "2026-10-20", "to_date": "2026-10-10"},
			{"reference_at": "not-a-datetime"},
			{"review_days": 95},
			{"review_days": -1},
			{"review_days": True},
			{"mfg_status": "NonexistentStatus"},
			{"warehouse": "nonexistent_warehouse_123"},
			{"customer": "nonexistent_customer_123"},
			{"project": "nonexistent_project_123"},
			{"unsupported_param": "foo"},
		):
			with self.assertRaises(frappe.ValidationError, msg=str(extra)):
				get_manufacturing_inventory_summary({"company": self.companies[0], **extra})

	def test_read_errors_sanitization(self):
		"""Internal exceptions are sanitized without leaking database internals."""
		from sarathi_visibility.api.data_helpers import DashboardReadError
		self.user("owner")
		with patch("sarathi_owner.api.manufacturing_inventory.get_manufacturing_summary", side_effect=RuntimeError("internal db error")), patch.object(frappe, "log_error"):
			with self.assertRaises(DashboardReadError) as err:
				get_manufacturing_inventory_summary({"company": self.companies[0]})
			self.assertNotIn("internal db error", str(err.exception))


class ManufacturingInventoryUnitTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash012_mfg_class")
		cls.company = frappe.get_all("Company", pluck="name", limit=1)[0]
		cls.currency = frappe.get_cached_value("Company", cls.company, "default_currency") or "INR"

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash012_mfg_class")

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash012_mfg_case")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash012_mfg_case")

	def test_work_order_classification(self):
		"""Validate work order lifecycle and health classification."""
		ref = date(2026, 10, 14)

		# Draft
		self.assertEqual(classify_work_order({"docstatus": 0, "status": "Draft"}, ref), ("Draft", "Draft"))
		# Cancelled
		self.assertEqual(classify_work_order({"docstatus": 2, "status": "Cancelled"}, ref), ("Cancelled", "Cancelled"))
		# Stopped
		self.assertEqual(classify_work_order({"docstatus": 1, "status": "Stopped"}, ref), ("Stopped", "Stopped"))
		# Completed
		self.assertEqual(classify_work_order({"docstatus": 1, "status": "Completed"}, ref), ("Completed", "Completed"))

		# Active - Overdue (expected date before ref)
		wo_overdue = {"docstatus": 1, "status": "In Process", "planned_end_date": "2026-10-10"}
		self.assertEqual(classify_work_order(wo_overdue, ref, 7), ("Active", "Overdue"))

		# Active - Due soon (within 7 days)
		wo_due_soon = {"docstatus": 1, "status": "In Process", "expected_delivery_date": "2026-10-18"}
		self.assertEqual(classify_work_order(wo_due_soon, ref, 7), ("Active", "Due soon"))

		# Active - On track (> 7 days)
		wo_on_track = {"docstatus": 1, "status": "Not Started", "planned_end_date": "2026-10-30"}
		self.assertEqual(classify_work_order(wo_on_track, ref, 7), ("Active", "On track"))

		# Active - Unknown (no completion date)
		wo_unknown = {"docstatus": 1, "status": "Not Started", "planned_end_date": None, "expected_delivery_date": None}
		self.assertEqual(classify_work_order(wo_unknown, ref, 7), ("Active", "Unknown"))

	def test_target_completion_date_fallback(self):
		"""Verify fallback between planned_end_date and expected_delivery_date."""
		# Planned end date takes precedence
		row1 = {"planned_end_date": "2026-11-01", "expected_delivery_date": "2026-11-15"}
		self.assertEqual(get_target_completion_date(row1), date(2026, 11, 1))

		# Expected delivery date fallback
		row2 = {"planned_end_date": None, "expected_delivery_date": "2026-11-15"}
		self.assertEqual(get_target_completion_date(row2), date(2026, 11, 15))

		# Neither
		row3 = {"planned_end_date": None, "expected_delivery_date": None}
		self.assertIsNone(get_target_completion_date(row3))

	def test_uom_grouping_never_mixes_units(self):
		"""Verify production output aggregates cleanly per UOM."""
		summary = get_manufacturing_inventory_summary({"company": self.company})
		self.assertTrue(summary["manufacturing"]["available"])
		uom_summaries = summary["manufacturing"]["production_output"]["uom_summaries"]

		# Ensure all UOM entries have positive/zero planned and produced and documented variance
		for uom in uom_summaries:
			self.assertIn("stock_uom", uom)
			self.assertIn("planned_qty", uom)
			self.assertIn("produced_qty", uom)
			self.assertIn("variance", uom)
			self.assertIn("achievement_pct", uom)
			# Variance = produced - planned
			self.assertAlmostEqual(uom["variance"], uom["produced_qty"] - uom["planned_qty"], places=2)
			if uom["planned_qty"] > 0:
				expected_pct = round(uom["produced_qty"] / uom["planned_qty"] * 100, 1)
				self.assertEqual(uom["achievement_pct"], expected_pct)

	def test_inventory_valuation_uses_erpnext_engine(self):
		"""Verify inventory valuation uses native ERPNext Bin stock value, never a naive price formula."""
		summary = get_manufacturing_inventory_summary({"company": self.company})
		inv = summary["inventory"]
		self.assertTrue(inv["available"])
		self.assertGreaterEqual(inv["valuation"], 0.0)
		self.assertEqual(inv["currency"], self.currency)
		self.assertIn("Perpetual", inv["method"])

		# Compare with direct SQL calculation across company leaf warehouses
		direct_val = frappe.db.sql(
			"""
			SELECT IFNULL(SUM(b.stock_value), 0.0) as total_val
			FROM `tabBin` b
			INNER JOIN `tabWarehouse` w ON b.warehouse = w.name
			WHERE w.company = %s AND w.is_group = 0
			""",
			(self.company,),
			as_dict=True,
		)[0].total_val

		self.assertAlmostEqual(inv["valuation"], round(direct_val, 2), places=2)

	def test_stock_risk_distinguishes_actual_reserved_projected(self):
		"""Verify stock risk distinguishes physical, reserved, available, and projected stock."""
		summary = get_manufacturing_inventory_summary({"company": self.company})
		risk = summary["stock_risk"]
		self.assertTrue(risk["available"])
		self.assertIn("counts", risk)
		self.assertIn("low_stock_items", risk["counts"])
		self.assertIn("negative_projected_items", risk["counts"])
		self.assertIn("zero_stock_with_demand", risk["counts"])
		self.assertIn("unconfigured_items", risk["counts"])

		for row in risk["rows"]:
			self.assertIn("actual_qty", row)
			self.assertIn("reserved_qty", row)
			self.assertIn("available_qty", row)
			self.assertIn("projected_qty", row)
			self.assertIn("risk_status", row)
			# available = max(0, actual - reserved)
			expected_avail = round(max(0.0, row["actual_qty"] - row["reserved_qty"]), 2)
			self.assertEqual(row["available_qty"], expected_avail)

	def test_material_shortage_calculation(self):
		"""Verify material shortage calculation: remaining required vs available stock."""
		summary = get_manufacturing_inventory_summary({"company": self.company, "shortage_only": False})
		shortages = summary["shortages"]
		self.assertTrue(shortages["available"])

		for line in shortages["rows"]:
			self.assertIn("work_order", line)
			self.assertIn("item_code", line)
			self.assertIn("source_warehouse", line)
			self.assertIn("required_qty", line)
			self.assertIn("transferred_qty", line)
			self.assertIn("remaining_required", line)
			self.assertIn("available_stock", line)
			self.assertIn("shortage_qty", line)

			expected_shortage = round(max(0.0, line["remaining_required"] - line["available_stock"]), 2)
			self.assertEqual(line["shortage_qty"], expected_shortage)
			self.assertEqual(line["has_shortage"], expected_shortage > 0.0)


def run():
	suite = unittest.TestSuite()
	suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ManufacturingInventorySecurityTests))
	suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ManufacturingInventoryUnitTests))
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	frappe.db.rollback()
	if not result.wasSuccessful():
		raise AssertionError("DASH-012 manufacturing & inventory tests failed.")
	return {"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "passed": True}
