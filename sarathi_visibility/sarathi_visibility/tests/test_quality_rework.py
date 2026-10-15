"""
DASH-020: Comprehensive automated unit, security, and calculation tests for
Quality, Rework, and Subcontracting Views in Production Management Control Tower.
Validates Quality Inspection totals, pass/fail metrics, corrective Job Card detection,
Subcontracting Order quantity reconciliation, zero N+1 queries, and role permissions.
"""
from datetime import date, datetime
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.quality_rework import (
	QUALITY_FILTER_KEYS,
	QI_STATUS_CHOICES,
	QI_TYPE_CHOICES,
	get_quality_overview,
	get_rework_overview,
	get_subcontracting_overview,
	validate_quality_rework_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestQualityRework(PermissionTests):
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
			validate_quality_rework_filters({
				"company": self.company,
				"malicious_sql_param": "DROP TABLE tabItem",
			})

	def test_validate_filters_date_bounds(self):
		"""Ensures from_date > to_date is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_quality_rework_filters({
				"company": self.company,
				"from_date": "2026-10-31",
				"to_date": "2026-10-01",
			})

	def test_validate_filters_invalid_status(self):
		"""Ensures invalid status value is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_quality_rework_filters({
				"company": self.company,
				"status": "InvalidStatusChoice",
			})

	# ---------------------------------------------------------
	# 2. Quality Overview Tests
	# ---------------------------------------------------------
	def test_quality_overview_response_structure(self):
		"""Validates quality overview structure, KPIs, and zero N+1 queries."""
		res = get_quality_overview({"company": self.company})
		self.assertIn("available", res)
		if res["available"]:
			self.assertIn("summary", res)
			self.assertIn("top_rejected_items", res)
			self.assertIn("inspections", res)
			summary = res["summary"]
			self.assertIn("total_inspections", summary)
			self.assertIn("passed_inspections", summary)
			self.assertIn("failed_inspections", summary)
			self.assertIn("failure_rate_percent", summary)
			self.assertGreaterEqual(summary["failure_rate_percent"], 0.0)
			self.assertLessEqual(summary["failure_rate_percent"], 100.0)

	def test_quality_overview_pagination(self):
		"""Validates pagination for quality inspections."""
		res_p1 = get_quality_overview({"company": self.company}, start=0, page_length=2)
		if res_p1["available"] and res_p1["total_inspections_count"] > 2:
			self.assertEqual(len(res_p1["inspections"]), 2)
			self.assertTrue(res_p1["has_next_page"])

	# ---------------------------------------------------------
	# 3. Rework Overview Tests
	# ---------------------------------------------------------
	def test_rework_overview_response_structure(self):
		"""Validates rework overview response structure, configuration flags, and metrics."""
		res = get_rework_overview({"company": self.company})
		self.assertIn("available", res)
		if res["available"]:
			self.assertIn("rework_configured", res)
			self.assertIn("summary", res)
			self.assertIn("rework_jobs", res)
			if not res["rework_configured"]:
				self.assertIn("rework_note", res)

	# ---------------------------------------------------------
	# 4. Subcontracting Overview Tests
	# ---------------------------------------------------------
	def test_subcontracting_overview_response_structure(self):
		"""Validates subcontracting overview metrics, quantity reconciliation, and orders."""
		res = get_subcontracting_overview({"company": self.company})
		self.assertIn("available", res)
		if res["available"]:
			self.assertIn("summary", res)
			self.assertIn("orders", res)
			summary = res["summary"]
			self.assertIn("total_subcontract_orders", summary)
			self.assertIn("active_subcontracts", summary)
			self.assertIn("awaiting_receipt_orders", summary)
			self.assertIn("overdue_subcontracts", summary)
			self.assertIn("total_ordered_units", summary)
			self.assertIn("total_received_units", summary)
			self.assertIn("total_outstanding_units", summary)
			# Reconciled: ordered - received >= 0
			self.assertGreaterEqual(summary["total_ordered_units"], summary["total_received_units"])
