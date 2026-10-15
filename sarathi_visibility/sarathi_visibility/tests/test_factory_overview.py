"""DASH-015: Unit tests for Factory Overview KPIs and Filters."""
from datetime import date, datetime, timedelta
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.factory_overview import (
	get_factory_overview,
	get_target_completion_date,
	validate_factory_filters,
)


class TestFactoryOverview(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.company = "SarathiAILabs"

	def test_get_target_completion_date_fallback(self):
		"""Ensures target date falls back to expected_delivery_date when planned_end_date is None."""
		row1 = {"planned_end_date": "2026-10-25 10:00:00", "expected_delivery_date": "2026-10-30"}
		self.assertEqual(get_target_completion_date(row1), date(2026, 10, 25))

		row2 = {"planned_end_date": None, "expected_delivery_date": "2026-10-30"}
		self.assertEqual(get_target_completion_date(row2), date(2026, 10, 30))

		row3 = {"planned_end_date": None, "expected_delivery_date": None}
		self.assertIsNone(get_target_completion_date(row3))

	def test_validate_filters_allowlist(self):
		"""Ensures unknown filter keys are rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({"company": self.company, "hacker_key": "drop table"})

	def test_validate_filters_date_bounds(self):
		"""Ensures inverted date range is strictly rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({
				"company": self.company,
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_validate_filters_invalid_status(self):
		"""Ensures unsupported Work Order status is rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({
				"company": self.company,
				"status": "NonExistentStatus",
			})

	def test_validate_filters_invalid_workstation(self):
		"""Ensures non-existent workstation throws ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({
				"company": self.company,
				"workstation": "Fake Workstation 999",
			})

	def test_validate_filters_review_days_range(self):
		"""Ensures review_days must be between 0 and 90."""
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({
				"company": self.company,
				"review_days": 150,
			})
		with self.assertRaises(frappe.ValidationError):
			validate_factory_filters({
				"company": self.company,
				"review_days": -5,
			})

	def test_factory_overview_structure_and_kpis(self):
		"""Verifies that get_factory_overview returns all 7 required KPIs with verified types."""
		res = get_factory_overview({"company": self.company})
		self.assertTrue(res.get("available"))
		self.assertEqual(res.get("applied_filters", {}).get("company"), self.company)

		kpis = res.get("kpis", {})
		required_kpis = [
			"active_work_orders",
			"planned_production",
			"actual_production",
			"production_achievement",
			"overdue_work_orders",
			"open_job_cards",
			"material_blockers",
		]
		for kpi in required_kpis:
			self.assertIn(kpi, kpis, f"Missing required KPI: {kpi}")
			self.assertIn("label", kpis[kpi])
			self.assertIn("value", kpis[kpi])
			self.assertIn("description", kpis[kpi])

		# Active work orders count must be integer >= 0
		self.assertIsInstance(kpis["active_work_orders"]["value"], int)
		self.assertGreaterEqual(kpis["active_work_orders"]["value"], 0)

		# Production achievement must handle percentages cleanly
		self.assertIn("pct", kpis["production_achievement"])
		self.assertIsInstance(kpis["production_achievement"]["pct"], float)

	def test_factory_overview_summary_sections(self):
		"""Verifies status distribution, item production summary, and overdue/approaching job lists."""
		res = get_factory_overview({"company": self.company})
		summary = res.get("summary", {})

		self.assertIn("status_distribution", summary)
		self.assertIn("item_production_summary", summary)
		self.assertIn("overdue_jobs", summary)
		self.assertIn("approaching_jobs", summary)

		for item in summary["item_production_summary"]:
			self.assertIn("item_code", item)
			self.assertIn("stock_uom", item)
			self.assertIn("planned_qty", item)
			self.assertIn("produced_qty", item)
			self.assertIn("achievement_pct", item)
			self.assertIn("work_orders", item)
			self.assertIsInstance(item["work_orders"], list)

	def test_factory_overview_workstation_filter(self):
		"""Verifies filtering by a specific workstation."""
		ws_list = frappe.get_all("Workstation", filters={"name": "Laser Cutting Shop"}, limit=1)
		if ws_list:
			res = get_factory_overview({"company": self.company, "workstation": "Laser Cutting Shop"})
			self.assertTrue(res.get("available"))
			self.assertEqual(res.get("applied_filters", {}).get("workstation"), "Laser Cutting Shop")

	def test_future_reference_date_overdue_detection(self):
		"""Verifies that active Work Orders past due are accurately detected when evaluated against a future reference date."""
		future_ref = "2026-11-15 00:00:00"
		res = get_factory_overview({"company": self.company, "reference_at": future_ref})
		self.assertTrue(res.get("available"))
		kpis = res.get("kpis", {})
		overdue_count = kpis["overdue_work_orders"]["value"]
		overdue_jobs = res.get("summary", {}).get("overdue_jobs", [])

		self.assertEqual(overdue_count, len(overdue_jobs))
		for job in overdue_jobs:
			self.assertGreater(job["days_overdue"], 0)
			self.assertEqual(job["drilldown_route"], ["Form", "Work Order", job["work_order"]])

	def test_unauthorized_access_denied(self):
		"""Ensures user without production capability is denied access."""
		test_user = "guest@example.com"
		if not frappe.db.exists("User", test_user):
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": test_user,
				"first_name": "Test",
				"roles": [{"role": "Customer"}],
			})
			user_doc.insert(ignore_permissions=True)

		frappe.set_user(test_user)
		try:
			with self.assertRaises(frappe.PermissionError):
				get_factory_overview({"company": self.company})
		finally:
			frappe.set_user("Administrator")

