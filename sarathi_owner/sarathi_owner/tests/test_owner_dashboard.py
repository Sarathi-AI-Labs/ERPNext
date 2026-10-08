"""Unit and integration tests for Sarathi Owner Dashboard."""

import unittest

import frappe

import sarathi_owner.api.owner_dashboard as od
from sarathi_owner.api.permissions import (
	can_access_owner,
	can_view_finance,
	get_permission_context,
)
from sarathi_owner.api.pipeline import get_project_pipeline


class TestOwnerDashboard(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init("frontend")
		frappe.connect()

	def setUp(self):
		frappe.set_user("Administrator")

	def test_permission_checks(self):
		"""Verify role validation and permission payload."""
		perm = get_permission_context()
		self.assertTrue(perm["is_admin"])
		self.assertTrue(perm["can_access_owner"])
		self.assertTrue(perm["can_view_finance"])

		# Test guest user
		self.assertFalse(can_access_owner("Guest"))
		self.assertFalse(can_view_finance("Guest"))

	def test_owner_summary_aggregation(self):
		"""Verify get_owner_summary returns all executive KPI cards and data structures."""
		summary = od.get_owner_summary({})
		self.assertIn("cards", summary)
		self.assertEqual(len(summary["cards"]), 6)
		card_labels = [c["label"] for c in summary["cards"]]
		self.assertIn("Active Manufacturing Projects", card_labels)
		self.assertIn("Commercial Order Book", card_labels)
		self.assertIn("Accounts Receivable (AR)", card_labels)
		self.assertIn("Inventory Working Capital", card_labels)
		self.assertIn("Total Expenses", card_labels)
		self.assertIn("Net Profit", card_labels)

		self.assertIn("capital_allocation", summary)
		self.assertIn("pipelines", summary)
		self.assertIn("output_trend", summary)
		self.assertIn("action_alerts", summary)
		self.assertIn("live_activity", summary)
		self.assertIsInstance(summary["live_activity"], list)
		self.assertIn("active_projects", summary)
		self.assertIn("financial_snapshot", summary)

	def test_owner_endpoints_reject_users_without_owner_access(self):
		from unittest.mock import patch

		with patch.object(
			od,
			"get_permission_context",
			return_value={
				"can_access_owner": False,
				"can_view_finance": False,
			},
		):
			for call in (od.get_owner_context, od.get_owner_summary, lambda: od.get_page_data("projects")):
				with self.assertRaises(frappe.PermissionError):
					call()

	def test_page_loaders_all_views(self):
		"""Verify that all dedicated owner views return structured executive data."""
		pages = [
			"projects",
			"project_detail",
			"customers",
			"sales_orders",
			"manufacturing",
			"stock_quality",
			"invoicing",
			"payments",
			"financial_reports",
			"accounts_setup",
			"taxes",
			"banking",
			"budget",
			"share_management",
			"subscription",
			"reports",
		]
		for p in pages:
			res = od.get_page_data(p, {})
			self.assertIsInstance(res, dict, f"Page {p} did not return a dictionary")
			self.assertTrue(len(res) > 0, f"Page {p} returned empty payload")

	def test_accounting_modules_all_views(self):
		"""Verify all 9 ERPNext Accounting sidebar modules return cards, shortcuts, and valid tables."""
		accounting_modules = [
			"invoicing",
			"payments",
			"financial_reports",
			"accounts_setup",
			"taxes",
			"banking",
			"budget",
			"share_management",
			"subscription",
		]
		for mod in accounting_modules:
			data = od.get_page_data(mod, {"company": "SarathiAILabs"})
			self.assertIn("cards", data, f"Module {mod} missing KPI cards")
			self.assertTrue(len(data["cards"]) >= 1, f"Module {mod} has no cards")
			self.assertIn("shortcuts", data, f"Module {mod} missing shortcuts")
			self.assertTrue(len(data["shortcuts"]) >= 3, f"Module {mod} has insufficient shortcuts")
			self.assertIn("table", data, f"Module {mod} missing table")
			self.assertIn("headers", data["table"])
			self.assertIn("rows", data["table"])
			if data["table"]["rows"]:
				for row in data["table"]["rows"]:
					self.assertEqual(
						len(row),
						len(data["table"]["headers"]),
						f"Module {mod} row length mismatch with headers",
					)

	def test_reports_page_executive_focus(self):
		"""Verify reports page provides 100% executive reports and excludes shop-floor noise."""
		rep_data = od.get_page_data("reports", {})
		self.assertIn("reports", rep_data)
		rep_titles = [r["title"] for r in rep_data["reports"]]

		# Must include high-level financial, commercial, and project reports
		self.assertIn("Gross and Net Profit Report", rep_titles)
		self.assertIn("Accounts Receivable", rep_titles)
		self.assertIn("Financial Ratios", rep_titles)
		self.assertIn("Sales Order Analysis", rep_titles)
		self.assertIn("Project Summary", rep_titles)
		self.assertIn("Production Analytics", rep_titles)
		self.assertIn("Warehouse Wise Stock Balance", rep_titles)

		# Must NOT include micro-level operator job card reports or BOM stock line breakdowns
		self.assertNotIn("Job Card Summary", rep_titles)
		self.assertNotIn("BOM Stock Report", rep_titles)

	def test_pipeline_states_and_options(self):
		"""Test manufacturing pipeline: 24 distinct industrial process stages across 3 lines of 8 with in-charges."""
		pipe = get_project_pipeline("PROJ-0001")
		self.assertIn("stages", pipe)
		self.assertEqual(len(pipe["stages"]), 24)

		stages_map = {s["id"]: s for s in pipe["stages"]}

		# Check key stages from the 24-step industrial flowchart
		# Line 1 (1-8)
		self.assertIn("lead", stages_map)
		self.assertIn("req_collection", stages_map)
		self.assertIn("tech_eval", stages_map)
		self.assertIn("costing", stages_map)
		self.assertIn("quotation", stages_map)
		self.assertIn("customer_po", stages_map)
		self.assertIn("po_verification", stages_map)
		self.assertIn("sales_order", stages_map)

		# Line 2 (9-16)
		self.assertIn("accounts_approval", stages_map)
		self.assertIn("production_plan", stages_map)
		self.assertIn("bom", stages_map)
		self.assertIn("store_avail", stages_map)
		self.assertIn("purchase_receipt", stages_map)
		self.assertIn("raw_qc", stages_map)
		self.assertIn("laser_cutting", stages_map)
		self.assertIn("bending", stages_map)

		# Line 3 (17-24)
		self.assertIn("cutting_qc", stages_map)
		self.assertIn("welding", stages_map)
		self.assertIn("welding_qc", stages_map)
		self.assertIn("grinding", stages_map)
		self.assertIn("painting", stages_map)
		self.assertIn("final_qc", stages_map)
		self.assertIn("packing", stages_map)
		self.assertIn("documentation_dispatch", stages_map)

		# In-charge verification matching flowchart
		self.assertEqual(stages_map["lead"]["in_charge"], "Sakshi Sawant / Narendra Sir")
		self.assertEqual(stages_map["accounts_approval"]["in_charge"], "Pooja Chougule")
		self.assertEqual(stages_map["welding"]["in_charge"], "Dhashrat Salavi")
		self.assertEqual(stages_map["painting"]["in_charge"], "Babaso Aagale")
		self.assertEqual(stages_map["final_qc"]["in_charge"], "QC / Shrikant Magdum")
		self.assertEqual(stages_map["packing"]["in_charge"], "Logistics Team")
		self.assertEqual(stages_map["documentation_dispatch"]["in_charge"], "Pooja Chougule / Samir Patil")

		# Line 1 vs Lines 2-3 separation metrics
		self.assertIn("line1_completed", pipe)
		self.assertIn("line1_percent", pipe)
		self.assertIn("mfg_total_steps", pipe)
		self.assertEqual(pipe["mfg_total_steps"], 16)
		self.assertIn("mfg_percent", pipe)

	def test_production_manager_dashboard_isolation(self):
		"""Verify that sarathi_visibility production manager dashboard remains 100% operational."""
		import sarathi_visibility.api.dashboard as pm_dash

		pm_data = pm_dash.load()
		self.assertIsInstance(pm_data, dict)
		self.assertIn("projects", pm_data)

	def test_multiple_work_orders_and_stock_entry(self):
		"""Verify multi-WO planned vs produced aggregation and Stock Entry completion rule."""
		try:
			# Create test project using autoname
			proj = frappe.get_doc(
				{
					"doctype": "Project",
					"project_name": "Test Pipeline Multi WO Project",
					"company": "SarathiAILabs",
					"status": "Open",
				}
			).insert(ignore_permissions=True)
			p_name = proj.name

			# Test 1: Project with No Production Plan
			pipe = get_project_pipeline(p_name)
			stages = {s["id"]: s for s in pipe["stages"]}
			self.assertEqual(stages["production_plan"]["status"], "wait")

			# Test 2: Project with Work Order -> Laser Cutting & Welding are triggered
			wo1 = frappe.get_doc(
				{
					"doctype": "Work Order",
					"company": "SarathiAILabs",
					"production_item": "001",
					"qty": 10,
					"produced_qty": 5,
					"project": p_name,
					"status": "In Process",
					"wip_warehouse": "Work In Progress - S",
					"fg_warehouse": "Finished Goods - S",
					"docstatus": 1,
				}
			)
			wo1.flags.ignore_mandatory = True
			wo1.flags.ignore_validate = True
			wo1.insert(ignore_permissions=True)

			pipe = get_project_pipeline(p_name)
			stages = {s["id"]: s for s in pipe["stages"]}
			self.assertEqual(stages["laser_cutting"]["status"], "done")
			self.assertEqual(stages["welding"]["in_charge"], "Dhashrat Salavi")

			# Test 3: Multiple Work Orders aggregation
			wo2 = frappe.get_doc(
				{
					"doctype": "Work Order",
					"company": "SarathiAILabs",
					"production_item": "002",
					"qty": 20,
					"produced_qty": 15,
					"project": p_name,
					"status": "In Process",
					"wip_warehouse": "Work In Progress - S",
					"fg_warehouse": "Finished Goods - S",
					"docstatus": 1,
				}
			)
			wo2.flags.ignore_mandatory = True
			wo2.flags.ignore_validate = True
			wo2.insert(ignore_permissions=True)

			pipe = get_project_pipeline(p_name)
			self.assertEqual(pipe["wo_planned_qty"], 30.0)
			self.assertEqual(pipe["wo_produced_qty"], 20.0)
			self.assertEqual(pipe["manufacturing_progress"], 66.7)

			# Test 4: Manufacture Stock Entry satisfying planned qty completes Final QC
			se = frappe.get_doc(
				{
					"doctype": "Stock Entry",
					"purpose": "Manufacture",
					"company": "SarathiAILabs",
					"project": p_name,
					"work_order": wo1.name,
					"from_warehouse": "Work In Progress - S",
					"to_warehouse": "Finished Goods - S",
					"fg_completed_qty": 30.0,
					"docstatus": 1,
				}
			)
			se.flags.ignore_mandatory = True
			se.flags.ignore_validate = True
			se.insert(ignore_permissions=True)

			pipe = get_project_pipeline(p_name)
			stages = {s["id"]: s for s in pipe["stages"]}
			self.assertEqual(stages["final_qc"]["status"], "done")
			self.assertIn("Passed Final QC", stages["final_qc"]["badge"])

		finally:
			frappe.db.rollback()

	def test_live_report_runner(self):
		"""Verify get_live_report_data executes native ERPNext reports in-memory and returns structured columns and results."""
		# 1. Project Summary Report
		proj_res = od.get_live_report_data("Project Summary", {"company": "SarathiAILabs"})
		self.assertEqual(proj_res["report_name"], "Project Summary")
		self.assertIn("columns", proj_res)
		self.assertIn("result", proj_res)
		self.assertIsInstance(proj_res["columns"], list)
		self.assertTrue(len(proj_res["columns"]) > 0)

		# 2. Accounts Receivable Report
		ar_res = od.get_live_report_data("Accounts Receivable", {"company": "SarathiAILabs"})
		self.assertEqual(ar_res["report_name"], "Accounts Receivable")
		self.assertIn("columns", ar_res)
		self.assertIn("result", ar_res)

		# 3. Profit and Loss Statement Report
		pnl_res = od.get_live_report_data("Profit and Loss Statement", {"company": "SarathiAILabs"})
		self.assertEqual(pnl_res["report_name"], "Profit and Loss Statement")
		self.assertIn("columns", pnl_res)
		self.assertIn("result", pnl_res)

	def test_all_executive_reports_execute_without_error(self):
		for report in od._get_reports_page()["reports"]:
			with self.subTest(report=report["report"]):
				result = od.get_live_report_data(report["report"], {})
				self.assertNotIn("error", result, result.get("error"))
				self.assertTrue(result["columns"])

	def test_live_notifications_wait_for_commit(self):
		from unittest.mock import patch

		from sarathi_visibility.setup.dashboard import notify_dashboard

		with patch.object(frappe, "publish_realtime") as publish:
			doc = frappe._dict(doctype="Sales Invoice", name="private-invoice")
			od.broadcast_live_event(doc)
			notify_dashboard(doc)
			self.assertEqual(publish.call_count, 3)
			for call in publish.call_args_list:
				self.assertEqual(call.kwargs["message"], {})
				self.assertTrue(call.kwargs["after_commit"])

	def test_executive_reports_with_selected_project(self):
		project = frappe.get_all("Project", fields=["name", "company"], limit=1)
		if not project:
			self.skipTest("An existing project is needed")
		for name in (
			"Accounts Receivable",
			"Profit and Loss Statement",
			"Gross and Net Profit Report",
			"Project Summary",
		):
			with self.subTest(report=name):
				result = od.get_live_report_data(
					name,
					{
						"company": project[0].company,
						"project": project[0].name,
						"date_range": "this_year",
						"search": "dashboard search",
					},
				)
				self.assertNotIn("error", result, result.get("error"))
				if name == "Project Summary":
					self.assertTrue(all(row["name"] == project[0].name for row in result["result"]))

	def test_chart_data_generation(self):
		"""Verify that multi-series chart datasets are generated for Frappe Charts."""
		fin_chart = od._get_financial_chart_data("SarathiAILabs")
		self.assertEqual(len(fin_chart["labels"]), 6)
		self.assertEqual(len(fin_chart["datasets"]), 3)
		self.assertEqual(fin_chart["datasets"][0]["name"], "Revenue")
		self.assertEqual(fin_chart["datasets"][1]["name"], "Expenses")
		self.assertEqual(fin_chart["datasets"][2]["name"], "Net Profit")

		cap_chart = od._get_working_capital_chart_data(100.0, 50.0, 75.0)
		self.assertEqual(cap_chart["labels"], ["Raw Materials", "Work In Progress", "Finished Goods"])
		self.assertEqual(cap_chart["datasets"][0]["values"], [100.0, 50.0, 75.0])

		prod_chart = od._get_production_chart_data("SarathiAILabs")
		self.assertEqual(len(prod_chart["labels"]), 6)
		self.assertEqual(len(prod_chart["datasets"]), 2)

	def test_date_bounds_parsing(self):
		"""Verify date range preset calculation."""
		from_d, to_d = od._get_date_bounds("today")
		self.assertIsNotNone(from_d)
		self.assertEqual(from_d, to_d)

		from_d, to_d = od._get_date_bounds("this_month")
		self.assertTrue(from_d.endswith("-01"))
		self.assertIsNotNone(to_d)

		from_d, to_d = od._get_date_bounds("all")
		self.assertIsNone(from_d)
		self.assertIsNone(to_d)
