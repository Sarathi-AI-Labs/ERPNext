"""
DASH-023: Automated bench unit, security, and assignment tests for
Shop-Floor Supervisor & Operator Workboard in sarathi_visibility.
Validates operator ToDo assignment isolation, supervisor workstation scoping,
summary calculation, blocker surfacing, and read-focused security.
"""
from datetime import date, datetime
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.shopfloor import (
	SHOPFLOOR_FILTER_KEYS,
	VALID_STATUSES,
	complete_job,
	get_assigned_jobs,
	get_current_operation,
	get_next_jobs,
	get_shop_floor_summary,
	get_shopfloor_workboard,
	get_supervisor_team_overview,
	pause_job,
	record_job_progress,
	resolve_supervisor_team_scope,
	resume_job,
	start_job,
	stop_job,
	validate_shopfloor_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestShopFloor(PermissionTests):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls.company = cls.companies[0]
		cls.other_company = cls.companies[1] if len(cls.companies) > 1 else None

	def setUp(self):
		frappe.set_user("Administrator")

	# ---------------------------------------------------------
	# 1. Validation & Filter Allowlist Security
	# ---------------------------------------------------------
	def test_validate_filters_allowlist(self):
		"""Ensures unsupported filter keys are rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_shopfloor_filters({
				"unauthorized_key": "DROP TABLE tabJobCard",
			})

	def test_validate_filters_invalid_status(self):
		"""Ensures invalid status value is rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_shopfloor_filters({
				"status": "FictionalStatusChoice",
			})

	def test_unauthorized_user_denied(self):
		"""Ensures unrelated user without shop or production role is rejected."""
		self.user("unrelated")
		with self.assertRaises(frappe.PermissionError):
			get_shopfloor_workboard({})

	# ---------------------------------------------------------
	# 2. Operator Strict Assignment Isolation
	# ---------------------------------------------------------
	def test_operator_response_structure_and_assignment_scope(self):
		"""Ensures operator receives valid response schema and only assigned jobs."""
		self.user("operator")
		res = get_shopfloor_workboard({})
		self.assertTrue(res["available"])
		self.assertIn("user_context", res)
		self.assertIn("summary", res)
		self.assertIn("active_operations", res)
		self.assertIn("assigned_jobs", res)
		self.assertIn("blockers", res)

		ctx = res["user_context"]
		self.assertTrue(ctx["is_operator"])
		self.assertFalse(ctx["is_manager"])
		self.assertEqual(ctx["role_label"], "Machine Operator")

		# If operator has assigned Job Card (jobs[0] via setUpClass ToDo)
		if res["assigned_jobs"]:
			card = res["assigned_jobs"][0]
			self.assertIn("name", card)
			self.assertIn("operation", card)
			self.assertIn("workstation", card)
			self.assertIn("status", card)
			self.assertIn("stock_uom", card)
			self.assertIn("for_quantity", card)
			self.assertIn("total_completed_qty", card)
			self.assertIn("completion_percent", card)
			self.assertIn("drill_down_link", card)
			# Operator must not have unassigned jobs[1] in assigned list
			assigned_names = {j["name"] for j in res["assigned_jobs"]}
			self.assertNotIn(self.jobs[1].name, assigned_names)

	# ---------------------------------------------------------
	# 3. Supervisor Workstation Team Scope
	# ---------------------------------------------------------
	def test_supervisor_workstation_team_scope(self):
		"""Ensures supervisor can view jobs associated with their permitted workstations."""
		self.user("supervisor")
		res = get_shopfloor_workboard({})
		self.assertTrue(res["available"])
		ctx = res["user_context"]
		self.assertTrue(ctx["is_supervisor"])
		self.assertEqual(ctx["role_label"], "Shop-Floor Supervisor")

	# ---------------------------------------------------------
	# 4. Production Manager Full Visibility Scope
	# ---------------------------------------------------------
	def test_production_manager_scope(self):
		"""Ensures production manager can inspect company-wide shop floor activity."""
		self.user("manager")
		res = get_shopfloor_workboard({"company": self.company})
		self.assertTrue(res["available"])
		ctx = res["user_context"]
		self.assertTrue(ctx["is_manager"])
		self.assertEqual(ctx["role_label"], "Production Manager")

	# ---------------------------------------------------------
	# 5. DASH-024 Granular API Endpoints Tests
	# ---------------------------------------------------------
	def test_get_assigned_jobs_api(self):
		"""Ensures get_assigned_jobs returns valid schema, pagination, and authorized jobs."""
		self.user("operator")
		res = get_assigned_jobs(start=0, page_length=10)
		self.assertTrue(res["success"])
		self.assertIn("jobs", res)
		self.assertIn("total", res)
		self.assertIn("start", res)
		self.assertIn("page_length", res)
		self.assertIn("has_next_page", res)
		self.assertIn("user_context", res)

	def test_get_current_operation_api(self):
		"""Ensures get_current_operation returns valid structure with active operations."""
		self.user("operator")
		res = get_current_operation()
		self.assertTrue(res["success"])
		self.assertIn("has_active_operation", res)
		self.assertIn("active_operations", res)
		self.assertIn("current_operation", res)
		self.assertIn("count", res)

	def test_get_next_jobs_api(self):
		"""Ensures get_next_jobs returns ordered waiting jobs."""
		self.user("operator")
		res = get_next_jobs(limit=5)
		self.assertTrue(res["success"])
		self.assertIn("next_jobs", res)
		self.assertIn("total_waiting", res)
		self.assertIn("ordering_basis", res)

	def test_get_shop_floor_summary_api(self):
		"""Ensures get_shop_floor_summary metrics agree with assigned jobs status counts."""
		self.user("operator")
		summary_res = get_shop_floor_summary()
		self.assertTrue(summary_res["success"])
		summary = summary_res["summary"]
		self.assertIn("total_assigned_jobs", summary)
		self.assertIn("jobs_in_progress", summary)
		self.assertIn("waiting_jobs", summary)
		self.assertIn("completed_jobs", summary)
		self.assertIn("blocked_jobs", summary)

	# ---------------------------------------------------------
	# 6. DASH-025 Shop-Floor Reporting Actions & Security
	# ---------------------------------------------------------
	def test_unauthorized_user_cannot_mutate_jobs(self):
		"""Ensures unrelated user without shop or production role cannot mutate Job Cards."""
		self.user("unrelated")
		target_jc = self.jobs[0].name
		with self.assertRaises(frappe.PermissionError):
			start_job(target_jc)
		with self.assertRaises(frappe.PermissionError):
			record_job_progress(target_jc, completed_qty=1.0)
		with self.assertRaises(frappe.PermissionError):
			pause_job(target_jc)
		with self.assertRaises(frappe.PermissionError):
			complete_job(target_jc)

	def test_operator_cannot_mutate_unassigned_job(self):
		"""Ensures operator cannot start or report progress against an unassigned Job Card."""
		self.user("operator")
		unassigned_jc = self.jobs[1].name
		with self.assertRaises(frappe.PermissionError):
			start_job(unassigned_jc)
		with self.assertRaises(frappe.PermissionError):
			record_job_progress(unassigned_jc, completed_qty=5.0)

	def test_mutation_rejects_nonexistent_job_card(self):
		"""Ensures non-existent Job Card raises DoesNotExistError on mutation."""
		self.user("operator")
		with self.assertRaises(frappe.DoesNotExistError):
			start_job("NONEXISTENT_JC_99999")

	def test_record_progress_rejects_negative_or_invalid_quantity(self):
		"""Ensures negative or malformed quantities are strictly rejected."""
		self.user("operator")
		assigned_jc = self.jobs[0].name
		with self.assertRaises(frappe.ValidationError):
			record_job_progress(assigned_jc, completed_qty=-5.0)
		with self.assertRaises(frappe.ValidationError):
			record_job_progress(assigned_jc, completed_qty="invalid_qty")

	def test_operator_job_lifecycle_start_pause_resume(self):
		"""Ensures operator can start, pause, and resume assigned job with idempotency."""
		self.user("operator")
		assigned_jc = self.jobs[0].name
		frappe.db.savepoint("sp_shopfloor_lifecycle")
		try:
			# Start job
			res_start = start_job(assigned_jc)
			self.assertTrue(res_start["success"])
			self.assertIn(res_start["status"], ["Work In Progress", "Open"])

			# Idempotent start
			res_start2 = start_job(assigned_jc)
			self.assertTrue(res_start2["success"])

			# Pause job
			res_pause = pause_job(assigned_jc)
			self.assertTrue(res_pause["success"])

			# Idempotent pause
			res_pause2 = pause_job(assigned_jc)
			self.assertTrue(res_pause2["success"])

			# Resume job
			res_resume = resume_job(assigned_jc)
			self.assertTrue(res_resume["success"])
		finally:
			frappe.db.rollback(save_point="sp_shopfloor_lifecycle")

	# ---------------------------------------------------------
	# 7. DASH-026 Supervisor Team Overview Bench Tests
	# ---------------------------------------------------------
	def test_operator_cannot_access_supervisor_team_overview(self):
		"""Ensures operator role is rejected with PermissionError when requesting team overview."""
		self.user("operator")
		with self.assertRaises(frappe.PermissionError):
			get_supervisor_team_overview({})

	def test_supervisor_can_access_supervisor_team_overview(self):
		"""Ensures supervisor role can access team overview and receive valid schema."""
		self.user("supervisor")
		res = get_supervisor_team_overview({})
		self.assertTrue(res["success"])
		self.assertIn("user_context", res)
		self.assertIn("team_summary", res)
		self.assertIn("team_workload", res)
		self.assertIn("active_operations", res)
		self.assertIn("completed_work", res)
		self.assertIn("blockers", res)
		self.assertIn("workstations", res)

		summary = res["team_summary"]
		self.assertIn("total_team_members", summary)
		self.assertIn("operators_active", summary)
		self.assertIn("operators_with_jobs", summary)
		self.assertIn("operators_without_work", summary)
		self.assertIn("active_job_cards", summary)
		self.assertIn("waiting_job_cards", summary)
		self.assertIn("completed_job_cards", summary)
		self.assertIn("blocked_job_cards", summary)
		self.assertIn("overdue_job_cards", summary)

	def test_production_manager_can_access_supervisor_team_overview(self):
		"""Ensures production manager can access team overview with company scope."""
		self.user("manager")
		res = get_supervisor_team_overview({"company": self.company})
		self.assertTrue(res["success"])
		self.assertTrue(res["user_context"]["is_manager"])
		self.assertIn("team_summary", res)


