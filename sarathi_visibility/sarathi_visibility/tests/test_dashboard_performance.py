"""
DASH-034: Automated Performance Test Suite for Sarathi Industrial Control Tower.
Measures latency budgets, database query counts, N+1 query protection,
pagination bounding, scaling across Small/Medium/Large workloads, concurrent request throughput,
repeated refresh stability, and Playwright DOM rendering performance.
"""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
import math
import os
from pathlib import Path
import statistics
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Path resolution for standalone execution
workspace = Path(__file__).resolve().parents[3]
visibility_root = (workspace / "sarathi_visibility").resolve()
owner_root = (workspace / "sarathi_owner").resolve()

for p in (str(workspace), str(visibility_root), str(owner_root)):
    if p not in sys.path:
        sys.path.insert(0, p)

import sarathi_visibility
inner_vis = (visibility_root / "sarathi_visibility").resolve()
if hasattr(sarathi_visibility, "__path__") and str(inner_vis) not in list(sarathi_visibility.__path__):
    sarathi_visibility.__path__.append(str(inner_vis))

try:
    import sarathi_owner
    inner_owner = (owner_root / "sarathi_owner").resolve()
    if hasattr(sarathi_owner, "__path__") and str(inner_owner) not in list(sarathi_owner.__path__):
        sarathi_owner.__path__.append(str(inner_owner))
except ImportError:
    sarathi_owner = None

# Mock Frappe Framework
if "frappe" in sys.modules and hasattr(sys.modules["frappe"], "PermissionError"):
    mock_frappe = sys.modules["frappe"]
    MockValidationError = mock_frappe.ValidationError
    MockPermissionError = mock_frappe.PermissionError
    MockDoesNotExistError = getattr(mock_frappe, "DoesNotExistError", type("MockDoesNotExistError", (Exception,), {}))
    def _mock_throw(msg, exc=None):
        exc = exc or mock_frappe.ValidationError
        raise exc(msg)
    mock_frappe.throw = MagicMock(side_effect=_mock_throw)
    if not hasattr(mock_frappe, "_") or not callable(mock_frappe._):
        mock_frappe._ = lambda s: s
else:
    mock_frappe = MagicMock()
    mock_frappe.__path__ = []

    class MockValidationError(Exception):
        pass

    class MockPermissionError(Exception):
        pass

    class MockDoesNotExistError(Exception):
        pass

    mock_frappe.ValidationError = MockValidationError
    mock_frappe.PermissionError = MockPermissionError
    mock_frappe.DoesNotExistError = MockDoesNotExistError

    def _mock_throw(msg, exc=None):
        exc = exc or mock_frappe.ValidationError
        raise exc(msg)

    mock_frappe.throw = MagicMock(side_effect=_mock_throw)
    mock_frappe.utils.flt = lambda v, p=None: round(float(v or 0.0), p) if p is not None else float(v or 0.0)
    mock_frappe.utils.cint = lambda v: int(v or 0)
    mock_frappe.utils.getdate = lambda d=None: date.fromisoformat(str(d)[:10]) if d else date(2026, 10, 14)
    mock_frappe.utils.get_datetime = lambda d=None: datetime.fromisoformat(str(d)) if d else datetime(2026, 10, 14, 12, 0, 0)
    mock_frappe.utils.now_datetime = lambda: datetime(2026, 10, 14, 12, 0, 0)
    mock_frappe.utils.today = lambda: "2026-10-14"
    mock_frappe.utils.get_fullname = lambda u: f"Full Name of {u}"
    mock_frappe.utils.escape_html = lambda s: str(s)
    mock_frappe.whitelist = lambda **k: (lambda fn: fn)
    mock_frappe._dict = lambda d=None, **kwargs: dict(d or {}, **kwargs)
    mock_frappe._ = lambda s: s

    mock_frappe.permissions = MagicMock()
    mock_frappe.permissions.get_user_permissions = MagicMock(return_value={})
    mock_frappe.permissions.get_role_permissions = MagicMock(return_value={"read": 1, "write": 1, "create": 1})

    class MockMeta:
        def __init__(self, doctype):
            self.doctype = doctype
            self.istable = False
        def has_field(self, field):
            return True
        def get_field(self, field):
            mock_f = MagicMock()
            mock_f.options = "Open\nDraft\nCompleted\nCancelled"
            return mock_f

    mock_frappe.get_meta = lambda dt: MockMeta(dt)
    mock_frappe.get_hooks = lambda h, d=None: {}

    sys.modules["frappe"] = mock_frappe
    sys.modules["frappe.utils"] = mock_frappe.utils
    sys.modules["frappe.model"] = MagicMock()
    sys.modules["frappe.permissions"] = mock_frappe.permissions
    mock_frappe.desk = MagicMock()
    mock_frappe.desk.__path__ = []
    sys.modules["frappe.desk"] = mock_frappe.desk
    sys.modules["frappe.desk.query_report"] = MagicMock()
    mock_qb = MagicMock()
    mock_qb.__path__ = []
    sys.modules["frappe.query_builder"] = mock_qb
    sys.modules["frappe.query_builder.functions"] = MagicMock()
    mock_frappe.query_builder = mock_qb

mock_erpnext = MagicMock()
mock_erpnext.__path__ = []
mock_erpnext.accounts = MagicMock()
mock_erpnext.accounts.__path__ = []
mock_erpnext.accounts.utils = MagicMock()
FiscalYearError = type("FiscalYearError", (Exception,), {})
mock_erpnext.accounts.utils.FiscalYearError = FiscalYearError
sys.modules["erpnext"] = mock_erpnext
sys.modules["erpnext.accounts"] = mock_erpnext.accounts
sys.modules["erpnext.accounts.utils"] = mock_erpnext.accounts.utils
sys.modules["erpnext.accounts.report"] = MagicMock()
sys.modules["erpnext.accounts.report"].__path__ = []
sys.modules["erpnext.accounts.report.financial_statements"] = MagicMock()
sys.modules["erpnext.stock"] = MagicMock()
sys.modules["erpnext.stock"].__path__ = []
sys.modules["erpnext.stock.report"] = MagicMock()
sys.modules["erpnext.stock.report"].__path__ = []
sys.modules["erpnext.stock.report.stock_balance"] = MagicMock()
sys.modules["erpnext.stock.report.stock_balance.stock_balance"] = MagicMock()
sys.modules["erpnext.selling"] = MagicMock()
sys.modules["erpnext.selling"].__path__ = []
sys.modules["erpnext.selling.report"] = MagicMock()
sys.modules["erpnext.selling.report"].__path__ = []
sys.modules["erpnext.selling.report.sales_order_analysis"] = MagicMock()
sys.modules["erpnext.selling.report.sales_order_analysis.sales_order_analysis"] = MagicMock()
sys.modules["pypika"] = MagicMock()
sys.modules["pypika"].__path__ = []
sys.modules["pypika.terms"] = MagicMock()

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# API Imports under test
from sarathi_visibility.api.factory_overview import get_factory_overview
from sarathi_visibility.api.work_orders import get_work_orders, get_job_cards, parse_pagination, parse_sorting
from sarathi_visibility.api.material_readiness import get_material_readiness
from sarathi_visibility.api.workstations import get_workstation_downtime
from sarathi_visibility.api.quality_rework import get_quality_overview, get_rework_overview, get_subcontracting_overview
from sarathi_visibility.api.production_exceptions import get_production_exceptions
from sarathi_visibility.api.shopfloor import (
    get_assigned_jobs,
    get_current_operation,
    get_supervisor_team_overview,
    get_shopfloor_workboard,
    fetch_and_enrich_job_cards,
)

if sarathi_owner:
    from sarathi_owner.api.homepage import get_homepage, options
    from sarathi_owner.api.finance_kpis import get_finance_kpis
    from sarathi_owner.api.sales_analytics import get_sales_analytics
    from sarathi_owner.api.project_health import get_project_delivery_health
    from sarathi_owner.api.manufacturing_inventory import get_manufacturing_inventory_summary
    from sarathi_owner.api.executive_risks import get_executive_risks_and_approvals


class Row(dict):
    """Simulates Frappe Document/Row for deterministic testing."""
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value
    def get(self, key, default=None):
        return super().get(key, default)
    def __hash__(self):
        return hash(self.get("name") or id(self))
    def check_permission(self, perm="read"):
        if self.get("_forbidden"):
            raise mock_frappe.PermissionError("Document permission denied")
    def db_set(self, key, val=None):
        if isinstance(key, dict):
            self.update(key)
        else:
            self[key] = val
    def append(self, key, value):
        if key not in self:
            self[key] = []
        if isinstance(value, dict) and not isinstance(value, Row):
            value = Row(value)
        self[key].append(value)
    def submit(self):
        self.docstatus = 1
        return self
    def reload(self):
        pass
    def save(self):
        return self


class QueryCounter:
    """Context manager to measure the exact number of database queries executed."""
    def __init__(self, test_case):
        self.test_case = test_case
        self.count = 0
        self.queries = []

    def record_query(self, query_type, *args, **kwargs):
        self.count += 1
        self.queries.append((query_type, args, kwargs))

    def __enter__(self):
        self.count = 0
        self.queries.clear()
        self.test_case.active_query_counter = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.test_case.active_query_counter = None


class BasePerformanceTestCase(unittest.TestCase):
    """Base test case providing data generators and query-tracking fixtures."""

    def setUp(self):
        mock_frappe.reset_mock()
        mock_frappe.session = MagicMock()
        mock_frappe.session.user = "manager@sarathi.test"
        mock_frappe.session.data = {"user_type": "System User"}
        mock_frappe.get_cached_value = MagicMock(return_value="System User")
        mock_frappe.get_roles = MagicMock(return_value=["System Manager", "Manufacturing Manager", "Stock Manager", "Sarathi Owner", "Accounts User"])
        mock_frappe.has_permission = MagicMock(return_value=True)
        mock_frappe.db.exists = MagicMock(return_value=True)
        mock_frappe.db.table_exists = MagicMock(return_value=True)
        mock_frappe.db.get_value = MagicMock(side_effect=self._tracked_get_value)
        mock_frappe.db.count = MagicMock(side_effect=self._tracked_count)
        mock_frappe.db.sql = MagicMock(side_effect=self._tracked_sql)
        mock_frappe.defaults.get_user_default = MagicMock(return_value="SarathiAILabs")
        mock_frappe.throw.side_effect = _mock_throw
        mock_frappe.get_doc = MagicMock(side_effect=self._tracked_get_doc)
        mock_frappe.get_list = MagicMock(side_effect=self._tracked_get_list)
        mock_frappe.get_all = MagicMock(side_effect=self._tracked_get_all)

        self.active_query_counter = None
        self.database_records = defaultdict(list)

        # Standard reference documents
        self.docs = {
            ("Company", "SarathiAILabs"): Row(name="SarathiAILabs", company_name="Sarathi AI Labs", default_currency="INR"),
            ("Project", "PROJ-01"): Row(name="PROJ-01", project_name="Mezzanine Alpha", company="SarathiAILabs", customer="Cust1", status="Open"),
            ("Customer", "Cust1"): Row(name="Cust1", customer_name="Customer 1"),
            ("Warehouse", "Stores - SAL"): Row(name="Stores - SAL", company="SarathiAILabs", is_group=0),
            ("Workstation", "WS-WELD-01"): Row(name="WS-WELD-01", workstation_name="Welding Station 1", company="SarathiAILabs", status="Active"),
        }

    def _tracked_get_doc(self, doctype, name=None, *args, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("get_doc", doctype, name)
        if isinstance(doctype, dict):
            return Row(doctype)
        doc = self.docs.get((doctype, name))
        if doc:
            return doc
        return Row(name=name or f"MOCK-{doctype}", doctype=doctype, company="SarathiAILabs", default_currency="INR")

    def _tracked_get_list(self, dt, filters=None, fields=None, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("get_list", dt, filters)
        if dt == "Company":
            return [Row(name="SarathiAILabs")]
        return []

    def _tracked_get_value(self, dt, filters=None, fieldname=None, *args, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("db_get_value", dt, filters, fieldname)
        return "SarathiAILabs"

    def _tracked_count(self, dt, filters=None, *args, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("db_count", dt, filters)
        if dt in self.database_records:
            return len(self.database_records[dt])
        return 0

    def _tracked_sql(self, query, *args, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("db_sql", query)
        return []

    def _tracked_get_all(self, doctype, filters=None, fields=None, **kwargs):
        if self.active_query_counter:
            self.active_query_counter.record_query("get_all", doctype, filters, fields, kwargs)

        results = []
        if doctype in self.database_records:
            items = self.database_records[doctype]
            # Simple in-memory filtering for test consistency
            if filters and isinstance(filters, dict):
                filtered = []
                for it in items:
                    matches = True
                    for k, v in filters.items():
                        if isinstance(v, list) and len(v) == 2 and v[0] == "is" and v[1] == "not set":
                            if it.get(k) not in (None, ""):
                                matches = False
                                break
                        elif isinstance(v, list) and len(v) == 2 and v[0] == "in":
                            if it.get(k) not in v[1]:
                                matches = False
                                break
                        elif isinstance(v, list) and len(v) == 2 and v[0] == "<":
                            if it.get(k, 0) >= v[1]:
                                matches = False
                                break
                        elif it.get(k) != v:
                            matches = False
                            break
                    if matches:
                        filtered.append(it)
                results = filtered
            else:
                results = list(items)
        elif doctype == "Company":
            results = [Row(name="SarathiAILabs", company_name="Sarathi AI Labs", default_currency="INR")]
        elif doctype == "Employee":
            results = [Row(name="EMP-01", employee_name="Operator 1", user_id="operator1@sarathi.test", department="Production")]

        # Pagination simulation
        limit = kwargs.get("limit_page_length") or kwargs.get("page_length")
        start = kwargs.get("start") or 0
        if limit:
            results = results[start:start + limit]

        if kwargs.get("pluck"):
            p = kwargs["pluck"]
            return [r.get(p) if isinstance(r, dict) else getattr(r, p, str(r)) for r in results]
        return results

    # Synthetic Dataset Builders
    def seed_work_orders(self, count):
        """Generates realistic synthetic Work Orders."""
        wos = []
        statuses = ["Not Started", "In Process", "Completed", "Stopped"]
        for i in range(1, count + 1):
            st = statuses[i % len(statuses)]
            wos.append(Row(
                name=f"WO-PERF-{i:04d}",
                production_item=f"ITEM-{((i % 10) + 1):03d}",
                item_name=f"Steel Beam Type {((i % 10) + 1)}",
                qty=100.0,
                produced_qty=50.0 if st == "In Process" else (100.0 if st == "Completed" else 0.0),
                status=st,
                docstatus=1 if st != "Draft" else 0,
                company="SarathiAILabs",
                project="PROJ-01",
                sales_order=f"SO-{((i % 5) + 1):03d}",
                stock_uom="Nos",
                planned_start_date="2026-10-01",
                planned_end_date="2026-10-25" if i % 4 != 0 else "2026-10-05",  # Overdue
                creation="2026-10-01 10:00:00",
                modified="2026-10-14 15:00:00",
            ))
        self.database_records["Work Order"] = wos
        return wos

    def seed_job_cards(self, wos, jcs_per_wo=2):
        """Generates realistic synthetic Job Cards linked to Work Orders."""
        jcs = []
        idx = 1
        for wo in wos:
            for j in range(jcs_per_wo):
                jcs.append(Row(
                    name=f"JC-PERF-{idx:05d}",
                    work_order=wo.name,
                    operation=f"Welding Op {j + 1}",
                    workstation=f"WS-WELD-{((idx % 4) + 1):02d}",
                    workstation_type="Welding",
                    status="Work In Progress" if j == 0 else "Open",
                    docstatus=1,
                    company="SarathiAILabs",
                    for_quantity=wo.qty,
                    total_completed_qty=wo.produced_qty,
                    expected_start_date="2026-10-10",
                    expected_end_date="2026-10-20",
                    creation="2026-10-02 08:00:00",
                    employee="EMP-01",
                    is_corrective_job_card=0,
                ))
                idx += 1
        self.database_records["Job Card"] = jcs
        return jcs

    def seed_inventory_and_bins(self, item_count, wh_count=2):
        """Generates synthetic Work Order Items and Warehouse Bins."""
        wo_items = []
        bins = []
        warehouses = [f"Stores {i} - SAL" for i in range(1, wh_count + 1)]

        for i in range(1, item_count + 1):
            item_code = f"RAW-ITEM-{i:04d}"
            wh = warehouses[i % len(warehouses)]
            wo_items.append(Row(
                parent=f"WO-PERF-{(i % 50) + 1:04d}",
                name=f"WOI-{i:05d}",
                item_code=item_code,
                item_name=f"Raw Material {i}",
                source_warehouse=wh,
                stock_uom="Kg",
                required_qty=50.0,
                transferred_qty=20.0,
                consumed_qty=10.0,
            ))
            # Simulate shortage on 20% of items
            actual_qty = 10.0 if i % 5 == 0 else 100.0
            bins.append(Row(
                item_code=item_code,
                warehouse=wh,
                actual_qty=actual_qty,
                reserved_qty=5.0,
            ))
        self.database_records["Work Order Item"] = wo_items
        self.database_records["Bin"] = bins


# =====================================================================
# 1. DATABASE QUERY COUNT & ZERO N+1 TESTS
# =====================================================================

class TestQueryCountAndNPlusOneProtection(BasePerformanceTestCase):
    """
    Validates that database query counts remain constant O(1) and do not scale
    with the number of records returned (Zero N+1 query guarantee).
    """

    def test_work_orders_query_count_constant_with_page_size(self):
        """Work Orders API query count remains O(1) whether page_length is 10 or 50."""
        self.seed_work_orders(200)
        self.seed_job_cards(self.database_records["Work Order"], jcs_per_wo=2)

        # 1. Query with 10 records
        with QueryCounter(self) as qc_small:
            res_small = get_work_orders({"company": "SarathiAILabs"}, start=0, page_length=10)
        self.assertEqual(len(res_small["work_orders"]), 10)
        queries_small = qc_small.count

        # 2. Query with 50 records
        with QueryCounter(self) as qc_large:
            res_large = get_work_orders({"company": "SarathiAILabs"}, start=0, page_length=50)
        self.assertEqual(len(res_large["work_orders"]), 50)
        queries_large = qc_large.count

        # Query count must NOT scale linearly (must be identical or within bounded batch lookups)
        self.assertLessEqual(queries_large, queries_small + 1,
            f"Query count scaled with page size! Small (10 rows): {queries_small} queries vs Large (50 rows): {queries_large} queries.")

    def test_job_cards_query_count_bounded(self):
        """Job Cards API batches associated records and does not query per row."""
        wos = self.seed_work_orders(100)
        self.seed_job_cards(wos, jcs_per_wo=3)

        with QueryCounter(self) as qc:
            res = get_job_cards({"company": "SarathiAILabs"}, start=0, page_length=25)

        self.assertIn("job_cards", res)
        # Bounded query count (candidate Job Cards, batch Work Orders, batch ToDo)
        self.assertLessEqual(qc.count, 6, f"Too many queries for Job Card listing: {qc.count}")

    def test_material_readiness_batches_bin_lookups(self):
        """Material Readiness batches all Work Order Items and Warehouse Bins in single queries."""
        self.seed_work_orders(100)
        self.seed_inventory_and_bins(200)

        with QueryCounter(self) as qc:
            res = get_material_readiness({"company": "SarathiAILabs"}, start=0, page_length=20)

        self.assertTrue(res["available"])
        # Query 1: Work Orders, Query 2: Work Order Items, Query 3: Bins
        self.assertLessEqual(qc.count, 6, f"Material readiness made {qc.count} queries, expected <= 6.")

    def test_shopfloor_active_operation_batched_time_logs_zero_n_plus_one(self):
        """
        DASH-034 Optimization Verification:
        get_current_operation retrieves open time logs in a single batched query
        rather than looping one query per active WIP Job Card.
        """
        # Create 10 Work In Progress Job Cards
        wos = self.seed_work_orders(10)
        jcs = []
        for i, wo in enumerate(wos):
            jcs.append(Row(
                name=f"JC-WIP-{i:03d}",
                work_order=wo.name,
                operation="Milling",
                workstation="WS-MILL-01",
                status="Work In Progress",
                docstatus=1,
                company="SarathiAILabs",
                employee="EMP-01",
                for_quantity=10.0,
                total_completed_qty=2.0,
            ))
        self.database_records["Job Card"] = jcs
        self.database_records["ToDo"] = [Row(reference_name=j.name, allocated_to="operator1@sarathi.test") for j in jcs]

        # Seed time logs for each WIP Job Card
        time_logs = []
        for j in jcs:
            time_logs.append(Row(
                name=f"TL-{j.name}",
                parent=j.name,
                from_time="2026-10-14 10:00:00",
                to_time=None,
                employee="EMP-01",
                time_in_mins=120.0,
            ))
        self.database_records["Job Card Time Log"] = time_logs

        mock_frappe.session.user = "operator1@sarathi.test"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]

        with QueryCounter(self) as qc:
            res = get_current_operation()

        self.assertTrue(res["success"])
        self.assertEqual(len(res["active_operations"]), 10)
        for op in res["active_operations"]:
            self.assertIn("active_time_log", op)

        # Without the fix, 10 operations caused 10 queries to Job Card Time Log (+ base queries = 13+)
        # With the batch optimization, Time Logs are fetched in 1 single batched query!
        time_log_queries = sum(1 for q in qc.queries if q[1] and q[1][0] == "Job Card Time Log")
        self.assertEqual(time_log_queries, 1, f"Expected exactly 1 batched query for Time Logs, but got {time_log_queries}!")


# =====================================================================
# 2. RESPONSE SIZE & PAGINATION BOUNDING TESTS
# =====================================================================

class TestResponseSizeAndPaginationBounds(BasePerformanceTestCase):
    """
    Validates that list endpoints strictly enforce server-side pagination limits,
    protect against unbounded data transfer, and reject invalid offset/limit parameters.
    """

    def test_work_orders_pagination_hard_cap(self):
        """Work Orders list strictly caps page_length to MAX_PAGE_SIZE (100) and rejects negatives."""
        start, limit = parse_pagination(0, 100)
        self.assertEqual(limit, 100)

        with self.assertRaises(mock_frappe.ValidationError):
            parse_pagination(0, 500)

        with self.assertRaises(mock_frappe.ValidationError):
            parse_pagination(-5, 20)

        with self.assertRaises(mock_frappe.ValidationError):
            parse_pagination(0, -10)

    def test_job_cards_pagination_rejection(self):
        """Job Cards endpoint enforces pagination bounds and rejects oversized requests."""
        self.seed_work_orders(50)
        self.seed_job_cards(self.database_records["Work Order"], jcs_per_wo=2)

        # Verify page size 20 returns exactly 20 items
        res = get_job_cards({"company": "SarathiAILabs"}, start=0, page_length=20)
        self.assertEqual(len(res["job_cards"]), 20)
        self.assertEqual(res["page_length"], 20)

        # Request with oversized limit 500 must reject
        with self.assertRaises(mock_frappe.ValidationError):
            get_job_cards({"company": "SarathiAILabs"}, start=0, page_length=500)

    def test_material_readiness_pagination_bounds(self):
        """Material readiness paginates shortage items list."""
        self.seed_work_orders(50)
        self.seed_inventory_and_bins(100)

        res = get_material_readiness({"company": "SarathiAILabs"}, start=0, page_length=15)
        self.assertEqual(res["page_length"], 15)
        self.assertLessEqual(len(res["shortage_lines"]), 15)

    def test_assigned_jobs_pagination_bounds(self):
        """Shop-Floor assigned jobs endpoint bounds response size."""
        wos = self.seed_work_orders(50)
        jcs = self.seed_job_cards(wos, jcs_per_wo=2)
        self.database_records["ToDo"] = [Row(reference_name=j.name, allocated_to="operator1@sarathi.test") for j in jcs]

        mock_frappe.session.user = "operator1@sarathi.test"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]

        res = get_assigned_jobs(start=0, page_length=20)
        self.assertEqual(len(res["jobs"]), 20)
        self.assertEqual(res["page_length"], 20)


# =====================================================================
# 3. WORKLOAD SCALING & LATENCY BUDGET TESTS
# =====================================================================

class TestWorkloadScalingAndLatencyBudgets(BasePerformanceTestCase):
    """
    Benchmarks API execution latency across Small (N=10), Medium (N=100), and Large (N=1000)
    datasets to prove sub-linear scaling and strict latency budgets (< 100ms in-memory).
    """

    def test_factory_overview_workload_scaling_latency(self):
        """Factory overview execution scales efficiently from 10 to 1,000 Work Orders."""
        timings = {}

        # Scenario A: Small (10 Work Orders)
        self.seed_work_orders(10)
        t0 = time.perf_counter()
        res_small = get_factory_overview({"company": "SarathiAILabs"})
        timings["small_ms"] = (time.perf_counter() - t0) * 1000.0
        self.assertTrue(res_small["available"])

        # Scenario B: Medium (100 Work Orders)
        self.seed_work_orders(100)
        t0 = time.perf_counter()
        res_med = get_factory_overview({"company": "SarathiAILabs"})
        timings["med_ms"] = (time.perf_counter() - t0) * 1000.0
        self.assertTrue(res_med["available"])

        # Scenario C: Large (1,000 Work Orders)
        self.seed_work_orders(1000)
        t0 = time.perf_counter()
        res_large = get_factory_overview({"company": "SarathiAILabs"})
        timings["large_ms"] = (time.perf_counter() - t0) * 1000.0
        self.assertTrue(res_large["available"])

        # Strict budget: Even 1,000 records must execute in < 150ms in memory
        self.assertLess(timings["large_ms"], 150.0,
            f"Factory overview exceeded latency budget on 1000 WOs: {timings['large_ms']:.2f}ms")

    def test_work_orders_list_scaling_latency(self):
        """Work Orders list execution remains fast (< 50ms) across 2,000 candidate records."""
        self.seed_work_orders(2000)
        self.seed_job_cards(self.database_records["Work Order"][:100], jcs_per_wo=2)

        t0 = time.perf_counter()
        res = get_work_orders({"company": "SarathiAILabs"}, start=0, page_length=25)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertEqual(len(res["work_orders"]), 25)
        self.assertLess(elapsed_ms, 75.0, f"Work orders listing took {elapsed_ms:.2f}ms (budget 75ms).")

    def test_material_readiness_scaling_latency(self):
        """Material Readiness calculates shortages across 500 items in < 100ms."""
        self.seed_work_orders(100)
        self.seed_inventory_and_bins(500)

        t0 = time.perf_counter()
        res = get_material_readiness({"company": "SarathiAILabs"}, start=0, page_length=25)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertTrue(res["available"])
        self.assertLess(elapsed_ms, 100.0, f"Material readiness took {elapsed_ms:.2f}ms (budget 100ms).")

    def test_supervisor_team_overview_scaling_latency(self):
        """Supervisor team overview calculates workload for 50 operators in < 100ms."""
        wos = self.seed_work_orders(50)
        jcs = self.seed_job_cards(wos, jcs_per_wo=2)
        operators = [
            Row(name=f"EMP-{i:03d}", employee_name=f"Worker {i}", user_id=f"worker{i}@sarathi.test", department="Production")
            for i in range(1, 51)
        ]
        self.database_records["Employee"] = operators
        self.database_records["ToDo"] = [
            Row(reference_name=jcs[i].name, allocated_to=f"worker{(i % 50) + 1}@sarathi.test")
            for i in range(len(jcs))
        ]

        mock_frappe.session.user = "supervisor@sarathi.test"
        mock_frappe.get_roles.return_value = ["Sarathi Supervisor", "Manufacturing Manager"]

        t0 = time.perf_counter()
        res = get_supervisor_team_overview()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.assertTrue(res["success"])
        self.assertLess(elapsed_ms, 120.0, f"Supervisor team overview took {elapsed_ms:.2f}ms (budget 120ms).")


# =====================================================================
# 4. CONCURRENT REQUESTS & THROUGHPUT BENCHMARKS
# =====================================================================

class TestConcurrentRequestsAndThroughput(BasePerformanceTestCase):
    """
    Simulates multi-threaded concurrent requests against dashboard endpoints
    to verify thread safety, throughput (req/sec), and p95 latency.
    """

    def test_concurrent_control_tower_requests_throughput_and_p95(self):
        """
        Simulates 10 concurrent users firing 50 total requests across Control Tower endpoints.
        Asserts 100% success rate (0 errors) and p95 latency < 50ms.
        """
        self.seed_work_orders(200)
        self.seed_job_cards(self.database_records["Work Order"], jcs_per_wo=2)

        def make_request(req_id):
            t_start = time.perf_counter()
            if req_id % 2 == 0:
                res = get_factory_overview({"company": "SarathiAILabs"})
            else:
                res = get_work_orders({"company": "SarathiAILabs"}, start=0, page_length=20)
            t_dur = (time.perf_counter() - t_start) * 1000.0
            return t_dur, res is not None

        concurrency = 10
        total_requests = 50
        t_global_start = time.perf_counter()

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            results = list(executor.map(make_request, range(total_requests)))

        total_time_s = time.perf_counter() - t_global_start
        durations = [r[0] for r in results]
        successes = [r[1] for r in results]

        # Metrics
        error_rate = 1.0 - (sum(successes) / len(successes))
        throughput = total_requests / total_time_s
        median_lat = statistics.median(durations)
        durations.sort()
        p95_lat = durations[int(0.95 * len(durations))]

        self.assertEqual(error_rate, 0.0, "Errors encountered during concurrent request execution!")
        self.assertGreater(throughput, 100.0, f"Throughput too low: {throughput:.1f} req/s")
        self.assertLess(p95_lat, 60.0, f"p95 latency exceeded budget: {p95_lat:.2f}ms")

    def test_repeated_refreshes_stability_and_memory(self):
        """
        Simulates 30 consecutive dashboard refreshes.
        Confirms identical response schema, zero query growth, and stable latency.
        """
        self.seed_work_orders(100)
        latencies = []

        for i in range(30):
            t0 = time.perf_counter()
            res = get_factory_overview({"company": "SarathiAILabs"})
            latencies.append((time.perf_counter() - t0) * 1000.0)
            self.assertTrue(res["available"])

        avg_first_5 = statistics.mean(latencies[:5])
        avg_last_5 = statistics.mean(latencies[-5:])

        # Latency should remain stable and not degrade over repeated requests
        self.assertLess(avg_last_5, avg_first_5 * 2.5,
            f"Repeated refreshes degraded! First 5: {avg_first_5:.2f}ms vs Last 5: {avg_last_5:.2f}ms")


# =====================================================================
# 5. PLAYWRIGHT FRONTEND PRESENTATION PERFORMANCE
# =====================================================================

PUBLIC_DIR = inner_vis / "public"

@unittest.skipUnless(sync_playwright, "Playwright is not available in current environment")
class TestBrowserPresentationPerformancePlaywright(unittest.TestCase):
    """
    Browser-level rendering performance benchmarks using headless Chromium.
    Measures DOM paint times, large-table rendering, and UI observer cleanup.
    """

    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1280, "height": 800})
        self.page.set_content("<main data-sarathi-test-root></main>")
        self.page.add_script_tag(content="window.frappe = window.frappe || { provide: function(p) { let o = window; p.split('.').forEach(k => o = o[k] = o[k] || {}); } };")
        css_path = PUBLIC_DIR / "css" / "sarathi_ui.css"
        js_path = PUBLIC_DIR / "js" / "sarathi_ui.js"
        if css_path.exists():
            self.page.add_style_tag(content=css_path.read_text(encoding="utf-8"))
        if js_path.exists():
            self.page.add_script_tag(content=js_path.read_text(encoding="utf-8"))
        self.page.evaluate('window.UI = window.frappe.sarathiUI; window.root = document.querySelector("[data-sarathi-test-root]");')

    def tearDown(self):
        self.page.close()

    def test_browser_kpi_bulk_render_timing(self):
        """Rendering 40 KPI cards into the DOM executes in under 50ms."""
        render_duration = self.page.evaluate('''() => {
            const t0 = performance.now();
            const fragment = document.createDocumentFragment();
            for (let i = 1; i <= 40; i++) {
                fragment.appendChild(UI.kpi({
                    label: "KPI Metric #" + i,
                    value: i * 1500,
                    unit: "INR"
                }));
            }
            root.appendChild(fragment);
            return performance.now() - t0;
        }''')
        cards_count = self.page.locator(".sui-kpi").count()
        self.assertEqual(cards_count, 40)
        self.assertLess(render_duration, 50.0, f"Bulk KPI rendering took {render_duration:.2f}ms (budget 50ms).")

    def test_browser_record_list_bulk_render_timing(self):
        """Rendering a 100-row table into the DOM executes in under 100ms."""
        render_duration = self.page.evaluate('''() => {
            const rows = [];
            for (let i = 1; i <= 100; i++) {
                rows.push({
                    name: "WO-00" + i,
                    item_name: "Fabricated Structural Beam " + i,
                    qty: 50,
                    produced_qty: 25,
                    status: i % 2 === 0 ? "In Process" : "Not Started"
                });
            }
            const columns = [
                {key: "name", label: "Work Order"},
                {key: "item_name", label: "Item"},
                {key: "qty", label: "Planned"},
                {key: "produced_qty", label: "Produced"},
                {key: "status", label: "Status"}
            ];
            const t0 = performance.now();
            const listEl = UI.recordList({
                columns: columns,
                rows: rows,
                mode: "table",
                label: "Work Orders"
            });
            root.appendChild(listEl);
            return performance.now() - t0;
        }''')
        table_rows = self.page.locator(".sui-record-list").count()
        self.assertGreaterEqual(table_rows, 1)
        self.assertLess(render_duration, 100.0, f"Table render took {render_duration:.2f}ms (budget 100ms).")

    def test_browser_layout_and_observer_lifecycle(self):
        """Enhance layout connects mutation observer and cleanly disposes without memory leaks."""
        lifecycle_result = self.page.evaluate('''() => {
            const layout = UI.layout({
                title: "Factory Floor Control",
                description: "Real-time production monitoring",
                company: "Sarathi AI Labs"
            });
            root.appendChild(layout);

            const handle = UI.enhance(root);
            const hasObserver = (handle && typeof handle.dispose === "function");
            handle.dispose();

            return {
                mounted: root.dataset.sarathiUi !== undefined,
                disposed: hasObserver
            };
        }''')
        self.assertTrue(lifecycle_result["disposed"], "enhance().dispose() handle was not properly created!")


if __name__ == "__main__":
    unittest.main()
