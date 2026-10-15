"""
DASH-021: Automated bench unit, security, and calculation tests for
Production Exception and Escalation Queue in Production Management Control Tower.
Validates exception aggregation across Work Orders, Job Cards, Material Shortages,
Workstation Downtime, Quality Inspections, Rework cases, and Subcontracting Orders.
"""
from datetime import date, datetime
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.production_exceptions import (
	EXCEPTION_FILTER_KEYS,
	SEVERITY_RANKS,
	VALID_CATEGORIES,
	VALID_SEVERITIES,
	get_production_exceptions,
	validate_exception_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestProductionExceptions(PermissionTests):
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
			validate_exception_filters({
				"company": self.company,
				"malicious_sql_param": "DROP TABLE tabItem",
			})

	def test_validate_filters_date_bounds(self):
		"""Ensures from_date > to_date is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_exception_filters({
				"company": self.company,
				"from_date": "2026-10-31",
				"to_date": "2026-10-01",
			})

	def test_validate_filters_invalid_category(self):
		"""Ensures invalid category value is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_exception_filters({
				"company": self.company,
				"category": "FictionalCategoryChoice",
			})

	def test_validate_filters_invalid_severity(self):
		"""Ensures invalid severity value is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_exception_filters({
				"company": self.company,
				"severity": "EmergencyCriticalMax",
			})

	def test_cross_company_isolation(self):
		"""Ensures filters targeting records from other companies are rejected if unauthorized."""
		if not self.other_company:
			return
		# If user tries to filter with a work order from another company
		other_wos = frappe.get_all(
			"Work Order",
			filters={"company": self.other_company},
			limit=1,
			pluck="name",
		)
		if other_wos:
			with self.assertRaises((frappe.PermissionError, frappe.ValidationError)):
				validate_exception_filters({
					"company": self.company,
					"work_order": other_wos[0],
				})

	# ---------------------------------------------------------
	# 2. Production Exceptions Queue Structure & Aggregation
	# ---------------------------------------------------------
	def test_production_exceptions_response_structure(self):
		"""Validates exception queue structure, summary metrics, and field contracts."""
		res = get_production_exceptions({"company": self.company})
		self.assertIn("available", res)
		if res["available"]:
			self.assertIn("summary", res)
			self.assertIn("exceptions", res)
			self.assertIn("total_exceptions_count", res)
			self.assertIn("categories", res)
			self.assertIn("severities", res)

			summary = res["summary"]
			self.assertIn("total_open_exceptions", summary)
			self.assertIn("critical_exceptions", summary)
			self.assertIn("high_exceptions", summary)
			self.assertIn("medium_exceptions", summary)
			self.assertIn("low_exceptions", summary)
			self.assertIn("material_exceptions", summary)
			self.assertIn("quality_exceptions", summary)
			self.assertIn("subcontracting_exceptions", summary)
			self.assertIn("overdue_exceptions", summary)

			# Ensure deterministic field schema on every returned exception
			for exc in res["exceptions"]:
				self.assertIn("exception_id", exc)
				self.assertIn("category", exc)
				self.assertIn("exception_type", exc)
				self.assertIn("title", exc)
				self.assertIn("description", exc)
				self.assertIn("severity", exc)
				self.assertIn(exc["severity"], VALID_SEVERITIES)
				self.assertIn("status", exc)
				self.assertIn("source_doctype", exc)
				self.assertIn("source_name", exc)
				self.assertIn("recommended_action", exc)
				self.assertIn("source_link", exc)

	def test_production_exceptions_pagination(self):
		"""Validates pagination controls and capped result size."""
		res_p1 = get_production_exceptions({"company": self.company}, start=0, page_length=2)
		if res_p1["available"] and res_p1["total_exceptions_count"] > 2:
			self.assertEqual(len(res_p1["exceptions"]), 2)
			self.assertTrue(res_p1["has_next_page"])

			# Page 2
			res_p2 = get_production_exceptions({"company": self.company}, start=2, page_length=2)
			self.assertNotEqual(res_p1["exceptions"][0]["exception_id"], res_p2["exceptions"][0]["exception_id"])

	def test_production_exceptions_filtering(self):
		"""Validates category and severity filter narrowing."""
		res_all = get_production_exceptions({"company": self.company})
		if not res_all["available"] or not res_all["exceptions"]:
			return

		# Filter by first available severity
		first_sev = res_all["exceptions"][0]["severity"]
		res_sev = get_production_exceptions({"company": self.company, "severity": first_sev})
		for exc in res_sev["exceptions"]:
			self.assertEqual(exc["severity"], first_sev)

	def test_production_exceptions_deterministic_sorting(self):
		"""Verifies that returned exceptions strictly follow severity rank ordering."""
		res = get_production_exceptions({"company": self.company})
		if not res["available"] or len(res["exceptions"]) < 2:
			return

		for i in range(len(res["exceptions"]) - 1):
			current_rank = SEVERITY_RANKS.get(res["exceptions"][i]["severity"], 99)
			next_rank = SEVERITY_RANKS.get(res["exceptions"][i + 1]["severity"], 99)
			self.assertLessEqual(current_rank, next_rank, "Exceptions must be sorted in descending severity order")
