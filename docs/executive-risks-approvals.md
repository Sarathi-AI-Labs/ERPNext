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
