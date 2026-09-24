"""Integration and API unit tests for Sarathi Accounting Control Tower."""

import unittest

import frappe

from sarathi_visibility.api.accounting import (
    _resolve_period_dates,
    get_accounting_card_summary,
    get_accounting_dashboard,
)
from sarathi_visibility.api.dashboard import get_summary


class TestAccounting(unittest.TestCase):
    def test_period_date_resolution(self):
        # Test default and various presets
        start, end, p_start, p_end = _resolve_period_dates("this_month")
        self.assertTrue(start <= end)
        self.assertTrue(p_start <= p_end)

        start_y, end_y, p_start_y, p_end_y = _resolve_period_dates("this_year")
        self.assertTrue(start_y.endswith("-01-01"))
        self.assertTrue(p_start_y.endswith("-01-01"))

    def test_accounting_card_summary_structure(self):
        summary = get_accounting_card_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("currency", summary)
        self.assertIn("revenue", summary)
        self.assertIn("expense", summary)
        self.assertIn("net_profit", summary)
        self.assertIn("net_margin", summary)
        self.assertIn("receivables", summary)
        self.assertIn("payables", summary)
        self.assertIn("cash_and_bank", summary)
        self.assertIn("budget_used_pct", summary)

        self.assertIsInstance(summary["revenue"], (int, float))
        self.assertIsInstance(summary["expense"], (int, float))
        self.assertIsInstance(summary["net_profit"], (int, float))

    def test_accounting_dashboard_structure(self):
        dashboard = get_accounting_dashboard()
        self.assertIsInstance(dashboard, dict)
        self.assertIn("currency", dashboard)
        self.assertIn("filters", dashboard)
        self.assertIn("period_dates", dashboard)
        self.assertIn("kpis", dashboard)
        self.assertIn("waterfall", dashboard)
        self.assertIn("cash_control", dashboard)
        self.assertIn("ageing", dashboard)
        self.assertIn("trends", dashboard)
        self.assertIn("checklist", dashboard)

        # Verify 9 Core Overview KPIs
        kpis = dashboard["kpis"]
        expected_kpis = [
            "revenue",
            "expense",
            "net_profit",
            "cash_in_hand",
            "bank_balance",
            "receivables",
            "payables",
            "tax_liability",
            "budget_used",
        ]
        for k in expected_kpis:
            self.assertIn(k, kpis, f"Missing KPI: {k}")

        # Verify Waterfall structure (Page 7)
        wf = dashboard["waterfall"]
        expected_wf_fields = [
            "gross_revenue",
            "cogs",
            "gross_profit",
            "gross_margin",
            "operating_expense",
            "operating_profit",
            "finance_cost",
            "tax_expense",
            "net_profit",
            "net_margin",
        ]
        for f in expected_wf_fields:
            self.assertIn(f, wf, f"Missing Waterfall field: {f}")

        # Verify Checklist has 10 standard items
        checklist = dashboard["checklist"]
        self.assertEqual(
            len(checklist), 10, "Month-end checklist should contain 10 items"
        )

    def test_main_dashboard_summary_integration(self):
        res = get_summary()
        self.assertIsInstance(res, dict)
        self.assertIn(
            "accounting_summary", res, "get_summary must include accounting_summary"
        )
        acc_s = res["accounting_summary"]
        self.assertIn("net_profit", acc_s)
        self.assertIn("revenue", acc_s)
