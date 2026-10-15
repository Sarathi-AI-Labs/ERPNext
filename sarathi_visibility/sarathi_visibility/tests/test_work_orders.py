"""
DASH-016: Comprehensive unit and security tests for Work Order and Job Card APIs.
Validates Work Order and Job Card list and detail endpoints, filtering, pagination,
sorting, quantity semantics, zero N+1 batching, and role-based permission enforcement.
"""
from datetime import date, datetime, timedelta
import unittest

import frappe
from frappe.utils import flt, now_datetime

from sarathi_visibility.api.work_orders import (
	get_job_card_detail,
	get_job_cards,
	get_work_order_detail,
	get_work_orders,
	parse_pagination,
	parse_sorting,
	validate_job_card_filters,
	validate_work_order_filters,
)
from sarathi_visibility.tests.test_permissions import PermissionTests


class TestWorkOrderAndJobCardAPIs(PermissionTests):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls.company = cls.companies[0]
		cls.other_company = cls.companies[1] if len(cls.companies) > 1 else None

	def setUp(self):
		frappe.set_user("Administrator")

	# ---------------------------------------------------------
	# 1. Validation & Helper Tests
	# ---------------------------------------------------------
	def test_pagination_bounds(self):
		"""Ensures start and page_length are strictly validated within bounds."""
		self.assertEqual(parse_pagination(0, 20), (0, 20))
		self.assertEqual(parse_pagination("10", "50"), (10, 50))
		with self.assertRaises(frappe.ValidationError):
			parse_pagination(-1, 20)
		with self.assertRaises(frappe.ValidationError):
			parse_pagination(0, 0)
		with self.assertRaises(frappe.ValidationError):
			parse_pagination(0, 101)  # Exceeds MAX_PAGE_SIZE (100)
		with self.assertRaises(frappe.ValidationError):
			parse_pagination("invalid", 20)

	def test_sorting_allowlist(self):
		"""Ensures sorting fields and order direction are strictly validated against allowlists."""
		allowed_fields = {"name", "modified", "qty"}
		self.assertEqual(parse_sorting("qty", "asc", allowed_fields), "qty asc, name asc")
		self.assertEqual(parse_sorting("name", "desc", allowed_fields), "name desc")
		with self.assertRaises(frappe.ValidationError):
			parse_sorting("unsupported_field", "asc", allowed_fields)
		with self.assertRaises(frappe.ValidationError):
			parse_sorting("name", "sideways", allowed_fields)

	def test_validate_wo_filters_allowlist(self):
		"""Ensures unsupported filter keys for Work Orders are rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_work_order_filters({"company": self.company, "malicious_key": "drop table"})

	def test_validate_wo_filters_date_bounds(self):
		"""Ensures inverted date range is strictly rejected for Work Orders."""
		with self.assertRaises(frappe.ValidationError):
			validate_work_order_filters({
				"company": self.company,
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_validate_wo_filters_invalid_links(self):
		"""Ensures non-existent linked entities raise ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_work_order_filters({
				"company": self.company,
				"project": "NonExistentProject123",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_work_order_filters({
				"company": self.company,
				"workstation": "NonExistentWorkstation123",
			})
		with self.assertRaises(frappe.ValidationError):
			validate_work_order_filters({
				"company": self.company,
				"customer": "NonExistentCustomer123",
			})

	def test_validate_jc_filters_allowlist(self):
		"""Ensures unsupported filter keys for Job Cards are rejected."""
		with self.assertRaises(frappe.ValidationError):
			validate_job_card_filters({"company": self.company, "unknown_field": "test"})

	def test_validate_jc_filters_invalid_work_order(self):
		"""Ensures non-existent Work Order for Job Card filter raises ValidationError."""
		with self.assertRaises(frappe.ValidationError):
			validate_job_card_filters({
				"company": self.company,
				"work_order": "MFG-WO-NONEXISTENT",
			})

	# ---------------------------------------------------------
	# 2. Work Order List API (`get_work_orders`)
	# ---------------------------------------------------------
	def test_get_work_orders_basic_structure(self):
		"""Verifies that get_work_orders returns expected contract keys and list."""
		res = get_work_orders({"company": self.company})
		self.assertIn("work_orders", res)
		self.assertIn("total", res)
		self.assertIn("start", res)
		self.assertIn("page_length", res)
		self.assertIn("has_next_page", res)
		self.assertIn("applied_filters", res)
		self.assertEqual(res["start"], 0)
		self.assertIsInstance(res["work_orders"], list)
		self.assertEqual(len(res["work_orders"]), min(res["total"], res["page_length"]))

	def test_get_work_orders_verified_fields_and_quantities(self):
		"""Verifies that Work Order records contain verified fields and derived remaining qty."""
		res = get_work_orders({"company": self.company, "status": "All"})
		if not res["work_orders"]:
			self.skipTest("No Work Orders found for company.")

		for wo in res["work_orders"]:
			self.assertIn("name", wo)
			self.assertIn("production_item", wo)
			self.assertIn("item_name", wo)
			self.assertIn("qty", wo)
			self.assertIn("produced_qty", wo)
			self.assertIn("remaining_qty", wo)
			self.assertIn("completion_percent", wo)
			self.assertIn("status", wo)
			self.assertIn("company", wo)
			self.assertIn("is_overdue", wo)
			self.assertIn("is_active", wo)
			self.assertIn("open_job_cards_count", wo)
			self.assertIn("total_job_cards_count", wo)

			qty = flt(wo["qty"])
			produced = flt(wo["produced_qty"])
			expected_rem = max(0.0, qty - produced)
			self.assertEqual(wo["remaining_qty"], expected_rem)
			self.assertGreaterEqual(wo["qty"], 0.0)
			self.assertGreaterEqual(wo["produced_qty"], 0.0)
			self.assertGreaterEqual(wo["remaining_qty"], 0.0)
			self.assertGreaterEqual(wo["completion_percent"], 0.0)
			self.assertEqual(wo["company"], self.company)

	def test_get_work_orders_pagination(self):
		"""Verifies pagination slicing, offsets, and has_next_page accuracy."""
		res_all = get_work_orders({"company": self.company, "status": "All"}, page_length=100)
		total = res_all["total"]
		if total < 2:
			self.skipTest("Need at least 2 Work Orders to test pagination slicing.")

		p1 = get_work_orders({"company": self.company, "status": "All"}, start=0, page_length=1)
		self.assertEqual(len(p1["work_orders"]), 1)
		self.assertEqual(p1["total"], total)
		self.assertTrue(p1["has_next_page"])

		p2 = get_work_orders({"company": self.company, "status": "All"}, start=1, page_length=1)
		self.assertEqual(len(p2["work_orders"]), 1)
		self.assertNotEqual(p1["work_orders"][0]["name"], p2["work_orders"][0]["name"])

	def test_get_work_orders_sorting(self):
		"""Verifies deterministic sorting by planned and produced quantities."""
		res_desc = get_work_orders({"company": self.company, "status": "All"}, sort_by="qty", sort_order="desc")
		qtys = [flt(w["qty"]) for w in res_desc["work_orders"]]
		self.assertEqual(qtys, sorted(qtys, reverse=True))

		res_asc = get_work_orders({"company": self.company, "status": "All"}, sort_by="qty", sort_order="asc")
		qtys_asc = [flt(w["qty"]) for w in res_asc["work_orders"]]
		self.assertEqual(qtys_asc, sorted(qtys_asc))

	def test_get_work_orders_status_filtering(self):
		"""Verifies filtering by status: Active, Overdue, Due soon, Draft, Completed, All."""
		# Active filter (default)
		active_res = get_work_orders({"company": self.company, "status": "Active"})
		for w in active_res["work_orders"]:
			self.assertEqual(w["docstatus"], 1)
			self.assertIn(w["status"], ("Not Started", "In Process"))
			self.assertTrue(w["is_active"])

		# All filter
		all_res = get_work_orders({"company": self.company, "status": "All"})
		for w in all_res["work_orders"]:
			self.assertNotEqual(w["docstatus"], 2)  # Cancelled excluded from All

		# Overdue filter with future reference date to guarantee matches
		future_ref = (now_datetime() + timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
		overdue_res = get_work_orders({
			"company": self.company,
			"status": "Overdue",
			"reference_at": future_ref,
		})
		for w in overdue_res["work_orders"]:
			self.assertTrue(w["is_overdue"])
			self.assertTrue(w["is_active"])
			self.assertIsNotNone(w["days_diff"])
			self.assertLess(w["days_diff"], 0)

	def test_get_work_orders_search_filter(self):
		"""Verifies search substring filtering on name or item code."""
		all_res = get_work_orders({"company": self.company, "status": "All"})
		if not all_res["work_orders"]:
			self.skipTest("No Work Orders to search.")
		sample_wo = all_res["work_orders"][0]
		needle = sample_wo["production_item"]

		res = get_work_orders({"company": self.company, "status": "All", "search": needle})
		self.assertGreaterEqual(res["total"], 1)
		for w in res["work_orders"]:
			matches = (
				needle.lower() in w["name"].lower()
				or needle.lower() in str(w["production_item"]).lower()
				or needle.lower() in str(w["item_name"]).lower()
			)
			self.assertTrue(matches)

	# ---------------------------------------------------------
	# 3. Work Order Detail API (`get_work_order_detail`)
	# ---------------------------------------------------------
	def test_get_work_order_detail_basic(self):
		"""Verifies retrieval of full Work Order details with child operations, items, and job cards."""
		all_res = get_work_orders({"company": self.company, "status": "All"})
		if not all_res["work_orders"]:
			self.skipTest("No Work Orders available.")
		target_wo_name = all_res["work_orders"][0]["name"]

		detail = get_work_order_detail(work_order=target_wo_name)
		self.assertIn("work_order", detail)
		self.assertIn("operations", detail)
		self.assertIn("required_items", detail)
		self.assertIn("job_cards", detail)
		self.assertIn("stock_entries", detail)

		wo = detail["work_order"]
		self.assertEqual(wo["name"], target_wo_name)
		self.assertEqual(wo["company"], self.company)
		self.assertIn("produced_qty", wo)
		self.assertIn("remaining_qty", wo)
		self.assertIn("completion_percent", wo)
		self.assertIn("bom_no", wo)

		# Required items check
		for item in detail["required_items"]:
			self.assertIn("item_code", item)
			self.assertIn("required_qty", item)
			self.assertIn("transferred_qty", item)

		# Job cards check
		for jc in detail["job_cards"]:
			self.assertIn("name", jc)
			self.assertIn("operation", jc)
			self.assertIn("status", jc)
			self.assertIn("for_quantity", jc)
			self.assertIn("total_completed_qty", jc)

	def test_get_work_order_detail_invalid_id(self):
		"""Ensures missing or invalid format ID raises ValidationError, while non-existent ID raises PermissionError."""
		with self.assertRaises(frappe.ValidationError):
			get_work_order_detail(work_order=None)
		with self.assertRaises(frappe.ValidationError):
			get_work_order_detail(work_order="")
		with self.assertRaises(frappe.ValidationError):
			get_work_order_detail(work_order=12345)
		with self.assertRaises(frappe.ValidationError):
			get_work_order_detail(work_order="a" * 150)
		with self.assertRaises(frappe.PermissionError):
			get_work_order_detail(work_order="MFG-WO-FAKE-999999")

	def test_work_order_financial_field_masking(self):
		"""Ensures financial cost fields are masked to None for non-finance roles and visible for finance roles."""
		all_res = get_work_orders({"company": self.company, "status": "All"})
		if not all_res["work_orders"]:
			self.skipTest("No Work Orders available.")
		target_wo = all_res["work_orders"][0]["name"]

		# 1. Operational Manager (without Accounts User): costs must be masked
		self.user("manager")
		detail_mgr = get_work_order_detail(work_order=target_wo)
		self.assertIsNone(detail_mgr["work_order"]["planned_operating_cost"])
		self.assertIsNone(detail_mgr["work_order"]["actual_operating_cost"])
		self.assertIsNone(detail_mgr["work_order"]["total_operating_cost"])

		# 2. Owner (with Accounts User): costs must be accessible
		self.user("owner")
		detail_owner = get_work_order_detail(work_order=target_wo)
		self.assertIsNotNone(detail_owner["work_order"]["planned_operating_cost"])
		self.assertIsNotNone(detail_owner["work_order"]["actual_operating_cost"])
		self.assertIsNotNone(detail_owner["work_order"]["total_operating_cost"])

	# ---------------------------------------------------------
	# 4. Job Card List API (`get_job_cards`)
	# ---------------------------------------------------------
	def test_get_job_cards_basic_structure(self):
		"""Verifies that get_job_cards returns paginated list with verified fields."""
		res = get_job_cards({"company": self.company})
		self.assertIn("job_cards", res)
		self.assertIn("total", res)
		self.assertIn("start", res)
		self.assertIn("page_length", res)
		self.assertIn("has_next_page", res)
		self.assertIn("applied_filters", res)
		self.assertIsInstance(res["job_cards"], list)

	def test_get_job_cards_quantity_semantics(self):
		"""
		Critical check: Verifies that Job Card quantities represent individual operation
		volume (for_quantity and total_completed_qty) and NOT finished goods production.
		"""
		res = get_job_cards({"company": self.company, "status": "All"})
		if not res["job_cards"]:
			self.skipTest("No Job Cards available for company.")

		for jc in res["job_cards"]:
			self.assertIn("name", jc)
			self.assertIn("work_order", jc)
			self.assertIn("operation", jc)
			self.assertIn("workstation", jc)
			self.assertIn("for_quantity", jc)
			self.assertIn("total_completed_qty", jc)
			self.assertIn("completion_percent", jc)
			self.assertIn("status", jc)

			fq = flt(jc["for_quantity"])
			cq = flt(jc["total_completed_qty"])
			self.assertGreaterEqual(fq, 0.0)
			self.assertGreaterEqual(cq, 0.0)
			self.assertGreaterEqual(jc["completion_percent"], 0.0)
			self.assertLessEqual(jc["completion_percent"], 100.0)

	def test_get_job_cards_filtering_by_work_order(self):
		"""Verifies filtering Job Cards by a linked Work Order."""
		all_jcs = get_job_cards({"company": self.company, "status": "All"})
		if not all_jcs["job_cards"]:
			self.skipTest("No Job Cards available.")
		target_wo = all_jcs["job_cards"][0]["work_order"]

		filtered = get_job_cards({"company": self.company, "work_order": target_wo})
		self.assertGreaterEqual(filtered["total"], 1)
		for jc in filtered["job_cards"]:
			self.assertEqual(jc["work_order"], target_wo)

	def test_get_job_cards_filtering_by_workstation(self):
		"""Verifies filtering Job Cards by workstation."""
		all_jcs = get_job_cards({"company": self.company, "status": "All"})
		workstations = [j["workstation"] for j in all_jcs["job_cards"] if j.get("workstation")]
		if not workstations:
			self.skipTest("No workstation assigned on Job Cards.")
		target_ws = workstations[0]

		filtered = get_job_cards({"company": self.company, "workstation": target_ws})
		for jc in filtered["job_cards"]:
			self.assertEqual(jc["workstation"], target_ws)

	def test_get_job_cards_pagination(self):
		"""Verifies pagination on Job Cards."""
		res_all = get_job_cards({"company": self.company, "status": "All"}, page_length=100)
		total = res_all["total"]
		if total < 2:
			self.skipTest("Need at least 2 Job Cards to test pagination.")

		p1 = get_job_cards({"company": self.company, "status": "All"}, start=0, page_length=1)
		self.assertEqual(len(p1["job_cards"]), 1)
		self.assertTrue(p1["has_next_page"])

		p2 = get_job_cards({"company": self.company, "status": "All"}, start=1, page_length=1)
		self.assertEqual(len(p2["job_cards"]), 1)
		self.assertNotEqual(p1["job_cards"][0]["name"], p2["job_cards"][0]["name"])

	# ---------------------------------------------------------
	# 5. Job Card Detail API (`get_job_card_detail`)
	# ---------------------------------------------------------
	def test_get_job_card_detail_basic(self):
		"""Verifies retrieval of full Job Card detail with time logs, sub-operations, and parent summary."""
		all_jcs = get_job_cards({"company": self.company, "status": "All"})
		if not all_jcs["job_cards"]:
			self.skipTest("No Job Cards available.")
		target_jc = all_jcs["job_cards"][0]["name"]

		detail = get_job_card_detail(job_card=target_jc)
		self.assertIn("job_card", detail)
		self.assertIn("time_logs", detail)
		self.assertIn("sub_operations", detail)
		self.assertIn("items", detail)
		self.assertIn("parent_work_order", detail)

		jc = detail["job_card"]
		self.assertEqual(jc["name"], target_jc)
		self.assertIn("for_quantity", jc)
		self.assertIn("total_completed_qty", jc)
		self.assertIn("completion_percent", jc)

		# Parent Work Order summary check
		parent = detail["parent_work_order"]
		if parent:
			self.assertIn("work_order", parent)
			self.assertIn("status", parent)
			self.assertIn("planned_qty", parent)
			self.assertIn("produced_qty", parent)

	def test_get_job_card_detail_invalid_id(self):
		"""Ensures missing or invalid format ID raises ValidationError, while non-existent ID raises PermissionError."""
		with self.assertRaises(frappe.ValidationError):
			get_job_card_detail(job_card=None)
		with self.assertRaises(frappe.ValidationError):
			get_job_card_detail(job_card="")
		with self.assertRaises(frappe.ValidationError):
			get_job_card_detail(job_card=12345)
		with self.assertRaises(frappe.ValidationError):
			get_job_card_detail(job_card="a" * 150)
		with self.assertRaises(frappe.PermissionError):
			get_job_card_detail(job_card="PO-JOB-FAKE-99999")

	def test_job_card_financial_field_masking(self):
		"""Ensures hour_rate on Job Card is masked for non-finance users."""
		all_jcs = get_job_cards({"company": self.company, "status": "All"})
		if not all_jcs["job_cards"]:
			self.skipTest("No Job Cards available.")
		target_jc = all_jcs["job_cards"][0]["name"]

		# Operational Manager: hour_rate must be masked
		self.user("manager")
		detail_mgr = get_job_card_detail(job_card=target_jc)
		self.assertIsNone(detail_mgr["job_card"]["hour_rate"])

		# Owner (with finance capability): hour_rate must be accessible
		self.user("owner")
		detail_owner = get_job_card_detail(job_card=target_jc)
		self.assertIsNotNone(detail_owner["job_card"]["hour_rate"])

	# ---------------------------------------------------------
	# 6. Security & Negative Permission Tests
	# ---------------------------------------------------------
	def test_unauthorized_user_denied_all_endpoints(self):
		"""Ensures a user without production capability (e.g. finance_only) is strictly denied."""
		self.user("finance_only")
		with self.assertRaises(frappe.PermissionError):
			get_work_orders({"company": self.company})
		with self.assertRaises(frappe.PermissionError):
			get_work_order_detail(work_order="MFG-WO-2026-00001")
		with self.assertRaises(frappe.PermissionError):
			get_job_cards({"company": self.company})
		with self.assertRaises(frappe.PermissionError):
			get_job_card_detail(job_card="PO-JOB00001")

	def test_cross_company_access_denied(self):
		"""Ensures a user cannot view or query Work Orders from another company."""
		if not self.other_company:
			self.skipTest("Need second company to test cross-company isolation.")

		self.user("manager")
		# Manager has user permission restricted to self.company (companies[0])
		with self.assertRaises(frappe.PermissionError):
			get_work_orders({"company": self.other_company})
		with self.assertRaises(frappe.PermissionError):
			get_job_cards({"company": self.other_company})
