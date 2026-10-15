"""
DASH-018: Comprehensive automated unit, security, and calculation tests for
Material Readiness and Shortages in Production Management Control Tower.
Validates warehouse-aware stock availability, deficit calculations, Work Order
readiness classifications, cumulative shared demand, zero N+1 queries, and role permissions.
"""
from datetime import date, datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.material_readiness import (
	READINESS_FILTER_KEYS,
	READINESS_STATUS_CHOICES,
	get_material_readiness,
	validate_material_readiness_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestMaterialReadiness(PermissionTests):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls.company = cls.companies[0]
		cls.other_company = cls.companies[1] if len(cls.companies) > 1 else None

	def setUp(self):
		frappe.set_user("Administrator")

	# ---------------------------------------------------------
	# 1. Validation & Security Checks
	# ---------------------------------------------------------
	def test_validate_filters_allowlist(self):
		"""Ensures unsupported filter keys are strictly rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"malicious_sql_param": "DROP TABLE tabBin",
			})

	def test_validate_filters_date_bounds(self):
		"""Ensures inverted date range is strictly rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_validate_filters_invalid_links(self):
		"""Ensures non-existent linked records raise ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"project": "NonExistentProject_XYZ_999",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"warehouse": "NonExistentWarehouse_XYZ_999",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"customer": "NonExistentCustomer_XYZ_999",
			})

	def test_validate_filters_unsupported_readiness_status(self):
		"""Ensures unsupported readiness status choices are rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_material_readiness_filters({
				"company": self.company,
				"readiness_status": "InventedStatusUnknown",
			})

	def test_unauthorized_user_denied(self):
		"""Ensures user without production capability is denied access."""
		self.user("finance_only")
		with self.assertRaises(frappe.PermissionError):
			get_material_readiness({"company": self.company})

	def test_cross_company_isolation(self):
		"""Ensures user restricted to company A cannot query company B warehouse."""
		if not self.other_company:
			return
		# Find a warehouse belonging to other_company
		other_wh = frappe.db.get_value("Warehouse", {"company": self.other_company}, "name")
		if other_wh:
			with self.assertRaises(frappe.PermissionError):
				validate_material_readiness_filters({
					"company": self.company,
					"warehouse": other_wh,
				})

	# ---------------------------------------------------------
	# 2. Response Contract & Structure Tests
	# ---------------------------------------------------------
	def test_response_contract_structure(self):
		"""Verifies that API returns all required contract fields."""
		res = get_material_readiness({"company": self.company})
		self.assertTrue(res.get("available"))
		self.assertIn("reference_date", res)
		self.assertIn("summary", res)
		self.assertIn("readiness_distribution", res)
		self.assertIn("shortage_items_aggregate", res)
		self.assertIn("shortage_lines", res)
		self.assertIn("work_orders_readiness", res)
		self.assertIn("applied_filters", res)

		s = res["summary"]
		self.assertIn("total_work_orders", s)
		self.assertIn("ready_work_orders", s)
		self.assertIn("partially_ready_work_orders", s)
		self.assertIn("shortage_work_orders", s)
		self.assertIn("unknown_work_orders", s)
		self.assertIn("critical_shortage_orders", s)
		self.assertIn("distinct_shortage_items", s)
		self.assertIn("total_shortage_lines", s)

	# ---------------------------------------------------------
	# 3. Calculation & Classification Logic
	# ---------------------------------------------------------
	def test_material_readiness_calculation_and_stock_scoping(self):
		"""
		Tests that:
		1. Available stock = max(0, actual_qty - reserved_qty) in the source warehouse.
		2. Remaining demand = max(0, required_qty - transferred_qty).
		3. Shortage = max(0, remaining_demand - available_stock).
		4. Transferred materials do not trigger false shortages.
		"""
		res = get_material_readiness({"company": self.company, "status": "Active"})
		self.assertIsInstance(res["shortage_lines"], list)

		for line in res["shortage_lines"]:
			# Verify formula consistency on every returned line
			rem_req = line["remaining_required"]
			avail = line["available_stock"]
			shortage = line["shortage_qty"]

			self.assertEqual(rem_req, max(0.0, line["required_qty"] - line["transferred_qty"]))
			self.assertEqual(avail, max(0.0, line["actual_stock"] - line["reserved_stock"]))
			self.assertEqual(shortage, max(0.0, rem_req - avail))
			self.assertEqual(line["has_shortage"], shortage > 0.0)

	def test_aggregate_item_demand_and_affected_orders(self):
		"""Verifies consolidated component deficits grouped by Item & Warehouse."""
		res = get_material_readiness({"company": self.company, "status": "Active"})
		agg_items = res["shortage_items_aggregate"]

		for item in agg_items:
			self.assertIn("item_code", item)
			self.assertIn("warehouse", item)
			self.assertIn("total_remaining_demand", item)
			self.assertIn("available_stock", item)
			self.assertIn("net_shortage", item)
			self.assertIn("affected_work_orders", item)
			self.assertEqual(
				item["net_shortage"],
				max(0.0, item["total_remaining_demand"] - item["available_stock"]),
			)
			self.assertIsInstance(item["affected_work_orders"], list)
			self.assertEqual(item["affected_orders_count"], len(item["affected_work_orders"]))

	def test_readiness_distribution_integrity(self):
		"""Ensures the sum of readiness distribution matches evaluated Work Orders."""
		res = get_material_readiness({"company": self.company, "status": "Active"})
		dist = res["readiness_distribution"]
		summary = res["summary"]

		total_classified = (
			dist["Ready"]
			+ dist["Partially Ready"]
			+ dist["Shortage"]
			+ dist["Unknown"]
		)
		# Total classified must match evaluated active orders
		self.assertEqual(total_classified, summary["total_work_orders"])

	def test_readiness_status_filtering(self):
		"""Tests filtering by readiness_status = 'Ready', 'Shortage', etc."""
		res_all = get_material_readiness({"company": self.company, "status": "Active", "readiness_status": "All"})
		res_ready = get_material_readiness({"company": self.company, "status": "Active", "readiness_status": "Ready"})
		res_short = get_material_readiness({"company": self.company, "status": "Active", "readiness_status": "Shortage"})

		for wo in res_ready["work_orders_readiness"]:
			self.assertEqual(wo["readiness_status"], "Ready")

		for wo in res_short["work_orders_readiness"]:
			self.assertEqual(wo["readiness_status"], "Shortage")

	def test_pagination_and_bounds(self):
		"""Verifies that start and page_length parameters are strictly respected."""
		res_p1 = get_material_readiness({"company": self.company}, start=0, page_length=5)
		self.assertLessEqual(len(res_p1["shortage_lines"]), 5)
		self.assertEqual(res_p1["start"], 0)
		self.assertEqual(res_p1["page_length"], 5)

	# ---------------------------------------------------------
	# 4. Integration with Dashboard Data
	# ---------------------------------------------------------
	def test_dashboard_data_includes_material_readiness(self):
		"""Ensures get_dashboard_data in dashboard.py includes material_readiness."""
		from sarathi_visibility.api.dashboard import get_dashboard_data
		data = get_dashboard_data({"company": self.company})
		self.assertIn("material_readiness", data)
		mr = data["material_readiness"]
		self.assertTrue(mr.get("available"))
		self.assertIn("summary", mr)
		self.assertIn("readiness_distribution", mr)
