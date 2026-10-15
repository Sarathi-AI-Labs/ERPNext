"""
DASH-021: Standalone unit test suite for Production Exception and Escalation Queue logic.
Executes locally using standard library unittest and unittest.mock without requiring
a live ERPNext site connection.
"""
from datetime import date, datetime
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add sarathi_visibility app root to sys.path
app_root = str(Path(__file__).resolve().parents[2])
if app_root not in sys.path:
	sys.path.insert(0, app_root)

mock_frappe = MagicMock()
mock_frappe.ValidationError = type("ValidationError", (Exception,), {})
mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
mock_frappe.throw = MagicMock(side_effect=lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg)))
mock_frappe.utils.flt = float
mock_frappe.utils.now_datetime = lambda: datetime(2026, 10, 14, 12, 0, 0)
mock_frappe.whitelist = lambda **kwargs: (lambda fn: fn)

class Row(dict):
	def __getattr__(self, key):
		return self.get(key)
	def __setattr__(self, key, value):
		self[key] = value

mock_frappe._dict = Row

if "frappe" not in sys.modules:
	sys.modules["frappe"] = mock_frappe
if "frappe.utils" not in sys.modules:
	sys.modules["frappe.utils"] = mock_frappe.utils

# Mock sarathi_visibility.api.access
mock_access = MagicMock()
mock_access.require_capability = MagicMock()
mock_access.deny = MagicMock(side_effect=lambda: (_ for _ in ()).throw(mock_frappe.PermissionError("Access denied")))
mock_access.check_record = MagicMock(side_effect=lambda dt, name, *args: Row(company="SarathiAILabs", name=name))
mock_access.has_capability = MagicMock(return_value=True)
mock_access.require_session = MagicMock()

sys.modules["sarathi_visibility.api.access"] = mock_access

# Now import production_exceptions module
from sarathi_visibility.api.production_exceptions import (
	EXCEPTION_FILTER_KEYS,
	SEVERITY_RANKS,
	VALID_CATEGORIES,
	VALID_SEVERITIES,
	get_production_exceptions,
	validate_exception_filters,
)


class TestProductionExceptionsLogic(unittest.TestCase):
	def setUp(self):
		mock_frappe.reset_mock()
		mock_access.reset_mock()
		mock_access.deny.side_effect = lambda: (_ for _ in ()).throw(mock_frappe.PermissionError("Access denied"))
		mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))
		mock_frappe.db.exists.return_value = True
		mock_frappe.db.table_exists.return_value = True
		mock_frappe.has_permission.return_value = True
		mock_frappe.get_list.return_value = [Row(name="SarathiAILabs")]

	# -------------------------------------------------------------
	# 1. Strict Validation Tests
	# -------------------------------------------------------------
	def test_filter_allowlist_rejection(self):
		"""Ensures unknown filter keys throw ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_exception_filters({
				"company": "SarathiAILabs",
				"malicious_key": "unauthorized_sql_scan",
			})

	def test_date_bounds_validation(self):
		"""Ensures from_date > to_date throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_exception_filters({
				"company": "SarathiAILabs",
				"from_date": "2026-10-31",
				"to_date": "2026-10-01",
			})

	def test_unsupported_category_choice(self):
		"""Ensures invalid category throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_exception_filters({
				"company": "SarathiAILabs",
				"category": "FictionalCategory",
			})

	def test_unsupported_severity_choice(self):
		"""Ensures invalid severity throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_exception_filters({
				"company": "SarathiAILabs",
				"severity": "EmergencyCriticalMax",
			})

	def test_cross_company_isolation(self):
		"""Ensures Work Order belonging to another company raises PermissionError."""
		mock_access.check_record.side_effect = lambda dt, name, *args: Row(company="OtherCompany", name=name)
		with self.assertRaises(mock_frappe.PermissionError):
			validate_exception_filters({
				"company": "SarathiAILabs",
				"work_order": "WO-2026-0001",
			})

	# -------------------------------------------------------------
	# 2. Exception Generation & Severity Escalation Tests
	# -------------------------------------------------------------
	def test_overdue_work_order_exception_critical(self):
		"""Tests that Work Order overdue by >= 7 days is classified as Critical."""
		mock_jc_meta = MagicMock()
		mock_jc_meta.has_field.return_value = True
		mock_frappe.get_meta.return_value = mock_jc_meta

		sample_wos = [
			Row(name="WO-001", production_item="PART-A", item_name="Part A", status="In Process", planned_end_date="2026-10-01", expected_delivery_date="2026-10-01", qty=10, produced_qty=2),
		]
		mock_frappe.get_all.side_effect = [
			sample_wos,  # Work Order
			[],          # Job Card
		]

		res = get_production_exceptions({
			"company": "SarathiAILabs",
		}, material_readiness={"available": True, "shortage_lines": []}, workstation_downtime={"available": True, "downtime_events": []}, quality_overview={"available": True, "inspections": []}, rework_overview={"available": True, "rework_configured": True, "rework_jobs": []}, subcontracting_overview={"available": True, "orders": []})

		self.assertTrue(res["available"])
		self.assertEqual(res["summary"]["total_open_exceptions"], 1)
		self.assertEqual(res["summary"]["critical_exceptions"], 1)
		exc = res["exceptions"][0]
		self.assertEqual(exc["exception_id"], "EXC-WO-WO-001")
		self.assertEqual(exc["severity"], "Critical")
		self.assertEqual(exc["category"], "Production")
		# 2026-10-14 - 2026-10-01 = 13 days
		self.assertEqual(exc["delay_days"], 13)

	def test_material_shortage_exception_in_process_wo(self):
		"""Tests that a shortage on an In-Process Work Order produces a Critical exception."""
		mock_frappe.get_all.side_effect = [[], []]

		mock_mr = {
			"available": True,
			"shortage_lines": [
				{
					"work_order": "WO-002",
					"item_code": "RAW-STEEL",
					"item_name": "Raw Steel",
					"source_warehouse": "Stores - S",
					"stock_uom": "Kg",
					"shortage_qty": 25.0,
					"required_qty": 50.0,
					"available_stock": 25.0,
					"has_shortage": True,
					"is_time_critical": True,
					"is_overdue": False,
					"target_date": "2026-10-16",
					"days_to_target": 2,
				}
			]
		}

		res = get_production_exceptions({
			"company": "SarathiAILabs",
		}, material_readiness=mock_mr, workstation_downtime={"available": True, "downtime_events": []}, quality_overview={"available": True, "inspections": []}, rework_overview={"available": True, "rework_configured": True, "rework_jobs": []}, subcontracting_overview={"available": True, "orders": []})

		self.assertEqual(res["summary"]["total_open_exceptions"], 1)
		self.assertEqual(res["summary"]["material_exceptions"], 1)
		self.assertEqual(res["summary"]["critical_exceptions"], 1)
		exc = res["exceptions"][0]
		self.assertEqual(exc["exception_id"], "EXC-SHORTAGE-WO-002-RAW-STEEL-Stores - S")
		self.assertEqual(exc["severity"], "Critical")
		self.assertIn("Shortage of 25", exc["title"])

	def test_subcontracting_overdue_exception_critical(self):
		"""Tests that Subcontracting Order overdue by >= 7 days produces a Critical exception."""
		mock_frappe.get_all.side_effect = [[], []]

		mock_sco = {
			"available": True,
			"orders": [
				{
					"subcontracting_order": "SCO-001",
					"purchase_order": "PO-001",
					"supplier": "SUPP-01",
					"supplier_name": "Supplier 1",
					"item_code": "SHAFT-SUB",
					"item_name": "Turned Shaft",
					"stock_uom": "Nos",
					"ordered_qty": 50.0,
					"received_qty": 0.0,
					"outstanding_qty": 50.0,
					"schedule_date": "2026-10-01",
					"days_to_target": -13,
					"is_overdue": True,
				}
			]
		}

		res = get_production_exceptions({
			"company": "SarathiAILabs",
		}, material_readiness={"available": True, "shortage_lines": []}, workstation_downtime={"available": True, "downtime_events": []}, quality_overview={"available": True, "inspections": []}, rework_overview={"available": True, "rework_configured": True, "rework_jobs": []}, subcontracting_overview=mock_sco)

		self.assertEqual(res["summary"]["subcontracting_exceptions"], 1)
		self.assertEqual(res["summary"]["critical_exceptions"], 1)
		exc = res["exceptions"][0]
		self.assertEqual(exc["exception_id"], "EXC-SCO-SCO-001")
		self.assertEqual(exc["severity"], "Critical")
		self.assertEqual(exc["delay_days"], 13)

	def test_deterministic_prioritization_and_deduplication(self):
		"""Ensures multiple exceptions are sorted by severity, delay, due date, and document ID."""
		mock_frappe.get_all.side_effect = [[], []]

		mock_mr = {
			"available": True,
			"shortage_lines": [
				{
					"work_order": "WO-010",
					"item_code": "PART-X",
					"item_name": "Part X",
					"source_warehouse": "Stores",
					"stock_uom": "Nos",
					"shortage_qty": 5.0,
					"has_shortage": True,
					"is_time_critical": False,
					"is_overdue": False,
					"target_date": "2026-10-20",
				}
			]  # High severity
		}

		mock_qo = {
			"available": True,
			"inspections": [
				{
					"name": "QI-001",
					"inspection_type": "Outgoing",
					"item_code": "ASSY-FINAL",
					"item_name": "Final Assembly",
					"stock_uom": "Nos",
					"sample_size": 15,
					"is_rejected": True,
					"report_date": "2026-10-12",
				}
			]  # Critical severity (Outgoing)
		}

		res = get_production_exceptions({
			"company": "SarathiAILabs",
		}, material_readiness=mock_mr, workstation_downtime={"available": True, "downtime_events": []}, quality_overview=mock_qo, rework_overview={"available": True, "rework_configured": True, "rework_jobs": []}, subcontracting_overview={"available": True, "orders": []})

		self.assertEqual(len(res["exceptions"]), 2)
		# 1st item must be Critical (QI-001)
		self.assertEqual(res["exceptions"][0]["severity"], "Critical")
		self.assertEqual(res["exceptions"][0]["exception_id"], "EXC-QI-QI-001")
		# 2nd item must be High (WO-010 shortage)
		self.assertEqual(res["exceptions"][1]["severity"], "High")
		self.assertEqual(res["exceptions"][1]["exception_id"], "EXC-SHORTAGE-WO-010-PART-X-Stores")

	def test_filter_by_category_and_severity(self):
		"""Ensures category and severity filter parameters properly isolate matching exceptions."""
		mock_frappe.get_all.side_effect = [[], []]

		mock_mr = {
			"available": True,
			"shortage_lines": [
				{"work_order": "WO-010", "item_code": "PART-X", "source_warehouse": "Stores", "shortage_qty": 5.0, "has_shortage": True, "is_time_critical": False}
			]
		}
		mock_wsd = {
			"available": True,
			"downtime_events": [
				{"name": "DT-001", "workstation": "WS-01", "duration_mins": 150.0, "is_active_stop": True}
			]
		}

		# Request only Workstation category
		res_ws = get_production_exceptions({
			"company": "SarathiAILabs",
			"category": "Workstation",
		}, material_readiness=mock_mr, workstation_downtime=mock_wsd, quality_overview={"available": True, "inspections": []}, rework_overview={"available": True, "rework_configured": True, "rework_jobs": []}, subcontracting_overview={"available": True, "orders": []})

		self.assertEqual(len(res_ws["exceptions"]), 1)
		self.assertEqual(res_ws["exceptions"][0]["category"], "Workstation")
		self.assertEqual(res_ws["exceptions"][0]["exception_id"], "EXC-DT-DT-001")


if __name__ == "__main__":
	unittest.main()
