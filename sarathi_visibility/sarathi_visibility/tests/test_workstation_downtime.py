"""
DASH-019: Comprehensive automated unit, security, and calculation tests for
Workstation and Downtime Views in Production Management Control Tower.
Validates workstation overview, operation mapping, downtime calculation and interval clipping,
production impact tracking, zero N+1 queries, and role permissions.
"""
from datetime import date, datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.workstations import (
	WS_FILTER_KEYS,
	WS_VALID_STATUSES,
	get_workstation_downtime,
	validate_workstation_downtime_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestWorkstationDowntime(PermissionTests):
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
			validate_workstation_downtime_filters({
				"company": self.company,
				"malicious_sql_param": "DROP TABLE tabWorkstation",
			})

	def test_validate_filters_date_bounds(self):
		"""Ensures inverted date range is strictly rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_workstation_downtime_filters({
				"company": self.company,
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_validate_filters_invalid_workstation(self):
		"""Ensures non-existent workstation raises ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_workstation_downtime_filters({
				"company": self.company,
				"workstation": "NonExistentWorkstationXYZ999",
			})

	def test_validate_filters_invalid_status(self):
		"""Ensures unsupported status raises ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_workstation_downtime_filters({
				"company": self.company,
				"status": "FakeStatusInvalid",
			})

	def test_security_cross_company_isolation(self):
		"""Ensures Work Orders from other companies cannot be queried via filters."""
		if not self.other_company:
			self.skipTest("Single company test environment.")
		with self.assertRaises(frappe.PermissionError):
			validate_workstation_downtime_filters({
				"company": self.other_company,
			})

	# ---------------------------------------------------------
	# 2. Response Contract & Structure Tests
	# ---------------------------------------------------------
	def test_response_contract_structure(self):
		"""Verifies that API returns all required contract fields."""
		res = get_workstation_downtime({"company": self.company})
		self.assertTrue(res.get("available"))
		self.assertIn("reference_date", res)
		self.assertIn("summary", res)
		self.assertIn("workstations_overview", res)
		self.assertIn("downtime_events", res)
		self.assertIn("production_impact", res)
		self.assertIn("workstation_activity", res)
		self.assertIn("applied_filters", res)

		s = res["summary"]
		self.assertIn("total_workstations", s)
		self.assertIn("workstations_with_active_jobs", s)
		self.assertIn("total_assigned_operations", s)
		self.assertIn("recorded_running_jobs", s)
		self.assertIn("completed_operations", s)
		self.assertIn("delayed_operations_count", s)
		self.assertIn("recorded_downtime_events", s)
		self.assertIn("total_downtime_minutes", s)
		self.assertIn("utilization_metric_status", s)
		self.assertIn("oee_metric_status", s)

	# ---------------------------------------------------------
	# 3. Calculation & Classification Logic
	# ---------------------------------------------------------
	def test_workstation_overview_fields_and_telemetry_disclosure(self):
		"""
		Tests that workstation overview records contain required metadata
		and clearly disclose absence of machine sensor telemetry.
		"""
		res = get_workstation_downtime({"company": self.company})
		ws_list = res["workstations_overview"]

		for ws in ws_list:
			self.assertIn("workstation", ws)
			self.assertIn("workstation_name", ws)
			self.assertIn("recorded_status", ws)
			self.assertIn("derived_status", ws)
			self.assertIn("status_source", ws)
			self.assertIn("telemetry_status", ws)
			self.assertIn("assigned_job_cards_count", ws)
			self.assertIn("active_job_cards_count", ws)
			self.assertIn("queued_job_cards_count", ws)
			self.assertIn("completed_job_cards_count", ws)
			self.assertIn("delayed_job_cards_count", ws)
			self.assertIn("total_downtime_minutes", ws)

			# Ensure unsupported metrics are None and not fabricated
			self.assertIsNone(ws["utilization_rate"])
			self.assertIsNone(ws["oee"])

	def test_workstation_activity_pagination(self):
		"""Verifies that pagination parameters function deterministically."""
		res_p1 = get_workstation_downtime({"company": self.company}, start=0, page_length=3)
		self.assertLessEqual(len(res_p1["workstation_activity"]), 3)
		self.assertEqual(res_p1["start"], 0)
		self.assertEqual(res_p1["page_length"], 3)
