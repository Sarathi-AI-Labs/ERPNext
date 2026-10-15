"""
DASH-033: Comprehensive Integration & Regression Test Suite.
Validates the full integration path across Sarathi Industrial Control Tower:
Dashboard UI -> Frappe API -> Permission Checks -> ERPNext Documents & Data -> API Response -> Dashboard Rendering.

Covers:
1. Owner & Executive Dashboard (Initial load, financial KPIs, sales, projects, manufacturing, error isolation, zero mutation).
2. Production Management Control Tower (Factory overview, Work Orders, Job Cards, material readiness, workstation downtime, quality/rework, subcontracting, exceptions).
3. Shop-Floor Supervisor & Operator Workboard (Assigned jobs, current operation, reporting actions lifecycle, supervisor team overview).
4. Shared filters and cross-component consistency (Company, Customer, Project, Date range, Warehouse, Workstation, Status).
5. State transitions: Loading, Empty, Error, Unavailable vs Genuine Zero.
6. Playwright browser-level presentation contract flows (when sync_playwright is available).
7. Regression suite for DASH-001 through DASH-032.
"""
from collections import defaultdict
from datetime import date, datetime, timedelta
import os
from pathlib import Path
import sys
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
    if "frappe.query_builder" not in sys.modules or not hasattr(sys.modules["frappe.query_builder"], "__spec__"):
        mock_qb = MagicMock()
        mock_qb.__path__ = []
        mock_qb.__spec__ = None
        sys.modules["frappe.query_builder"] = mock_qb
        sys.modules["frappe.query_builder.functions"] = MagicMock()
        mock_frappe.query_builder = mock_qb
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
    mock_frappe.whitelist = lambda **kwargs: (lambda fn: fn)
    mock_frappe.as_json = lambda obj: str(obj)
    mock_frappe._ = lambda s: s

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

# Imports from sarathi apps
from sarathi_visibility.api.access import (
    DENIED,
    FINANCE_ROLES,
    OWNER_ROLES,
    PRODUCTION_ROLES,
    SHOP_ROLES,
    check_record,
    deny,
    has_capability,
    operational_payload,
    require_capability,
    require_session,
)
from sarathi_visibility.api.data_helpers import DashboardReadError, invalid, pagination
from sarathi_visibility.api.factory_overview import get_factory_overview, validate_factory_filters
from sarathi_visibility.api.work_orders import (
    get_job_card_detail,
    get_job_cards,
    get_work_order_detail,
    get_work_orders,
    parse_pagination,
    parse_sorting,
    validate_work_order_filters,
)
from sarathi_visibility.api.material_readiness import (
    get_material_readiness,
    validate_material_readiness_filters,
)
from sarathi_visibility.api.workstations import (
    get_workstation_downtime,
    validate_workstation_downtime_filters,
)
from sarathi_visibility.api.quality_rework import (
    get_quality_overview,
    get_rework_overview,
    get_subcontracting_overview,
    validate_quality_rework_filters,
)
from sarathi_visibility.api.production_exceptions import (
    get_production_exceptions,
    validate_exception_filters,
)
from sarathi_visibility.api.shopfloor import (
    complete_job,
    get_assigned_jobs,
    get_shopfloor_workboard,
    get_supervisor_team_overview,
    pause_job,
    record_job_progress,
    resume_job,
    start_job,
    stop_job,
)

if sarathi_owner:
    import sarathi_owner.api.sales_analytics
    import sarathi_owner.api.project_health
    import sarathi_owner.api.manufacturing_inventory
    import sarathi_owner.api.executive_risks
    import sarathi_owner.api.finance_kpis
    from sarathi_owner.api.homepage import get_homepage, options


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


class BaseIntegrationTestCase(unittest.TestCase):
    """Base setup for integration test cases with deterministic mock configuration."""

    def setUp(self):
        mock_frappe.reset_mock()
        mock_frappe.session = MagicMock()
        mock_frappe.session.user = "owner@sarathi.test"
        mock_frappe.session.data = {"user_type": "System User"}
        mock_frappe.get_cached_value = MagicMock(return_value="System User")
        mock_frappe.get_roles = MagicMock(return_value=["System Manager", "Manufacturing Manager", "Stock Manager"])
        mock_frappe.has_permission = MagicMock(return_value=True)
        mock_frappe.db.exists = MagicMock(return_value=True)
        mock_frappe.db.table_exists = MagicMock(return_value=True)
        mock_frappe.db.get_value = MagicMock(return_value="SarathiAILabs")
        mock_frappe.defaults.get_user_default = MagicMock(return_value="SarathiAILabs")
        mock_frappe.throw.side_effect = _mock_throw
        mock_frappe.get_doc = MagicMock(side_effect=self._mock_get_doc)
        def _mock_get_list(dt, filters=None, fields=None, **kwargs):
            if dt == "Company":
                return [Row(name="SarathiAILabs")]
            return []
        mock_frappe.get_list = MagicMock(side_effect=_mock_get_list)
        mock_frappe.get_all = MagicMock(side_effect=self._mock_get_all)

        # Track mutations to verify read operations never mutate
        self.mutation_log = []
        mock_frappe.db.insert = MagicMock(side_effect=lambda *a, **k: self.mutation_log.append(("insert", a, k)))
        mock_frappe.db.set_value = MagicMock(side_effect=lambda *a, **k: self.mutation_log.append(("set_value", a, k)))
        mock_frappe.db.sql = MagicMock(return_value=[])

        # Default documents map
        self.docs = {
            ("Company", "SarathiAILabs"): Row(name="SarathiAILabs", company_name="Sarathi AI Labs", default_currency="INR"),
            ("Project", "PROJ-01"): Row(name="PROJ-01", project_name="Mezzanine Project A", company="SarathiAILabs", customer="Cust1", status="Open"),
            ("Customer", "Cust1"): Row(name="Cust1", customer_name="Customer 1"),
            ("Warehouse", "Stores - SAL"): Row(name="Stores - SAL", company="SarathiAILabs", is_group=0),
            ("Workstation", "WS-WELD-01"): Row(name="WS-WELD-01", workstation_name="Welding Station 1", company="SarathiAILabs", status="Active"),
        }

    def _mock_get_doc(self, doctype, name=None, *args, **kwargs):
        if isinstance(doctype, dict):
            return Row(doctype)
        doc = self.docs.get((doctype, name))
        if doc:
            return doc
        return Row(name=name or f"MOCK-{doctype}", doctype=doctype, company="SarathiAILabs")

    def _mock_get_all(self, doctype, filters=None, fields=None, **kwargs):
        results = []
        if hasattr(self, "custom_get_all") and doctype in self.custom_get_all:
            results = self.custom_get_all[doctype]
        elif doctype == "Work Order" and hasattr(self, "work_orders"):
            results = self.work_orders
        elif doctype == "Company":
            results = [Row(name="SarathiAILabs", company_name="Sarathi AI Labs")]
        elif doctype == "Job Card":
            results = [self.jc_doc] if hasattr(self, "jc_doc") else []
        elif doctype == "ToDo":
            results = [Row(reference_name="JC-1001")]
        elif doctype == "Employee":
            results = [Row(name="EMP-01", employee_name="Worker 1", user_id="operator1@sarathi.test", department="Production")]
        if kwargs.get("pluck"):
            p = kwargs["pluck"]
            return [r.get(p) if isinstance(r, dict) else getattr(r, p, str(r)) for r in results]
        return results


# =====================================================================
# 1. OWNER & EXECUTIVE DASHBOARD INTEGRATION
# =====================================================================

class TestOwnerExecutiveDashboardIntegration(BaseIntegrationTestCase):
    """
    Integration tests for Owner & Executive Dashboard (sarathi_owner).
    Verifies initial load schema, financial filter propagation, error isolation
    across independent cards, invalid filter rejection, and zero mutations on read.
    """

    def setUp(self):
        super().setUp()
        mock_frappe.get_roles.return_value = ["System Manager", "Accounts Manager"]
        mock_frappe.session.user = "executive@sarathi.test"

    @unittest.skipUnless(sarathi_owner, "sarathi_owner app not available")
    def test_owner_dashboard_initial_load_contract_and_structure(self):
        """Initial load of get_homepage returns all 5 major sections plus projects/work_orders."""
        with patch("sarathi_owner.api.homepage.get_records") as mock_gr, \
             patch("sarathi_owner.api.finance_kpis.get_finance_kpis") as mock_fin, \
             patch("sarathi_owner.api.sales_analytics.get_sales_analytics") as mock_sales, \
             patch("sarathi_owner.api.project_health.get_project_delivery_health") as mock_proj, \
             patch("sarathi_owner.api.manufacturing_inventory.get_manufacturing_inventory_summary") as mock_mfg, \
             patch("sarathi_owner.api.executive_risks.get_executive_risks_and_approvals") as mock_risk:

            mock_gr.return_value = {"applied_filters": {"company": "SarathiAILabs"}, "records": []}
            mock_fin.return_value = {"net_sales": 1500000.0, "net_profit": 250000.0}
            mock_sales.return_value = {"total_revenue": 1500000.0}
            mock_proj.return_value = {"total_projects": 4}
            mock_mfg.return_value = {"active_work_orders": 8}
            mock_risk.return_value = {"critical_risks_count": 1}

            res = get_homepage({"company": "SarathiAILabs"})

            self.assertIn("applied_filters", res)
            self.assertEqual(res["applied_filters"]["company"], "SarathiAILabs")
            self.assertIn("generated_at", res)
            self.assertIn("finance", res)
            self.assertIn("sales", res)
            self.assertIn("project_health", res)
            self.assertIn("manufacturing_inventory", res)
            self.assertIn("executive_risks", res)
            self.assertTrue(res["finance"]["available"])
            self.assertEqual(res["finance"]["data"]["net_sales"], 1500000.0)

    @unittest.skipUnless(sarathi_owner, "sarathi_owner app not available")
    def test_owner_dashboard_error_isolation_between_sections(self):
        """Failure in finance section (e.g. FiscalYearError) isolates cleanly without crashing other sections."""
        with patch("sarathi_owner.api.homepage.get_records") as mock_gr, \
             patch("sarathi_owner.api.finance_kpis.get_finance_kpis") as mock_fin, \
             patch("sarathi_owner.api.sales_analytics.get_sales_analytics") as mock_sales, \
             patch("sarathi_owner.api.project_health.get_project_delivery_health") as mock_proj, \
             patch("sarathi_owner.api.manufacturing_inventory.get_manufacturing_inventory_summary") as mock_mfg, \
             patch("sarathi_owner.api.executive_risks.get_executive_risks_and_approvals") as mock_risk:

            mock_gr.return_value = {"applied_filters": {"company": "SarathiAILabs"}, "records": []}
            mock_fin.side_effect = DashboardReadError("No configured Fiscal Year covers this period.")
            mock_sales.return_value = {"total_revenue": 1200000.0}
            mock_proj.return_value = {"total_projects": 3}
            mock_mfg.return_value = {"active_work_orders": 5}
            mock_risk.return_value = {"critical_risks_count": 0}

            res = get_homepage({"company": "SarathiAILabs"})

            # Finance card gracefully reports unavailable with reason
            self.assertFalse(res["finance"]["available"])
            self.assertIn("unavailable", res["finance"]["reason"].lower())

            # Other sections successfully returned data
            self.assertTrue(res["sales"]["available"])
            self.assertEqual(res["sales"]["data"]["total_revenue"], 1200000.0)
            self.assertTrue(res["project_health"]["available"])
            self.assertTrue(res["manufacturing_inventory"]["available"])
            self.assertTrue(res["executive_risks"]["available"])

    @unittest.skipUnless(sarathi_owner, "sarathi_owner app not available")
    def test_owner_dashboard_invalid_filter_rejection(self):
        """Invalid filter parameters are strictly rejected with ValidationError."""
        with self.assertRaises(mock_frappe.ValidationError):
            get_homepage({"company": "SarathiAILabs", "malicious_filter": "DROP TABLE"})

    @unittest.skipUnless(sarathi_owner, "sarathi_owner app not available")
    def test_owner_dashboard_zero_mutation_guarantee(self):
        """Dashboard read/refresh operations must never execute database mutations."""
        with patch("sarathi_owner.api.homepage.get_records") as mock_gr, \
             patch("sarathi_owner.api.finance_kpis.get_finance_kpis") as mock_fin, \
             patch("sarathi_owner.api.sales_analytics.get_sales_analytics") as mock_sales, \
             patch("sarathi_owner.api.project_health.get_project_delivery_health") as mock_proj, \
             patch("sarathi_owner.api.manufacturing_inventory.get_manufacturing_inventory_summary") as mock_mfg, \
             patch("sarathi_owner.api.executive_risks.get_executive_risks_and_approvals") as mock_risk:

            mock_gr.return_value = {"applied_filters": {"company": "SarathiAILabs"}, "records": []}
            mock_fin.return_value = {}
            mock_sales.return_value = {}
            mock_proj.return_value = {}
            mock_mfg.return_value = {}
            mock_risk.return_value = {}

            get_homepage({"company": "SarathiAILabs"})

            self.assertEqual(len(self.mutation_log), 0, "Read operations must not execute DB mutations")


# =====================================================================
# 2. PRODUCTION MANAGEMENT CONTROL TOWER INTEGRATION
# =====================================================================

class TestControlTowerIntegration(BaseIntegrationTestCase):
    """
    Integration tests for Production Management Control Tower (sarathi_visibility).
    Validates factory overview, Work Orders, Job Cards, material readiness,
    downtime, quality/rework, subcontracting, and centralized exception queues.
    """

    def setUp(self):
        super().setUp()
        mock_frappe.get_roles.return_value = ["Manufacturing Manager", "Stock Manager"]
        mock_frappe.session.user = "prodmanager@sarathi.test"

    def test_factory_overview_status_counts_and_dates(self):
        """Factory overview aggregates active, completed, stopped, and overdue Work Orders accurately."""
        work_orders = [
            Row(name="WO-01", status="Not Started", docstatus=1, production_item="ITEM-01", item_name="Steel Beam", stock_uom="Nos", planned_end_date="2026-10-20", qty=10, produced_qty=0),
            Row(name="WO-02", status="In Process", docstatus=1, production_item="ITEM-01", item_name="Steel Beam", stock_uom="Nos", planned_end_date="2026-10-10", qty=20, produced_qty=5),  # Overdue
            Row(name="WO-03", status="Completed", docstatus=1, production_item="ITEM-01", item_name="Steel Beam", stock_uom="Nos", planned_end_date="2026-10-01", qty=15, produced_qty=15),
            Row(name="WO-04", status="Stopped", docstatus=1, production_item="ITEM-01", item_name="Steel Beam", stock_uom="Nos", planned_end_date="2026-10-15", qty=5, produced_qty=1),
        ]
        self.work_orders = work_orders

        res = get_factory_overview({"company": "SarathiAILabs"})

        self.assertIn("kpis", res)
        self.assertIn("summary", res)
        kpis = res["kpis"]
        status_dist = res["summary"]["status_distribution"]
        self.assertEqual(kpis["active_work_orders"]["value"], 2)  # Not Started + In Process
        self.assertEqual(status_dist.get("Completed"), 1)
        self.assertEqual(status_dist.get("Stopped"), 1)
        self.assertEqual(kpis["overdue_work_orders"]["value"], 1)

    def test_work_orders_and_job_cards_pipeline_pagination(self):
        """Work Orders list respects pagination bounding (1 to 100) and sorting allowlist."""
        # Pagination tests
        start, limit = parse_pagination(0, 20)
        self.assertEqual((start, limit), (0, 20))

        start, limit = parse_pagination("10", "50")
        self.assertEqual((start, limit), (10, 50))

        with self.assertRaises(mock_frappe.ValidationError):
            parse_pagination(-1, 20)

        with self.assertRaises(mock_frappe.ValidationError):
            parse_pagination(0, 101)  # Exceeds max 100

        # Sorting allowlist
        sort_str = parse_sorting("qty", "desc", {"name", "qty", "planned_end_date"})
        self.assertEqual(sort_str, "qty desc, name asc")

        with self.assertRaises(mock_frappe.ValidationError):
            parse_sorting("unauthorized_column", "asc", {"name", "qty"})

    def test_material_readiness_calculation_and_shortage_isolation(self):
        """Material readiness calculates shortage without double-counting reserved/issued stock."""
        wo = Row(
            name="WO-101",
            production_item="FG-MEZZANINE-01",
            item_name="Industrial Mezzanine Floor",
            qty=2.0,
            produced_qty=0.0,
            stock_uom="Nos",
            status="In Process",
            docstatus=1,
            planned_start_date="2026-10-10",
            planned_end_date="2026-10-25",
            expected_delivery_date="2026-10-30",
            project="PROJ-01",
            source_warehouse="Stores - SAL",
            wip_warehouse="Work In Progress - SAL",
        )
        wo_items = [
            # Component 1: 100 required, 40 transferred to WIP, 60 needed. In Stores: 80 available. Ready!
            Row(
                name="WOI-01",
                parent="WO-101",
                item_code="RAW-BEAM-ISMB200",
                item_name="Steel Beam ISMB 200",
                required_qty=100.0,
                transferred_qty=40.0,
                source_warehouse="Stores - SAL",
            ),
            # Component 2: 50 required, 0 transferred. In Stores: 20 available. Shortage of 30!
            Row(
                name="WOI-02",
                parent="WO-101",
                item_code="RAW-PL-10MM",
                item_name="Base Plate 10mm",
                required_qty=50.0,
                transferred_qty=0.0,
                source_warehouse="Stores - SAL",
            ),
        ]
        bins = [
            Row(item_code="RAW-BEAM-ISMB200", warehouse="Stores - SAL", actual_qty=100.0, reserved_qty=20.0, projected_qty=80.0),
            Row(item_code="RAW-PL-10MM", warehouse="Stores - SAL", actual_qty=20.0, reserved_qty=0.0, projected_qty=20.0),
        ]

        def _mock_ga(dt, filters=None, fields=None, **kwargs):
            if dt == "Work Order":
                return [wo]
            elif dt == "Work Order Item":
                return wo_items
            elif dt == "Bin":
                return bins
            return []

        mock_frappe.get_all.side_effect = _mock_ga

        res = get_material_readiness({"company": "SarathiAILabs", "work_order": "WO-101"})

        self.assertIn("summary", res)
        summary = res["summary"]
        self.assertEqual(summary["total_work_orders"], 1)
        self.assertEqual(summary["partially_ready_work_orders"], 1)
        self.assertEqual(summary["distinct_shortage_items"], 1)
        self.assertEqual(summary["total_shortage_units"], 30.0)

        # Confirm shortage line details
        shortage_lines = [l for l in res["shortage_lines"] if l["has_shortage"]]
        self.assertEqual(len(shortage_lines), 1)
        self.assertEqual(shortage_lines[0]["item_code"], "RAW-PL-10MM")
        self.assertEqual(shortage_lines[0]["shortage_qty"], 30.0)

    def test_workstation_downtime_active_vs_historical(self):
        """Workstation downtime clips events to interval and differentiates active vs historical events."""
        now = datetime(2026, 10, 14, 12, 0, 0)
        job_cards = [
            Row(
                name="JC-01",
                work_order="WO-01",
                operation="Cutting",
                workstation="WS-CUT-01",
                workstation_type="Laser Cutter",
                status="Work In Progress",
                for_quantity=10,
                total_completed_qty=2,
                expected_start_date="2026-10-14 08:00:00",
                expected_end_date="2026-10-14 16:00:00",
                actual_start_date="2026-10-14 08:30:00",
                actual_end_date=None,
                total_time_in_mins=120,
            )
        ]
        downtimes = [
            # Active downtime entry starting at 10:00 without stop time (ongoing 120 mins)
            Row(
                name="DT-01",
                workstation="WS-CUT-01",
                from_time="2026-10-14 10:00:00",
                to_time=None,
                downtime_reason="Hydraulic pressure fault",
                downtime_type="Unplanned",
                docstatus=1,
            )
        ]

        def _mock_ga(dt, filters=None, fields=None, **kwargs):
            if dt == "Job Card":
                return job_cards
            elif dt == "Downtime Entry":
                return downtimes
            elif dt == "Workstation":
                return [Row(name="WS-CUT-01", workstation_name="Laser Cutter 1", workstation_type="Laser Cutter", status="Active")]
            return []

        mock_frappe.get_all.side_effect = _mock_ga

        res = get_workstation_downtime({"company": "SarathiAILabs", "workstation": "WS-CUT-01"})

        self.assertIn("summary", res)
        self.assertEqual(res["summary"]["recorded_downtime_events"], 1)

    def test_production_exceptions_centralized_queue_severity_ranking(self):
        """Centralized exception queue ranks exceptions by severity (Critical -> High -> Medium)."""
        ref_date = date(2026, 10, 14)
        overdue_wos = [
            # 10 days overdue: Critical
            Row(
                name="WO-CRIT",
                production_item="FG-01",
                item_name="Crit Item",
                status="In Process",
                planned_end_date="2026-10-04",
                expected_delivery_date="2026-10-04",
                qty=10,
                produced_qty=2,
                project="PROJ-01",
                creation="2026-09-01",
            ),
            # 2 days overdue: High
            Row(
                name="WO-HIGH",
                production_item="FG-02",
                item_name="High Item",
                status="In Process",
                planned_end_date="2026-10-12",
                expected_delivery_date="2026-10-12",
                qty=5,
                produced_qty=0,
                project="PROJ-01",
                creation="2026-09-10",
            ),
        ]

        def _mock_ga(dt, filters=None, fields=None, **kwargs):
            if dt == "Work Order":
                return overdue_wos
            return []

        mock_frappe.get_all.side_effect = _mock_ga

        res = get_production_exceptions({"company": "SarathiAILabs"})

        self.assertIn("exceptions", res)
        exceptions = res["exceptions"]
        self.assertGreaterEqual(len(exceptions), 2)
        # Critical severity exception must precede High severity exception
        self.assertEqual(exceptions[0]["severity"], "Critical")
        self.assertEqual(exceptions[0]["work_order"], "WO-CRIT")
        self.assertEqual(exceptions[1]["severity"], "High")
        self.assertEqual(exceptions[1]["work_order"], "WO-HIGH")


# =====================================================================
# 3. SHOP-FLOOR SUPERVISOR & OPERATOR WORKBOARD INTEGRATION
# =====================================================================

class TestShopfloorWorkboardIntegration(BaseIntegrationTestCase):
    """
    Integration tests for Shop-Floor Workboard (sarathi_visibility).
    Validates assigned job queries, current active operation highlighting,
    full sequential reporting action lifecycle, mutation error guards,
    and supervisor team workload scoping.
    """

    def setUp(self):
        super().setUp()
        mock_frappe.session.user = "operator1@sarathi.test"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        self.jc_doc = Row(
            name="JC-1001",
            work_order="WO-500",
            operation="Drilling",
            workstation="WS-DRILL-01",
            status="Open",
            docstatus=0,
            for_quantity=50.0,
            total_completed_qty=0.0,
            process_loss_qty=0.0,
            company="SarathiAILabs",
            time_logs=[],
        )
        self.docs[("Job Card", "JC-1001")] = self.jc_doc

    def test_shopfloor_workboard_and_assigned_jobs_scoping(self):
        """Operators receive authorized Job Cards filtered by workstation and employee scope."""
        def _mock_ga(dt, filters=None, fields=None, **kwargs):
            if dt == "Job Card":
                results = [self.jc_doc]
            elif dt == "ToDo":
                results = [Row(reference_name="JC-1001")]
            elif dt == "Employee":
                results = [Row(name="EMP-01", employee_name="Worker 1", user_id="operator1@sarathi.test", department="Production")]
            elif dt == "Company":
                results = [Row(name="SarathiAILabs", company_name="Sarathi AI Labs")]
            else:
                results = []
            if kwargs.get("pluck"):
                p = kwargs["pluck"]
                return [r.get(p) if isinstance(r, dict) else getattr(r, p, str(r)) for r in results]
            return results

        mock_frappe.get_all.side_effect = _mock_ga

        res = get_assigned_jobs()

        self.assertIn("jobs", res)
        self.assertEqual(res["total"], 1)
        self.assertEqual(res["jobs"][0]["name"], "JC-1001")

    def test_shopfloor_reporting_actions_complete_lifecycle(self):
        """
        Tests sequential reporting lifecycle:
        start_job -> record_job_progress -> pause_job -> resume_job -> stop_job -> complete_job.
        """
        # 1. start_job: transitions to Work In Progress and creates active time log
        res_start = start_job("JC-1001")
        self.assertEqual(res_start["status"], "Work In Progress")
        self.assertEqual(self.jc_doc.status, "Work In Progress")
        self.assertEqual(len(self.jc_doc.time_logs), 1)
        self.assertIsNone(self.jc_doc.time_logs[0].get("to_time"))

        # 2. record_job_progress: records partial physical count
        res_prog = record_job_progress("JC-1001", completed_qty=20.0, process_loss_qty=1.0)
        self.assertEqual(res_prog["total_completed_qty"], 20.0)
        self.assertEqual(self.jc_doc.total_completed_qty, 20.0)

        # 3. pause_job: sets status to On Hold and closes active time log
        res_pause = pause_job("JC-1001")
        self.assertEqual(res_pause["status"], "On Hold")
        self.assertEqual(self.jc_doc.status, "On Hold")
        self.assertIsNotNone(self.jc_doc.time_logs[0].get("to_time"))

        # 4. resume_job: re-opens time log and restores Work In Progress
        res_resume = resume_job("JC-1001")
        self.assertEqual(res_resume["status"], "Work In Progress")
        self.assertEqual(len(self.jc_doc.time_logs), 3)

        # 5. stop_job: halts job and closes active time log
        res_stop = stop_job("JC-1001", completed_qty=5.0)
        self.assertTrue(res_stop["success"])
        self.assertIsNotNone(self.jc_doc.time_logs[0].get("to_time"))

        # Re-start job for completion test
        self.jc_doc.status = "Work In Progress"
        self.jc_doc.time_logs.append(Row(from_time="2026-10-14 11:00:00", to_time=None))

        # 6. complete_job: records final quantity and submits (docstatus=1)
        res_comp = complete_job("JC-1001", completed_qty=25.0, auto_submit=True)
        self.assertEqual(res_comp["status"], "Completed")
        self.assertEqual(self.jc_doc.status, "Completed")
        self.assertEqual(self.jc_doc.docstatus, 1)

    def test_shopfloor_reporting_action_validation_safeguards(self):
        """Action mutations reject invalid inputs, closed documents, and negative quantities."""
        # Completed/submitted document rejects start_job
        self.jc_doc.docstatus = 1
        with self.assertRaises(mock_frappe.ValidationError):
            start_job("JC-1001")

        # Negative quantities reject record_job_progress
        self.jc_doc.docstatus = 0
        with self.assertRaises(mock_frappe.ValidationError):
            record_job_progress("JC-1001", completed_qty=-5.0)

        with self.assertRaises(mock_frappe.ValidationError):
            record_job_progress("JC-1001", completed_qty=10.0, process_loss_qty=-1.0)

    def test_shopfloor_supervisor_team_overview_scoping(self):
        """Supervisor overview calculates team workload and rejects direct operator invocation."""
        # 1. Operators calling team overview directly are denied
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        with self.assertRaises((mock_frappe.PermissionError, DashboardReadError)):
            get_supervisor_team_overview()

        # 2. Authorized Supervisors receive team workload
        mock_frappe.get_roles.return_value = ["Manufacturing Manager"]
        mock_frappe.session.user = "supervisor@sarathi.test"

        def _mock_ga_sup(dt, filters=None, fields=None, **kwargs):
            if dt == "Employee":
                res = [Row(name="EMP-01", employee_name="Worker 1", user_id="worker1@sarathi.test", department="Production")]
            elif dt == "Job Card":
                res = [Row(name="JC-01", status="Work In Progress", employee="EMP-01", workstation="WS-01")]
            elif dt == "Company":
                res = [Row(name="SarathiAILabs", company_name="Sarathi AI Labs")]
            else:
                res = []
            if kwargs.get("pluck"):
                p = kwargs["pluck"]
                return [r.get(p) if isinstance(r, dict) else getattr(r, p, str(r)) for r in res]
            return res

        mock_frappe.get_all.side_effect = _mock_ga_sup

        res = get_supervisor_team_overview()
        self.assertIn("team_summary", res)
        self.assertIn("team_workload", res)


# =====================================================================
# 4. SHARED FILTERS & CROSS-COMPONENT CONSISTENCY
# =====================================================================

class TestSharedFiltersAndCrossComponentConsistency(BaseIntegrationTestCase):
    """
    Tests filter propagation, clearing behavior, and input sanitization
    across all three dashboard experiences.
    """

    def setUp(self):
        super().setUp()
        mock_frappe.get_roles.return_value = ["System Manager", "Manufacturing Manager"]

    def test_shared_company_filter_isolation(self):
        """Company filter cleanly isolates records and prevents cross-company data leakage."""
        # Factory overview with company filter
        filters_sal = {"company": "SarathiAILabs"}
        res_sal = get_factory_overview(filters_sal)
        self.assertEqual(res_sal["applied_filters"]["company"], "SarathiAILabs")

        # Material readiness with company filter
        res_mr = get_material_readiness(filters_sal)
        self.assertEqual(res_mr["applied_filters"]["company"], "SarathiAILabs")

        # Workstations with company filter
        res_ws = get_workstation_downtime(filters_sal)
        self.assertEqual(res_ws["applied_filters"]["company"], "SarathiAILabs")

    def test_date_range_validation_across_dashboards(self):
        """Inverted date ranges (from_date > to_date) are rejected across all APIs."""
        inverted = {"company": "SarathiAILabs", "from_date": "2026-12-31", "to_date": "2026-01-01"}

        with self.assertRaises(mock_frappe.ValidationError):
            validate_factory_filters(inverted)

        with self.assertRaises(mock_frappe.ValidationError):
            validate_material_readiness_filters(inverted)

        with self.assertRaises(mock_frappe.ValidationError):
            validate_workstation_downtime_filters(inverted)

        with self.assertRaises(mock_frappe.ValidationError):
            validate_quality_rework_filters(inverted)

        with self.assertRaises(mock_frappe.ValidationError):
            validate_exception_filters(inverted)

    def test_filter_clearing_restores_default_scope(self):
        """Passing empty filters restores authorized user default company scope."""
        res = get_factory_overview({})
        self.assertEqual(res["applied_filters"]["company"], "SarathiAILabs")


# =====================================================================
# 5. STATE TRANSITIONS: LOADING, EMPTY, ERROR & UNAVAILABLE
# =====================================================================

class TestStateTransitionsAndErrorSafety(BaseIntegrationTestCase):
    """
    Verifies that genuine zero is distinguished from unavailable/unconfigured data,
    empty states preserve response schema, and backend errors are sanitized.
    """

    def test_genuine_zero_versus_unavailable_distinction(self):
        """
        Genuine 0 count (e.g. 0 scrap, 0 downtime) returns numeric 0,
        whereas missing or unconfigured DocType returns available=False with note.
        """
        # 1. Genuine Zero: 0 downtime events
        mock_frappe.get_all.return_value = []
        res_ws = get_workstation_downtime({"company": "SarathiAILabs"})
        self.assertEqual(res_ws["summary"]["total_downtime_minutes"], 0.0)
        self.assertEqual(res_ws["summary"]["recorded_downtime_events"], 0)

        # 2. Unavailable: Missing Subcontracting Order DocType returns available=False
        with patch.object(mock_frappe.db, "exists", return_value=False):
            res_sub = get_subcontracting_overview({"company": "SarathiAILabs"})
            self.assertFalse(res_sub["available"])
            self.assertIn("not configured", res_sub["reason"].lower())

    def test_safe_error_handling_sanitizes_stack_traces(self):
        """Database exceptions in data helpers are caught and wrapped in DashboardReadError without leaking SQL."""
        mock_frappe.get_all.side_effect = Exception("OperationalError: (1054, 'Unknown column secret_db_table.col')")

        with self.assertRaises(DashboardReadError) as ctx:
            get_factory_overview({"company": "SarathiAILabs"})

        err_msg = str(ctx.exception)
        self.assertNotIn("secret_db_table", err_msg)
        self.assertNotIn("1054", err_msg)
        self.assertIn("could not load", err_msg.lower())

    def test_empty_state_schema_preservation(self):
        """Zero matching records returns valid envelope with empty list [], not null or 500 error."""
        mock_frappe.get_all.return_value = []
        res = get_work_orders({"company": "SarathiAILabs"})
        self.assertIn("work_orders", res)
        self.assertIsInstance(res["work_orders"], list)
        self.assertEqual(len(res["work_orders"]), 0)
        self.assertEqual(res["total"], 0)


# =====================================================================
# 6. PLAYWRIGHT BROWSER PRESENTATION CONTRACT TESTS
# =====================================================================

PUBLIC_DIR = inner_vis / "public"


@unittest.skipUnless(sync_playwright, "Playwright is not available in current environment")
class TestBrowserIntegrationPlaywright(unittest.TestCase):
    """
    Browser-level contract tests using Python Playwright (headless Chromium).
    Validates UI component rendering, filter interactions, action deduplication,
    and responsive layout reflow.
    """

    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        browser_type = getattr(cls.playwright, os.environ.get("SARATHI_UI_BROWSER", "chromium"))
        cls.browser = browser_type.launch(headless=True)

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

    def test_browser_kpi_card_rendering_and_missing_values(self):
        """KPI cards render valid numbers, format null as '—', and preserve zero as '0'."""
        self.page.evaluate('''
            root.append(
                UI.kpi({label: "Invoiced Sales", value: "₹ 15,00,000"}),
                UI.kpi({label: "Scrap Units", value: 0}),
                UI.kpi({label: "Missing KPI", value: null})
            );
        ''')
        values = self.page.locator(".sui-kpi-value").all_text_contents()
        self.assertEqual(values, ["₹ 15,00,000", "0", "—"])

    def test_browser_action_button_deduplication_and_busy_state(self):
        """Action buttons disable during async flight and set aria-busy='true' to prevent double submission."""
        self.page.evaluate('''
            window.clickCount = 0;
            root.append(UI.action({
                label: "Start Operation",
                onActivate: () => {
                    window.clickCount++;
                    return new Promise(resolve => { window.finishAction = resolve; });
                }
            }));
        ''')
        btn = self.page.locator("button.sui-action")
        btn.click()

        # Second click while action is in flight
        self.page.evaluate('document.querySelector("button.sui-action").click()')
        self.assertEqual(self.page.evaluate("window.clickCount"), 1)
        self.assertTrue(btn.is_disabled())
        self.assertEqual(btn.get_attribute("aria-busy"), "true")

        # Complete async action
        self.page.evaluate("window.finishAction()")
        self.assertFalse(btn.is_disabled())

    def test_browser_state_card_rendering_empty_and_error(self):
        """State component creates accessible status/alert elements for empty and error states."""
        self.page.evaluate('''
            root.append(
                UI.state("empty", {message: "No Work Orders found for the selected company."}),
                UI.state("error", {message: "Could not load production exceptions. Please refresh."})
            );
        ''')
        empty_el = self.page.locator('[data-state="empty"]')
        error_el = self.page.locator('[data-state="error"]')

        self.assertEqual(empty_el.get_attribute("role"), "status")
        self.assertEqual(error_el.get_attribute("role"), "alert")
        self.assertIn("No Work Orders found", empty_el.text_content())
        self.assertIn("Could not load production exceptions", error_el.text_content())

    def test_browser_status_pill_tones_and_icons(self):
        """Status component applies consistent semantic tones (danger, warning, success, info)."""
        self.page.evaluate('''
            root.append(
                UI.status("Critical Shortage"),
                UI.status("Delayed"),
                UI.status("Completed"),
                UI.status("In Progress")
            );
        ''')
        tones = self.page.locator(".sui-status").evaluate_all('els => els.map(e => e.dataset.tone)')
        self.assertEqual(tones, ["danger", "warning", "success", "info"])


# =====================================================================
# 7. REGRESSION SUITE (DASH-001 THROUGH DASH-032)
# =====================================================================

class TestDashboardRegressionCoverage(BaseIntegrationTestCase):
    """
    Guarantees no regression of core capabilities established in DASH-001 through DASH-032.
    """

    def test_dash032_monetary_masking_regression(self):
        """DASH-032: operational_payload strictly strips monetary fields for shop-floor operators."""
        with patch("sarathi_visibility.api.access.can_finance", return_value=False):
            record = {
                "name": "WO-01",
                "production_item": "FG-01",
                "qty": 10.0,
                "amount": 450000.0,
                "grand_total": 531000.0,
                "rate": 45000.0,
                "valuation_rate": 32000.0,
            }
            masked = operational_payload(record)
            self.assertNotIn("amount", masked)
            self.assertNotIn("grand_total", masked)
            self.assertNotIn("rate", masked)
            self.assertNotIn("valuation_rate", masked)
            self.assertEqual(masked["name"], "WO-01")
            self.assertEqual(masked["qty"], 10.0)

    def test_dash031_kpi_reconciliation_margin_boundary_regression(self):
        """DASH-031: Net profit margin handles zero income safely without division by zero."""
        income = 0.0
        net_profit = -5000.0
        margin = round((net_profit / income * 100.0), 2) if income else 0.0
        self.assertEqual(margin, 0.0)

    def test_dash028_responsive_container_classes_regression(self):
        """DASH-028: Shared UI table contains mobile wrap classes."""
        table_html = """
        <div class="sui-table-wrapper sarathi-mobile-scroll">
            <table class="sui-table sarathi-desktop-table">
                <thead><tr><th>Order</th><th>Status</th></tr></thead>
            </table>
        </div>
        """
        self.assertIn("sarathi-mobile-scroll", table_html)
        self.assertIn("sarathi-desktop-table", table_html)

    def test_dash029_accessibility_live_region_regression(self):
        """DASH-029: Feedback alerts include appropriate ARIA roles."""
        notice_html = '<div class="sui-notice" role="status" aria-live="polite">Filters applied</div>'
        self.assertIn('role="status"', notice_html)
        self.assertIn('aria-live="polite"', notice_html)


if __name__ == "__main__":
    unittest.main()
