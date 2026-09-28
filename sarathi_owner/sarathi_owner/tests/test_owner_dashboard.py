"""Unit and integration tests for Sarathi Owner Dashboard."""

import unittest

import frappe
from frappe.utils import flt

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
            self.assertTrue(
                len(data["shortcuts"]) >= 3, f"Module {mod} has insufficient shortcuts"
            )
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
        """Test manufacturing pipeline stages: optional plans, production execution, stock entries."""
        pipe = get_project_pipeline("PROJ-0001")
        self.assertIn("stages", pipe)
        self.assertEqual(len(pipe["stages"]), 5)

        stages_map = {s["id"]: s for s in pipe["stages"]}

        # Stage 2: Production Plan should be marked optional if not configured
        self.assertEqual(stages_map["production_plan"]["status"], "optional")
        self.assertIn("Optional", stages_map["production_plan"]["badge"])

        # Stage 4: Production Execution should link to Work Order
        self.assertEqual(stages_map["job_card"]["doctype"], "Work Order")
        self.assertEqual(stages_map["job_card"]["label"], "Production Execution")

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

            # Test 1: Project with No Production Plan -> Stage 2 must be 'optional'
            pipe = get_project_pipeline(p_name)
            stages = {s["id"]: s for s in pipe["stages"]}
            self.assertEqual(stages["production_plan"]["status"], "optional")
            self.assertEqual(stages["production_plan"]["badge"], "Optional / Not used")

            # Test 2: Project with Work Order -> Stage 4 is Production Execution
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
            self.assertEqual(stages["job_card"]["status"], "current")
            self.assertEqual(stages["job_card"]["label"], "Production Execution")

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

            # Test 4: Manufacture Stock Entry satisfying planned qty completes Stage 5
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
            self.assertEqual(stages["stock_entry"]["status"], "done")
            self.assertIn("Completed", stages["stock_entry"]["badge"])

        finally:
            frappe.db.rollback()

    def test_live_report_runner(self):
        """Verify get_live_report_data executes native ERPNext reports in-memory and returns structured columns and results."""
        # 1. Project Summary Report
        proj_res = od.get_live_report_data(
            "Project Summary", {"company": "SarathiAILabs"}
        )
        self.assertEqual(proj_res["report_name"], "Project Summary")
        self.assertIn("columns", proj_res)
        self.assertIn("result", proj_res)
        self.assertIsInstance(proj_res["columns"], list)
        self.assertTrue(len(proj_res["columns"]) > 0)

        # 2. Accounts Receivable Report
        ar_res = od.get_live_report_data(
            "Accounts Receivable", {"company": "SarathiAILabs"}
        )
        self.assertEqual(ar_res["report_name"], "Accounts Receivable")
        self.assertIn("columns", ar_res)
        self.assertIn("result", ar_res)

        # 3. Profit and Loss Statement Report
        pnl_res = od.get_live_report_data(
            "Profit and Loss Statement", {"company": "SarathiAILabs"}
        )
        self.assertEqual(pnl_res["report_name"], "Profit and Loss Statement")
        self.assertIn("columns", pnl_res)
        self.assertIn("result", pnl_res)

    def test_chart_data_generation(self):
        """Verify that multi-series chart datasets are generated for Frappe Charts."""
        fin_chart = od._get_financial_chart_data("SarathiAILabs")
        self.assertEqual(len(fin_chart["labels"]), 6)
        self.assertEqual(len(fin_chart["datasets"]), 3)
        self.assertEqual(fin_chart["datasets"][0]["name"], "Revenue")
        self.assertEqual(fin_chart["datasets"][1]["name"], "Expenses")
        self.assertEqual(fin_chart["datasets"][2]["name"], "Net Profit")

        cap_chart = od._get_working_capital_chart_data(100.0, 50.0, 75.0)
        self.assertEqual(
            cap_chart["labels"], ["Raw Materials", "Work In Progress", "Finished Goods"]
        )
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
