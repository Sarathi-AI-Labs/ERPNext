"""DASH-032: Automated Security Tests for Role Permissions and Direct API Access.

Validates:
1. Dashboard Route Access (Owner, Control Tower, Shop-Floor Workboard)
2. Role Capabilities and Direct API Whitelist Access
3. Object-Level Authorization (Job Cards, Work Orders, Projects)
4. Company and Organizational Scope Restrictions
5. Filter Tampering, Parameter Allowlist, and SQL Injection Prevention
6. Data Leakage and Monetary Field Stripping (operational_payload)
7. Shop-Floor Production Reporting Mutation Authorization
"""

from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

# Path resolution for standalone unittest execution
repo_root = Path(__file__).resolve().parents[3]
visibility_root = (repo_root / "sarathi_visibility").resolve()
owner_root = (repo_root / "sarathi_owner").resolve()

for p in (str(visibility_root), str(owner_root)):
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
    pass

# Mock Frappe framework
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
mock_frappe.whitelist = lambda **kwargs: (lambda fn: fn)
mock_frappe.as_json = lambda obj: str(obj)
mock_frappe._ = lambda s: s

sys.modules["frappe"] = mock_frappe
sys.modules["frappe.utils"] = mock_frappe.utils
sys.modules["frappe.model"] = MagicMock()
sys.modules["frappe.permissions"] = mock_frappe.permissions
sys.modules["frappe.desk"] = MagicMock()
sys.modules["frappe.desk.query_report"] = MagicMock()
mock_erpnext = MagicMock()
mock_erpnext.accounts = MagicMock()
mock_erpnext.accounts.utils = MagicMock()
mock_erpnext.accounts.utils.FiscalYearError = type("FiscalYearError", (Exception,), {})
sys.modules["erpnext"] = mock_erpnext
sys.modules["erpnext.accounts"] = mock_erpnext.accounts
sys.modules["erpnext.accounts.utils"] = mock_erpnext.accounts.utils

from sarathi_visibility.api.access import (
    DENIED,
    FINANCE_ROLES,
    OWNER_ROLES,
    PRODUCTION_ROLES,
    SHOP_ROLES,
    allowed_fields,
    check_record,
    check_shop_job,
    deny,
    has_capability,
    operational_payload,
    require_capability,
    require_session,
    scoped_sql,
    validate_filters,
)
from sarathi_visibility.api.data_helpers import _date, _extra, _identifier, invalid, pagination


class Row(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value
    def get(self, key, default=None):
        return super().get(key, default)
    def check_permission(self, perm="read"):
        if self.get("_forbidden"):
            raise mock_frappe.PermissionError("Document permission denied")
    def db_set(self, key, val=None):
        if isinstance(key, dict):
            self.update(key)
        else:
            self[key] = val
    def reload(self):
        pass


class BaseSecurityTestCase(unittest.TestCase):
    """Common setup to ensure mock Frappe consistency across all test cases."""
    def setUp(self):
        mock_frappe.throw.side_effect = _mock_throw
        mock_frappe.session.user = "admin@example.com"
        mock_frappe.get_cached_value.return_value = "System User"
        mock_frappe.get_roles.side_effect = None
        mock_frappe.get_roles.return_value = ["System Manager"]
        mock_frappe.has_permission.return_value = True
        mock_frappe.db.exists.return_value = True
        mock_frappe.get_doc.side_effect = None
        mock_frappe.get_doc.return_value = Row(name="DOC-DEFAULT")
        mock_frappe.permissions.get_user_permissions.return_value = {}
        mock_frappe.local = MagicMock()
        mock_frappe.local.message_log = []


class TestDashboardRouteAccess(BaseSecurityTestCase):
    """Verifies route-level access rules for desk dashboard pages."""

    def test_owner_dashboard_route_roles(self):
        """Owner page (/desk/sarathiownertower) strictly restricted to Sarathi Owner & System Manager."""
        owner_page_json = json.loads(
            (repo_root / "sarathi_owner" / "sarathi_owner" / "sarathi_owner" / "page" / "sarathiownertower" / "sarathiownertower.json").read_text(encoding="utf-8")
        )
        roles = {r["role"] for r in owner_page_json.get("roles", [])}
        self.assertEqual(roles, {"Sarathi Owner", "System Manager"})
        self.assertNotIn("Manufacturing Manager", roles)
        self.assertNotIn("Sarathi Operator", roles)
        self.assertNotIn("Customer", roles)

    def test_control_tower_route_roles(self):
        """Control tower page (/desk/sarathicontroltower) restricted to production managers and owners."""
        control_page_json = json.loads(
            (repo_root / "sarathi_visibility" / "sarathi_visibility" / "sarathi_visibility" / "page" / "sarathicontroltower" / "sarathicontroltower.json").read_text(encoding="utf-8")
        )
        roles = {r["role"] for r in control_page_json.get("roles", [])}
        self.assertEqual(roles, {"Sarathi Owner", "Manufacturing Manager", "System Manager", "Sarathi Super Admin"})
        self.assertNotIn("Sarathi Operator", roles)
        self.assertNotIn("Accounts User", roles)

    def test_shopfloor_workboard_route_roles(self):
        """Shop-floor page (/desk/sarathishopfloor) admits operators and supervisors."""
        shopfloor_page_json = json.loads(
            (repo_root / "sarathi_visibility" / "sarathi_visibility" / "sarathi_visibility" / "page" / "sarathishopfloor" / "sarathishopfloor.json").read_text(encoding="utf-8")
        )
        roles = {r["role"] for r in shopfloor_page_json.get("roles", [])}
        self.assertIn("Sarathi Operator", roles)
        self.assertIn("Sarathi Supervisor", roles)
        self.assertIn("Manufacturing Manager", roles)
        self.assertNotIn("Customer", roles)
        self.assertNotIn("Accounts User", roles)


class TestRoleCapabilitiesAndDirectAPIAccess(BaseSecurityTestCase):
    """Verifies server-side capability gates and direct API call protection."""

    def test_unauthenticated_guest_denied_immediately(self):
        """require_session() strictly rejects Guest and unauthenticated sessions."""
        mock_frappe.session.user = "Guest"
        with self.assertRaises(mock_frappe.PermissionError):
            require_session()

        mock_frappe.session.user = None
        with self.assertRaises(mock_frappe.PermissionError):
            require_session()

    def test_non_system_user_denied(self):
        """Website users (e.g. Customer portal accounts) are denied dashboard capability."""
        mock_frappe.session.user = "customer@example.com"
        mock_frappe.get_cached_value.return_value = "Website User"
        with self.assertRaises(mock_frappe.PermissionError):
            require_session()

    def test_owner_capability_resolution(self):
        """Only users with Sarathi Owner or System Manager have owner capability."""
        mock_frappe.get_roles.side_effect = lambda u: {
            "owner@example.com": ["Sarathi Owner"],
            "admin@example.com": ["System Manager"],
            "manager@example.com": ["Manufacturing Manager"],
            "operator@example.com": ["Sarathi Operator"],
        }.get(u, [])

        self.assertTrue(has_capability("owner", "owner@example.com"))
        self.assertTrue(has_capability("owner", "admin@example.com"))
        self.assertFalse(has_capability("owner", "manager@example.com"))
        self.assertFalse(has_capability("owner", "operator@example.com"))

    def test_production_capability_resolution(self):
        """Production capability requires Manufacturing Manager, Sarathi Super Admin, or Owner."""
        mock_frappe.get_roles.side_effect = lambda u: {
            "manager@example.com": ["Manufacturing Manager"],
            "admin@example.com": ["Sarathi Super Admin"],
            "operator@example.com": ["Sarathi Operator"],
            "finance@example.com": ["Accounts User"],
        }.get(u, [])

        self.assertTrue(has_capability("production", "manager@example.com"))
        self.assertTrue(has_capability("production", "admin@example.com"))
        self.assertFalse(has_capability("production", "operator@example.com"))
        self.assertFalse(has_capability("production", "finance@example.com"))

    def test_shop_capability_resolution(self):
        """Shop capability requires Sarathi Supervisor or Sarathi Operator."""
        mock_frappe.get_roles.side_effect = lambda u: {
            "sup@example.com": ["Sarathi Supervisor"],
            "op@example.com": ["Sarathi Operator"],
            "other@example.com": ["Sales User"],
        }.get(u, [])

        self.assertTrue(has_capability("shop", "sup@example.com"))
        self.assertTrue(has_capability("shop", "op@example.com"))
        self.assertFalse(has_capability("shop", "other@example.com"))

    def test_finance_capability_resolution(self):
        """Finance capability requires financial roles or Owner."""
        mock_frappe.get_roles.side_effect = lambda u: {
            "owner@example.com": ["Sarathi Owner"],
            "accts@example.com": ["Accounts User"],
            "manager@example.com": ["Manufacturing Manager"],
        }.get(u, [])

        self.assertTrue(has_capability("finance", "owner@example.com"))
        self.assertTrue(has_capability("finance", "accts@example.com"))
        self.assertFalse(has_capability("finance", "manager@example.com"))

    def test_direct_api_get_finance_kpis_enforces_owner_and_finance(self):
        """Direct call to get_finance_kpis requires owner and finance capabilities."""
        from sarathi_owner.api.finance_kpis import get_finance_kpis

        # Non-finance manager denied
        mock_frappe.session.user = "manager@example.com"
        mock_frappe.get_roles.return_value = ["Manufacturing Manager"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_finance_kpis()

        # Operator denied
        mock_frappe.session.user = "operator@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_finance_kpis()

        # Accounts user (finance but not owner) denied
        mock_frappe.session.user = "accts@example.com"
        mock_frappe.get_roles.return_value = ["Accounts User"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_finance_kpis()

    def test_direct_api_get_factory_overview_enforces_production(self):
        """Direct call to get_factory_overview requires production capability."""
        from sarathi_visibility.api.factory_overview import get_factory_overview

        # Operator denied
        mock_frappe.session.user = "operator@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_factory_overview()

        # Finance user denied
        mock_frappe.session.user = "accts@example.com"
        mock_frappe.get_roles.return_value = ["Accounts User"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_factory_overview()

    def test_direct_api_get_material_readiness_enforces_production(self):
        """Direct call to get_material_readiness requires production capability."""
        from sarathi_visibility.api.material_readiness import get_material_readiness

        # Operator denied
        mock_frappe.session.user = "operator@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        with self.assertRaises(mock_frappe.PermissionError):
            get_material_readiness()

    def test_direct_api_get_assigned_jobs_enforces_session_and_roles(self):
        """Direct call to get_assigned_jobs requires authenticated session."""
        from sarathi_visibility.api.shopfloor import get_assigned_jobs

        # Guest denied
        mock_frappe.session.user = "Guest"
        with self.assertRaises(mock_frappe.PermissionError):
            get_assigned_jobs()


class TestObjectLevelAuthorization(BaseSecurityTestCase):
    """Verifies that accessing an endpoint does not bypass record-level permissions."""

    def test_check_record_rejects_missing_and_forbidden_documents(self):
        """check_record raises PermissionError identically for missing, non-string, or forbidden documents."""
        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_cached_value.return_value = "System User"

        # Non-string identifier
        with self.assertRaises(mock_frappe.PermissionError):
            check_record("Job Card", 12345)

        # Empty string identifier
        with self.assertRaises(mock_frappe.PermissionError):
            check_record("Job Card", "")

        # Excessively long identifier
        with self.assertRaises(mock_frappe.PermissionError):
            check_record("Job Card", "A" * 150)

        # Forbidden record
        forbidden_doc = Row(name="JC-FORBIDDEN", _forbidden=True)
        mock_frappe.get_doc.return_value = forbidden_doc
        with self.assertRaises(mock_frappe.PermissionError):
            check_record("Job Card", "JC-FORBIDDEN")

    def test_check_shop_job_enforces_operator_assignment(self):
        """Operators can only access Job Cards explicitly assigned via ToDo."""
        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]

        job_doc = Row(name="JC-001", company="SarathiAILabs", workstation="WS-01", work_order="WO-001")
        mock_frappe.get_doc.return_value = job_doc

        # Case 1: Assigned to this operator -> Allowed
        mock_frappe.db.exists.return_value = True
        doc = check_shop_job("JC-001", "read")
        self.assertEqual(doc.name, "JC-001")

        # Case 2: Not assigned to this operator -> Denied
        mock_frappe.db.exists.return_value = False
        with self.assertRaises(mock_frappe.PermissionError):
            check_shop_job("JC-001", "read")

    def test_check_shop_job_enforces_supervisor_workstation_scope(self):
        """Supervisors can access jobs on workstations granted in User Permission."""
        mock_frappe.session.user = "sup1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Supervisor"]

        job_doc = Row(name="JC-002", company="SarathiAILabs", workstation="WS-PERMITTED", work_order="WO-001")
        mock_frappe.get_doc.return_value = job_doc
        mock_frappe.db.exists.return_value = False

        # Case 1: Workstation in user permissions -> Allowed
        mock_frappe.permissions.get_user_permissions.return_value = {
            "Workstation": [{"doc": "WS-PERMITTED", "applicable_for": "Job Card"}]
        }
        doc = check_shop_job("JC-002", "read")
        self.assertEqual(doc.name, "JC-002")

        # Case 2: Workstation not in user permissions -> Denied
        mock_frappe.permissions.get_user_permissions.return_value = {
            "Workstation": [{"doc": "WS-OTHER", "applicable_for": "Job Card"}]
        }
        with self.assertRaises(mock_frappe.PermissionError):
            check_shop_job("JC-002", "read")


class TestCompanyAndOrganizationalScope(BaseSecurityTestCase):
    """Verifies company boundary isolation and linked document integrity."""

    def test_project_company_mismatch_denied(self):
        """Requesting a Project that belongs to Company B when filtering by Company A is rejected."""
        mock_frappe.session.user = "manager@example.com"
        mock_frappe.get_roles.return_value = ["Manufacturing Manager"]

        company_doc = Row(name="Company A", default_currency="INR")
        company_doc.meta = Row(has_field=lambda f: True)
        project_doc = Row(name="PROJ-001", company="Company B")
        project_doc.meta = Row(has_field=lambda f: True)

        def _get_doc(dt, name):
            if dt == "Company":
                return company_doc
            if dt == "Project":
                return project_doc
            return Row(name=name, meta=Row(has_field=lambda f: False))

        mock_frappe.get_doc.side_effect = _get_doc

        with self.assertRaises(mock_frappe.PermissionError):
            validate_filters(filters={"company": "Company A", "project": "PROJ-001"})

    def test_customer_project_mismatch_denied(self):
        """Requesting a Project with a Customer that does not match is rejected."""
        mock_frappe.session.user = "manager@example.com"
        mock_frappe.get_roles.return_value = ["Manufacturing Manager"]

        company_doc = Row(name="Company A", default_currency="INR")
        company_doc.meta = Row(has_field=lambda f: True)
        customer_doc = Row(name="Customer 1")
        customer_doc.meta = Row(has_field=lambda f: False)
        project_doc = Row(name="PROJ-001", company="Company A", customer="Customer 2")
        project_doc.meta = Row(has_field=lambda f: True)

        def _get_doc(dt, name):
            if dt == "Company":
                return company_doc
            if dt == "Customer":
                return customer_doc
            if dt == "Project":
                return project_doc
            return Row(name=name, meta=Row(has_field=lambda f: False))

        mock_frappe.get_doc.side_effect = _get_doc

        with self.assertRaises(mock_frappe.PermissionError):
            validate_filters(filters={"company": "Company A", "customer": "Customer 1", "project": "PROJ-001"})


class TestFilterTamperingAndInputValidation(BaseSecurityTestCase):
    """Verifies that malicious or malformed parameters are rejected safely."""

    def test_disallowed_extra_parameters_rejected(self):
        """Passing unexpected extra query parameters triggers ValidationError via _extra."""
        with self.assertRaises(mock_frappe.ValidationError):
            _extra({"malicious_injected_param": "drop tables"})

    def test_inverted_date_bounds_rejected(self):
        """from_date > to_date is strictly rejected by validate_filters."""
        mock_frappe.session.user = "owner@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Owner"]
        with self.assertRaises(mock_frappe.ValidationError):
            validate_filters(filters={"from_date": "2026-12-31", "to_date": "2026-01-01"})

    def test_invalid_date_format_rejected(self):
        """Non-date strings in date fields are rejected."""
        mock_frappe.session.user = "owner@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Owner"]
        with self.assertRaises(mock_frappe.ValidationError):
            _date("not-a-valid-date")

    def test_malformed_identifier_rejected(self):
        """Identifiers with whitespace only, non-strings, or length > 140 are rejected."""
        with self.assertRaises(mock_frappe.ValidationError):
            _identifier("")

        with self.assertRaises(mock_frappe.ValidationError):
            _identifier("   ")

        with self.assertRaises(mock_frappe.ValidationError):
            _identifier(12345)

        with self.assertRaises(mock_frappe.ValidationError):
            _identifier("A" * 150)

        with self.assertRaises(mock_frappe.ValidationError):
            _identifier("bad\x00control_char")

    def test_scoped_sql_blocks_injection_attempts(self):
        """scoped_sql strictly rejects SQL comments, stacked queries, and destructive commands."""
        mock_frappe.session.user = "manager@example.com"

        # Stacked query with semicolon
        with self.assertRaises(mock_frappe.PermissionError):
            scoped_sql("SELECT name FROM `tabWork Order`; DROP TABLE `tabUser`")

        # Comment injection
        with self.assertRaises(mock_frappe.PermissionError):
            scoped_sql("SELECT name FROM `tabWork Order` -- comment")

        # UNION injection
        with self.assertRaises(mock_frappe.PermissionError):
            scoped_sql("SELECT name FROM `tabWork Order` UNION SELECT name FROM `tabUser`")

        # Non-SELECT statement
        with self.assertRaises(mock_frappe.PermissionError):
            scoped_sql("DELETE FROM `tabWork Order`")

    def test_pagination_bounds_clamping(self):
        """Pagination parameters are safely validated against whole number and range limits."""
        with self.assertRaises(mock_frappe.ValidationError):
            pagination(-10, 20)

        start, limit = pagination(0, 50)
        self.assertEqual(start, 0)
        self.assertEqual(limit, 50)

        with self.assertRaises(mock_frappe.ValidationError):
            pagination(0, 500)


class TestKPIDataLeakageAndMonetaryMasking(BaseSecurityTestCase):
    """Verifies that non-finance users have monetary fields stripped from responses."""

    def test_operational_payload_strips_monetary_fields_for_non_finance(self):
        """Managers without finance capability have monetary keys stripped recursively."""
        with patch("sarathi_visibility.api.access.can_finance", return_value=False):
            data = {
                "work_order": "WO-001",
                "qty": 100,
                "produced_qty": 60,
                "rate": 250.0,
                "amount": 25000.0,
                "stock_value": 50000.0,
                "grand_total": 30000.0,
                "columns": [
                    {"fieldname": "qty", "label": "Qty", "fieldtype": "Float"},
                    {"fieldname": "rate", "label": "Rate", "fieldtype": "Currency"},
                    {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency"},
                ],
            }
            sanitized = operational_payload(data)

            self.assertIn("work_order", sanitized)
            self.assertIn("qty", sanitized)
            self.assertIn("produced_qty", sanitized)

            self.assertNotIn("rate", sanitized)
            self.assertNotIn("amount", sanitized)
            self.assertNotIn("stock_value", sanitized)
            self.assertNotIn("grand_total", sanitized)

            col_names = [c["fieldname"] for c in sanitized["columns"]]
            self.assertEqual(col_names, ["qty"])

    def test_operational_payload_preserves_monetary_for_finance_users(self):
        """Users with finance capability retain complete monetary metrics."""
        with patch("sarathi_visibility.api.access.can_finance", return_value=True):
            data = {
                "work_order": "WO-001",
                "amount": 25000.0,
                "stock_value": 50000.0,
            }
            sanitized = operational_payload(data)
            self.assertEqual(sanitized, data)


class TestShopFloorMutationAuthorization(BaseSecurityTestCase):
    """Verifies authorization, state enforcement, and quantity validation on shop-floor actions."""

    def test_unauthorized_operator_cannot_start_other_job(self):
        """Calling start_job on a Job Card not assigned to operator raises PermissionError."""
        from sarathi_visibility.api.shopfloor import start_job

        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        mock_frappe.db.exists.return_value = True
        mock_frappe.get_doc.return_value = Row(name="JC-OTHER", docstatus=0, status="Open")

        with patch("sarathi_visibility.api.shopfloor.resolve_shopfloor_context") as mock_ctx:
            mock_ctx.return_value = ({"is_manager": False}, {"JC-MINE"}, None)
            with self.assertRaises(mock_frappe.PermissionError):
                start_job("JC-OTHER")

    def test_operator_cannot_start_completed_or_cancelled_job(self):
        """start_job rejects Job Cards with docstatus=1 or docstatus=2."""
        from sarathi_visibility.api.shopfloor import start_job

        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        mock_frappe.db.exists.return_value = True

        completed_doc = Row(name="JC-01", docstatus=1, status="Completed", for_quantity=100, total_completed_qty=100)
        mock_frappe.get_doc.return_value = completed_doc

        with patch("sarathi_visibility.api.shopfloor.resolve_shopfloor_context") as mock_ctx:
            mock_ctx.return_value = ({"is_manager": False}, {"JC-01"}, None)
            with self.assertRaises(mock_frappe.ValidationError):
                start_job("JC-01")

        cancelled_doc = Row(name="JC-02", docstatus=2, status="Cancelled")
        mock_frappe.get_doc.return_value = cancelled_doc
        with patch("sarathi_visibility.api.shopfloor.resolve_shopfloor_context") as mock_ctx:
            mock_ctx.return_value = ({"is_manager": False}, {"JC-02"}, None)
            with self.assertRaises(mock_frappe.ValidationError):
                start_job("JC-02")

    def test_record_job_progress_validates_quantity_accounting(self):
        """record_job_progress rejects negative quantities or over-reporting."""
        from sarathi_visibility.api.shopfloor import record_job_progress

        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]
        mock_frappe.db.exists.return_value = True

        active_doc = Row(name="JC-01", docstatus=0, status="Work In Progress", for_quantity=100, total_completed_qty=50)
        mock_frappe.get_doc.return_value = active_doc

        with patch("sarathi_visibility.api.shopfloor.resolve_shopfloor_context") as mock_ctx:
            mock_ctx.return_value = ({"is_manager": False}, {"JC-01"}, None)

            # Negative completed_qty rejected
            with self.assertRaises(mock_frappe.ValidationError):
                record_job_progress("JC-01", completed_qty=-5.0)

            # Negative process_loss_qty rejected
            with self.assertRaises(mock_frappe.ValidationError):
                record_job_progress("JC-01", completed_qty=10.0, process_loss_qty=-2.0)

    def test_supervisor_team_overview_denies_direct_operator_call(self):
        """Operators calling get_supervisor_team_overview directly via API are rejected."""
        from sarathi_visibility.api.shopfloor import get_supervisor_team_overview

        mock_frappe.session.user = "operator1@example.com"
        mock_frappe.get_roles.return_value = ["Sarathi Operator"]

        with self.assertRaises(mock_frappe.PermissionError):
            get_supervisor_team_overview()


if __name__ == "__main__":
    unittest.main()
