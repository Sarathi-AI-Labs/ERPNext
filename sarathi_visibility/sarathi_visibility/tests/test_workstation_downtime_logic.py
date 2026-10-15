"""
DASH-019: Standalone unit test suite for Workstation and Downtime logic.
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

# Now import workstations module
from sarathi_visibility.api.workstations import (
	WS_FILTER_KEYS,
	WS_VALID_STATUSES,
	get_workstation_downtime,
	validate_workstation_downtime_filters,
)


class TestWorkstationDowntimeLogic(unittest.TestCase):
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
			validate_workstation_downtime_filters({
				"company": "SarathiAILabs",
				"malicious_key": "drop_tables",
			})

	def test_date_bounds_validation(self):
		"""Ensures from_date > to_date throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_workstation_downtime_filters({
				"company": "SarathiAILabs",
				"from_date": "2026-10-31",
				"to_date": "2026-10-01",
			})

	def test_unsupported_status_choice(self):
		"""Ensures invalid status choice throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_workstation_downtime_filters({
				"company": "SarathiAILabs",
				"status": "FakeStatus999",
			})

	def test_unauthorized_user_blocked(self):
		"""Ensures require_capability denial halts execution."""
		mock_access.require_capability.side_effect = mock_frappe.PermissionError("Forbidden")
		with self.assertRaises(mock_frappe.PermissionError):
			get_workstation_downtime({"company": "SarathiAILabs"})
		mock_access.require_capability.side_effect = None

	# -------------------------------------------------------------
	# 2. Workstation Overview & Activity Logic Tests
	# -------------------------------------------------------------
	@patch("sarathi_visibility.api.workstations.frappe.get_all")
	def test_workstation_activity_and_queue_breakdown(self, mock_get_all):
		"""
		Workstation WS-CNC-01 has 3 Job Cards:
		- JC-01: status="Work In Progress", qty=10, completed=4, target=2026-10-20
		- JC-02: status="Open", qty=5, completed=0, target=2026-10-25
		- JC-03: status="Completed", qty=8, completed=8, target=2026-10-10
		Workstation WS-LASER-01 has:
		- JC-04: status="Open", target=2026-10-12 (overdue relative to 2026-10-14!)
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Job Card":
				return [
					Row(name="JC-01", work_order="WO-01", operation="Milling", workstation="WS-CNC-01", workstation_type="CNC", status="Work In Progress", for_quantity=10, total_completed_qty=4, expected_start_date=date(2026, 10, 10), expected_end_date=date(2026, 10, 20), actual_start_date=date(2026, 10, 10), actual_end_date=None, total_time_in_mins=120.0, creation=date(2026, 10, 10)),
					Row(name="JC-02", work_order="WO-02", operation="Facing", workstation="WS-CNC-01", workstation_type="CNC", status="Open", for_quantity=5, total_completed_qty=0, expected_start_date=date(2026, 10, 21), expected_end_date=date(2026, 10, 25), actual_start_date=None, actual_end_date=None, total_time_in_mins=0.0, creation=date(2026, 10, 10)),
					Row(name="JC-03", work_order="WO-01", operation="Finishing", workstation="WS-CNC-01", workstation_type="CNC", status="Completed", for_quantity=8, total_completed_qty=8, expected_start_date=date(2026, 10, 5), expected_end_date=date(2026, 10, 10), actual_start_date=date(2026, 10, 5), actual_end_date=date(2026, 10, 10), total_time_in_mins=240.0, creation=date(2026, 10, 5)),
					Row(name="JC-04", work_order="WO-03", operation="Cutting", workstation="WS-LASER-01", workstation_type="Laser", status="Open", for_quantity=20, total_completed_qty=0, expected_start_date=date(2026, 10, 8), expected_end_date=date(2026, 10, 12), actual_start_date=None, actual_end_date=None, total_time_in_mins=0.0, creation=date(2026, 10, 8)),
				]
			elif doctype == "Work Order":
				return [
					Row(name="WO-01", production_item="FG-PUMP", item_name="Centrifugal Pump", status="In Process", planned_end_date=date(2026, 10, 25), expected_delivery_date=date(2026, 10, 25), project="PROJ-01", customer="Cust-01"),
					Row(name="WO-02", production_item="FG-VALVE", item_name="Globe Valve", status="Not Started", planned_end_date=date(2026, 10, 28), expected_delivery_date=date(2026, 10, 28), project=None, customer=None),
					Row(name="WO-03", production_item="FG-GEAR", item_name="Spur Gear", status="In Process", planned_end_date=date(2026, 10, 12), expected_delivery_date=date(2026, 10, 12), project=None, customer=None),
				]
			elif doctype == "Workstation":
				return [
					Row(name="WS-CNC-01", workstation_name="CNC Milling Center 1", workstation_type="CNC", status="Production", modified=datetime(2026, 10, 14, 10, 0, 0), description="5-axis milling machine"),
					Row(name="WS-LASER-01", workstation_name="Fiber Laser Cutter", workstation_type="Laser", status="Production", modified=datetime(2026, 10, 14, 9, 30, 0), description="2kW fiber laser"),
				]
			elif doctype == "Downtime Entry":
				return []
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_workstation_downtime({"company": "SarathiAILabs"})
		self.assertTrue(res["available"])
		s = res["summary"]
		self.assertEqual(s["total_workstations"], 2)
		self.assertEqual(s["workstations_with_active_jobs"], 1)  # WS-CNC-01 has WIP
		self.assertEqual(s["total_assigned_operations"], 4)
		self.assertEqual(s["recorded_running_jobs"], 1)
		self.assertEqual(s["completed_operations"], 1)
		self.assertEqual(s["delayed_operations_count"], 1)  # JC-04 is delayed (Oct 12 vs Oct 14)
		self.assertEqual(s["recorded_downtime_events"], 0)
		self.assertEqual(s["total_downtime_minutes"], 0.0)

		# Check workstation overview
		cnc = next(w for w in res["workstations_overview"] if w["workstation"] == "WS-CNC-01")
		self.assertEqual(cnc["assigned_job_cards_count"], 3)
		self.assertEqual(cnc["active_job_cards_count"], 1)
		self.assertEqual(cnc["queued_job_cards_count"], 1)
		self.assertEqual(cnc["completed_job_cards_count"], 1)
		self.assertEqual(cnc["delayed_job_cards_count"], 0)

		laser = next(w for w in res["workstations_overview"] if w["workstation"] == "WS-LASER-01")
		self.assertEqual(laser["delayed_job_cards_count"], 1)
		self.assertTrue(laser["has_production_impact"])

		# Verify production impact list
		self.assertEqual(len(res["production_impact"]), 1)
		impact = res["production_impact"][0]
		self.assertEqual(impact["workstation"], "WS-LASER-01")
		self.assertEqual(impact["delayed_jobs_count"], 1)
		self.assertEqual(impact["affected_jobs"][0]["job_card"], "JC-04")

		# Verify unsupported telemetry metrics are explicitly None with informative notes
		self.assertIsNone(cnc["utilization_rate"])
		self.assertIn("Telemetry", cnc["utilization_note"])
		self.assertIsNone(cnc["oee"])
		self.assertIn("Telemetry", cnc["oee_note"])

	# -------------------------------------------------------------
	# 3. Downtime Calculations & Clipping Logic Tests
	# -------------------------------------------------------------
	@patch("sarathi_visibility.api.workstations.frappe.get_all")
	def test_downtime_clipping_and_duration_calculation(self, mock_get_all):
		"""
		Tests valid closed and open Downtime Entry duration calculation:
		- Event 1: Closed event on WS-CNC-01 from 2026-10-14 08:00 to 09:30 (90 mins).
		- Event 2: Open event on WS-CNC-01 from 2026-10-14 11:00 (no to_time).
		  Reference time is 2026-10-14 12:00:00 -> duration = 60 mins.
		Total Downtime = 90 + 60 = 150 mins.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Job Card":
				return [
					Row(name="JC-10", work_order="WO-10", operation="Op1", workstation="WS-CNC-01", workstation_type="CNC", status="Open", for_quantity=5, total_completed_qty=0, expected_start_date=date(2026, 10, 14), expected_end_date=date(2026, 10, 15), actual_start_date=None, actual_end_date=None, total_time_in_mins=0.0, creation=date(2026, 10, 14)),
				]
			elif doctype == "Work Order":
				return [Row(name="WO-10", production_item="FG-10", item_name="FG 10", status="In Process", planned_end_date=date(2026, 10, 15), expected_delivery_date=date(2026, 10, 15), project=None, customer=None)]
			elif doctype == "Workstation":
				return [Row(name="WS-CNC-01", workstation_name="CNC Machine", workstation_type="CNC", status="Problem", modified=datetime(2026, 10, 14, 11, 0, 0), description=None)]
			elif doctype == "Downtime Entry":
				return [
					Row(name="DT-001", workstation="WS-CNC-01", from_time=datetime(2026, 10, 14, 8, 0, 0), to_time=datetime(2026, 10, 14, 9, 30, 0), downtime=90.0, stop_reason="Tool Breakage", remarks="Replaced cutting insert", operator="John"),
					Row(name="DT-002", workstation="WS-CNC-01", from_time=datetime(2026, 10, 14, 11, 0, 0), to_time=None, downtime=0.0, stop_reason="Hydraulic Leak", remarks="Awaiting maintenance tech", operator="Mike"),
				]
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_workstation_downtime({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["recorded_downtime_events"], 2)
		self.assertEqual(res["summary"]["total_downtime_minutes"], 150.0)

		events = res["downtime_events"]
		self.assertEqual(len(events), 2)
		self.assertEqual(events[0]["duration_minutes"], 90.0)
		self.assertFalse(events[0]["is_open"])
		self.assertEqual(events[1]["duration_minutes"], 60.0)  # 11:00 to 12:00
		self.assertTrue(events[1]["is_open"])

		# Production impact should show downtime
		impact = res["production_impact"]
		self.assertEqual(len(impact), 1)
		self.assertEqual(impact[0]["downtime_minutes"], 150.0)
		self.assertIn("Tool Breakage", impact[0]["downtime_reasons"])
		self.assertIn("Hydraulic Leak", impact[0]["downtime_reasons"])

	@patch("sarathi_visibility.api.workstations.frappe.get_all")
	def test_empty_downtime_records_handled_gracefully(self, mock_get_all):
		"""
		Ensures that 0 downtime records returns 0.0 minutes without fabricating downtime.
		"""
		def fake_get_all(doctype, filters=None, **kwargs):
			if doctype == "Job Card":
				return []
			elif doctype == "Work Order":
				return []
			elif doctype == "Workstation":
				return [Row(name="WS-STANDALONE", workstation_name="Standalone Station", workstation_type="Manual", status="Production", modified=None, description=None)]
			elif doctype == "Downtime Entry":
				return []
			return []

		mock_get_all.side_effect = fake_get_all

		res = get_workstation_downtime({"company": "SarathiAILabs"})
		self.assertEqual(res["summary"]["total_downtime_minutes"], 0.0)
		self.assertEqual(res["summary"]["recorded_downtime_events"], 0)
		self.assertEqual(len(res["downtime_events"]), 0)


if __name__ == "__main__":
	unittest.main(verbosity=2)
