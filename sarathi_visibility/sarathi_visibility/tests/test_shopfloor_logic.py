"""
DASH-023: Standalone unit test suite for Shop-Floor Workboard logic.
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
mock_frappe.utils.flt = lambda v, precision=None: float(v or 0.0)
mock_frappe.utils.cint = lambda v: int(v or 0)
mock_frappe.utils.getdate = lambda d: datetime.strptime(str(d), "%Y-%m-%d").date() if d else None
mock_frappe.utils.get_datetime = lambda dt: datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S") if dt else None
mock_frappe.utils.now_datetime = lambda: datetime(2026, 10, 14, 12, 0, 0)
mock_frappe.utils.get_fullname = lambda u: f"Full Name of {u}"
mock_frappe.utils.escape_html = lambda s: str(s)
mock_frappe.whitelist = lambda **kwargs: (lambda fn: fn)

class Row(dict):
	def __getattr__(self, key):
		return self.get(key)
	def __setattr__(self, key, value):
		self[key] = value
	def db_update(self):
		pass

class MockJobCardDoc(Row):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if "time_logs" not in self:
			self.time_logs = []

	def db_set(self, key, value=None):
		if isinstance(key, dict):
			for k, v in key.items():
				self[k] = v
		else:
			self[key] = value

	def append(self, table, row):
		if not isinstance(row, Row):
			row = Row(row)
		if table not in self:
			self[table] = []
		self[table].append(row)
		return row

	def reload(self):
		pass

	def submit(self):
		self.docstatus = 1
		self.status = "Completed"

	def save(self):
		pass

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

# Now import shopfloor module
from sarathi_visibility.api.shopfloor import (
	SHOPFLOOR_FILTER_KEYS,
	VALID_STATUSES,
	complete_job,
	get_assigned_jobs,
	get_current_operation,
	get_next_jobs,
	get_shop_floor_summary,
	get_shopfloor_workboard,
	get_supervisor_team_overview,
	pause_job,
	record_job_progress,
	resolve_supervisor_team_scope,
	resume_job,
	start_job,
	stop_job,
	validate_shopfloor_filters,
)


class TestShopFloorLogic(unittest.TestCase):
	def setUp(self):
		mock_frappe.reset_mock()
		mock_access.reset_mock()
		mock_access.deny.side_effect = lambda: (_ for _ in ()).throw(mock_frappe.PermissionError("Access denied"))
		mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))
		mock_frappe.db.exists.return_value = True
		mock_frappe.db.table_exists.return_value = True
		mock_frappe.has_permission.return_value = True
		mock_frappe.session.user = "operator1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Operator"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"

	# -------------------------------------------------------------
	# 1. Validation & Filter Security Tests
	# -------------------------------------------------------------
	def test_filter_allowlist_rejection(self):
		"""Ensures unknown filter keys throw ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_shopfloor_filters({
				"malicious_key": "drop table tabJobCard",
			})

	def test_invalid_status_filter(self):
		"""Ensures invalid status choice throws ValidationError."""
		with self.assertRaises(mock_frappe.ValidationError):
			validate_shopfloor_filters({
				"status": "FictionalStatusChoice",
			})

	def test_unauthorized_user_blocked(self):
		"""Ensures user lacking both shop and production capabilities is denied."""
		mock_access.has_capability.side_effect = None
		mock_access.has_capability.return_value = False
		with self.assertRaises(mock_frappe.PermissionError):
			validate_shopfloor_filters({})

	# -------------------------------------------------------------
	# 2. Operator Strict Assignment Isolation Tests
	# -------------------------------------------------------------
	def test_operator_receives_only_assigned_jobs(self):
		"""Ensures operator receives only Job Cards explicitly assigned via ToDo."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-001"],  # ToDo lookup: only JC-001 assigned
			[
				Row(
					name="JC-001",
					work_order="WO-001",
					production_item="PART-A",
					item_name="Part A",
					operation="Milling",
					workstation="WS-01",
					status="Open",
					docstatus=1,
					for_quantity=50.0,
					total_completed_qty=0.0,
					transferred_qty=50.0,
					expected_start_date="2026-10-15",
					expected_end_date="2026-10-16",
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				)
			],  # Job Card details
			[],  # Downtime Entry lookup
		]

		res = get_shopfloor_workboard({})
		self.assertTrue(res["available"])
		self.assertEqual(res["summary"]["total_assigned_jobs"], 1)
		self.assertEqual(len(res["assigned_jobs"]), 1)
		self.assertEqual(res["assigned_jobs"][0]["name"], "JC-001")
		self.assertEqual(res["assigned_jobs"][0]["status"], "Open")

	def test_unassigned_operator_returns_unconfigured_reason(self):
		"""Ensures unassigned operator gets 0 jobs and truthful explanation without fake data."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			[],  # ToDo lookup (empty!)
		]

		res = get_shopfloor_workboard({})
		self.assertTrue(res["available"])
		self.assertEqual(res["summary"]["total_assigned_jobs"], 0)
		self.assertEqual(len(res["assigned_jobs"]), 0)
		self.assertIsNotNone(res["unconfigured_reason"])
		self.assertIn("No jobs are currently assigned to you", res["unconfigured_reason"])

	# -------------------------------------------------------------
	# 3. Supervisor Workstation Team Scope Tests
	# -------------------------------------------------------------
	def test_supervisor_receives_workstation_team_jobs(self):
		"""Ensures supervisor receives jobs on workstations granted in User Permission."""
		mock_frappe.session.user = "supervisor1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"

		mock_frappe.permissions.get_user_permissions.return_value = {
			"Workstation": [{"doc": "WS-CNC-01", "applicable_for": "Job Card"}]
		}

		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			[],  # ToDo lookup
			["JC-100", "JC-101"],  # Station jobs lookup
			[
				Row(
					name="JC-100",
					work_order="WO-010",
					production_item="PART-B",
					item_name="Part B",
					operation="Turning",
					workstation="WS-CNC-01",
					status="Work In Progress",
					docstatus=1,
					for_quantity=20.0,
					total_completed_qty=5.0,
					transferred_qty=20.0,
					expected_start_date="2026-10-14",
					expected_end_date="2026-10-14",
					actual_start_date="2026-10-14 09:00:00",
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=60.0,
				),
				Row(
					name="JC-101",
					work_order="WO-010",
					production_item="PART-B",
					item_name="Part B",
					operation="Drilling",
					workstation="WS-CNC-01",
					status="Open",
					docstatus=1,
					for_quantity=20.0,
					total_completed_qty=0.0,
					transferred_qty=20.0,
					expected_start_date="2026-10-15",
					expected_end_date="2026-10-15",
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				),
			],  # Job Card details
			[],  # Downtime Entry lookup
		]

		res = get_shopfloor_workboard({})
		self.assertTrue(res["available"])
		self.assertEqual(res["summary"]["total_assigned_jobs"], 2)
		self.assertEqual(res["summary"]["jobs_in_progress"], 1)
		self.assertEqual(res["summary"]["waiting_jobs"], 1)
		# Current operation must be JC-100 (Work In Progress)
		self.assertIsNotNone(res["current_operation"])
		self.assertEqual(res["current_operation"]["name"], "JC-100")
		self.assertEqual(len(res["active_operations"]), 1)
		self.assertEqual(res["active_operations"][0]["name"], "JC-100")
		self.assertEqual(res["next_queued_job"]["name"], "JC-101")

	def test_multiple_active_operations_all_surfaced(self):
		"""Ensures multiple active operations are all returned in active_operations without arbitrary selection."""
		mock_frappe.session.user = "supervisor1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"

		mock_frappe.permissions.get_user_permissions.return_value = {
			"Workstation": [
				{"doc": "WS-01", "applicable_for": "Job Card"},
				{"doc": "WS-02", "applicable_for": "Job Card"},
			]
		}

		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			[],  # ToDo lookup
			["JC-201", "JC-202"],  # Station jobs lookup
			[
				Row(
					name="JC-201",
					work_order="WO-020",
					operation="Turning",
					workstation="WS-01",
					status="Work In Progress",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=2.0,
					stock_uom="Nos",
				),
				Row(
					name="JC-202",
					work_order="WO-021",
					operation="Milling",
					workstation="WS-02",
					status="Work In Progress",
					docstatus=1,
					for_quantity=25.0,
					total_completed_qty=10.0,
					stock_uom="Nos",
				),
			],
			[],  # Downtime
		]

		res = get_shopfloor_workboard({})
		self.assertEqual(len(res["active_operations"]), 2)
		active_names = {op["name"] for op in res["active_operations"]}
		self.assertEqual(active_names, {"JC-201", "JC-202"})
		self.assertIn("stock_uom", res["active_operations"][0])

	# -------------------------------------------------------------
	# 4. Blocker Detection Tests
	# -------------------------------------------------------------
	def test_blocker_detection_workstation_downtime(self):
		"""Ensures active workstation downtime flags the Job Card with Critical blocker."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-005"],  # ToDo lookup
			[
				Row(
					name="JC-005",
					work_order="WO-005",
					production_item="PART-C",
					item_name="Part C",
					operation="Welding",
					workstation="WS-WELD-01",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					transferred_qty=10.0,
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				)
			],
			[
				Row(
					name="DT-2026-001",
					workstation="WS-WELD-01",
					from_time="2026-10-14 10:00:00",
					to_time=None,  # Active stop!
					downtime_reason="Electrode Failure",
				)
			],  # Active Downtime Entry
		]

		res = get_shopfloor_workboard({})
		self.assertEqual(res["summary"]["blocked_jobs"], 1)
		card = res["assigned_jobs"][0]
		self.assertTrue(card["has_blocker"])
		self.assertEqual(card["blocker"]["type"], "Workstation Downtime")
		self.assertEqual(card["blocker"]["severity"], "Critical")
		self.assertIn("Electrode Failure", card["blocker"]["description"])

	def test_blocker_detection_rework_job(self):
		"""Ensures corrective rework Job Card is identified with Quality Rework blocker."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-RW-01"],  # ToDo lookup
			[
				Row(
					name="JC-RW-01",
					work_order="WO-006",
					production_item="PART-D",
					item_name="Part D",
					operation="Re-machining",
					workstation="WS-02",
					status="Open",
					docstatus=1,
					for_quantity=5.0,
					total_completed_qty=0.0,
					transferred_qty=5.0,
					is_corrective_job_card=1,  # Corrective rework!
					is_paused=0,
					total_time_in_mins=0.0,
				)
			],
			[],  # No downtime
		]

		res = get_shopfloor_workboard({})
		card = res["assigned_jobs"][0]
		self.assertTrue(card["has_blocker"])
		self.assertEqual(card["blocker"]["type"], "Quality Rework")
		self.assertEqual(card["blocker"]["severity"], "High")

	# -------------------------------------------------------------
	# 5. Search Filtering & Overdue Calculation Tests
	# -------------------------------------------------------------
	def test_search_and_overdue_calculations(self):
		"""Tests live search filtering and overdue delay calculation."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-1", "JC-2"],  # ToDo lookup
			[
				Row(
					name="JC-1",
					work_order="WO-100",
					production_item="SHAFT-X",
					item_name="Shaft X",
					operation="Turning",
					workstation="WS-01",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					transferred_qty=10.0,
					expected_end_date="2026-10-01",  # 13 days overdue vs 2026-10-14
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				),
				Row(
					name="JC-2",
					work_order="WO-200",
					production_item="GEAR-Y",
					item_name="Gear Y",
					operation="Cutting",
					workstation="WS-02",
					status="Open",
					docstatus=1,
					for_quantity=20.0,
					total_completed_qty=0.0,
					transferred_qty=20.0,
					expected_end_date="2026-10-20",
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				),
			],
			[],
		]

		# Search for "GEAR"
		res = get_shopfloor_workboard({"search": "GEAR"})
		self.assertEqual(len(res["assigned_jobs"]), 1)
		self.assertEqual(res["assigned_jobs"][0]["name"], "JC-2")

		# Check overdue on JC-1
		mock_frappe.get_all.side_effect = [
			[],
			["JC-1"],
			[
				Row(
					name="JC-1",
					work_order="WO-100",
					production_item="SHAFT-X",
					item_name="Shaft X",
					operation="Turning",
					workstation="WS-01",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					transferred_qty=10.0,
					expected_end_date="2026-10-01",
					is_corrective_job_card=0,
					is_paused=0,
					total_time_in_mins=0.0,
				)
			],
			[],
		]
		res_overdue = get_shopfloor_workboard({})
		jc1 = res_overdue["assigned_jobs"][0]
		self.assertTrue(jc1["is_overdue"])
		self.assertEqual(jc1["delay_days"], 13)

	# -------------------------------------------------------------
	# 6. DASH-024 Granular API Tests: API A, B, C, D
	# -------------------------------------------------------------
	def test_api_a_get_assigned_jobs_pagination_and_sorting(self):
		"""Tests API A: pagination slice, boundary indicators, and sort ordering."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-01", "JC-02", "JC-03"],  # ToDo lookup
			[
				Row(
					name="JC-01",
					work_order="WO-1",
					operation="Turning",
					workstation="WS-1",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-18",
				),
				Row(
					name="JC-02",
					work_order="WO-2",
					operation="Milling",
					workstation="WS-2",
					status="Open",
					docstatus=1,
					for_quantity=20.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-15",
				),
				Row(
					name="JC-03",
					work_order="WO-3",
					operation="Grinding",
					workstation="WS-3",
					status="Open",
					docstatus=1,
					for_quantity=30.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-20",
				),
			],
			[],  # Downtime
		]

		# Page 1: limit 2, sorted by expected_start_date asc
		res1 = get_assigned_jobs(start=0, page_length=2, sort_by="expected_start_date", sort_order="asc")
		self.assertTrue(res1["success"])
		self.assertEqual(res1["total"], 3)
		self.assertEqual(len(res1["jobs"]), 2)
		self.assertTrue(res1["has_next_page"])
		# JC-02 has earliest start date (2026-10-15)
		self.assertEqual(res1["jobs"][0]["name"], "JC-02")
		self.assertEqual(res1["jobs"][1]["name"], "JC-01")

		# Page 2: start=2, page_length=2
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01", "JC-02", "JC-03"],
			[
				Row(
					name="JC-01",
					work_order="WO-1",
					operation="Turning",
					workstation="WS-1",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-18",
				),
				Row(
					name="JC-02",
					work_order="WO-2",
					operation="Milling",
					workstation="WS-2",
					status="Open",
					docstatus=1,
					for_quantity=20.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-15",
				),
				Row(
					name="JC-03",
					work_order="WO-3",
					operation="Grinding",
					workstation="WS-3",
					status="Open",
					docstatus=1,
					for_quantity=30.0,
					total_completed_qty=0.0,
					expected_start_date="2026-10-20",
				),
			],
			[],
		]
		res2 = get_assigned_jobs(start=2, page_length=2, sort_by="expected_start_date", sort_order="asc")
		self.assertEqual(len(res2["jobs"]), 1)
		self.assertFalse(res2["has_next_page"])
		self.assertEqual(res2["jobs"][0]["name"], "JC-03")

	def test_api_b_get_current_operation_with_active_time_log(self):
		"""Tests API B: active operation surfacing and open Job Card Time Log duration."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-WIP-01"],  # ToDo lookup
			[
				Row(
					name="JC-WIP-01",
					work_order="WO-50",
					operation="Assembly",
					workstation="WS-ASSEMBLY-1",
					status="Work In Progress",
					docstatus=1,
					for_quantity=100.0,
					total_completed_qty=20.0,
					stock_uom="Nos",
					actual_start_date="2026-10-14 10:00:00",
				)
			],
			[],  # Downtime
			[
				Row(
					name="TL-001",
					parent="JC-WIP-01",
					from_time="2026-10-14 11:30:00",
					to_time=None,
					employee="EMP-001",
					time_in_mins=0.0,
				)
			],  # Open Job Card Time Log
		]

		res = get_current_operation()
		self.assertTrue(res["success"])
		self.assertTrue(res["has_active_operation"])
		self.assertEqual(res["count"], 1)
		op = res["current_operation"]
		self.assertIsNotNone(op)
		self.assertEqual(op["name"], "JC-WIP-01")
		self.assertIn("active_time_log", op)
		# 12:00:00 - 11:30:00 = 30.0 minutes
		self.assertEqual(op["active_time_log"]["elapsed_mins"], 30.0)
		self.assertEqual(op["active_time_log"]["employee"], "EMP-001")

	def test_api_b_get_current_operation_empty(self):
		"""Tests API B: returns clean empty result when no operations are currently active."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-OPEN-01"],  # ToDo lookup
			[
				Row(
					name="JC-OPEN-01",
					work_order="WO-50",
					operation="Assembly",
					workstation="WS-ASSEMBLY-1",
					status="Open",  # Waiting, not in progress!
					docstatus=1,
					for_quantity=100.0,
					total_completed_qty=0.0,
				)
			],
			[],  # Downtime
		]

		res = get_current_operation()
		self.assertTrue(res["success"])
		self.assertFalse(res["has_active_operation"])
		self.assertEqual(res["count"], 0)
		self.assertIsNone(res["current_operation"])
		self.assertEqual(res["active_operations"], [])

	def test_api_c_get_next_jobs_priority_ordering(self):
		"""Tests API C: upcoming waiting jobs prioritized by expected_start_date and sequence_id."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-SEQ-1", "JC-SEQ-2", "JC-WIP"],  # ToDo lookup
			[
				Row(
					name="JC-SEQ-2",
					work_order="WO-60",
					operation="Finishing",
					status="Open",
					docstatus=1,
					for_quantity=50.0,
					expected_start_date="2026-10-15",
					sequence_id=2,
				),
				Row(
					name="JC-SEQ-1",
					work_order="WO-60",
					operation="Roughing",
					status="Open",
					docstatus=1,
					for_quantity=50.0,
					expected_start_date="2026-10-15",
					sequence_id=1,
				),
				Row(
					name="JC-WIP",
					work_order="WO-60",
					operation="Setup",
					status="Work In Progress",  # In progress, not next waiting!
					docstatus=1,
					for_quantity=50.0,
					expected_start_date="2026-10-14",
					sequence_id=0,
				),
			],
			[],  # Downtime
		]

		res = get_next_jobs(limit=5)
		self.assertTrue(res["success"])
		self.assertEqual(res["total_waiting"], 2)
		self.assertEqual(len(res["next_jobs"]), 2)
		# JC-SEQ-1 (sequence 1) must precede JC-SEQ-2 (sequence 2) for same date
		self.assertEqual(res["next_jobs"][0]["name"], "JC-SEQ-1")
		self.assertEqual(res["next_jobs"][1]["name"], "JC-SEQ-2")
		self.assertIn("ordering_basis", res)

	def test_api_d_get_shop_floor_summary_counts(self):
		"""Tests API D: status counts and blocker counts correctly aggregated."""
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-S1", "JC-S2", "JC-S3", "JC-S4"],  # ToDo lookup
			[
				Row(
					name="JC-S1",
					work_order="WO-1",
					operation="Op1",
					workstation="WS-1",
					status="Work In Progress",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=2.0,
				),
				Row(
					name="JC-S2",
					work_order="WO-1",
					operation="Op2",
					workstation="WS-2",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
				),
				Row(
					name="JC-S3",
					work_order="WO-1",
					operation="Op3",
					workstation="WS-3",
					status="Completed",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=10.0,
				),
				Row(
					name="JC-S4",
					work_order="WO-1",
					operation="Op4",
					workstation="WS-4",
					status="Open",
					docstatus=1,
					for_quantity=10.0,
					total_completed_qty=0.0,
					is_corrective_job_card=1,  # Blocker!
				),
			],
			[],  # Downtime
		]

		res = get_shop_floor_summary()
		self.assertTrue(res["success"])
		summary = res["summary"]
		self.assertEqual(summary["total_assigned_jobs"], 4)
		self.assertEqual(summary["jobs_in_progress"], 1)
		self.assertEqual(summary["waiting_jobs"], 2)
		self.assertEqual(summary["completed_jobs"], 1)
		self.assertEqual(summary["blocked_jobs"], 1)

	# -------------------------------------------------------------
	# 7. DASH-025 Validated Shop-Floor Reporting Actions Tests
	# -------------------------------------------------------------
	def test_action_a_start_job_success(self):
		"""Ensures eligible operator can start an Open Job Card."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Open",
			for_quantity=50.0,
			total_completed_qty=0.0,
			time_logs=[],
			actual_start_date=None,
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup
			["JC-01"],  # ToDo lookup: JC-01 is assigned
		]

		res = start_job("JC-01")
		self.assertTrue(res["success"])
		self.assertEqual(res["job_card"], "JC-01")
		self.assertEqual(res["status"], "Work In Progress")
		self.assertIn("started_at", res)
		self.assertEqual(doc.status, "Work In Progress")
		self.assertEqual(len(doc.time_logs), 1)

	def test_action_a_start_job_idempotency(self):
		"""Ensures repeated start on an already running job returns idempotent success without duplicate logs."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			for_quantity=50.0,
			total_completed_qty=0.0,
			time_logs=[
				Row(
					from_time="2026-10-14 10:00:00",
					to_time=None,  # Open log!
					employee=None,
				)
			],
			actual_start_date="2026-10-14 10:00:00",
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		res = start_job("JC-01")
		self.assertTrue(res["success"])
		self.assertTrue(res.get("idempotent"))
		self.assertEqual(len(doc.time_logs), 1)

	def test_action_a_start_job_rejects_cancelled_or_submitted(self):
		"""Ensures starting a cancelled or submitted Job Card throws ValidationError."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=1,  # Submitted
			status="Completed",
			for_quantity=50.0,
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		with self.assertRaises(mock_frappe.ValidationError):
			start_job("JC-01")

	def test_action_a_start_job_rejects_unassigned_job(self):
		"""Ensures operator cannot start a Job Card not assigned to them."""
		doc = MockJobCardDoc(
			name="JC-OTHER",
			docstatus=0,
			status="Open",
			for_quantity=50.0,
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-MINE"],  # Operator is only assigned JC-MINE!
		]

		with self.assertRaises(mock_frappe.PermissionError):
			start_job("JC-OTHER")

	def test_action_b_record_job_progress_success(self):
		"""Ensures operator can record progress on an active Job Card."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			for_quantity=100.0,
			total_completed_qty=20.0,
			stock_uom="Nos",
			time_logs=[
				Row(
					from_time="2026-10-14 10:00:00",
					to_time=None,
					employee=None,
					completed_qty=0.0,
				)
			],
			remarks="",
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		res = record_job_progress("JC-01", completed_qty=15.0, remarks="Passes dimensions")
		self.assertTrue(res["success"])
		self.assertEqual(res["reported_qty"], 15.0)
		self.assertEqual(res["total_completed_qty"], 35.0)
		self.assertEqual(res["remaining_qty"], 65.0)
		self.assertEqual(res["completion_percent"], 35.0)

	def test_action_b_record_job_progress_rejects_negative_or_excessive(self):
		"""Ensures negative quantities or excessive values are rejected with ValidationError."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			for_quantity=10.0,
			total_completed_qty=0.0,
			time_logs=[],
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		with self.assertRaises(mock_frappe.ValidationError):
			record_job_progress("JC-01", completed_qty=-5.0)

		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]
		with self.assertRaises(mock_frappe.ValidationError):
			record_job_progress("JC-01", completed_qty=500.0)

	def test_action_c_pause_and_resume_job(self):
		"""Ensures pause and resume transitions update is_paused and status with idempotency."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			is_paused=0,
			time_logs=[Row(from_time="2026-10-14 10:00:00", to_time=None)],
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		# Pause
		res_pause = pause_job("JC-01")
		self.assertTrue(res_pause["success"])
		self.assertEqual(res_pause["status"], "On Hold")
		self.assertTrue(res_pause["is_paused"])

		# Idempotent pause
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]
		res_pause2 = pause_job("JC-01")
		self.assertTrue(res_pause2.get("idempotent"))

		# Resume
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]
		res_resume = resume_job("JC-01")
		self.assertTrue(res_resume["success"])
		self.assertEqual(res_resume["status"], "Work In Progress")
		self.assertFalse(res_resume["is_paused"])

	def test_action_c_stop_job_cycle(self):
		"""Ensures stop_job closes active time log and records completed quantity."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			for_quantity=20.0,
			total_completed_qty=5.0,
			time_logs=[Row(from_time="2026-10-14 10:00:00", to_time=None)],
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		res = stop_job("JC-01", completed_qty=5.0)
		self.assertTrue(res["success"])
		self.assertEqual(res["total_completed_qty"], 10.0)
		self.assertEqual(res["status"], "Open")

	def test_action_d_complete_job_success(self):
		"""Ensures complete_job completes quantities and submits Job Card."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=0,
			status="Work In Progress",
			for_quantity=50.0,
			total_completed_qty=40.0,
			work_order="WO-01",
			stock_uom="Nos",
			time_logs=[],
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]
		mock_frappe.db.get_value.return_value = "In Process"  # Work Order status

		res = complete_job("JC-01", completed_qty=10.0, auto_submit=True)
		self.assertTrue(res["success"])
		self.assertEqual(res["status"], "Completed")
		self.assertEqual(res["docstatus"], 1)
		self.assertEqual(res["total_completed_qty"], 50.0)

	def test_action_d_complete_job_rejects_invalid_state_and_negative_qty(self):
		"""Ensures complete_job rejects cancelled docs and negative quantities."""
		doc = MockJobCardDoc(
			name="JC-01",
			docstatus=2,  # Cancelled
			status="Cancelled",
			for_quantity=50.0,
			total_completed_qty=0.0,
		)
		mock_frappe.get_doc.return_value = doc
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]

		with self.assertRaises(mock_frappe.ValidationError):
			complete_job("JC-01", completed_qty=10.0)

		# Negative quantity check
		doc.docstatus = 0
		doc.status = "Work In Progress"
		mock_frappe.get_all.side_effect = [
			[],
			["JC-01"],
		]
		with self.assertRaises(mock_frappe.ValidationError):
			complete_job("JC-01", completed_qty=-10.0)

	# -------------------------------------------------------------
	# 7. DASH-026 Supervisor Team Overview Tests
	# -------------------------------------------------------------
	def test_supervisor_overview_unauthorized_operator_denied(self):
		"""Ensures an operator without supervisor or production role is strictly denied."""
		mock_frappe.session.user = "operator1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Operator"]
		mock_access.has_capability.side_effect = lambda cap, u=None: False
		with self.assertRaises(mock_frappe.PermissionError):
			get_supervisor_team_overview({})

	def test_supervisor_overview_unconfigured_supervisor_returns_reason(self):
		"""Ensures supervisor without direct reports, workstations, or JCs gets unconfigured reason."""
		mock_frappe.session.user = "supervisor1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"
		mock_frappe.permissions.get_user_permissions.return_value = {}
		mock_frappe.get_all.side_effect = [
			[],  # Employee lookup for supervisor
			[],  # ToDo lookup
		]

		res = get_supervisor_team_overview({})
		self.assertTrue(res["success"])
		self.assertIsNotNone(res["unconfigured_reason"])
		self.assertIn("No team members or permitted workstations", res["unconfigured_reason"])
		self.assertEqual(res["team_summary"]["total_team_members"], 0)
		self.assertEqual(len(res["team_workload"]), 0)

	def test_supervisor_overview_with_direct_reports_and_workload(self):
		"""Ensures supervisor overview computes correct KPIs, workload breakdown, and status."""
		mock_frappe.session.user = "supervisor1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"
		mock_frappe.permissions.get_user_permissions.return_value = {}

		mock_frappe.get_all.side_effect = [
			[Row(name="EMP-SUP", employee_name="Supervisor Sam", department="Production", designation="Supervisor", company="SarathiAILabs")],  # Supervisor Emp
			[
				Row(name="EMP-01", employee_name="Operator Alice", user_id="alice@example.com", department="Production", designation="Operator"),
				Row(name="EMP-02", employee_name="Operator Bob", user_id="bob@example.com", department="Production", designation="Operator"),
			],  # Direct reports
			[],  # ToDo for supervisor
			["JC-101", "JC-102"],  # Job cards for EMP-01 and EMP-02
			[],  # Rep todos
			[],  # Active TLS on JC-101, JC-102
			[],  # JC todos
			[
				Row(
					name="JC-101",
					work_order="WO-01",
					production_item="PART-1",
					item_name="Part 1",
					operation="Turning",
					workstation="WS-LATH-01",
					workstation_type="Lathe",
					status="Work In Progress",
					docstatus=1,
					company="SarathiAILabs",
					for_quantity=100.0,
					total_completed_qty=40.0,
					transferred_qty=100.0,
					stock_uom="Nos",
					expected_start_date="2026-10-14",
					expected_end_date="2026-10-18",
					actual_start_date="2026-10-14",
					actual_end_date=None,
					total_time_in_mins=120.0,
					is_paused=0,
					is_corrective_job_card=0,
					quality_inspection=None,
					sequence_id=1,
					creation="2026-10-14 08:00:00",
					modified="2026-10-14 09:00:00",
					employee="EMP-01",
				),
				Row(
					name="JC-102",
					work_order="WO-02",
					production_item="PART-2",
					item_name="Part 2",
					operation="Milling",
					workstation="WS-MILL-01",
					workstation_type="Mill",
					status="Open",
					docstatus=1,
					company="SarathiAILabs",
					for_quantity=50.0,
					total_completed_qty=0.0,
					transferred_qty=50.0,
					stock_uom="Nos",
					expected_start_date="2026-10-15",
					expected_end_date="2026-10-19",
					actual_start_date=None,
					actual_end_date=None,
					total_time_in_mins=0.0,
					is_paused=0,
					is_corrective_job_card=0,
					quality_inspection=None,
					sequence_id=1,
					creation="2026-10-14 08:30:00",
					modified="2026-10-14 08:30:00",
					employee="EMP-02",
				),
			],  # Job Card details
			[],  # Downtime Entry lookup
			[],  # open_tls
		]

		res = get_supervisor_team_overview({})
		self.assertTrue(res["success"])
		summary = res["team_summary"]
		self.assertEqual(summary["total_team_members"], 2)
		self.assertEqual(summary["operators_active"], 1)  # Alice is working
		self.assertEqual(summary["operators_with_jobs"], 2)  # Alice + Bob
		self.assertEqual(summary["operators_without_work"], 0)
		self.assertEqual(summary["active_job_cards"], 1)
		self.assertEqual(summary["waiting_job_cards"], 1)

		# Workload checks
		workload = res["team_workload"]
		self.assertEqual(len(workload), 2)
		alice = next(w for w in workload if w["employee_name"] == "Operator Alice")
		bob = next(w for w in workload if w["employee_name"] == "Operator Bob")

		self.assertEqual(alice["workload_status"], "Working")
		self.assertEqual(alice["in_progress_count"], 1)
		self.assertIsNotNone(alice["active_operation"])
		self.assertEqual(alice["active_operation"]["job_card"], "JC-101")

		self.assertEqual(bob["workload_status"], "Assigned")
		self.assertEqual(bob["waiting_count"], 1)
		self.assertIsNone(bob["active_operation"])

	def test_supervisor_overview_multiple_active_jobs_surfaces_blocker(self):
		"""Ensures an operator with multiple active WIP jobs triggers a Workload Alert."""
		mock_frappe.session.user = "supervisor1@example.com"
		mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]
		mock_access.has_capability.side_effect = lambda cap, u=None: cap == "shop"
		mock_frappe.permissions.get_user_permissions.return_value = {}

		mock_frappe.get_all.side_effect = [
			[Row(name="EMP-SUP", employee_name="Supervisor Sam", department="Production", designation="Supervisor", company="SarathiAILabs")],
			[Row(name="EMP-01", employee_name="Busy Operator", user_id="busy@example.com", department="Production", designation="Operator")],
			[],
			["JC-A", "JC-B"],
			[],
			[],
			[],
			[
				Row(
					name="JC-A",
					work_order="WO-01",
					production_item="PART-A",
					item_name="Part A",
					operation="Cutting",
					workstation="WS-01",
					workstation_type="Cutter",
					status="Work In Progress",
					docstatus=1,
					company="SarathiAILabs",
					for_quantity=10.0,
					total_completed_qty=2.0,
					transferred_qty=10.0,
					stock_uom="Nos",
					expected_start_date="2026-10-14",
					expected_end_date="2026-10-18",
					actual_start_date="2026-10-14",
					actual_end_date=None,
					total_time_in_mins=30.0,
					is_paused=0,
					is_corrective_job_card=0,
					quality_inspection=None,
					sequence_id=1,
					creation="2026-10-14 08:00:00",
					modified="2026-10-14 09:00:00",
					employee="EMP-01",
				),
				Row(
					name="JC-B",
					work_order="WO-02",
					production_item="PART-B",
					item_name="Part B",
					operation="Welding",
					workstation="WS-02",
					workstation_type="Welder",
					status="Work In Progress",
					docstatus=1,
					company="SarathiAILabs",
					for_quantity=20.0,
					total_completed_qty=5.0,
					transferred_qty=20.0,
					stock_uom="Nos",
					expected_start_date="2026-10-14",
					expected_end_date="2026-10-18",
					actual_start_date="2026-10-14",
					actual_end_date=None,
					total_time_in_mins=45.0,
					is_paused=0,
					is_corrective_job_card=0,
					quality_inspection=None,
					sequence_id=1,
					creation="2026-10-14 08:30:00",
					modified="2026-10-14 09:30:00",
					employee="EMP-01",
				),
			],
			[],
			[],
		]

		res = get_supervisor_team_overview({})
		self.assertTrue(res["success"])
		self.assertTrue(res["team_workload"][0]["has_multiple_active"])
		self.assertEqual(res["team_workload"][0]["in_progress_count"], 2)

		alert = next((b for b in res["blockers"] if b["type"] == "Multiple Active Operations"), None)
		self.assertIsNotNone(alert)
		self.assertEqual(alert["severity"], "High")
		self.assertIn("Busy Operator", alert["title"])


if __name__ == "__main__":
	unittest.main()

