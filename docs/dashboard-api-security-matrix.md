# Sarathi Industrial Control Tower — Dashboard API Security Matrix (DASH-032)

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-030 — Testing, Performance, Security & Release  
**Task ID:** DASH-032 — Role Permissions and Direct API Access Tests  
**Scope:** Automated server-side security tests, role permissions, record-level authorization, company scoping, filter tampering prevention, and shop-floor mutation validation  
**Status:** Verified & Documented  
**Test Suite:** `sarathi_visibility/sarathi_visibility/tests/test_role_permissions_api_access.py` (30 passing tests)

---

## 1. Executive Summary & Security Principles

The Sarathi Industrial Control Tower enforces a **defense-in-depth security model** across all three dashboard experiences. The frontend UI is strictly treated as a presentation layer and **never as a security boundary**:

1. **Dual-Layer Authorization:**
   - **Layer 1 — Dashboard Capability Gate:** Required system-level role capability (`owner`, `production`, `shop`, `finance`).
   - **Layer 2 — Native Frappe/ERPNext Document Permissions:** Underlying DocPerm, User Permissions, role permissions, and company restrictions must be independently satisfied.
2. **Strict Whitelist & Method Restrictions:**
   - Every public endpoint is protected by `@frappe.whitelist(methods=["GET"])` or `@frappe.whitelist(methods=["POST"])`.
   - Direct API calls bypassing Desk UI pages are subjected to the exact same server-side capability and document permission validations.
3. **No Information Leakage via Aggregates or Metadata:**
   - Unauthorized records are excluded at query execution time (`scoped_sql`, `scoped_rows`, native `get_list`).
   - Non-finance production managers querying production or accounting views have all monetary-derived keys (`amount`, `rate`, `stock_value`, `grand_total`, etc.) automatically stripped via `operational_payload`.
4. **Shop-Floor Identity & Assignment Integrity:**
   - Machine operators can only query or report progress on Job Cards directly assigned to them via open Frappe `ToDo` assignments or linked active `Employee` records.
   - Supervisors can only monitor jobs on workstations within their explicit `Workstation` User Permissions or direct assignments.
   - Production managers have company-wide scope but cannot bypass document validation workflows.
5. **Sanitized Input & Parameter Whitelisting:**
   - Query parameters are strictly validated against allowlists (`_extra`, `validate_filters`, `validate_shopfloor_filters`).
   - Date ranges are validated for ordering (`from_date <= to_date`) and ISO format.
   - SQL comments (`--`, `/*`), stacked queries (`;`), and UNION injections are rejected closed by `scoped_sql`.

---

## 2. Dashboard Persona & Role Matrix

| Persona | Dashboard Capability Role | Required ERPNext Native Roles | Primary Permitted Scope |
|---|---|---|---|
| **Executive / Owner** | `Sarathi Owner` | `Accounts User`, `Projects User`, `Sales User`, `Stock User`, `Manufacturing User` | Enterprise-wide financial, sales, inventory, and executive metrics within assigned Company. |
| **Production Manager** | `Manufacturing Manager` | `Manufacturing User`, `Stock User`, `Projects User` | Factory-wide Work Orders, Job Cards, material readiness, downtime, quality, and exception queues. |
| **Shop Supervisor** | `Sarathi Supervisor` | `Manufacturing User`, `Stock User` | Team operators, assigned workstations (via `User Permission`), floor operations, and active blockers. |
| **Machine Operator** | `Sarathi Operator` | `Manufacturing User` | Exclusively open Job Cards assigned to the caller via `ToDo` or active `Employee` record. |
| **System Administrator** | `System Manager` | System administrator roles | System management, audit logs, and dashboard setup. |
| **Setup Administrator** | `Sarathi Super Admin` | Technical setup roles | Technical setup, integration logging, and module profile management. |

---

## 3. Dashboard Route Access Matrix

| Dashboard Route | Target Page | Authorized Roles | Unauthorized Role Behavior | Authentication Bypass Prevention |
|---|---|---|---|---|
| `/desk/sarathiownertower` | Owner & Executive Dashboard | `Sarathi Owner`, `System Manager` | Redirected / Desk 403 Forbidden | Frappe desk routing verifies `Page.roles` server-side before serving page bundle. |
| `/desk/sarathicontroltower` | Production Control Tower | `Sarathi Owner`, `Manufacturing Manager`, `System Manager`, `Sarathi Super Admin` | Redirected / Desk 403 Forbidden | Page role check rejects Operators, Supervisors, and non-production users. |
| `/desk/sarathishopfloor` | Shop-Floor Workboard | `Sarathi Operator`, `Sarathi Supervisor`, `Manufacturing Manager`, `Sarathi Super Admin`, `Sarathi Owner` | Redirected / Desk 403 Forbidden | Page role check rejects Customer, Accounts User, and unauthenticated guests. |

---

## 4. Implemented Dashboard API Security Inventory

### 4.1 Owner & Executive Dashboard APIs (`sarathi_owner`)

| Endpoint Route | HTTP Method | Required Capabilities | Native DocType Checks | Input Parameters | Read / Mutate | Security Protections | Test Status |
|---|---|---|---|---|---|---|---|
| `sarathi_owner.api.finance_kpis.get_finance_kpis` | `GET` | `owner` AND `finance` | `Company`, `GL Entry`, `Sales Invoice` | `filters` (JSON string/dict) | Read | Server-side capability check, company validation, currency field check. Rejects non-finance managers. | **PASS** |
| `sarathi_owner.api.homepage.get_owner_homepage` | `GET` | `owner` | `Company`, `GL Entry`, `Sales Invoice`, `Project`, `Work Order` | `company`, `from_date`, `to_date` | Read | Scoped reads, finance masking for non-finance callers, strict company permission check. | **PASS** |
| `sarathi_owner.api.homepage.get_homepage_metric_detail` | `GET` | `owner` | Underlying source DocType | `metric_key`, `filters` | Read | Validates metric allowlist, enforces record permission on drill-down documents. | **PASS** |
| `sarathi_owner.api.sales_analytics.get_sales_analytics_summary` | `GET` | `owner` | `Sales Invoice`, `Sales Order`, `Customer` | `filters` (company, customer, dates) | Read | Parameter allowlist validation, company boundary verification, customer link validation. | **PASS** |
| `sarathi_owner.api.project_health.get_project_health_summary` | `GET` | `owner` | `Project`, `Task`, `Customer` | `filters` (company, customer, project) | Read | Validates project company matches filter company; rejects mismatched customer links. | **PASS** |
| `sarathi_owner.api.manufacturing_inventory.get_manufacturing_inventory_summary` | `GET` | `owner` | `Work Order`, `Bin`, `Warehouse` | `filters` (company, warehouse, status) | Read | Leaf warehouse enforcement (`is_group=0`), mutual exclusivity of status counts. | **PASS** |
| `sarathi_owner.api.executive_risks.get_executive_risks_summary` | `GET` | `owner` | `Sales Invoice`, `Project`, `Work Order` | `filters` (company, review_days) | Read | Strict integer review days (0-90), company isolation, severity deduplication. | **PASS** |
| `sarathi_owner.api.owner_dashboard.get_owner_summary` | `POST` | `owner` | `Company`, `Sales Invoice`, `GL Entry` | `filters` | Read | Scoped SQL reads, finance role gate on detailed ledger queries. | **PASS** |
| `sarathi_owner.api.owner_dashboard.clear_owner_cache` | `POST` | `admin` | System cache | None | Mutate (Cache) | Administrator / System Manager only; rejects standard business users. | **PASS** |
| `sarathi_owner.api.module_catalog.get_catalog` | `GET` | `owner` OR `production` | Desk workspace / module profile | None | Read | Filters workspaces by user role; strips finance modules if caller lacks finance role. | **PASS** |

### 4.2 Production Management Control Tower APIs (`sarathi_visibility`)

| Endpoint Route | HTTP Method | Required Capabilities | Native DocType Checks | Input Parameters | Read / Mutate | Security Protections | Test Status |
|---|---|---|---|---|---|---|---|
| `sarathi_visibility.api.factory_overview.get_factory_overview` | `GET` | `production` | `Work Order`, `Workstation`, `Project` | `filters` (company, project, workstation, status, review_days, reference_at) | Read | Parameter allowlist validation, company link verification, review days bound (0-90), date bounds ordering. | **PASS** |
| `sarathi_visibility.api.material_readiness.get_material_readiness` | `GET` | `production` | `Work Order`, `Work Order Item`, `Bin` | `filters` (company, warehouse, readiness_status) | Read | Cumulative stock demand allocation preventing false ready status; leaf warehouse filtering. | **PASS** |
| `sarathi_visibility.api.production_pipeline.get_production_pipeline` | `GET` | `production` | `Work Order`, `Job Card`, `Operation` | `filters` (company, stage, dates) | Read | Strict status allowlist, scoped Work Order reads, date bounds ordering. | **PASS** |
| `sarathi_visibility.api.workstations.get_workstation_downtime` | `GET` | `production` | `Workstation`, `Downtime Entry` | `filters` (company, workstation, status, dates) | Read | Status allowlist, open incident duration clipping, rejection of unknown filter keys. | **PASS** |
| `sarathi_visibility.api.quality_rework.get_quality_inspections` | `GET` | `production` | `Quality Inspection`, `Item` | `filters` (company, status, dates) | Read | Native inspection status allowlist, parameter validation, scoped query. | **PASS** |
| `sarathi_visibility.api.quality_rework.get_scrap_rework_summary` | `GET` | `production` | `Job Card`, `Work Order` | `filters` (company, dates) | Read | Division-by-zero protection on scrap rate, scoped reads. | **PASS** |
| `sarathi_visibility.api.quality_rework.get_subcontracting_orders` | `GET` | `production` | `Purchase Order`, `Supplier` | `filters` (company, supplier, dates) | Read | Restricts to `is_subcontracted='Yes'`, masks monetary purchase rates for non-finance callers. | **PASS** |
| `sarathi_visibility.api.production_exceptions.get_production_exceptions` | `GET` | `production` | `Work Order`, `Job Card`, `Bin` | `filters` (company, severity, status) | Read | Severity ranking (Critical > High > Medium > Low), duplicate exception suppression. | **PASS** |
| `sarathi_visibility.api.work_orders.get_work_orders` | `GET` | `production` | `Work Order` | `filters`, `start`, `page_length` | Read | Strict pagination limits, status allowlist, company verification. | **PASS** |
| `sarathi_visibility.api.accounting.get_accounting_dashboard` | `POST`/`GET`| `production` | `Company`, `Account`, `GL Entry` | `filters` | Read | Strips all monetary fields via `operational_payload` unless caller has `finance` capability. | **PASS** |
| `sarathi_visibility.api.subcontracting.get_subcontracting_summary` | `POST`/`GET`| `production` | `Purchase Order`, `Supplier` | `filters` | Read | Strips subcontract values for non-finance callers. | **PASS** |
| `sarathi_visibility.api.agent_chat.chat` | `POST` | `production` | Custom agent session | `message`, `session_id` | Read / Execute | User-namespaced conversations; prohibits arbitrary command execution or privilege escalation. | **PASS** |

### 4.3 Shop-Floor Supervisor & Operator Workboard APIs (`sarathi_visibility`)

| Endpoint Route | HTTP Method | Required Capabilities | Native DocType Checks | Input Parameters | Read / Mutate | Security Protections | Test Status |
|---|---|---|---|---|---|---|---|
| `sarathi_visibility.api.shopfloor.get_assigned_jobs` | `GET` | `shop` OR `production` | `Job Card`, `ToDo`, `Employee` | `filters`, `start`, `page_length`, `sort_by`, `sort_order` | Read | Operator restricted to open `ToDo` assignments or linked `Employee`. Strict pagination, sort field allowlist. | **PASS** |
| `sarathi_visibility.api.shopfloor.get_current_operation` | `GET` | `shop` OR `production` | `Job Card`, `Job Card Time Log` | None (reads caller context) | Read | Automatically isolates to authenticated operator's active running operation. | **PASS** |
| `sarathi_visibility.api.shopfloor.get_next_jobs` | `GET` | `shop` OR `production` | `Job Card`, `ToDo` | `filters`, `limit` | Read | Returns upcoming waiting operations for caller only; limits to maximum 20. | **PASS** |
| `sarathi_visibility.api.shopfloor.get_shop_floor_summary` | `GET` | `shop` OR `production` | `Job Card`, `ToDo` | `filters` | Read | Summary counts aggregate exclusively over caller's eligible Job Cards. | **PASS** |
| `sarathi_visibility.api.shopfloor.get_shopfloor_workboard` | `GET` | `shop` OR `production` | `Job Card`, `ToDo`, `Workstation` | `filters` | Read | Combined payload honoring operator vs supervisor vs manager scope. | **PASS** |
| `sarathi_visibility.api.shopfloor.get_supervisor_team_overview` | `GET` | Supervisor OR Manager | `Employee`, `Job Card`, `Workstation` | `filters` | Read | Rejects operators with `PermissionError`. Discovers team via direct reports, workstation perms, and ToDos. | **PASS** |
| `sarathi_visibility.api.shopfloor.start_job` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card` | Mutate | Rejects unassigned Job Card, rejects submitted (`docstatus=1`) or cancelled (`docstatus=2`), idempotent. | **PASS** |
| `sarathi_visibility.api.shopfloor.record_job_progress` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card`, `completed_qty`, `pending_qty`, `process_loss_qty`, `remarks` | Mutate | Rejects unassigned Job Card, validates negative quantities, bounds over-reporting (>150% of target). | **PASS** |
| `sarathi_visibility.api.shopfloor.pause_job` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card` | Mutate | Rejects unassigned Job Card, requires `Work In Progress` state, closes active time log. | **PASS** |
| `sarathi_visibility.api.shopfloor.resume_job` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card` | Mutate | Rejects unassigned Job Card, requires paused state, opens new time log. | **PASS** |
| `sarathi_visibility.api.shopfloor.stop_job` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card`, `completed_qty` | Mutate | Rejects unassigned Job Card, requires active time log, records completion. | **PASS** |
| `sarathi_visibility.api.shopfloor.complete_job` | `POST`/`GET`| `shop` OR `production` | `Job Card`, `Job Card Time Log` | `job_card`, `completed_qty`, `pending_qty`, `process_loss_qty`, `auto_submit` | Mutate | Rejects unassigned Job Card, verifies target quantity fulfillment, handles submit permissions. | **PASS** |

---

## 5. Security Boundary & Attack Scenario Verification

### 5.1 Direct API Access Without Authentication or Valid Session
- **Attack Scenario:** Calling whitelisted APIs using `curl` or Postman without session cookies or with `user="Guest"`.
- **Enforcement:** `require_session()` checks `not frappe.session.user or frappe.session.user == "Guest"` and verifies `User.user_type == "System User"`.
- **Result:** **PASS**. `MockPermissionError` is raised immediately before reading any business records.

### 5.2 Horizontal Privilege Escalation — Calling APIs Across Personas
- **Attack Scenario:** Machine Operator or Production Manager calling Owner financial APIs (`get_finance_kpis`).
- **Enforcement:** `require_capability("owner")` and `require_capability("finance")` check user roles against `OWNER_ROLES` and `FINANCE_ROLES`.
- **Result:** **PASS**. Callers lacking both roles receive `PermissionError` ("This resource or action is not available for your permissions").

### 5.3 Object-Level Access — Requesting Unassigned Job Cards
- **Attack Scenario:** Operator A passes Operator B's Job Card identifier (`JC-OPERATOR-B`) to `get_assigned_jobs`, `start_job`, or `record_job_progress`.
- **Enforcement:** `authorize_and_get_job_card` verifies `doc.name in eligible_jc_names`, where `eligible_jc_names` is strictly computed from Frappe `ToDo` assignments allocated to `frappe.session.user` or the operator's linked `Employee` record.
- **Result:** **PASS**. Direct manipulation of document IDs triggers `deny()` (`PermissionError`). Target document is never modified.

### 5.4 Cross-Company Parameter Tampering
- **Attack Scenario:** User authorized for Company A specifies `filters={"company": "Company A", "project": "PROJ-COMPANY-B"}`.
- **Enforcement:** `validate_filters` inspects linked document records (`check_record("Project", value)`) and asserts `proj.company == result["company"]`.
- **Result:** **PASS**. Discrepancies between linked entities and the filter company trigger immediate denial.

### 5.5 Filter Tampering and SQL Injection
- **Attack Scenario:** Supplying extra unexpected dictionary keys, SQL comments (`--`, `/*`), or stacked queries (`; DROP TABLE`).
- **Enforcement:**
  - `_extra(extra)`: Rejects unknown query keyword arguments with `ValidationError`.
  - `_identifier(val)`: Rejects empty strings, control characters, or identifiers > 140 chars.
  - `scoped_sql`: Uses regex validation to reject non-SELECT queries, SQL comments, UNION statements, and semicolons.
- **Result:** **PASS**. Malicious queries fail closed with `PermissionError` or `ValidationError`.

### 5.6 Data Leakage and Monetary Masking
- **Attack Scenario:** Production Manager without finance capability calls `get_accounting_dashboard` or `get_subcontracting_orders` to view unit costs or company inventory valuation.
- **Enforcement:** `operational_payload` recursively traverses response dictionaries and lists, stripping all monetary keys (`rate`, `amount`, `stock_value`, `grand_total`, `net_total`, `total_costing_amount`, etc.) and Currency columns.
- **Result:** **PASS**. Verified that non-finance users receive operational quantities and statuses only, with zero financial leakages.

### 5.7 Mutation Authorization on Terminal / Canceled States
- **Attack Scenario:** Calling `start_job` or `record_job_progress` on a Job Card that is already `Completed` (`status="Completed"`, `docstatus=1`) or `Cancelled` (`docstatus=2`).
- **Enforcement:** `start_job` asserts `doc.docstatus != 1` and `doc.docstatus != 2`; `record_job_progress` asserts `doc.docstatus == 0`.
- **Result:** **PASS**. Terminal states cannot undergo illegal transitions.

---

## 6. Vulnerabilities Discovered and Minimal Fixes Made

During implementation of automated security tests, one defect was discovered and resolved:

### Defect: `NameError: name '_' is not defined` in `resolve_supervisor_team_scope`
- **Location:** [sarathi_visibility/sarathi_visibility/api/shopfloor.py](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L9)
- **Root Cause:** When an unauthorized operator called `get_supervisor_team_overview()`, line 1119 attempted to raise `frappe.throw(_("Supervisor or Production Manager access required for Team Overview."), frappe.PermissionError)`. However, `_` had not been imported from `frappe` at the top of `shopfloor.py`. This caused a `NameError`, which `@read_errors` converted into a generic `DashboardReadError` (500) rather than a clean `PermissionError` (403).
- **Minimal Fix Applied:** Added `from frappe import _` to the imports in `shopfloor.py`.
- **Verification:** Security test `test_supervisor_team_overview_denies_direct_operator_call` now cleanly confirms that operators are denied with `PermissionError`.

---

## 7. Summary of Security Test Execution Results

| Test Category | Suite / Class | Checks | Result | Execution Time |
|---|---|---|---|---|
| **Dashboard Route Access** | `TestDashboardRouteAccess` | 3 | **PASS** | 0.003s |
| **Role Capabilities & Direct APIs** | `TestRoleCapabilitiesAndDirectAPIAccess` | 9 | **PASS** | 0.008s |
| **Object-Level Authorization** | `TestObjectLevelAuthorization` | 4 | **PASS** | 0.005s |
| **Company & Organizational Scope** | `TestCompanyAndOrganizationalScope` | 2 | **PASS** | 0.004s |
| **Filter Tampering & Validation** | `TestFilterTamperingAndInputValidation` | 6 | **PASS** | 0.004s |
| **Data Leakage & Monetary Masking**| `TestKPIDataLeakageAndMonetaryMasking` | 2 | **PASS** | 0.003s |
| **Shop-Floor Mutation Security** | `TestShopFloorMutationAuthorization` | 4 | **PASS** | 0.005s |
| **Total Security Tests** | `test_role_permissions_api_access.py` | **30** | **PASS** | **0.032s** |

All 30 automated security tests passed with zero failures and zero regressions.

---

## 8. Confirmation of Strict Scope Control

- **Task DASH-032 is complete.**
- **Tasks DASH-033 through DASH-036 were strictly NOT started.**
- No core Frappe or ERPNext files were modified.
- All pre-existing user code and working tree changes remain intact.
