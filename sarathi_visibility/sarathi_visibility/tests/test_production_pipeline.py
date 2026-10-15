"""
DASH-017: Comprehensive unit and security tests for Production Pipeline and Bottleneck Views.
Validates stage progression, operation sequencing, predecessor dependencies, delayed operations,
defensible bottleneck detection rules, deduplication, and role-based permissions.
"""
from datetime import date, datetime, timedelta
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.production_pipeline import (
	get_production_pipeline,
	validate_pipeline_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestProductionPipeline(PermissionTests):
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
		"""Ensures unsupported filter keys are rejected with ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_pipeline_filters({"company": self.company, "malicious_key": "DROP TABLE"})

	def test_validate_filters_date_bounds(self):
		"""Ensures inverted date range is strictly rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_pipeline_filters({
				"company": self.company,
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_validate_filters_invalid_links(self):
		"""Ensures non-existent linked records raise ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_pipeline_filters({
				"company": self.company,
				"project": "NonExistentProject123",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_pipeline_filters({
				"company": self.company,
				"workstation": "NonExistentWorkstation123",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_pipeline_filters({
				"company": self.company,
				"customer": "NonExistentCustomer123",
			})

	def test_unauthorized_user_denied(self):
		"""Ensures user without production capability is denied access."""
		self.user("finance_only")
		with self.assertRaises(frappe.PermissionError):
			get_production_pipeline({"company": self.company})

	def test_cross_company_isolation(self):
		"""Ensures user cannot access pipeline for an unauthorized company."""
		if not self.other_company:
			self.skipTest("Need second company for cross-company test.")
		self.user("manager")
		with self.assertRaises(frappe.PermissionError):
			get_production_pipeline({"company": self.other_company})

	# ---------------------------------------------------------
	# 2. Pipeline Structure & Stages
	# ---------------------------------------------------------
	def test_pipeline_basic_structure_and_stages(self):
		"""Verifies expected response contract, summary, and 4 verified stages."""
		res = get_production_pipeline({"company": self.company})
		self.assertTrue(res.get("available"))
		self.assertIn("summary", res)
		self.assertIn("stages", res)
		self.assertIn("pipeline_jobs", res)
		self.assertIn("delayed_operations", res)
		self.assertIn("bottlenecks", res)
		self.assertIn("applied_filters", res)

		summary = res["summary"]
		self.assertIn("total_work_orders", summary)
		self.assertIn("material_staging", summary)
		self.assertIn("in_production", summary)
		self.assertIn("manufacture_receipt", summary)
		self.assertIn("completed", summary)
		self.assertIn("overdue_work_orders", summary)
		self.assertIn("overdue_operations", summary)
		self.assertIn("bottlenecks_detected", summary)

		stage_keys = [s["key"] for s in res["stages"]]
		expected_keys = ["Material Staging", "In Production", "Manufacture Receipt", "Completed"]
		self.assertEqual(stage_keys, expected_keys)

		for stage in res["stages"]:
			self.assertIn("key", stage)
			self.assertIn("label", stage)
			self.assertIn("description", stage)
			self.assertIn("count", stage)
			self.assertIn("jobs", stage)
			self.assertIsInstance(stage["jobs"], list)

	def test_pipeline_jobs_verified_fields_and_quantities(self):
		"""Verifies that each pipeline job contains verified quantities and drill-down links."""
		res = get_production_pipeline({"company": self.company, "status": "All"})
		if not res["pipeline_jobs"]:
			self.skipTest("No Work Orders found for pipeline.")

		for job in res["pipeline_jobs"]:
			self.assertIn("work_order", job)
			self.assertIn("production_item", job)
			self.assertIn("qty", job)
			self.assertIn("produced_qty", job)
			self.assertIn("remaining_qty", job)
			self.assertIn("completion_percent", job)
			self.assertIn("stage", job)
			self.assertIn("status", job)
			self.assertIn("operations", job)
			self.assertIn("drilldown_route", job)

			qty = flt(job["qty"])
			produced = flt(job["produced_qty"])
			self.assertEqual(job["remaining_qty"], max(0.0, qty - produced))
			self.assertGreaterEqual(job["completion_percent"], 0.0)
			self.assertLessEqual(job["completion_percent"], 100.0)
			self.assertEqual(job["drilldown_route"], ["Form", "Work Order", job["work_order"]])

	# ---------------------------------------------------------
	# 3. Operation Sequencing & Dependency Tracking
	# ---------------------------------------------------------
	def test_pipeline_multi_operation_sequencing(self):
		"""Verifies that Work Orders with multiple Job Cards maintain ordered sequence numbers."""
		res = get_production_pipeline({"company": self.company, "status": "All"})
		multi_op_jobs = [j for j in res["pipeline_jobs"] if len(j.get("operations", [])) > 1]
		if not multi_op_jobs:
			self.skipTest("No multi-operation Work Orders found.")

		sample_job = multi_op_jobs[0]
		ops = sample_job["operations"]
		for idx, op in enumerate(ops):
			self.assertEqual(op["sequence"], idx + 1)
			self.assertIn("job_card", op)
			self.assertIn("operation", op)
			self.assertIn("status", op)
			if idx > 0:
				self.assertEqual(op["previous_operation"], ops[idx - 1]["operation"])
			else:
				self.assertIsNone(op["previous_operation"])
			if idx < len(ops) - 1:
				self.assertEqual(op["next_operation"], ops[idx + 1]["operation"])
			else:
				self.assertIsNone(op["next_operation"])

	def test_pipeline_dependency_and_waiting_predecessor_rules(self):
		"""
		Verifies that an uncompleted downstream operation whose predecessor
		is not completed is classified as 'Waiting on Predecessor'.
		"""
		res = get_production_pipeline({"company": self.company, "status": "All"})
		waiting_found = False
		for job in res["pipeline_jobs"]:
			ops = job.get("operations", [])
			if len(ops) >= 2:
				first_op = ops[0]
				second_op = ops[1]
				# If first operation is not completed, second operation must be Waiting on Predecessor
				if first_op["status"] != "Completed" and second_op["completed_qty"] == 0:
					self.assertEqual(second_op["status"], "Waiting on Predecessor")
					self.assertEqual(second_op["waiting_on"], first_op["operation"])
					waiting_found = True
		self.assertTrue(waiting_found, "Expected at least one operation in state 'Waiting on Predecessor'")

	# ---------------------------------------------------------
	# 4. Delayed Operations & Overdue Detection
	# ---------------------------------------------------------
	def test_delayed_operations_overdue_detection(self):
		"""Verifies that active operations past due date are detected in delayed_operations."""
		future_ref = (now_datetime() + timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
		res = get_production_pipeline({"company": self.company, "reference_at": future_ref})
		delayed_ops = res.get("delayed_operations", [])
		self.assertGreater(len(delayed_ops), 0)

		for op in delayed_ops:
			self.assertIn("job_card", op)
			self.assertIn("work_order", op)
			self.assertIn("operation", op)
			self.assertIn("days_overdue", op)
			self.assertGreater(op["days_overdue"], 0)
			self.assertEqual(op["drilldown_route"], ["Form", "Job Card", op["job_card"]])

	# ---------------------------------------------------------
	# 5. Bottleneck Identification Rules & Deduplication
	# ---------------------------------------------------------
	def test_bottleneck_detection_rules(self):
		"""Verifies that defensible bottleneck signals (queue backlog, material blocker, upstream lag) are identified."""
		res = get_production_pipeline({"company": self.company})
		bottlenecks = res.get("bottlenecks", [])
		self.assertGreater(len(bottlenecks), 0)

		b_types = {b["type"] for b in bottlenecks}
		# Ensure queue or material or predecessor bottlenecks are detected
		self.assertTrue(b_types.intersection({"queue", "material", "predecessor"}))

		for b in bottlenecks:
			self.assertIn("type", b)
			self.assertIn("title", b)
			self.assertIn("reason", b)
			self.assertIn("affected_work_orders_count", b)
			self.assertIn("affected_work_orders", b)
			self.assertIn("severity", b)
			self.assertIn("drilldown_records", b)
			self.assertIsInstance(b["affected_work_orders"], list)
			self.assertGreaterEqual(b["affected_work_orders_count"], 1)

	def test_bottleneck_work_order_deduplication(self):
		"""Ensures affected Work Orders in bottlenecks are never double counted."""
		res = get_production_pipeline({"company": self.company})
		for b in res.get("bottlenecks", []):
			wos = b["affected_work_orders"]
			self.assertEqual(len(wos), len(set(wos)), f"Duplicate Work Orders found in bottleneck: {b['title']}")
			self.assertEqual(b["affected_work_orders_count"], len(set(wos)))

	# ---------------------------------------------------------
	# 6. Filter Scoping
	# ---------------------------------------------------------
	def test_pipeline_filtering_by_status(self):
		"""Verifies filtering by status (Active vs Completed vs All)."""
		res_all = get_production_pipeline({"company": self.company, "status": "All"})
		res_completed = get_production_pipeline({"company": self.company, "status": "Completed"})
		for job in res_completed["pipeline_jobs"]:
			self.assertEqual(job["status"], "Completed")
		self.assertLessEqual(len(res_completed["pipeline_jobs"]), len(res_all["pipeline_jobs"]))

	def test_pipeline_filtering_by_workstation(self):
		"""Verifies filtering pipeline by assigned workstation."""
		ws_name = "Welding Shop"
		res = get_production_pipeline({"company": self.company, "workstation": ws_name})
		self.assertTrue(res.get("available"))
		for job in res["pipeline_jobs"]:
			job_workstations = [op.get("workstation") for op in job.get("operations", [])]
			self.assertIn(ws_name, job_workstations)
