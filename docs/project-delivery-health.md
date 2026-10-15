# DASH-011 — Project and delivery health

## Pre-implementation audit

Reviewed DASH-001–010 foundations, native permissions, KPI dictionary PROJ-001–005/007–008 and SALES-004/005, shared UI/data helpers, the actual homepage/finance/sales services and tests. Branch feature/Gaurav_2 contains earlier dirty work; scratch/dash-011/baseline.json preserves all pre-task source hashes. Installed Frappe 16.31.0 / ERPNext 16.33.0 source was inspected read-only. No core/configuration/history edits are permitted.

| Component | Decision |
| --- | --- |
| Owner homepage, shared filters/cards/progress/record lists | Retain; add one executive health section |
| DASH-006 validation and native permission-aware lists | Reuse for scoped Project/Task reads; no privileged project totals |
| Project.percent_complete/method | Display native stored value only, with method/coverage; never invoke an updating controller during reads |
| Project.customer/company | Explicit native links, no name inference |
| Project statuses | Installed Open, On hold, Completed, Cancelled; docstatus<2, cancelled labelled separately |
| Task dates/milestone | exp_end_date is Datetime, is_milestone exists; no Tasks currently configured on this site |
| Dependencies | Task Depends On exists; critical-path/blocker inference is not established, so not computed |
| DASH-010 delivery backlog query | Reuse verified current quantity/status/project-fallback rules; delivery counts/health distinct from Project deadlines and revenue |
| Forecast risk | PROJ-005's manufacturing dependency/risk model remains unapproved; expose evidence, not a forecast or a guaranteed On track score |

Project portfolio cohort uses Company/explicit Customer/Project and optional expected_start_date bounds, matching the existing homepage's schedule-date filter. Current Project status/progress and expected_end_date are evaluated at a configurable site-local reference timestamp; Project/order dates compare its calendar date and Task Datetimes compare the timestamp. Default reference is server now and review window is an explicit configurable 7 days (0–90), a review horizon, not an approved prediction.

Project schedule labels: Completed and Cancelled are terminal, never overdue; open/held dated end before reference day -> Overdue; otherwise On hold -> At risk (recorded hold); open end within review horizon -> Due soon; open dated later end -> Not overdue; missing/invalid dates -> Unknown. Visible overdue incomplete Tasks provide separate recorded At risk evidence when their Project is not already overdue/terminal. Absence of warning evidence does not prove forecast health. Stored progress is labelled recorded; no Tasks/zero weights/missing or restricted Task coverage are disclosed. Cancelled Tasks follow the installed Project controller's progress method, while deadline lists exclude Completed/Cancelled/Template Tasks.

Delivery scope uses Company/Customer and explicit line Project with header fallback; optional global dates select order transaction-date cohort (not Project expected end), and existing delivery bounds select line delivery_date. Counts are at unique order/order-line grain; remaining stock qty=max(qty-delivered_qty,0)*conversion_factor by item+stock_uom. Submitted open undelivered lines only; closed/stopped/cancelled/completed/To Bill and drafts excluded; held demand separate. Money is not needed for delivery health and will not be returned. Native delivered counters incorporate Delivery Notes and applicable invoices; reads do not replay fulfillment. Delivery Note links are not inferred from names.

## Implemented definitions and calculation logic

### 1. Project portfolio and health classification
- **Cohort & Filters:** Company, Customer (explicit link), Project (explicit link), and global date range (`from_date` to `to_date` bounding `expected_start_date`).
- **Site Reference & Horizon:** Evaluated at a configurable site-local reference timestamp (`reference_at`, default `now_datetime()`) and review horizon window (`review_days`, default 7 days, bounded 0–90 days).
- **Classification Rules:**
  - **Completed / Cancelled:** Terminal states; excluded from deadline alerts, never overdue.
  - **Overdue:** Open or On Hold with valid `expected_end_date` strictly before reference date.
  - **At risk:** Open/held with recorded hold status, OR having accessible incomplete overdue Tasks, while not already classified as overdue.
  - **Due soon:** Open status with `expected_end_date` between reference date and `reference_date + review_days`.
  - **Not overdue:** Valid expected end date strictly after review horizon. (Clearly labelled: this is date compliance, not a guarantee or forecast of "On track").
  - **Unknown:** Missing, unparseable, or invalid schedule dates (e.g. expected start after expected end).
- **Project Progress:** Stored native `percent_complete` and `percent_complete_method` from ERPNext. No arbitrary re-averaging or synthetic formula is performed during reads. Progress warnings explicitly flag missing task coverage, zero visible weights, or manual methods.

### 2. Tasks & Milestones
- Native `Task` doctype queries enforce parent-child boundaries and native permissions (`has_permission`, `docstatus < 2`).
- Aggregates visible tasks, overdue tasks, due soon tasks, and milestones.
- Attention view filters incomplete tasks (`status not in ('Completed', 'Cancelled', 'Template')`) due within the review window.

### 3. Customer Delivery Commitments (Quantity Health)
- **Scope:** Submitted open Sales Orders (`docstatus = 1`, status not in `Closed`, `Stopped`, `Cancelled`, `Completed`, `To Bill`).
- **Held Demand:** `On Hold` orders separated into held demand.
- **Project Association:** Uses explicit `Sales Order Item.project` with header `Sales Order.project` fallback. No name-based inference.
- **Remaining Stock Quantity:** Calculated per line as `(qty - delivered_qty) * conversion_factor` grouped by `item_code` and `stock_uom`.
- **Financial Segregation:** Delivery health strictly measures quantity commitments and deadlines. Delivery value is not mixed into delivery health or represented as recognized revenue.
- **Line Health:**
  - `Overdue`: line `delivery_date < reference_date`
  - `Due soon`: line `delivery_date` within `[reference_date, reference_date + review_days]`
  - `Not overdue`: line `delivery_date > reference_date + review_days`
  - `Held`: parent order status is `On Hold`
  - `Unknown`: missing line `delivery_date`

---

## API and UI contracts

### Backend Method
`sarathi_owner.api.project_health.get_project_delivery_health(filters=None, **extra)`:
- GET-only, whitelist-protected, requires `owner` capability.
- Validates all filters against strict allowlists (`BASE_KEYS` and `FEATURE_KEYS`).
- Returns structured JSON payload containing:
  - `applied_filters`, `generated_at`, `reference_at`, `reference_date`, `review_days`
  - `projects`: `available`, `counts` (total, active, completed, cancelled, overdue, due_soon, held, at_risk, unknown), `health_partition`, `rows` (paginated), `tasks` (counts and attention rows), `basis`, `forecast`
  - `deliveries`: `available`, `counts` (open_orders, overdue_orders, due_soon_orders, held_orders, partially_delivered_orders, unknown_date_orders), `line_counts`, `quantities` (by item_code & stock_uom), `rows` (paginated), `basis`, `coverage`

### Owner Dashboard UI Integration
Implemented in `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js`:
- `renderProjectHealth`: Dedicated section rendered on the Owner Homepage.
- Displays executive KPI row: Relevant, Active, Completed, Cancelled, Overdue, Due Soon, At Risk, Unknown.
- Paginated Project health table with status badges, progress indicators with method labels, deadline counts, and drill-downs (`Form/Project`).
- Incomplete Tasks & Milestones view with attention filtering and direct Desk drill-down (`Form/Task`).
- Customer delivery commitments card grid, undelivered order-line list, and expandable remaining quantities by Item/UOM.

---

## Executed validation — 14 October 2026

| Validation Suite / Audit | Check Description | Result |
| --- | --- | --- |
| `test_project_health.py` | Native project counts, status rules, date boundaries, task weight/completion methods, cancelled task handling, pagination, security & capability gates, company/customer denial, delivery line partial/full fulfillment, held orders, and amended orders | **Passed (40 tests, 0 skipped, 44.82s)** |
| Combined Regression Suite | `ProjectNativeTests`, `ProjectSecurityTests`, `ProjectDeliveryTests`, `HomepageTests`, `FinanceSecurityTests` | **Passed (117 tests, 0 skipped, 41.75s)** |
| `reconcile_project_health.py` | Direct read-only comparison with native `Project`, `Task`, and `Sales Order` documents across whole company, customer scope, and 0-day window | **Passed: 0 differences across 100+ checks** |
| Direct HTTP Security Audit | `audit_finance_http_local.py` & `audit_sales_http_local.py` | **Passed: 100% checks passed, unauthorized access denied** |
| Playwright Browser Audit | `audit_project_health_browser_local.py` & `audit_homepage_local.py` | **Passed: 9 viewports (360–1440px), 0 overflow, 0 JS errors, 0 unexpected HTTP errors** |

---

## Live reconciliation results

Tested against populated live site `frontend` (Company `SarathiAILabs`):

| Scope | Project Portfolio (Total / Active / Overdue) | Delivery Commitments (Open Orders / Overdue) | Stored Progress Reconciliation | Discrepancies |
| --- | ---: | ---: | --- | :---: |
| **Whole Company** (`SarathiAILabs`) | 10 / 9 / 1 | 6 / 0 | 100% matched native `percent_complete` across all 10 projects | **0** |
| **Selected Customer** (`Tata Motors Passenger Vehicles Ltd`) | 1 / 1 / 0 | 0 / 0 | 100% matched native `percent_complete` | **0** |
| **Zero-Day Window** (`review_days: 0`) | 10 / 9 / 1 (0 due soon) | 6 / 0 (0 due soon) | 100% matched native `percent_complete` | **0** |

All source comparisons and line stock quantities (`AERO-MOUNT-01`, `DIE-FIXTURE-01`, `EV-BATTPACK-01`, `EV-CHASSIS-01`, `ROBOT-ARM-01`) reconciled identically with native ERPNext documents.

---

## Acceptance criteria fulfillment (DASH-011)

- [x] **Project overview metrics use verified source records and explicit rules:** Open, On hold, Completed, Cancelled, Overdue, and Due soon follow documented inclusion/exclusion rules.
- [x] **Project progress uses documented and defensible calculation:** Uses stored ERPNext `percent_complete` and displays method; no synthetic averages invented.
- [x] **Project deadline and status classifications are reproducible:** Overdue, Due soon, At risk, and Terminal statuses independently verified against native calendar dates.
- [x] **Customer filters rely on verified data relationships:** Explicit `Project.customer` link verified; no name-based heuristics.
- [x] **Delivery health uses actual order and delivery records:** Submitted open Sales Orders and lines, with stock UOM conversion factors.
- [x] **Partial fulfillment and relevant document statuses are handled correctly:** Native delivered counters and amended replacement orders tested.
- [x] **Project deadlines and customer delivery commitments remain distinct:** Project schedules and delivery line commitments are kept strictly in separate data structures and UI cards.
- [x] **Backend APIs validate filters and enforce permissions:** Parameter allowlists, company validation, and capability checks enforced.
- [x] **Aggregations avoid duplicate project counts and delivery values:** Separate query grains and sets ensure one project/order is never multiplied by one-to-many child rows.
- [x] **Drill-down links open authorized source records:** Form links to `Project`, `Task`, and `Sales Order` via `frappe.set_route`.
- [x] **Dashboard remains responsive on desktop, tablet, and mobile:** Tested across 9 viewport widths (360px to 1440px) with 0 horizontal overflow.
- [x] **Relevant tests executed and actual results recorded:** 117 tests passing; zero unexplained differences in live reconciliation.

