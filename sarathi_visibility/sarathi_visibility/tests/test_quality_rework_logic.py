"""
DASH-020: Standalone unit test suite for Quality, Rework, and Subcontracting logic.
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

# Now import quality_rework module
from sarathi_visibility.api.quality_rework import (
	QUALITY_FILTER_KEYS,
	QI_STATUS_CHOICES,
	QI_TYPE_CHOICES,
	get_quality_overview,
	get_rework_overview,
	get_subcontracting_overview,
	validate_quality_rework_filters,
)


class TestQualityReworkLogic(unittest.TestCase):
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
	# 1. Filter Validation Tests
	# -------------------------------------------------------------
	def test_filter_allowlist_rejection(self):
		"""Ensures unknown filter keys throw ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_quality_rework_filters({
				"company": "SarathiAILabs",
				"unauthorized_field": "test",
			})

	def test_date_bounds_validation(self):
		"""Ensures from_date > to_date throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_quality_rework_filters({
				"company": "SarathiAILabs",
				"from_date": "2026-10-31",
				"to_date": "2026-10-01",
			})

	def test_unsupported_status_choice(self):
		"""Ensures invalid status choice throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_quality_rework_filters({
				"company": "SarathiAILabs",
				"status": "NonExistentStatus",
			})

	def test_cross_company_isolation(self):
		"""Ensures Work Order belonging to another company raises PermissionError."""
		mock_access.check_record.side_effect = lambda dt, name, *args: Row(company="OtherCompany", name=name)
		with self.assertRaises(mock_frappe.PermissionError):
			validate_quality_rework_filters({
				"company": "SarathiAILabs",
				"work_order": "WO-2026-0001",
			})

	# -------------------------------------------------------------
	# 2. Quality Overview Logic Tests
	# -------------------------------------------------------------
	def test_quality_overview_passed_failed_calculation(self):
		"""Tests pass/fail metrics, defect groupings, and failure rate percentage."""
		mock_qi_meta = MagicMock()
		mock_qi_meta.has_field.return_value = True
		mock_frappe.get_meta.return_value = mock_qi_meta

		sample_qis = [
			Row(name="QI-001", inspection_type="Incoming", item_code="RAW-STEEL", item_name="Raw Steel", status="Accepted", docstatus=1, sample_size=10, report_date="2026-10-10", inspected_by="Inspector 1"),
			Row(name="QI-002", inspection_type="In Process", item_code="FAB-BRACKET", item_name="Fabricated Bracket", status="Rejected", docstatus=1, sample_size=5, report_date="2026-10-11", inspected_by="Inspector 2"),
			Row(name="QI-003", inspection_type="Incoming", item_code="FAB-BRACKET", item_name="Fabricated Bracket", status="Rejected", docstatus=1, sample_size=3, report_date="2026-10-12", inspected_by="Inspector 1"),
			Row(name="QI-004", inspection_type="Outgoing", item_code="RAW-STEEL", item_name="Raw Steel", status="Draft", docstatus=0, sample_size=8, report_date="2026-10-13", inspected_by="Inspector 2"),
		]
		mock_frappe.get_all.side_effect = [
			sample_qis,  # Query 1: Quality Inspection
			[Row(name="RAW-STEEL", item_name="Raw Steel", stock_uom="Kg"), Row(name="FAB-BRACKET", item_name="Fabricated Bracket", stock_uom="Nos")],  # Query 2: Item
		]

		res = get_quality_overview({"company": "SarathiAILabs"})

		self.assertTrue(res["available"])
		summary = res["summary"]
		self.assertEqual(summary["total_inspections"], 3)  # docstatus == 1
		self.assertEqual(summary["passed_inspections"], 1)
		self.assertEqual(summary["failed_inspections"], 2)
		self.assertEqual(summary["pending_inspections"], 1)  # docstatus == 0
		# Failure rate = 2 / 3 * 100 = 66.7%
		self.assertEqual(summary["failure_rate_percent"], 66.7)
		self.assertEqual(summary["distinct_rejected_items"], 1)

		# Top defect items
		top_defects = res["top_rejected_items"]
		self.assertEqual(len(top_defects), 1)
		self.assertEqual(top_defects[0]["item_code"], "FAB-BRACKET")
		self.assertEqual(top_defects[0]["rejections_count"], 2)
		self.assertEqual(top_defects[0]["sample_units"], 8.0)

	def test_quality_overview_unauthorized_scope(self):
		"""Ensures restricted quality inspection scope returns informative disabled state."""
		mock_frappe.has_permission.return_value = False
		res = get_quality_overview({"company": "SarathiAILabs"})
		self.assertFalse(res["available"])
		self.assertIn("not accessible", res["reason"])

	# -------------------------------------------------------------
	# 3. Rework Overview Logic Tests
	# -------------------------------------------------------------
	def test_rework_overview_corrective_jobs(self):
		"""Tests identification of corrective Job Cards and overdue calculations."""
		mock_jc_meta = MagicMock()
		mock_jc_meta.has_field.side_effect = lambda f: f == "is_corrective_job_card"
		mock_frappe.get_meta.return_value = mock_jc_meta

		sample_rework_jcs = [
			Row(name="JC-CORR-001", work_order="WO-001", operation="Re-welding", workstation="WS-WELD", status="Work In Progress", for_quantity=5, total_completed_qty=2, for_job_card="JC-ORIG-001", quality_inspection="QI-002", expected_end_date="2026-10-10", total_time_in_mins=45),
			Row(name="JC-CORR-002", work_order="WO-001", operation="Grinding", workstation="WS-GRIND", status="Open", for_quantity=3, total_completed_qty=0, for_job_card="JC-ORIG-002", quality_inspection=None, expected_end_date="2026-10-20", total_time_in_mins=0),
			Row(name="JC-CORR-003", work_order="WO-002", operation="Deburring", workstation="WS-DEBURR", status="Completed", for_quantity=2, total_completed_qty=2, for_job_card=None, quality_inspection=None, expected_end_date="2026-10-05", total_time_in_mins=30),
		]
		mock_frappe.get_all.side_effect = [
			sample_rework_jcs,  # Query 1: Corrective Job Cards
			[Row(name="WO-001", production_item="PART-A", item_name="Part A"), Row(name="WO-002", production_item="PART-B", item_name="Part B")],  # Query 2: Work Order
		]

		res = get_rework_overview({"company": "SarathiAILabs"})

		self.assertTrue(res["available"])
		self.assertTrue(res["rework_configured"])
		s = res["summary"]
		self.assertEqual(s["total_rework_jobs"], 3)
		self.assertEqual(s["in_progress_rework"], 1)
		self.assertEqual(s["queued_rework"], 1)
		self.assertEqual(s["completed_rework"], 1)
		# Ref date: 2026-10-14. Expected end: 2026-10-10 and status is WIP -> delayed
		self.assertEqual(s["delayed_rework"], 1)
		self.assertEqual(s["total_rework_units"], 10.0)

	def test_rework_overview_unconfigured_field(self):
		"""Ensures that when is_corrective_job_card field is missing, a truthful note is returned."""
		mock_jc_meta = MagicMock()
		mock_jc_meta.has_field.return_value = False
		mock_frappe.get_meta.return_value = mock_jc_meta

		res = get_rework_overview({"company": "SarathiAILabs"})

		self.assertTrue(res["available"])
		self.assertFalse(res["rework_configured"])
		self.assertIn("not configured with the corrective rework field", res["rework_note"])
		self.assertEqual(res["summary"]["total_rework_jobs"], 0)

	# -------------------------------------------------------------
	# 4. Subcontracting Overview Logic Tests
	# -------------------------------------------------------------
	def test_subcontracting_overview_quantities_and_overdue(self):
		"""Tests order aggregation, quantity reconciliation, and overdue schedule calculation."""
		sample_scos = [
			Row(name="SCO-001", purchase_order="PO-001", supplier="SUPP-ALPHA", supplier_name="Alpha Tech", transaction_date="2026-10-01", schedule_date="2026-10-10", status="Partially Received", docstatus=1, total_qty=100, per_received=60.0),
			Row(name="SCO-002", purchase_order="PO-002", supplier="SUPP-BETA", supplier_name="Beta Forgings", transaction_date="2026-10-05", schedule_date="2026-10-25", status="Open", docstatus=1, total_qty=50, per_received=0.0),
			Row(name="SCO-003", purchase_order=None, supplier="SUPP-ALPHA", supplier_name="Alpha Tech", transaction_date="2026-09-15", schedule_date="2026-09-30", status="Completed", docstatus=1, total_qty=80, per_received=100.0),
		]
		sample_items = [
			Row(parent="SCO-001", item_code="SUB-SHAFT", item_name="Turned Shaft", qty=100, received_qty=60, stock_uom="Nos"),
			Row(parent="SCO-002", item_code="SUB-GEAR", item_name="Machined Gear", qty=50, received_qty=0, stock_uom="Nos"),
			Row(parent="SCO-003", item_code="SUB-SHAFT", item_name="Turned Shaft", qty=80, received_qty=80, stock_uom="Nos"),
		]
		mock_frappe.get_all.side_effect = [
			sample_scos,  # Query 1: Subcontracting Orders
			sample_items,  # Query 2: Subcontracting Order Items
		]

		res = get_subcontracting_overview({"company": "SarathiAILabs"})

		self.assertTrue(res["available"])
		s = res["summary"]
		self.assertEqual(s["total_subcontract_orders"], 3)
		self.assertEqual(s["active_subcontracts"], 2)  # SCO-001 (Partially Received) & SCO-002 (Open)
		self.assertEqual(s["completed_subcontracts"], 1)
		# SCO-001 schedule 2026-10-10 < ref_date 2026-10-14 -> 1 overdue
		self.assertEqual(s["overdue_subcontracts"], 1)
		# Total ordered = 100 + 50 + 80 = 230
		self.assertEqual(s["total_ordered_units"], 230.0)
		# Total received = 60 + 0 + 80 = 140
		self.assertEqual(s["total_received_units"], 140.0)
		# Outstanding = 230 - 140 = 90
		self.assertEqual(s["total_outstanding_units"], 90.0)

		# Verify order line details
		lines = res["orders"]
		self.assertEqual(len(lines), 3)
		line1 = lines[0]
		self.assertEqual(line1["subcontracting_order"], "SCO-001")
		self.assertEqual(line1["ordered_qty"], 100.0)
		self.assertEqual(line1["received_qty"], 60.0)
		self.assertEqual(line1["outstanding_qty"], 40.0)
		self.assertTrue(line1["is_overdue"])


if __name__ == "__main__":
	unittest.main()
