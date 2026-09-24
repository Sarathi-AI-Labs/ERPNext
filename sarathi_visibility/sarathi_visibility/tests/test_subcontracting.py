"""Integration and API unit tests for Subcontracting Control Tower."""

import unittest
import frappe
from sarathi_visibility.api.subcontracting import (
    get_subcontracting_card_summary,
    get_subcontracting_dashboard,
)
from sarathi_visibility.api.dashboard import get_summary


class TestSubcontracting(unittest.TestCase):
    def test_subcontracting_card_summary_structure(self):
        summary = get_subcontracting_card_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("active_subcontracts", summary)
        self.assertIn("material_with_suppliers", summary)
        self.assertIn("pending_subcontracts", summary)
        self.assertIn("currency", summary)
        self.assertIsInstance(summary["active_subcontracts"], int)
        self.assertIsInstance(summary["material_with_suppliers"], (int, float))
        self.assertIsInstance(summary["pending_subcontracts"], int)

    def test_subcontracting_dashboard_structure(self):
        dashboard = get_subcontracting_dashboard()
        self.assertIsInstance(dashboard, dict)

        # Check KPIs
        kpis = dashboard.get("kpis", {})
        expected_kpis = [
            "total_subcontract_orders",
            "active_orders",
            "material_value_at_subcontractors",
            "pending_scrap_reconciliation",
            "orders_pending_delivery",
            "on_time_delivery_rate",
            "total_subcontracting_spend",
            "rejected_rework_quantity",
        ]
        for k in expected_kpis:
            self.assertIn(k, kpis, f"Missing KPI: {k}")

        # Check 7-Stage Pipeline
        pipeline = dashboard.get("pipeline", [])
        self.assertEqual(len(pipeline), 7, "Pipeline must contain exactly 7 lifecycle stages")
        stage_keys = [p["key"] for p in pipeline]
        expected_stages = [
            "po",
            "stock_transfer",
            "sco",
            "in_production",
            "quality_inspection",
            "receipt",
            "billing",
        ]
        self.assertEqual(stage_keys, expected_stages)

        # Check Charts & Analysis payload
        self.assertIn("status_distribution", dashboard)
        self.assertIn("cost_trends", dashboard)
        self.assertIn("supplier_analysis", dashboard)
        self.assertIn("project_analysis", dashboard)
        self.assertIn("materials_with_subcontractors", dashboard)
        self.assertIn("orders", dashboard)
        self.assertIn("attention_required", dashboard)
        self.assertIn("supplier_performance", dashboard)
        self.assertIn("live_activity", dashboard)

    def test_dashboard_get_summary_integration(self):
        summary = get_summary({})
        self.assertIn("subcontracting_summary", summary)
        sub_card = summary["subcontracting_summary"]
        self.assertIn("active_subcontracts", sub_card)
        self.assertIn("material_with_suppliers", sub_card)
        self.assertIn("pending_subcontracts", sub_card)

    def test_subcontracting_filter_handling(self):
        filters = {
            "company": "SarathiAILabs",
            "status": "Open",
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "cost_granularity": "daily",
        }
        res = get_subcontracting_dashboard(filters)
        self.assertEqual(res["filters"]["company"], "SarathiAILabs")
        self.assertEqual(res["filters"]["status"], "Open")
        self.assertEqual(res["filters"]["cost_granularity"], "daily")
