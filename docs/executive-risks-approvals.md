# DASH-013: Executive Risks, Approvals, and Drill-downs Documentation

- **Task ID:** DASH-013
- **Task Name:** Build Executive Risks, Approvals, and Drill-downs
- **Parent Epic:** DASH-007 — Owner & Executive Dashboard
- **Priority:** P1 — High
- **Primary Application:** `sarathi_owner`
- **Dashboard Route:** `/desk/sarathiownertower`
- **Status:** **Implemented & Verified**

---

## 1. Overview & Objective

DASH-013 implements a permission-aware executive action and exception view on the Sarathi Owner & Executive Dashboard (`/desk/sarathiownertower`). It highlights critical business exceptions, surfaces pending workflow approvals genuinely assigned to or authorized for the logged-in user, and provides reliable, permission-aware drill-down links to standard ERPNext records.

Unlike operational task lists, the Executive Risks view is designed for owner and executive management to answer:
- Which customer payments are overdue or due soon?
- Which project deadlines or milestone tasks are slipping?
- Which customer deliveries are overdue or at risk?
- Which production commitments or Work Orders face active material shortages?
- Which workflow approval decisions are awaiting the logged-in user?
- What exact ERPNext transaction record needs to be investigated or acted upon?

---

## 2. Supported Alert Categories & Trigger Rules

Every alert is computed dynamically from authorized ERPNext transactional records using verified business rules and field definitions. No placeholder records, fake counters, or arbitrary risk scores are used.

| Category | Record Type | Trigger Rule | Evaluated Fields | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **Receivables** | `Sales Invoice` | Submitted invoice (`docstatus=1`) with `outstanding_amount > 0` and `due_date < ref_date`. Overdue by >=30 days. | `outstanding_amount`, `due_date`, `docstatus`, `company`, `customer` | **Critical** |
| **Receivables** | `Sales Invoice` | Submitted invoice (`docstatus=1`) with `outstanding_amount > 0` and `due_date < ref_date`. Overdue by <30 days. | `outstanding_amount`, `due_date`, `docstatus`, `company`, `customer` | **High** |
| **Receivables** | `Sales Invoice` | Submitted invoice (`docstatus=1`) with `outstanding_amount > 0` and `ref_date <= due_date <= ref_date + review_days`. | `outstanding_amount`, `due_date`, `docstatus`, `company`, `customer` | **Medium** |
| **Projects** | `Project` | Project in status `On hold` (`docstatus < 2`). | `status`, `company`, `customer`, `project_name` | **High** |
| **Projects** | `Project` | Project with `status='Open'`, `expected_end_date < ref_date`, overdue by >=30 days. | `expected_end_date`, `status`, `company`, `percent_complete` | **Critical** |
| **Projects** | `Project` | Project with `status='Open'`, `expected_end_date < ref_date`, overdue by <30 days. | `expected_end_date`, `status`, `company`, `percent_complete` | **High** |
| **Projects** | `Project` | Project with `status='Open'`, `ref_date <= expected_end_date <= ref_date + review_days`. | `expected_end_date`, `status`, `company`, `percent_complete` | **Medium** |
| **Projects** | `Task` | Milestone task (`is_milestone=1`, `status not in ('Completed', 'Cancelled')`) with `exp_end_date < ref_dt`. | `is_milestone`, `status`, `exp_end_date`, `project` | **High** |
| **Deliveries** | `Sales Order` | Submitted Sales Order line (`docstatus=1`) with `delivered_qty < qty` and order `status='On Hold'`. | `delivered_qty`, `qty`, `status`, `company`, `customer` | **High** |
| **Deliveries** | `Sales Order` | Submitted Sales Order line (`docstatus=1`) with `delivered_qty < qty` and `delivery_date < ref_date`, overdue by >=14 days. | `delivery_date`, `delivered_qty`, `qty`, `docstatus` | **Critical** |
| **Deliveries** | `Sales Order` | Submitted Sales Order line (`docstatus=1`) with `delivered_qty < qty` and `delivery_date < ref_date`, overdue by <14 days. | `delivery_date`, `delivered_qty`, `qty`, `docstatus` | **High** |
| **Deliveries** | `Sales Order` | Submitted Sales Order line (`docstatus=1`) with `delivered_qty < qty` and `ref_date <= delivery_date <= ref_date + review_days`. | `delivery_date`, `delivered_qty`, `qty`, `docstatus` | **Medium** |
| **Manufacturing** | `Work Order` | Active Work Order (`docstatus=1`, status in `('Not Started', 'In Process', 'Submitted')`) with target completion date in past. | `status`, `planned_end_date`, `expected_delivery_date`, `qty`, `produced_qty` | **High** |
| **Manufacturing** | `Work Order` | Active Work Order with target completion date within `review_days`. | `status`, `planned_end_date`, `expected_delivery_date`, `qty`, `produced_qty` | **Medium** |
| **Manufacturing** | `Work Order Item` | Raw material requirement (`required_qty - transferred_qty > 0`) exceeding warehouse available stock (`actual_qty - reserved_qty`). | `required_qty`, `transferred_qty`, `actual_qty`, `reserved_qty`, `source_warehouse` | **Critical** (if WO is overdue/due soon) / **High** |

---

## 3. Severity Model & Prioritization Logic

Alerts follow a strict, deterministic four-tier severity model:

1. **Critical:** Direct financial or operational halt requiring immediate executive intervention:
   - Receivables overdue by 30+ days.
   - Active customer deliveries overdue by 14+ days.
   - Open projects overdue by 30+ days.
   - Material shortages actively blocking overdue or imminent Work Orders.
2. **High:** Significant overdue commitments or recorded blockers:
   - Receivables overdue by 1 to 29 days.
   - Projects or deliveries on recorded hold.
   - Milestone tasks overdue.
   - Work Orders past target completion date.
   - Raw material shortages on active Work Orders.
3. **Medium:** Approaching deadlines within the configurable review window:
   - Receivables due within review window (default: 7 days).
   - Projects completing within review window.
   - Customer deliveries promised within review window.
   - Work Orders scheduled to finish within review window.
4. **Informational:** Non-critical operational notices or low-severity exceptions.

### Deterministic Sorting Order
Alerts are prioritized deterministically:
1. `severity` ascending: `Critical (0) -> High (1) -> Medium (2) -> Informational (3)`.
2. `days_due` ascending (most overdue first: e.g., `-75` before `-14` before `+3`).
3. Tie-breaker by `title` alphabetical.

---

## 4. Pending Approvals & Assignment Mechanism

### Mandatory Scoping Rule
**Only approval actions genuinely pending and assigned to, or explicitly authorized for, the logged-in user are shown.**

### Implementation Details
The backend inspects:
1. **`tabWorkflow Action`**:
   - `status = 'Open'`
   - User assignment check: `user = frappe.session.user` OR role assignment check: `role IN frappe.get_roles(frappe.session.user)`.
   - Read permission verification: Underlying document must be readable by the current user via `frappe.has_permission(reference_doctype, 'read', reference_name)`.
   - Company restriction: If the underlying document contains a `company` field, it must match the active filter company.
2. **`tabToDo`**:
   - `status = 'Open'`
   - `allocated_to = frappe.session.user`
   - Read permission verification on referenced document.
   - Company boundary enforcement.

### Read-Focused Workflow Behavior
Opening an approval navigates directly to the native ERPNext Form route (`['Form', doctype, name]`). The dashboard does not bypass workflow transition validations or allow arbitrary transitions from unauthorized generic endpoints, preserving full ERPNext audit trails.

---

## 5. Reliable Drill-Down Navigation

Every alert and approval card provides a direct, permission-respecting drill-down route:
- **Sales Invoice:** `['Form', 'Sales Invoice', inv_name]`
- **Project:** `['Form', 'Project', project_name]`
- **Task:** `['Form', 'Task', task_name]`
- **Sales Order:** `['Form', 'Sales Order', so_name]`
- **Work Order:** `['Form', 'Work Order', wo_name]`
- **Workflow Document:** `['Form', reference_doctype, reference_name]`

All links use `frappe.set_route(route)` within Desk, ensuring standard ERPNext permission checks, session timeouts, and audit logging apply.

---

## 6. Duplicate Suppression & Lifecycle

- **Deduplication:** A composite hash key `(category, record_type, affected_record, title)` is computed for every evaluated alert. Duplicate items across multi-line joins (e.g. multiple items in a single Sales Order or repeated bin joins) are suppressed so each distinct exception is alerted exactly once.
- **Dynamic Lifecycle:** Alerts are computed dynamically upon each request from the current database state. When an invoice is paid (`outstanding_amount = 0`), a project is marked completed, a material transfer entry is submitted, or a workflow action is completed, the alert disappears immediately upon the next refresh. No permanent stale alert rows are written to disk.

---

## 7. Automated Testing & Validation Evidence

### Test Suite (`sarathi_owner/sarathi_owner/tests/test_executive_risks.py`)
Ran full test suite inside Docker backend (`frappe_docker_main-backend-1`):
```text
Ran 49 tests in 16.011s
OK
```

Key test cases verified:
1. `test_capability_and_company_denial`: Access denied for non-owners (`manager`, `operator`, `supervisor`, `unrelated`, `finance_only`) and unauthorized company scopes.
2. `test_strict_filter_validations`: Unknown filter keys, bad dates, inverted date ranges, non-existent customer/project IDs, and invalid severity/category values strictly rejected with `ValidationError`.
3. `test_read_errors_sanitization`: Internal errors sanitized via `@read_errors` without database trace leakage.
4. `test_payment_risks_overdue_and_settled`: Submitted invoices with `outstanding_amount > 0` trigger alerts; settled invoices (`outstanding_amount <= 0`) are 100% excluded.
5. `test_project_risks_active_and_completed`: Open overdue projects trigger; completed or cancelled projects do not.
6. `test_production_and_shortage_risks`: Active Work Orders and material shortages trigger; completed/cancelled orders do not.
7. `test_approval_visibility_and_scoping`: Unassigned or unauthorized workflow actions excluded.
8. `test_deduplication_and_sorting`: Proper deduplication and strict severity ordering verified.
9. `test_homepage_integration`: Homepage API returns `executive_risks` cleanly alongside finance, sales, projects, and manufacturing summaries.

### Live Reconciliation (`sarathi_owner/sarathi_owner/tests/reconcile_executive_risks.py`)
Ran database reconciliation against all 9 configured companies in ERPNext:
```json
{
  "company": "SarathiAILabs",
  "reference_date": "2026-10-14",
  "total_risks_detected": 6,
  "critical_count": 1,
  "high_count": 1,
  "medium_count": 4,
  "pending_approvals_count": 0,
  "receivable_alerts_count": 2,
  "db_overdue_invoices_count": 1,
  "overdue_receivables_diff": 0,
  "project_alerts_count": 2,
  "db_overdue_projects_count": 1,
  "overdue_projects_diff": 0,
  "delivery_alerts_count": 1,
  "mfg_alerts_count": 1,
  "status": "RECONCILED"
}
```
**Discrepancies:** Exactly 0 across all companies.

### Responsive Browser Audit (`sarathi_owner/sarathi_owner/tests/audit_executive_risks_browser_local.py`)
Tested across 9 viewports in Chromium:
- 360x800: `horizontal_scroll: false`
- 390x844: `horizontal_scroll: false`
- 480x900: `horizontal_scroll: false`
- 767x1000: `horizontal_scroll: false`
- 768x1000: `horizontal_scroll: false`
- 1023x1000: `horizontal_scroll: false`
- 1024x1000: `horizontal_scroll: false`
- 1440x1000: `horizontal_scroll: false`
- 844x390: `horizontal_scroll: false`

- **JavaScript Errors:** 0
- **HTTP Errors:** 0
- **Screenshots saved:** `docs/executive-risks-evidence/*.png`

---

## 8. Unsupported or Unconfigured Alert Categories

- **Machine Breakdown / Telemetry Stop:** Not implemented under DASH-013. IoT telemetry and workstation breakdowns belong exclusively to the Production Management Control Tower and are not inferred from ERPNext records without configured machine sensors.
- **Customer Sentiment / NPS Risk:** Not implemented as no standard ERPNext customer sentiment fields exist in this installation.

---

## 9. Deliverable Files Summary

| File Path | Description |
| :--- | :--- |
| `sarathi_owner/sarathi_owner/api/executive_risks.py` | Core backend API: validation, risk detection, approval lookup, severity sorting, pagination. |
| `sarathi_owner/sarathi_owner/api/homepage.py` | Homepage API adapter: mounts `executive_risks` under `get_homepage`. |
| `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js` | UI rendering: risk filters, KPI summary cards, business exceptions table, pending approvals queue, drill-downs. |
| `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css` | High-aesthetic styling: severity badges (`Critical`, `High`, `Medium`, `Informational`), responsive layout, touch targets. |
| `sarathi_owner/sarathi_owner/tests/test_executive_risks.py` | Automated security and unit tests for triggers, approvals, and permissions. |
| `sarathi_owner/sarathi_owner/tests/reconcile_executive_risks.py` | Database reconciliation script verifying zero discrepancy with ERPNext tables. |
| `sarathi_owner/sarathi_owner/tests/audit_executive_risks_browser_local.py` | Playwright browser audit verifying 9 viewports, zero horizontal scroll, and zero errors. |
| `docs/executive-risks-approvals.md` | Complete architectural, rule, and verification documentation. |
| `docs/executive-risks-evidence/` | Viewport screenshots and audit JSON report. |



and


# DASH-014 — Production Management Control Tower

## Task Information

- **Task ID:** DASH-014
- **Task Type:** Epic
- **Priority:** P1 — High
- **Module:** Production Control Tower
- **Recommended Assignee:** Gaurav
- **Primary Application:** `sarathi_visibility`
- **Expected Route:** `/desk/sarathicontroltower`
- **Objective:** Build a factory-wide Production Management Control Tower using actual ERPNext manufacturing data, providing production managers with visibility into Work Orders, Job Cards, production progress, material shortages, workstations, bottlenecks, quality issues, and subcontracting.

## 1. Project Context

I am developing custom dashboards inside my existing Sarathi AI Labs ERPNext/Frappe project.

Our system has three distinct dashboard experiences:

### Dashboard A — Owner & Executive Dashboard

- Application: `sarathi_owner`
- Expected route: `/desk/sarathiownertower`
- Audience: Company owner, directors, CEO, CFO, and authorized senior management.
- Purpose: Business performance, financial health, customer performance, projects, manufacturing summaries, inventory risks, and executive decisions.

### Dashboard B — Production Management Control Tower

- Application: `sarathi_visibility`
- Expected route: `/desk/sarathicontroltower`
- Audience: Factory manager, production manager, production planners, and authorized production coordinators.
- Purpose: Factory-wide production visibility, operational coordination, delays, material constraints, bottlenecks, quality, and production exceptions.

### Dashboard C — Shop-Floor Supervisor & Operator Dashboard

- To be implemented within the appropriate existing custom application, following the repository audit.
- Audience: Shop-floor supervisors and operators.
- Purpose: Assigned operations, current job status, large status indicators, permitted production reporting, and minimal navigation.

Each business company using our ERPNext solution has its own dedicated VPS and complete ERPNext installation. A company can manage multiple Customer records within its installation. Do not create a separate ERPNext installation for each Customer record.

The Production Management Control Tower must use real ERPNext data and existing manufacturing workflows.

## 2. Dashboard Objectives

The Control Tower should answer these questions:

1. What is happening across the factory right now, according to the available production records?
2. How many Work Orders are active, completed, delayed, or blocked?
3. Is actual production meeting the defined production target?
4. Which Job Cards and operations require attention?
5. Which materials are preventing or threatening production?
6. Which workstations have recorded issues or downtime?
7. Which quality and rework problems require intervention?
8. Which subcontracted operations are delayed?
9. Which production commitments are approaching their deadlines?
10. What should the production manager investigate first?

The Control Tower should support factory-wide coordination and direct navigation to relevant authorized ERPNext records.

It must not duplicate the Owner Dashboard's financial analysis or the Shop-Floor Dashboard's individual operator controls.

## 3. Mandatory Prerequisite Review

Before modifying code, inspect these tasks and deliverables where available:

- DASH-001 — Dashboard Foundation & Architecture.
- DASH-002 — Audit Existing Dashboard Apps and Routes.
- DASH-003 — Role and Permission Matrix.
- DASH-004 — KPI Dictionary and Metric Formulas.
- DASH-005 — Shared Responsive UI Components.
- DASH-006 — Permission-Aware Filter and Data Helpers.
- DASH-007 through DASH-013 — Owner & Executive Dashboard.

Inspect the actual repository and establish which components already exist and which remain incomplete. Do not assume previous tasks have been completed successfully.

Inspect the current `sarathi_visibility` application, page implementation, JavaScript, CSS, Python APIs, DocTypes, backend permissions, configuration, and test coverage.

Verify the installed or configured Frappe/ERPNext version and the actual manufacturing configuration, including relevant Work Order, Job Card, BOM, Routing, Workstation, Stock Entry, and material-reservation behavior.

Check the current Git branch and `git status`. Preserve all uncommitted changes and working features.

If a prerequisite or data source is missing, document the dependency instead of inventing a solution or fabricated data.

## 4. Strict Scope

This is the parent Epic for production management functionality.

Its child tasks are:

- DASH-015 — Build Factory Overview KPIs and Filters.
- DASH-016 — Implement Work Order and Job Card APIs.
- DASH-017 — Build Production Pipeline and Bottleneck Views.
- DASH-018 — Implement Material Readiness and Shortages.
- DASH-019 — Build Workstation and Downtime Views.
- DASH-020 — Implement Quality, Rework, and Subcontracting Views.
- DASH-021 — Build Production Exception and Escalation Queue.

Use this Epic as the master requirements document for these child tasks.

**For the current implementation run, work only on DASH-015.** Build the factory overview homepage and filters. Do not implement all the child-task features in one run.

If the homepage depends on later APIs, use existing verified data where available and document the remaining dependencies. Never substitute fake production values.

## 5. Recommended Control Tower Homepage

Design a professional factory-wide overview for managers.

### A. Header and Production Filters

Provide:

- Production Management Control Tower title.
- Concise factory operations description.
- Authorized company context.
- Reporting date or period.
- Production shift, if configured.
- Project filter, where a verified relationship exists.
- Customer filter, where supported by the actual data model.
- Workstation or production-area filter, where configured.
- Work Order status filter.
- Refresh control and last-updated timestamp where supported.

Do not introduce filters that cannot be applied to the relevant records.

All filters must be validated on the backend and must respect the user's authorized scope.

### B. Factory Production KPI Cards

Provide placements for approved summary indicators, where actual data sources are available:

- Active Work Orders.
- Planned versus actual production.
- Delayed Work Orders or operations.
- Open or in-progress Job Cards.
- Material shortages affecting production.
- Jobs approaching expected completion dates.

Each KPI must have a documented definition, reporting period, status rule, and source record.

Do not define an active Work Order count by simply counting every non-completed record without verifying the actual lifecycle and relevant statuses.

Do not display an invented production target or percentage.

### C. Production Summary

Provide a clear management-level view of production output and progress.

Where supported by reliable source data, show:

- Planned production quantity.
- Actual produced quantity.
- Production variance.
- Production achievement.
- Relevant period or shift.

Follow the approved KPI dictionary and actual manufacturing records.

Do not calculate production achievement using quantities with incompatible units or mismatched periods.

Do not claim live or shift-level performance if the required time-based records do not exist.

### D. Work Order Overview

Prepare the homepage area for a summarized Work Order view containing appropriate fields such as:

- Work Order identifier.
- Item.
- Planned quantity.
- Produced quantity.
- Status.
- Expected completion date.
- Project or Customer relationship, where verified.
- Operational exception, where supported.

Detailed Work Order and Job Card APIs are part of DASH-016. In this run, integrate existing verified APIs if available and otherwise document the integration point for DASH-016.

Do not build an entire detailed tracker or duplicate APIs as part of DASH-015.

### E. Production Exceptions Summary

Reserve a clear location for important production exceptions, such as delayed jobs or material blockers.

The complete exception and escalation logic belongs to DASH-021. For the current task, only integrate existing verified exceptions and document the future integration contract.

Do not invent severity values or pretend that unsupported blockers have been detected.

## 6. Production Pipeline — Architectural Requirement

The complete Control Tower should support visibility across the configured production process:

BOM and Routing → Work Order → Material Readiness → Job Cards and Operations → Manufacture / Stock Entry → Finished Goods.

Verify which stages and transitions are actually configured in the installation.

This pipeline is part of the overall Epic, not a requirement to implement the detailed pipeline under DASH-015. Its detailed production-flow visualization belongs to DASH-017.

## 7. Backend and Data Access Requirements

Follow the existing Frappe backend conventions.

Reuse permission-aware helpers from DASH-006, if implemented and appropriate.

Requirements:

- Use verified ERPNext DocTypes and fields.
- Enforce server-side authorization.
- Validate company, date, project, Customer, workstation, status, and other supported filters.
- Avoid N+1 queries and duplicate aggregation.
- Use appropriate pagination and result limits.
- Restrict responses to relevant fields.
- Follow actual Work Order and Job Card status behavior.
- Respect warehouse, reservation, and production scope.
- Avoid unrestricted privileged queries.
- Do not use hardcoded or fabricated business records.

If custom SQL is necessary, use safe query construction and separately validate permissions. Parameterized SQL alone does not make a query permission-safe.

Do not create a generic endpoint that exposes arbitrary ERPNext DocTypes or production records.

## 8. Responsive Design Requirements

The Control Tower must be mobile-compatible.

### Phone

- Stack production KPI cards.
- Show important delays and blockers first.
- Use collapsible or wrapping filters.
- Use concise production record cards where suitable.
- Prevent page-wide horizontal scrolling.

### Tablet

- Use compact two-column layouts where appropriate.
- Keep production records readable.
- Make filters and status indicators easy to operate by touch.

### Desktop and factory management displays

- Use a factory-wide overview.
- Present production KPIs and exceptions in a clear hierarchy.
- Support detailed tables and summary visualizations.
- Keep status, dates, and quantities readable.

Use shared responsive components from DASH-005 where available.

Do not confuse the manager's Control Tower with the separate Shop-Floor screen, which needs larger controls and substantially less navigation.

## 9. Test and Validation Requirements

Use the existing test framework and repository conventions.

For DASH-015, test where applicable:

- Homepage initialization and route behavior.
- Filter validation and consistent propagation.
- KPI definitions and empty data.
- Production-status classification.
- Permission-denied behavior.
- Responsive layout at phone, tablet, and desktop widths.
- Error, loading, and refresh states.
- Record links and existing page functionality.

Do not report production KPI reconciliation unless the values were compared against appropriate real ERPNext source records or reports.

If the actual ERPNext site or test fixtures are unavailable, record which checks could not be performed.

## 10. Strict Constraints

- Work only on DASH-015 in the current implementation run.
- Do not implement the complete DASH-014 Epic.
- Do not implement DASH-016 Work Order and Job Card APIs unless a minimal integration with an existing API is required.
- Do not implement the detailed pipeline from DASH-017.
- Do not implement material-shortage calculations from DASH-018.
- Do not implement workstation and downtime analysis from DASH-019.
- Do not implement quality and subcontracting views from DASH-020.
- Do not implement the full exception queue from DASH-021.
- Do not modify ERPNext/Frappe core files.
- Do not replace working application routes without justification.
- Do not invent machine telemetry or production status.
- Do not bypass permissions or ERPNext workflow validation.
- Do not add unnecessary frameworks or dependencies.
- Do not rewrite the entire application.
- Do not discard unrelated changes.
- Do not automatically proceed to DASH-016.

If an existing feature already meets the requirement, reuse it and document that decision.

## 11. Acceptance Criteria

DASH-015 is ready for review when:

1. The factory overview homepage is implemented within the existing application.
2. Production KPIs use verified data or clearly documented integration points for later tasks.
3. Global production filters are implemented and validated where applicable.
4. KPI definitions and status rules are documented.
5. Existing verified production APIs and shared components are reused appropriately.
6. Loading, empty, error, and refresh states are handled.
7. The page is responsive on desktop, tablet, and phone.
8. Backend authorization remains enforced.
9. Relevant tests are executed with their actual results documented.
10. Existing routes and working functionality are preserved.
11. No fabricated production metrics are shown.
12. Code changes remain limited to DASH-015.

## 12. Required Final Report

After completing the current child task, provide:

- Existing Control Tower functionality inspected and reused.
- Homepage sections and filters implemented.
- Actual source data used by each displayed KPI.
- Components, API methods, and files created or modified.
- Test commands executed and actual results.
- Responsive and runtime verification evidence, if available.
- Dependencies on DASH-016 through DASH-021.
- Known limitations and unresolved business rules.
- Confirmation that no unrelated features were implemented.
- Recommended next task from the backlog.

Do not claim the entire Production Management Control Tower Epic is complete while its child tasks remain unfinished.

**Final instruction: Use DASH-014 as the master scope, implement only DASH-015 in this run, inspect existing functionality first, make justified changes, test the result, document any dependencies, and stop. Do not automatically proceed to DASH-016 or implement unrelated dashboard functionality.**


and


# DASH-015 — Build Factory Overview KPIs and Filters

## Task Information

- **Task ID:** DASH-015
- **Task Name:** Build Factory Overview KPIs and Filters
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Priority:** P1 — High
- **Module:** Production Control Tower
- **Recommended Assignee:** Sayali
- **Primary Application:** `sarathi_visibility`
- **Expected Route:** `/desk/sarathicontroltower`
- **Objective:** Build a responsive, factory-wide production management homepage with verified production KPIs, operational filters, clear exception indicators, and links to relevant ERPNext records.

---

## 1. Project Context

I am developing custom dashboards inside my existing Sarathi AI Labs ERPNext/Frappe project.

We have three separate dashboard experiences:

1. **Owner & Executive Dashboard** — business performance, financial health, customers, projects, and management decisions.
2. **Production Management Control Tower** — factory-wide production output, Work Orders, Job Cards, material readiness, bottlenecks, and operational exceptions.
3. **Shop-Floor Supervisor & Operator Dashboard** — assigned production operations, large status indicators, production reporting, and minimal navigation.

This task is for the Production Management Control Tower.

The Control Tower is intended for factory managers, production managers, production planners, and authorized production coordinators.

Each company using our ERPNext solution has its own dedicated VPS and ERPNext installation. One company can manage multiple Customer records within that installation. Do not create a separate installation for every Customer record.

The dashboard must use actual ERPNext manufacturing data. Do not display fabricated production quantities, simulated job statuses, or hardcoded operational metrics as real data.

## 2. Strict Scope

Work ONLY on DASH-015.

Implement:

- The factory overview homepage layout.
- Production overview KPI cards.
- Appropriate reporting filters.
- Consistent filter behavior for implemented widgets.
- Production status indicators.
- Integration with verified existing APIs.
- Responsive loading, empty, error, and refresh states.
- Links to relevant authorized production records.
- Tests and documentation for this task.

Do not implement all the features in the DASH-014 Epic.

The detailed Work Order and Job Card APIs belong to DASH-016. Production pipeline and bottleneck views belong to DASH-017. Material readiness and shortage calculations belong to DASH-018. Workstation and downtime views belong to DASH-019. Quality, rework, and subcontracting belong to DASH-020. The production exception and escalation queue belongs to DASH-021.

You may integrate an existing verified API, but do not duplicate future child-task functionality.

---

## 3. Mandatory Prerequisite Review

Before modifying code:

1. Inspect DASH-001 architecture documentation, if available.
2. Review the DASH-002 application and route audit, if available.
3. Review DASH-003 role and permission requirements.
4. Review DASH-004 KPI definitions and formulas.
5. Inspect shared components from DASH-005, if implemented.
6. Inspect permission-aware helpers from DASH-006, if implemented.
7. Review the DASH-014 Control Tower architecture requirements.
8. Inspect the existing `sarathi_visibility` page and its current implementation.
9. Check the current Git branch, `git status`, uncommitted changes, and relevant tests.
10. Verify the configured Frappe/ERPNext version and the available manufacturing DocTypes, fields, and status values.

Do not assume that previous tasks have been completed merely because their GitHub issues exist.

Preserve current working functionality and all unrelated local changes. Verify actual source paths and route registration before making changes.

If a prerequisite is incomplete, document the dependency and continue only where a correct implementation is possible.

---

## 4. Factory Overview Homepage

Build a professional, manager-focused homepage within the existing Frappe Desk environment.

The homepage should provide an at-a-glance view of factory performance without reproducing all the detailed operational screens.

### A. Header

Include:

- Production Management Control Tower title.
- Short description of the factory overview.
- Authorized company context.
- Reporting-period controls.
- Applicable production filters.
- Refresh control where supported.
- Last-updated timestamp where reliable.

Do not claim real-time data unless the backend provides a reliable real-time source.

### B. Production KPI Cards

Create KPI card placements for the following measures, using approved formulas and available data.

#### 1. Active Work Orders

Count Work Orders included in the approved active-status definition.

Requirements:

- Verify actual status values and lifecycle behavior.
- Distinguish active work from draft, completed, closed, and cancelled records.
- Avoid duplicate counts caused by joins to Job Cards, operations, or stock transactions.
- Link to the corresponding authorized Work Order list or view.

#### 2. Planned Production

Display planned production quantity for the selected period where a reliable production-plan definition exists.

Requirements:

- Use the approved KPI dictionary.
- Verify the actual quantity field and period basis.
- Do not count the complete planned quantity repeatedly across multiple dates.
- Do not aggregate incompatible Items or units of measure into a meaningless total.

If reliable period-based planned quantity is unavailable, document the limitation rather than inventing a target.

#### 3. Actual Production

Display produced quantity according to the approved production-output definition.

Verify the relevant Work Order fields, Job Card behavior, manufacture transactions, and posting dates used by the installation.

Requirements:

- Exclude invalid, cancelled, or otherwise ineligible transactions according to the documented rules.
- Avoid double-counting the same output through related DocTypes.
- Apply date and other relevant filters consistently.
- Display the proper unit or aggregation scope.

#### 4. Production Achievement

If compatible planned and actual quantities exist, calculate:

`Production Achievement (%) = Actual Produced Quantity / Planned Production Quantity × 100`

Only apply this formula when both quantities cover a comparable period and compatible measurement scope.

Handle a zero planned quantity safely. Do not display a misleading percentage when the calculation is unsupported.

#### 5. Overdue Work Orders or Operations

Show the number of eligible overdue jobs based on documented date and status rules.

Verify the actual expected-completion fields and supported statuses.

Do not classify completed or cancelled jobs as overdue merely because their original due date is in the past.

Do not treat an open Job Card as automatically overdue without checking its documented due-date and lifecycle rules.

#### 6. Open Job Cards or Operations

If supported by the configured manufacturing process, show the count of open or in-progress operations.

Verify the actual DocType, statuses, and intended counting unit.

A count of Job Cards is not automatically a count of distinct Work Orders.

#### 7. Material Blockers

Reserve or populate a material-shortage summary only when a verified source exists.

Detailed shortage calculations belong to DASH-018. Reuse an existing verified API if available; otherwise, document the integration dependency and show a clearly identified unavailable state rather than a fabricated count.

### General KPI Card Requirements

Each card should provide:

- Clear metric label.
- Actual formatted value when available.
- Relevant unit or currency, if applicable.
- Reporting period or reference date.
- Optional concise explanatory text.
- Optional status indicator where justified.
- An appropriate drill-down destination when one exists.

Do not calculate business metrics independently in JavaScript components. The approved backend definitions must supply the values.

---

## 5. Production Summary Section

Below the KPI cards, provide a management-level summary of production progress.

Use existing verified data where available.

Potential components include:

- Planned versus actual production visualization.
- Production completion summaries.
- Distribution of eligible Work Order statuses.
- Concise list of overdue jobs.
- Short summary of jobs approaching their expected completion dates.

The visualization must clearly identify what each measure represents.

Requirements:

- Correct labels and units.
- Clear reporting-period context.
- Responsive charts.
- Accessible text and status descriptions.
- Consistent filter behavior.
- Loading, empty, and error states.
- Direct navigation to relevant authorized records.

Do not invent completion targets, status categories, blocker counts, or time-based performance.

If a chart requires a detailed API that has not been implemented, document its required data contract instead of writing a duplicate backend implementation.

---

## 6. Operational Filter Bar

Build the filters that are relevant to the factory overview.

### Required filter candidates

- Company context, where supported by existing permissions.
- Reporting start date.
- Reporting end date.
- Work Order status.
- Project, where the actual relationship exists.
- Customer, where the actual relationship exists.
- Workstation or production area, if configured.
- Production shift, if configured.

Do not force every filter onto every widget. Document which KPI each filter affects.

### Filter behavior

1. Provide clear default date ranges and document the default behavior.
2. Validate the start and end dates.
3. Support applying and clearing filters where appropriate.
4. Ensure connected widgets use consistent filter values.
5. Avoid filters that have no meaningful relationship to a metric.
6. Preserve supported filter state during refresh and drill-down navigation.
7. Prevent unnecessary repeated API calls.
8. Display loading feedback while updated data is retrieved.
9. Handle empty results and backend errors safely.
10. Keep the filters usable on phone, tablet, and desktop screens.

### Security

Use the permission-aware helpers from DASH-006 where available.

The frontend must never be the only place that enforces filtering or permissions.

Validate company, Project, Customer, Workstation, shift, status, and date parameters on the server. Only support filter types and relationships verified in the actual codebase and data model.

A user must not obtain unauthorized production records by changing a filter or directly invoking an API.

---

## 7. Production Status and Exception Indicators

Use consistent, text-based status indicators that reflect the actual ERPNext data.

Requirements:

- Use verified Work Order and Job Card statuses.
- Distinguish completed, in-progress, overdue, and cancelled states where supported.
- Use both text and appropriate visual styling.
- Never rely on color alone to communicate status.
- Do not invent new workflow states for presentation purposes.
- Do not display unsupported material-blocked or machine-stopped states as facts.
- Link to an underlying record or supported filtered view when possible.

The complete production exception prioritization and escalation behavior belongs to DASH-021. In DASH-015, focus on basic verified factory overview indicators and reusable entry points.

---

## 8. Navigation and Integration

Preserve the current `/desk/sarathicontroltower` route if it exists and is working.

Use existing Frappe navigation and the project's shared components.

Where a functional destination exists, provide links to:

- Work Order details or filtered lists.
- Job Card or operation records.
- Relevant supported production reports.
- Other verified operational views.

Do not create placeholder links, duplicate navigation systems, or empty pages that appear functional.

The Owner Dashboard should link to this Control Tower for detailed manufacturing investigation. The Shop-Floor Dashboard remains a distinct experience for supervisors and operators.

Do not modify either dashboard unnecessarily as part of this task.

---

## 9. Responsive Design Requirements

Mobile compatibility is mandatory.

### Phone — under 480 CSS pixels

- Stack KPI cards vertically or in a compact grid.
- Keep the most important production statuses visible.
- Use collapsible or wrapping filters.
- Use compact production summaries.
- Prevent unintended page-wide horizontal scrolling.

### Large phone and small tablet — 480–767 CSS pixels

- Use suitable one- or two-column KPI layouts.
- Make filter controls touch-friendly.
- Keep labels, quantities, dates, and statuses readable.

### Tablet — 768–1023 CSS pixels

- Use responsive two-column layouts where appropriate.
- Support touch-friendly navigation.
- Keep summary charts and production lists readable.

### Desktop — 1024 CSS pixels and above

- Use a factory-wide KPI and summary layout.
- Make efficient use of available space.
- Keep production trends and exception information easy to scan.

Use shared components from DASH-005 if implemented and suitable.

Do not confuse this manager-focused homepage with the Shop-Floor Dashboard. The latter requires larger operator controls and minimal navigation.

Test representative widths in the available browser or UI testing tools. Do not claim runtime visual validation if the page was not actually tested.

---

## 10. Backend, Data Accuracy, and Performance

Use the existing Frappe/Python backend and ERPNext records.

Requirements:

- Use approved KPI definitions.
- Verify DocTypes, field names, relationships, and status rules.
- Reuse existing production APIs where suitable.
- Enforce permissions server-side.
- Validate the filter contract.
- Avoid N+1 queries.
- Avoid duplicate aggregation.
- Use pagination for detail lists.
- Avoid returning entire DocTypes or unrestricted production records.
- Return only the fields required by the homepage.
- Provide consistent error and empty-result handling.
- Maintain clear refresh timestamps where available.

Do not modify ERPNext/Frappe core files or bypass its manufacturing validations.

Do not change the business calculation merely to produce an attractive chart.

If a KPI cannot yet be calculated correctly, document its missing dependency and do not substitute a fake value.

---

## 11. Testing Requirements

Use the existing test framework and conventions.

Test:

### Page and layout

- Route registration and page initialization.
- Layout with available KPI widgets.
- Empty, loading, unavailable, and error states.
- Refresh and last-updated behavior.
- Desktop, tablet, and mobile responsiveness.

### KPI and filter behavior

- Date-range filters.
- Work Order status filtering.
- Valid Project or Customer filters.
- Correct propagation of supported filters.
- Status inclusion and exclusion rules.
- Zero planned quantity.
- Empty production periods.
- Different Items and units of measure.
- Duplicate aggregation risks.

### Security and navigation

- Authorized manager access.
- Unauthorized page and API access.
- Attempts to change company or record identifiers.
- Permission-safe drill-down links.
- Invalid filter values.

### Regression

Verify that the existing route, production features, navigation, and relevant API contracts remain functional.

Run applicable tests and record actual results. If the ERPNext runtime or test fixtures are unavailable, document the limitation honestly.

---

## 12. Documentation Deliverable

Prefer updating existing project documentation. If no suitable location exists, create:

`docs/factory-overview-kpis-filters.md`

Document:

- Implemented homepage sections.
- KPI names and definitions.
- Source DocTypes and fields.
- Date and status rules.
- Supported filters and affected widgets.
- Filter validation and authorization behavior.
- Available and unavailable integrations.
- Navigation destinations.
- Responsive behavior.
- Tests and verification evidence.
- Dependencies on DASH-016 through DASH-021.
- Known limitations and unresolved requirements.

Clearly distinguish verified features from proposed integrations.

---

## 13. Strict Constraints

- Work ONLY on DASH-015.
- Do not implement the complete DASH-014 Epic.
- Do not implement the complete Work Order and Job Card APIs from DASH-016.
- Do not implement the detailed production pipeline from DASH-017.
- Do not implement shortage calculations from DASH-018.
- Do not implement workstation and downtime analytics from DASH-019.
- Do not implement quality, rework, and subcontracting views from DASH-020.
- Do not implement the full exception escalation queue from DASH-021.
- Do not implement the Shop-Floor Dashboard.
- Do not redesign the Owner Dashboard.
- Do not modify ERPNext/Frappe core files.
- Do not fabricate production figures or machine states.
- Do not bypass permissions or manufacturing validation.
- Do not add unnecessary frameworks or dependencies.
- Do not remove unrelated code.
- Do not automatically proceed to DASH-016.

If an existing component already satisfies a requirement, reuse it rather than duplicating it.

---

## 14. Acceptance Criteria

DASH-015 is ready for review when:

1. The existing Production Control Tower homepage is inspected and preserved.
2. The factory overview homepage is implemented at the verified route.
3. KPI cards use actual data or clearly documented integration points.
4. Production KPI formulas and status rules are documented.
5. Filter controls are implemented for supported dimensions.
6. Filters update relevant widgets consistently.
7. Backend validation and authorization remain enforced.
8. Existing shared UI components are reused where practical.
9. Loading, empty, unavailable, and error states work correctly.
10. Responsive layouts work on desktop, tablet, and phone.
11. Relevant automated tests and checks are executed, with actual results reported.
12. Documentation includes verified data sources and remaining dependencies.
13. Existing functionality and local changes are preserved.
14. The code changes are limited to DASH-015.

Do not mark the task complete if key metrics are fabricated or critical access and calculation checks remain unresolved.

---

## 15. Required Final Report

When finished, provide:

- Existing Control Tower features inspected and reused.
- Homepage sections and KPIs implemented.
- Exact source DocTypes, fields, and formulas used.
- Filters implemented and their supported scope.
- Exact files created or modified.
- API methods reused or changed.
- Tests executed and actual results.
- Responsive and runtime verification evidence.
- Dependencies on DASH-016 through DASH-021.
- Known limitations and unresolved decisions.
- Confirmation that no unrelated tasks were implemented.
- Recommended next task from the existing backlog.

**Final instruction: Inspect the actual repository first, implement only DASH-015, preserve existing functionality, use verified ERPNext data and approved KPI definitions, test the actual changes, document the results, and stop. Do not automatically proceed to DASH-016.**

and


# DASH-016 — Implement Work Order and Job Card APIs

## Task Information

- **Task ID:** DASH-016
- **Task Name:** Implement Work Order and Job Card APIs
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Priority:** P1 — High
- **Module:** Production Control Tower
- **Recommended Assignee:** Manoj
- **Primary Application:** `sarathi_visibility`
- **Expected Route:** `/desk/sarathicontroltower`
- **Objective:** Implement secure, reusable, paginated backend APIs for retrieving Work Order and Job Card information from actual ERPNext records, with validated filters, correct status handling, and reliable production quantities.

---

## 1. Project Context

I am developing a Production Management Control Tower inside my existing Sarathi AI Labs ERPNext/Frappe project.

We have three connected dashboards:

1. **Owner & Executive Dashboard:** Financial performance, customer analytics, projects, and high-level manufacturing summaries.
2. **Production Management Control Tower:** Factory-wide Work Orders, Job Cards, operations, production status, material shortages, and bottlenecks.
3. **Shop-Floor Supervisor & Operator Dashboard:** Assigned jobs, current operation status, large status indicators, and authorized production reporting.

This task belongs to the Production Management Control Tower.

The company operating ERPNext can have multiple Customer records inside its installation. Each company using our solution has its own dedicated VPS and ERPNext installation. Do not create a separate installation for each Customer record.

Expected existing custom application:

`sarathi_visibility`

Expected dashboard route:

`/desk/sarathicontroltower`

Verify these against the repository before implementation.

## 2. Strict Scope

Work ONLY on DASH-016.

Implement or improve backend APIs for:

1. Work Order list retrieval.
2. Work Order detail retrieval.
3. Job Card list retrieval.
4. Job Card detail retrieval.
5. Related operation and workstation information where configured.
6. Planned and produced quantity fields using verified ERPNext semantics.
7. Expected completion dates and status information.
8. Customer and Project relationships where explicitly available.
9. Server-side filtering, pagination, sorting, and permissions.
10. API tests and documentation.

Do not implement the full production pipeline view from DASH-017, material shortage calculations from DASH-018, workstation downtime analytics from DASH-019, quality/subcontracting screens from DASH-020, or the full exception queue from DASH-021.

Do not implement or redesign the entire dashboard in this task.

## 3. Mandatory Prerequisite Review

Before changing files, inspect these deliverables if available:

- DASH-001 — Dashboard Foundation & Architecture.
- DASH-002 — Audit Existing Dashboard Apps and Routes.
- DASH-003 — Role and Permission Matrix.
- DASH-004 — KPI Dictionary and Metric Formulas.
- DASH-005 — Shared Responsive UI Components.
- DASH-006 — Permission-Aware Filter and Data Helpers.
- DASH-014 — Production Management Control Tower Epic.
- DASH-015 — Factory Overview KPIs and Filters.

Inspect what has actually been implemented. Do not assume a previous task is complete merely because its GitHub issue exists.

Review the existing `sarathi_visibility` backend, Python API methods, JavaScript consumers, routes, DocTypes, custom fields, permissions, tests, and Frappe/ERPNext version.

Check the current Git branch and `git status`. Preserve uncommitted changes and existing working functionality.

If DASH-015 is incomplete, identify what data contract the homepage currently expects. Maintain compatibility where possible and document any required integration changes.

## 4. Inspect the Actual ERPNext Manufacturing Data Model

Inspect the installed version's implementation and metadata for:

- Work Order.
- Job Card.
- BOM.
- Routing, where configured.
- Workstation, where configured.
- Operation records or child tables.
- Relevant Stock Entry or manufacture records, where required to interpret quantities.
- Project and Sales Order relationships, where explicitly configured.

Verify actual field names, data types, links, lifecycle behavior, and status values from the code and metadata.

Do not invent fields, assume all installations use the same customizations, or infer relationships from document names.

Use the APIs and permission conventions supported by the installed Frappe/ERPNext version.

## 5. API A — Work Order List

Implement a focused, permission-aware API for retrieving Work Orders relevant to the authenticated user.

### Required behavior

Support only filters that the actual DocType and business logic can safely handle, such as:

- Work Order identifier.
- Item.
- Work Order status.
- Start or expected completion date, as appropriate.
- Project, where a verified relationship exists.
- Customer, where a verified relationship exists.
- Workstation or operation filters only where the relationship is supported.
- Other filters required by DASH-015 and documented by the project.

The exact API signature and module location must follow existing repository conventions.

### Suggested response fields

Return only necessary fields that actually exist and are authorized, potentially including:

- Work Order identifier.
- Item code and description.
- Status.
- Planned quantity.
- Produced quantity.
- Remaining quantity, if supported or safely derivable.
- Planned start date.
- Expected completion date.
- Relevant Project or Customer reference, where verified.
- Relevant production status information.
- Links or identifiers for authorized source records.

Do not expose every field simply because it exists in the DocType.

### Status handling

Document how active, completed, closed, cancelled, draft, and other statuses are treated.

Use the actual status lifecycle supported by the installed version. Do not invent status values or combine distinct states without an explicit requirement.

Avoid counting or returning duplicate Work Orders because of joins with Job Cards, operations, or stock transactions.

### Acceptance criteria

- Work Orders are retrieved from actual ERPNext records.
- Filters are validated and behave consistently.
- Status handling is documented.
- Results are paginated.
- Unauthorized records cannot be retrieved by changing filters or identifiers.
- Returned fields match the documented API contract.

## 6. API B — Work Order Detail

Implement a focused API for retrieving an individual Work Order and its relevant production details.

Requirements:

- Validate the supplied Work Order identifier.
- Check document-level permissions on the server.
- Return only fields needed by the Control Tower.
- Include supported quantity, status, date, Item, BOM, and relevant operation information.
- Include Project or Customer information only where an explicit relationship exists and the user is authorized to access it.
- Avoid returning the full document or unnecessary linked records.
- Handle missing, cancelled, or inaccessible records safely.
- Follow the project's established error-response conventions.

Do not allow a user to access a restricted Work Order by submitting its identifier directly to the API.

## 7. API C — Job Card List

Implement a focused API that retrieves Job Cards and relevant operation status for production monitoring.

### Required behavior

Support appropriate, verified filters, such as:

- Job Card identifier.
- Associated Work Order.
- Operation.
- Workstation.
- Job Card status.
- Relevant date filters.
- Authorized user or assignment filters, only where supported by the actual data model.

Use the real relationships between Job Cards, Work Orders, operations, and workstations.

### Suggested response fields

Where available and authorized, return:

- Job Card identifier.
- Associated Work Order.
- Operation.
- Workstation.
- Item.
- Status.
- Planned quantity.
- Completed or transferred quantity where applicable.
- Expected start or end information where available.
- Actual start/end or recorded time where available.
- Authorized assignee information where configured.

Verify every field against the actual installation. Do not substitute a similarly named field without confirming its meaning.

### Important quantity rules

A Job Card's quantity fields may represent different stages of the manufacturing process.

Inspect the installed implementation to establish the meaning of each selected field. Do not assume that a Job Card's completed quantity is equivalent to the finished-goods quantity produced by its entire Work Order.

Do not add quantities across multiple operations and present the sum as total finished production. The same Item may pass through multiple operations, which would cause double counting.

### Acceptance criteria

- Job Cards map to their correct Work Orders and operations.
- Status and quantity meanings are documented.
- Results are paginated and permission-aware.
- Operation-level data is not mistaken for finished-goods output.
- Duplicate aggregation is prevented.

## 8. API D — Job Card Detail

Implement a focused endpoint for an individual Job Card.

Return relevant details such as:

- Job Card identifier.
- Linked Work Order.
- Operation and workstation.
- Actual status.
- Planned quantity.
- Verified reported quantity fields.
- Applicable scheduling information.
- Existing operation or assignment data required by an authorized frontend.

Requirements:

- Verify the record exists.
- Enforce document-level permissions.
- Restrict the returned fields.
- Validate the current record state.
- Handle inaccessible or missing records safely.
- Avoid performing production actions as a side effect of a read request.

Do not assume that opening a Job Card implies permission to modify, submit, cancel, or complete it.

## 9. Production Quantities and Derived Values

Use the approved KPI dictionary from DASH-004 where it defines manufacturing quantities.

Where a derived field is required, document the exact formula and verify that it is meaningful for the underlying record type.

Potential examples include:

`Remaining Work Order Quantity = Planned Work Order Quantity − Valid Produced Quantity`

Use this only if it matches the installed Work Order fields and their business meaning.

Requirements:

- Distinguish planned, produced, completed-operation, rejected, and remaining quantities.
- Handle unit-of-measure consistency.
- Account for cancelled or reversed records where relevant.
- Do not count the same production output multiple times.
- Define whether quantities are cumulative or period-based.
- Avoid presenting a Work Order's lifetime quantity as output for a filtered date range.
- Handle zero and missing values safely.
- Do not fabricate a production target.

If a reliable derived quantity is not available from the data model, return the verified source fields and document the limitation rather than inventing a formula.

## 10. Permission-Aware Filtering

Reuse DASH-006 filter and data helpers if implemented and suitable.

Every API must:

- Authenticate the current user.
- Enforce role and DocType permissions.
- Enforce document-level access where relevant.
- Validate company and other filter values against authorized scope.
- Validate field names, statuses, dates, sorting, and pagination.
- Use an allowlist of supported filters and ordering fields.
- Return only necessary fields.
- Prevent access to restricted records through direct API requests.
- Avoid leaking restricted records through counts, aggregates, filter options, or related-record lookups.

Do not rely on frontend visibility to enforce permissions.

Do not use unrestricted privileged queries. If a privileged operation is necessary, document its justification, validate authorization independently, constrain the result set, and test negative cases.

Do not create a generic API that permits unrestricted retrieval of arbitrary DocTypes or fields.

## 11. Pagination, Sorting, and Performance

All detailed list APIs must have a documented pagination contract.

Requirements:

- Set a safe maximum page size.
- Validate limit, offset or page parameters.
- Validate sort fields and direction.
- Use stable deterministic ordering where practical.
- Avoid unbounded retrieval.
- Avoid N+1 query patterns.
- Fetch only required fields.
- Avoid duplicate results caused by one-to-many joins.
- Use efficient query or ORM methods supported by the installed version.
- Document performance concerns identified during implementation.

If an aggregate query is used, verify that permission restrictions apply to the underlying records and not just to the endpoint's frontend.

## 12. API Contracts and Error Handling

Document each API's:

- Method name and location.
- Input parameters.
- Supported filters.
- Returned fields and data types.
- Permission requirements.
- Pagination and sorting contract.
- Error behavior.
- Related DocTypes.
- Test coverage.

Follow established Frappe conventions.

Handle these cases safely:

- Invalid filters.
- Missing identifiers.
- Inaccessible records.
- Invalid pagination.
- Unsupported sorting.
- Empty result sets.
- Backend failures.

Do not expose stack traces, SQL statements, or internal secrets in the response.

Do not swallow exceptions and return false success responses.

Do not make read APIs modify business records.

## 13. Integration With the Control Tower

Inspect the current frontend and API contract used by DASH-015.

Integrate the new APIs with existing components only where necessary to make the current homepage or production lists functional.

Preserve the existing dashboard route and working functionality.

The APIs should prepare the foundation for:

- DASH-017 — Production Pipeline and Bottleneck Views.
- DASH-018 — Material Readiness and Shortages.
- DASH-019 — Workstation and Downtime Views.
- DASH-020 — Quality, Rework, and Subcontracting.
- DASH-021 — Production Exception and Escalation Queue.

Do not implement those complete features in this task.

Document the API contracts future child tasks can reuse.

Do not introduce frontend mock data as a substitute for missing backend results.

## 14. Testing Requirements

Use the existing repository's test framework and test conventions.

Create focused tests for Work Order and Job Card APIs.

### Work Order tests

- Valid authorized Work Order retrieval.
- Filtering by supported status and date fields.
- Invalid filter values.
- Completed, cancelled, and other verified statuses.
- Partial production.
- Missing or inaccessible identifiers.
- Company and record-level permissions.
- Pagination and sorting.
- Duplicate joins or aggregation risks.

### Job Card tests

- Correct association with a Work Order.
- Correct operation and workstation relationship.
- Different supported statuses.
- Verified quantity interpretation.
- Missing or inaccessible Job Cards.
- Invalid Work Order, operation, or workstation filters.
- Assignment and role restrictions where supported.
- Pagination and stable ordering.

### Security tests

- Authorized manager access.
- Access to only permitted records.
- Attempts to retrieve an unauthorized Work Order by changing its identifier.
- Attempts to retrieve an unauthorized Job Card directly.
- Attempts to use unsupported filters or sorting fields.
- Direct API requests without the required role.

### Regression tests

Verify that existing Control Tower routes and APIs still work and that the DASH-015 homepage remains compatible with any API contract changes.

Run applicable tests and report actual results. If the ERPNext runtime or test fixtures are unavailable, identify which checks remain unverified.

## 15. Documentation Deliverable

Update existing documentation if an appropriate file already exists. Otherwise, create:

`docs/work-order-job-card-apis.md`

Document:

1. API names and source files.
2. Input filters and validation.
3. Returned fields and their meanings.
4. Work Order and Job Card relationship handling.
5. Quantity semantics and derived calculations.
6. Status inclusion and exclusion rules.
7. Permission enforcement.
8. Pagination and sorting.
9. Error contracts.
10. Test cases and actual results.
11. Known limitations and dependencies for future tasks.

Use actual method signatures and source fields from the implementation. Do not document APIs or fields that have not been implemented.

## 16. Strict Constraints

- Work ONLY on DASH-016.
- Do not implement the entire DASH-014 Epic.
- Do not implement the detailed production pipeline from DASH-017.
- Do not implement material shortage calculations from DASH-018.
- Do not implement workstation and downtime analytics from DASH-019.
- Do not implement quality and subcontracting screens from DASH-020.
- Do not implement the full exception queue from DASH-021.
- Do not implement Shop-Floor reporting actions.
- Do not modify ERPNext/Frappe core files.
- Do not bypass permissions or manufacturing validation.
- Do not fabricate quantities or statuses.
- Do not add unnecessary frameworks or dependencies.
- Do not rewrite unrelated application code.
- Do not discard existing uncommitted changes.
- Do not automatically proceed to DASH-017.

If a required field or relationship is not configured, document the gap and use only verified information.

## 17. Acceptance Criteria

DASH-016 is ready for review when:

1. Work Order list and detail APIs are implemented or verified as existing and suitable.
2. Job Card list and detail APIs are implemented or verified as existing and suitable.
3. Filters are validated server-side.
4. Pagination and sorting are safe and documented.
5. Document-level permissions are enforced.
6. Returned fields match the documented API contracts.
7. Quantity fields use verified semantics.
8. Duplicate Work Order or production quantity aggregation is avoided.
9. API tests cover valid requests, invalid filters, and unauthorized access.
10. The existing Control Tower remains functional.
11. Future child tasks have documented API contracts to reuse.
12. Documentation reflects actual implementation.
13. The Git diff contains only changes justified by DASH-016.

Do not mark the task complete if critical security tests fail or returned quantities have unresolved meanings.

## 18. Required Final Report

When finished, report:

- Existing APIs inspected and reused.
- Work Order and Job Card APIs created or updated.
- Exact files created or modified.
- Supported filters, sorting, and pagination.
- Actual DocTypes and fields used.
- Quantity and status interpretation.
- Permission checks and negative tests performed.
- Test commands and actual results.
- DASH-015 integration changes.
- Known limitations and unresolved fields or relationships.
- Documentation location.
- Recommended next task from the existing GitHub backlog.

**Final instruction: Inspect the existing manufacturing implementation first, implement only DASH-016, preserve existing functionality, enforce server-side permissions, test the API contracts and production quantity semantics, document the result, and stop. Do not automatically proceed to DASH-017 or implement unrelated features.**


and


# DASH-017 — Build Production Pipeline and Bottleneck Views

## Task Information

- **Task ID:** DASH-017
- **Task Name:** Build Production Pipeline and Bottleneck Views
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Priority:** P1 — High
- **Module:** Production Control Tower
- **Recommended Assignee:** Sayali
- **Primary Application:** `sarathi_visibility`
- **Expected Route:** `/desk/sarathicontroltower`
- **Objective:** Build an interactive, responsive production pipeline and bottleneck view that helps production managers understand manufacturing progress, identify delayed operations, and investigate verified operational constraints using actual ERPNext data.

---

## 1. Project Context

I am developing a factory-wide Production Management Control Tower inside my existing Sarathi AI Labs ERPNext/Frappe project.

The system has three connected dashboard experiences:

1. **Owner & Executive Dashboard:** Business performance, finance, customers, projects, manufacturing summaries, and management decisions.
2. **Production Management Control Tower:** Factory-wide production execution, Work Orders, Job Cards, operation progress, material constraints, bottlenecks, and production exceptions.
3. **Shop-Floor Supervisor & Operator Dashboard:** Assigned operations, prominent status indicators, production reporting, and minimal navigation.

This task belongs to the Production Management Control Tower.

Each company using our ERPNext solution has its own dedicated VPS and ERPNext installation. One company can manage multiple Customer records inside its ERPNext installation. Do not create a separate ERPNext installation for each Customer record.

The Control Tower must use actual ERPNext records and configured manufacturing relationships. Do not fabricate production stages, dependencies, machine states, or bottleneck measurements.

## 2. Expected Business Outcome

The production manager should be able to answer:

- What stage has each production job reached?
- Which operations are completed, in progress, waiting, or delayed?
- Which jobs are waiting for a previous operation?
- Where is work accumulating?
- Which operations have missed or are approaching their expected completion time?
- Which jobs are blocked by a verified material, quality, or other recorded issue?
- Which Work Order or Job Card should be opened to investigate the problem?
- Which production bottlenecks deserve attention first?

The view should focus on operational visibility and investigation. It must not replace ERPNext's manufacturing transactions or configured workflows.

## 3. Mandatory Prerequisite Review

Before implementation, inspect the following tasks and deliverables if available:

- DASH-001 — Dashboard Foundation & Architecture.
- DASH-002 — Audit Existing Dashboard Apps and Routes.
- DASH-003 — Role and Permission Matrix.
- DASH-004 — KPI Dictionary and Metric Formulas.
- DASH-005 — Shared Responsive UI Components.
- DASH-006 — Permission-Aware Filter and Data Helpers.
- DASH-014 — Production Management Control Tower.
- DASH-015 — Factory Overview KPIs and Filters.
- DASH-016 — Work Order and Job Card APIs.

Inspect the actual repository and verify which functionality has been implemented. Do not assume a previous task is complete merely because its GitHub issue exists.

Inspect the installed or configured Frappe/ERPNext version, `sarathi_visibility`, the current Control Tower UI, Work Order and Job Card APIs, BOM and Routing configurations, operation relationships, permissions, relevant DocTypes, and existing tests.

Check the current Git branch and `git status`. Preserve uncommitted changes and existing working functionality.

If DASH-016 is incomplete, identify the actual available API contracts and implement only what is necessary for a correct pipeline view. Do not duplicate APIs unnecessarily.

## 4. Strict Scope

Work ONLY on DASH-017.

Implement:

1. A production pipeline visualization.
2. Work Order and operation progress across configured manufacturing stages.
3. Identification of operations waiting for prior operations where dependencies are verifiable.
4. Delayed-operation and overdue-job indicators.
5. Bottleneck summary views based on documented rules.
6. Filters for navigating and investigating production flow.
7. Drill-down links to authorized Work Orders and Job Cards.
8. Responsive UI for desktop, tablet, and mobile.
9. Focused tests and documentation.

Do not implement the complete material-shortage engine from DASH-018, workstation/downtime analytics from DASH-019, quality and subcontracting screens from DASH-020, or the complete exception escalation queue from DASH-021.

You may show a clear material or quality blocker when a reliable, existing source is available, but the detailed calculation and analysis belong to their respective child tasks.

## 5. Inspect the Actual Manufacturing Workflow

Before designing the pipeline, inspect how manufacturing is actually configured in this ERPNext installation.

Investigate relevant records such as:

- BOM.
- Routing, where configured.
- Work Order.
- Job Card.
- Operation and operation child tables where applicable.
- Workstation, where applicable.
- Relevant Stock Entry or manufacture records.
- Explicit operation or dependency relationships, if available.

Verify the actual DocTypes, field names, statuses, relationships, and process behavior in the installed version.

Do not assume every production flow uses the same routing or every Work Order has multiple Job Cards.

### Manufacturing pipeline

The proposed conceptual flow is:

**BOM / Routing → Work Order → Material Readiness → Job Cards / Operations → Manufacture or Stock Entry → Finished Goods**

Treat this as a conceptual overview, not an assumption that every stage exists as a separate record or mandatory transition in every installation.

Derive the actual pipeline stages from verified records and configured business rules.

If a required relationship or stage is not configured, document the limitation rather than inventing it.

## 6. Feature A — Production Pipeline Visualization

### Objective

Provide a clear representation of production work as it progresses through the configured manufacturing operations.

Choose a suitable visualization based on the actual data model and existing UI conventions, such as:

- A horizontal or vertical stage pipeline.
- A status-grouped board.
- A Work Order progress timeline.
- An operation-sequence view.
- Another appropriate representation that is supported by the actual records.

Do not introduce a visual pattern that cannot accurately represent the configured production process.

### Required information

Where available and authorized, provide:

- Work Order identifier.
- Item code or description.
- Planned production quantity.
- Produced quantity.
- Work Order status.
- Current or relevant operation.
- Operation status.
- Expected completion date.
- Project or Customer relationship where explicitly configured.
- Verified blocker information, where available.

Keep the overview readable. Detailed operation information can appear in a drill-down view.

### Stage handling

Document how each stage is determined and which source records are used.

Examples might include material readiness, operation execution, and manufacture completion, but only include stages that can be established from verified data.

Do not mark a job as completed just because every visible Job Card appears completed if the configured Work Order or manufacture lifecycle indicates otherwise.

Do not assume a missing Job Card means an operation is blocked.

### Acceptance criteria

- Pipeline stages reflect the actual configured production process.
- Work Orders and operations map to the correct source records.
- Status indicators are based on actual fields and verified rules.
- Users can open the relevant authorized records.
- Unsupported stages are documented rather than fabricated.

## 7. Feature B — Operation Sequence and Dependency Tracking

### Objective

Help managers understand which operations have been completed, which are active, and which are waiting for other operations.

Inspect the actual Routing, Job Card, and operation relationships.

Where a verified sequence or dependency exists, display:

- Previous operation.
- Current operation.
- Next operation, where determinable.
- Actual operation status.
- Expected completion information, where available.
- Relevant Work Order.
- Verified waiting or dependency information.

Use actual sequence or dependency fields. Do not infer a dependency solely from the order in which records happen to be returned by a query.

If a preceding operation is incomplete, do not automatically label the next operation as blocked unless the configured process establishes that dependency and the status rule supports it.

### Acceptance criteria

- Operation order is based on verified configuration.
- Waiting and blocked classifications have explicit rules.
- Unconfigured or unavailable dependencies are not invented.
- Multiple operations associated with a Work Order are handled without duplicate production quantities.
- Drill-downs open the relevant authorized Job Card or operation record.

## 8. Feature C — Delayed Jobs and Overdue Operations

### Objective

Make time-sensitive production work easy to identify.

Implement documented date and status rules for delayed or overdue work.

### Required checks

Inspect the actual fields used for:

- Planned start.
- Expected start or completion.
- Actual start and completion where recorded.
- Operation or Job Card status.
- Work Order status.
- Any configured production scheduling or dependency information.

Use the approved KPI dictionary and existing Control Tower definitions where available.

### Example overdue rule

An operation might be considered overdue when:

- A verified expected completion date is before the reference time.
- The operation is not completed or otherwise excluded under the approved rule.
- The operation is visible to the logged-in user.

This is an example only. Verify the actual fields, timezone/date behavior, and business definition before implementation.

Distinguish:

- An overdue operation.
- An overdue Work Order.
- An operation that has not yet started but is not overdue.
- An operation waiting for a prerequisite.
- A completed operation.
- A cancelled or excluded operation.

Do not classify every open operation as delayed.

### Display

Where data is available, show:

- Work Order and Job Card references.
- Operation.
- Workstation where configured.
- Expected completion.
- Actual status.
- Duration overdue, if a valid calculation can be made.
- Source record link.

### Acceptance criteria

- Overdue rules are explicitly documented.
- Completed and cancelled records are treated consistently.
- Date boundaries are tested.
- Delayed status is not inferred from incomplete data alone.

## 9. Feature D — Bottleneck Identification

### Objective

Help managers discover where production work is accumulating or becoming delayed.

A bottleneck should be identified from a documented operational rule and verified records, not from an arbitrary status color or invented score.

### Supported bottleneck signals

Where the data supports them, identify:

- Multiple jobs waiting for the same operation.
- Operations repeatedly delayed against their expected completion.
- Work waiting for an explicitly required predecessor operation.
- A cluster of overdue Job Cards at a particular stage.
- A production stage accumulating more waiting work than its configured process or planning rules permit.
- A verified material, quality, or other blocker supplied by a reliable data source.

For each bottleneck signal, document:

- Detection rule.
- Required source fields or records.
- Time window or reporting scope.
- Inclusion and exclusion rules.
- Whether the signal is a count, an overdue duration, or another defined metric.
- Known limitations.

Do not claim that a workstation is a bottleneck simply because many Job Cards reference it. The count must be interpreted within the configured process and applicable time or workload context.

Do not introduce an arbitrary weighted bottleneck score unless a defined and approved business rule exists.

### Suggested bottleneck summary

Where data supports the analysis, display:

- Operation or production stage.
- Number of affected jobs.
- Number of overdue operations.
- Oldest applicable waiting or overdue duration.
- Related Work Orders.
- Verified reason for the bottleneck.

Avoid counting the same Work Order multiple times when summarizing the number of affected jobs.

### Acceptance criteria

- Each bottleneck indicator has a documented formula or detection rule.
- The source data supports the stated reason.
- Duplicate counting is avoided.
- Managers can investigate the affected records.
- Unverified bottleneck hypotheses are not presented as confirmed findings.

## 10. Feature E — Filter and Search Controls

Reuse the existing Control Tower filters and permission-aware helpers wherever practical.

Support only filters that have a verified relationship to the underlying production data, such as:

- Work Order.
- Item.
- Production status.
- Operation.
- Workstation, where configured.
- Reporting date or due-date range.
- Project, where explicitly linked.
- Customer, where explicitly linked.
- Production shift, where configured.

Requirements:

- Validate filters on the server.
- Do not assume that a filter is applicable to every visualization.
- Ensure pipeline, delayed-job lists, and bottleneck summaries use consistent filters when they represent the same scope.
- Support clearing and refreshing filters where appropriate.
- Avoid unnecessary repeated API calls.
- Keep results permission-aware.
- Prevent unauthorized record access through direct API requests.

Do not create a new, unrelated global filtering system when the existing Control Tower already has a suitable filter implementation.

## 11. Backend and API Integration

Use the Work Order and Job Card APIs from DASH-016 where available and verified.

Requirements:

- Preserve existing API contracts where practical.
- Request only required data.
- Use permission-aware backend methods.
- Validate filters and document identifiers.
- Use efficient queries and aggregation.
- Avoid N+1 query patterns.
- Paginate large lists.
- Use verified fields and relationships.
- Avoid duplicate operation or Work Order counts.
- Provide clear loading, empty, and error states.
- Do not use frontend mock data as a substitute for missing backend information.

If an additional backend method is necessary specifically for pipeline relationships or bottleneck analysis, implement it within this task's scope, with explicit permissions, documented inputs and outputs, and relevant tests.

Do not build a generic endpoint that exposes arbitrary DocTypes or unrestricted manufacturing records.

If custom SQL is necessary, use safe parameterization and separately verify authorization. Parameterization alone does not make a query permission-safe.

Do not modify ERPNext/Frappe core files or bypass its manufacturing workflows.

## 12. UI and Navigation

Implement a production-focused interface that integrates with the existing `/desk/sarathicontroltower` page.

Use the shared components from DASH-005 if available.

Design priorities:

- Easy-to-understand pipeline stages.
- Clear separation between operation status and Work Order status.
- Strong visibility of overdue and waiting jobs.
- Concise bottleneck summaries.
- Direct navigation to source records.
- Useful loading, empty, error, and unavailable-data states.
- Consistent visual status labels.
- No reliance on color alone.
- No fake controls or nonfunctional links.

The manager should be able to move from a stage summary to the affected Work Order or Job Card without navigating through unnecessary screens.

Do not implement the Shop-Floor Dashboard's operator action buttons as part of this task.

## 13. Mobile Compatibility

The pipeline and bottleneck views must work on phone, tablet, and desktop.

### Phone

- Stack pipeline stages vertically or use a compact horizontal-scrolling component contained within the view.
- Avoid page-wide horizontal scrolling.
- Show important overdue and waiting jobs first.
- Use compact cards for affected operations.
- Keep dates, quantities, and status labels readable.

### Tablet

- Support touch-friendly filters and navigation.
- Use readable pipeline or status-board layouts.
- Avoid clipping longer Work Order and operation identifiers.

### Desktop

- Use the available width to display the pipeline and associated operation information clearly.
- Keep bottleneck summaries easy to scan.
- Support detailed records without overcrowding the overview.

Test the actual page at representative screen widths where tooling permits. Do not claim responsive runtime verification unless it was performed.

## 14. Validation and Testing

Follow the repository's existing test framework and conventions.

Create or update tests for:

### Pipeline correctness

- A Work Order with multiple operations.
- A Work Order with one operation.
- Completed and partially completed production.
- Missing or unconfigured Routing.
- Multiple Job Cards linked to the same Work Order.
- Correct mapping of operation sequence.
- Duplicate counts caused by joins.

### Dependency and delay rules

- A completed predecessor operation.
- An incomplete predecessor operation.
- An operation waiting for a prerequisite.
- A not-yet-due operation.
- An overdue operation.
- Completed and cancelled operations.
- Missing expected completion dates.
- Relevant date boundaries.

### Bottleneck analysis

- Multiple jobs waiting at a configured stage.
- Jobs delayed for different reasons.
- Multiple Job Cards belonging to the same Work Order.
- Empty workload.
- Unsupported or incomplete source data.
- Filters changing the bottleneck scope consistently.

### Security

- Authorized production-manager access.
- Unauthorized Work Order access.
- Unauthorized Job Card access.
- Direct API requests using modified record identifiers.
- Invalid filters and sorting options.
- Permission-safe aggregation.

### Regression

Verify that the existing Control Tower homepage, DASH-015 filters, and DASH-016 APIs remain functional.

Run the relevant tests and report actual results. If the ERPNext runtime or suitable test fixtures are unavailable, document what could not be verified.

## 15. Documentation Deliverable

Review existing project documentation first. If there is no appropriate location, create:

`docs/production-pipeline-bottlenecks.md`

Document:

1. The production pipeline visualization.
2. Source DocTypes and actual relationships.
3. Operation sequencing and dependency rules.
4. Overdue-job definitions.
5. Bottleneck detection rules and formulas.
6. Filters and their supported scope.
7. API methods and response contracts.
8. Permission enforcement.
9. Responsive design behavior.
10. Tests and validation evidence.
11. Missing configuration or unsupported stages.
12. Remaining dependencies on DASH-018 through DASH-021.

Clearly distinguish verified features from proposed or unavailable functionality.

## 16. Strict Constraints

- Work ONLY on DASH-017.
- Do not implement the entire DASH-014 Epic.
- Do not duplicate DASH-016 APIs unnecessarily.
- Do not implement the complete material-shortage engine from DASH-018.
- Do not implement workstation/downtime analytics from DASH-019.
- Do not implement quality and subcontracting views from DASH-020.
- Do not implement the full exception queue from DASH-021.
- Do not build the Shop-Floor Dashboard.
- Do not modify ERPNext/Frappe core files.
- Do not invent production dependencies, statuses, durations, or bottleneck scores.
- Do not claim live machine telemetry without a valid data source.
- Do not weaken permission checks.
- Do not introduce unnecessary dependencies.
- Do not restructure unrelated application code.
- Do not discard existing changes.
- Do not automatically proceed to DASH-018.

If a pipeline stage or bottleneck cannot be identified reliably, document the missing data and show only the supported information.

## 17. Acceptance Criteria

DASH-017 is ready for review when:

1. The production pipeline is based on verified manufacturing relationships.
2. Work Orders and operations are represented accurately.
3. Operation dependencies use actual configured sequencing or relationships.
4. Overdue and waiting statuses follow documented rules.
5. Bottleneck signals have defensible detection rules.
6. Counts avoid duplication across Job Cards and operations.
7. Filters are validated and applied consistently.
8. Backend permissions prevent access to unauthorized records.
9. Users can drill down into the relevant authorized ERPNext records.
10. The pipeline and bottleneck views work on desktop, tablet, and mobile.
11. Automated tests cover the important pipeline, dependency, date, and permission cases.
12. Documentation records formulas, rules, limitations, and validation evidence.
13. Existing dashboard functionality remains intact.
14. The Git diff contains only changes justified by DASH-017.

Do not mark the task complete if a key bottleneck is based on a guessed relationship or an undocumented threshold.

## 18. Required Final Report

When finished, provide:

- Existing pipeline and API functionality inspected and reused.
- Pipeline views implemented.
- Bottleneck detection rules and supporting fields.
- Exact files created or modified.
- Backend methods and API contracts changed.
- Relevant tests executed and actual results.
- Permission and responsive testing evidence.
- Known limitations and missing manufacturing configuration.
- Documentation location.
- Dependencies on DASH-018 through DASH-021.
- Recommended next task from the existing backlog.

**Final instruction: Inspect the actual manufacturing configuration first, implement only DASH-017, use verified Work Order and Job Card relationships, document every bottleneck rule, test authorization and correctness, and stop. Do not automatically proceed to DASH-018 or implement unrelated features.**