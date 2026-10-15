"""
DASH-018: Standalone unit test suite for Material Readiness and Shortage logic.
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

if "frappe" not in sys.modules:
	sys.modules["frappe"] = mock_frappe
if "frappe.utils" not in sys.modules:
	sys.modules["frappe.utils"] = mock_frappe.utils

class Row(dict):
	def __getattr__(self, key):
		return self.get(key)
	def __setattr__(self, key, value):
		self[key] = value

# Mock sarathi_visibility.api.access and data_helpers
mock_access = MagicMock()
mock_access.require_capability = MagicMock()
mock_access.deny = MagicMock(side_effect=lambda: (_ for _ in ()).throw(mock_frappe.PermissionError("Access denied")))
mock_access.check_record = MagicMock(side_effect=lambda dt, name, *args: Row(company="SarathiAILabs", customer="Cust1", name=name))
mock_access.has_capability = MagicMock(return_value=True)
mock_access.require_session = MagicMock()

sys.modules["sarathi_visibility.api.access"] = mock_access

# Now import material_readiness
from sarathi_visibility.api.material_readiness import (
	READINESS_FILTER_KEYS,
	READINESS_STATUS_CHOICES,
	get_material_readiness,
	validate_material_readiness_filters,
)


class TestMaterialReadinessLogic(unittest.TestCase):
	def setUp(self):
		mock_frappe.reset_mock()
		mock_access.reset_mock()
		mock_access.deny.side_effect = lambda: (_ for _ in ()).throw(mock_frappe.PermissionError("Access denied"))
		mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))
		mock_frappe.db.exists.return_value = True
		mock_frappe.has_permission.return_value = True
		mock_frappe.get_list.return_value = [Row(name="SarathiAILabs")]

	# -------------------------------------------------------------
	# 1. Strict Validation Tests
	# -------------------------------------------------------------
	def test_filter_allowlist_rejection(self):
		"""Ensures unknown filter keys throw ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_material_readiness_filters({
				"company": "SarathiAILabs",
				"invalid_key_xyz": "hack",
			})

	def test_date_bounds_validation(self):
		"""Ensures from_date > to_date throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_material_readiness_filters({
				"company": "SarathiAILabs",
				"from_date": "2026-12-31",
				"to_date": "2026-01-01",
			})

	def test_unsupported_readiness_choice(self):
		"""Ensures invalid readiness_status choice throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_material_readiness_filters({
				"company": "SarathiAILabs",
				"readiness_status": "FakeReadiness",
			})

	# -------------------------------------------------------------
	# 2. Calculation and Classification Logic Tests
	# -------------------------------------------------------------
	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_work_order_fully_ready(self, mock_get_all):
		"""
		Work Order WO-001 requires:
		- Item A: required=10, transferred=0 -> remaining=10. Bin available=20 (actual=25, res=5) -> Shortage=0.
		- Item B: required=5, transferred=0 -> remaining=5. Bin available=10 -> Shortage=0.
		Expected: Readiness = "Ready", 0 shortages.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(
						name="WO-001",
						production_item="FG-01",
						item_name="Finished Good 1",
						qty=5,
						produced_qty=0,
						stock_uom="Nos",
						status="In Process",
						docstatus=1,
						planned_start_date=date(2026, 10, 10),
						planned_end_date=date(2026, 10, 20),
						expected_delivery_date=date(2026, 10, 20),
						project="PRJ-01",
						sales_order="SO-01",
						source_warehouse="Stores - SL",
						wip_warehouse="Work In Progress - SL",
					)
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-001", item_code="RAW-01", item_name="Raw Material 1", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=10.0, transferred_qty=0.0, consumed_qty=0.0),
					Row(parent="WO-001", item_code="RAW-02", item_name="Raw Material 2", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=5.0, transferred_qty=0.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return [
					Row(item_code="RAW-01", warehouse="Stores - SL", actual_qty=25.0, reserved_qty=5.0, projected_qty=20.0),
					Row(item_code="RAW-02", warehouse="Stores - SL", actual_qty=15.0, reserved_qty=5.0, projected_qty=10.0),
				]
			elif doctype == "Item":
				return [
					Row(name="RAW-01", item_name="Raw Material 1", stock_uom="Nos"),
					Row(name="RAW-02", item_name="Raw Material 2", stock_uom="Nos"),
				]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		self.assertTrue(res["available"])
		self.assertEqual(res["summary"]["ready_work_orders"], 1)
		self.assertEqual(res["summary"]["shortage_work_orders"], 0)
		self.assertEqual(res["summary"]["partially_ready_work_orders"], 0)
		self.assertEqual(len(res["shortage_lines"]), 2)
		self.assertFalse(res["shortage_lines"][0]["has_shortage"])
		self.assertFalse(res["shortage_lines"][1]["has_shortage"])
		self.assertEqual(res["work_orders_readiness"][0]["readiness_status"], "Ready")

	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_work_order_partially_ready(self, mock_get_all):
		"""
		Work Order WO-002 requires:
		- Item A: remaining=10, available=20 -> shortage=0 (Ready).
		- Item B: remaining=5, available=2 -> shortage=3 (Shortage).
		Expected: Readiness = "Partially Ready", 1 shortage line.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(
						name="WO-002",
						production_item="FG-02",
						item_name="Finished Good 2",
						qty=2,
						produced_qty=0,
						stock_uom="Nos",
						status="Not Started",
						docstatus=1,
						planned_start_date=date(2026, 10, 10),
						planned_end_date=date(2026, 10, 25),
						expected_delivery_date=date(2026, 10, 25),
						project=None,
						sales_order=None,
						source_warehouse="Stores - SL",
						wip_warehouse="Work In Progress - SL",
					)
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-002", item_code="RAW-01", item_name="Raw Material 1", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=10.0, transferred_qty=0.0, consumed_qty=0.0),
					Row(parent="WO-002", item_code="RAW-02", item_name="Raw Material 2", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=5.0, transferred_qty=0.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return [
					Row(item_code="RAW-01", warehouse="Stores - SL", actual_qty=20.0, reserved_qty=0.0, projected_qty=20.0),
					Row(item_code="RAW-02", warehouse="Stores - SL", actual_qty=2.0, reserved_qty=0.0, projected_qty=2.0),
				]
			elif doctype == "Item":
				return [
					Row(name="RAW-01", item_name="Raw Material 1", stock_uom="Nos"),
					Row(name="RAW-02", item_name="Raw Material 2", stock_uom="Nos"),
				]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["partially_ready_work_orders"], 1)
		self.assertEqual(res["summary"]["ready_work_orders"], 0)
		self.assertEqual(res["summary"]["shortage_work_orders"], 0)
		self.assertEqual(res["work_orders_readiness"][0]["readiness_status"], "Partially Ready")
		self.assertEqual(res["summary"]["distinct_shortage_items"], 1)
		self.assertEqual(res["summary"]["total_shortage_units"], 3.0)

	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_work_order_complete_shortage(self, mock_get_all):
		"""
		Work Order WO-003 requires:
		- Item A: remaining=10, available=0 (Bin missing or actual=0) -> shortage=10.
		Expected: Readiness = "Shortage".
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(
						name="WO-003",
						production_item="FG-03",
						item_name="Finished Good 3",
						qty=1,
						produced_qty=0,
						stock_uom="Nos",
						status="Not Started",
						docstatus=1,
						planned_start_date=date(2026, 10, 10),
						planned_end_date=date(2026, 10, 12),
						expected_delivery_date=date(2026, 10, 12),
						project=None,
						sales_order=None,
						source_warehouse="Stores - SL",
						wip_warehouse="Work In Progress - SL",
					)
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-003", item_code="RAW-03", item_name="Raw Material 3", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=10.0, transferred_qty=0.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return []  # No bin exists in warehouse
			elif doctype == "Item":
				return [Row(name="RAW-03", item_name="Raw Material 3", stock_uom="Nos")]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["shortage_work_orders"], 1)
		self.assertEqual(res["work_orders_readiness"][0]["readiness_status"], "Shortage")
		self.assertEqual(res["summary"]["critical_shortage_orders"], 1)  # Due in past (Oct 12 vs Oct 14)

	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_cumulative_shared_demand_across_work_orders(self, mock_get_all):
		"""
		Two Work Orders WO-A and WO-B both require RAW-STEEL from 'Stores - SL':
		- WO-A demands 15.
		- WO-B demands 20.
		- Total Demand = 35.
		- Warehouse Bin available = 25.
		- Individual: WO-A can be satisfied alone (available 25 >= 15), WO-B has shortage of 5 alone.
		- Cumulative Net Shortage: max(0, 35 - 25) = 10 units!
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(name="WO-A", production_item="FG-A", item_name="FG A", qty=1, produced_qty=0, stock_uom="Nos", status="In Process", docstatus=1, planned_start_date=date(2026, 10, 10), planned_end_date=date(2026, 10, 20), expected_delivery_date=date(2026, 10, 20), project=None, sales_order=None, source_warehouse="Stores - SL", wip_warehouse="WIP"),
					Row(name="WO-B", production_item="FG-B", item_name="FG B", qty=1, produced_qty=0, stock_uom="Nos", status="In Process", docstatus=1, planned_start_date=date(2026, 10, 10), planned_end_date=date(2026, 10, 20), expected_delivery_date=date(2026, 10, 20), project=None, sales_order=None, source_warehouse="Stores - SL", wip_warehouse="WIP"),
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-A", item_code="RAW-STEEL", item_name="Steel Ingot", source_warehouse="Stores - SL", stock_uom="Kg", required_qty=15.0, transferred_qty=0.0, consumed_qty=0.0),
					Row(parent="WO-B", item_code="RAW-STEEL", item_name="Steel Ingot", source_warehouse="Stores - SL", stock_uom="Kg", required_qty=20.0, transferred_qty=0.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return [
					Row(item_code="RAW-STEEL", warehouse="Stores - SL", actual_qty=30.0, reserved_qty=5.0, projected_qty=25.0),
				]
			elif doctype == "Item":
				return [Row(name="RAW-STEEL", item_name="Steel Ingot", stock_uom="Kg")]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		agg = res["shortage_items_aggregate"]
		self.assertEqual(len(agg), 1)
		self.assertEqual(agg[0]["item_code"], "RAW-STEEL")
		self.assertEqual(agg[0]["total_remaining_demand"], 35.0)
		self.assertEqual(agg[0]["available_stock"], 25.0)
		self.assertEqual(agg[0]["net_shortage"], 10.0)
		self.assertEqual(agg[0]["affected_orders_count"], 2)  # Both WO-A and WO-B are affected by aggregate deficit
		self.assertEqual(agg[0]["affected_work_orders"], ["WO-A", "WO-B"])

	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_work_order_fully_transferred_is_ready(self, mock_get_all):
		"""
		Work Order WO-004 has required_qty=10 and transferred_qty=10.
		Remaining demand = 0.
		Stock in warehouse is 0, but since materials are already transferred to WIP,
		readiness status must be "Ready" and no shortage line created.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(name="WO-004", production_item="FG-04", item_name="FG 4", qty=5, produced_qty=0, stock_uom="Nos", status="In Process", docstatus=1, planned_start_date=date(2026, 10, 10), planned_end_date=date(2026, 10, 20), expected_delivery_date=date(2026, 10, 20), project=None, sales_order=None, source_warehouse="Stores - SL", wip_warehouse="WIP"),
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-004", item_code="RAW-04", item_name="Raw Material 4", source_warehouse="Stores - SL", stock_uom="Nos", required_qty=10.0, transferred_qty=10.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return [Row(item_code="RAW-04", warehouse="Stores - SL", actual_qty=0.0, reserved_qty=0.0, projected_qty=0.0)]
			elif doctype == "Item":
				return [Row(name="RAW-04", item_name="Raw Material 4", stock_uom="Nos")]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["ready_work_orders"], 1)
		self.assertEqual(res["summary"]["shortage_work_orders"], 0)
		self.assertEqual(res["summary"]["total_shortage_lines"], 0)
		self.assertEqual(res["work_orders_readiness"][0]["readiness_status"], "Ready")
		self.assertIn("transferred to WIP", res["work_orders_readiness"][0]["readiness_note"])
		self.assertFalse(res["shortage_lines"][0]["has_shortage"])
		self.assertTrue(res["shortage_lines"][0]["is_fully_transferred"])
		self.assertEqual(res["shortage_lines"][0]["shortage_qty"], 0.0)

		# With shortage_only=1 filter, zero lines should be returned in shortage_lines pool
		res_short = get_material_readiness({"company": "SarathiAILabs", "shortage_only": 1})
		self.assertEqual(len(res_short["shortage_lines"]), 0)

	@patch("sarathi_visibility.api.material_readiness.frappe.get_all")
	def test_unconfigured_warehouse_is_unknown(self, mock_get_all):
		"""
		Work Order WO-005 item has neither item-level nor WO-level source_warehouse configured.
		Status must be classified as "Unknown" with readiness_note indicating missing warehouse.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Work Order":
				return [
					Row(name="WO-005", production_item="FG-05", item_name="FG 5", qty=1, produced_qty=0, stock_uom="Nos", status="Not Started", docstatus=1, planned_start_date=date(2026, 10, 10), planned_end_date=date(2026, 10, 20), expected_delivery_date=date(2026, 10, 20), project=None, sales_order=None, source_warehouse=None, wip_warehouse="WIP"),
				]
			elif doctype == "Work Order Item":
				return [
					Row(parent="WO-005", item_code="RAW-05", item_name="Raw Material 5", source_warehouse=None, stock_uom="Nos", required_qty=5.0, transferred_qty=0.0, consumed_qty=0.0),
				]
			elif doctype == "Bin":
				return []
			elif doctype == "Item":
				return [Row(name="RAW-05", item_name="Raw Material 5", stock_uom="Nos")]
			elif doctype == "Company":
				return ["SarathiAILabs"]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_material_readiness({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["unknown_work_orders"], 1)
		self.assertEqual(res["work_orders_readiness"][0]["readiness_status"], "Unknown")
		self.assertIn("Missing source warehouse", res["work_orders_readiness"][0]["readiness_note"])

	def test_unauthorized_user_blocked(self):
		"""Ensures require_capability denial halts execution."""
		mock_access.require_capability.side_effect = mock_frappe.PermissionError("Forbidden")
		with self.assertRaises(mock_frappe.PermissionError):
			get_material_readiness({"company": "SarathiAILabs"})
		mock_access.require_capability.side_effect = None


if __name__ == "__main__":
	unittest.main(verbosity=2)

