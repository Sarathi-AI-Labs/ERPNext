# Factory Overview KPIs and Filters (DASH-015)

## 1. Executive Summary

Task **DASH-015** delivers the factory-wide production homepage for the **Production Management Control Tower** (`sarathi_visibility`, route `/desk/sarathicontroltower`). It provides manufacturing managers, production controllers, and shop-floor leaders with at-a-glance visibility into factory performance, active operational volumes, deadlines, workstation engagement, and material readiness using actual ERPNext manufacturing records.

All operational values are computed server-side from live ERPNext DocTypes (`Work Order`, `Job Card`, `Workstation`, `Bin`, `Work Order Item`, `Item`). No simulated values, hardcoded quantities, or client-side business metrics are used.

---

## 2. Implemented Homepage Sections

The Factory Overview homepage is integrated into `/desk/sarathicontroltower` as a manager-focused operational command view:

1. **Header & Context Bar:**
   - Title: `Production Management Control Tower`
   - Subtitle: `Factory-wide production output, Work Orders, Job Cards, material readiness, and operational exceptions`
   - Real-time refresh control and live last-updated timestamp.
   - Reference date badge indicating current evaluation horizon.

2. **Factory Overview KPI Cards (7 Metrics):**
   - 7 responsive KPI cards rendered with `frappe.sarathiUI.kpi`:
     - **Active Work Orders** (count of active jobs)
     - **Planned Production** (planned quantity segregated by stock UOM)
     - **Actual Production** (actual completed quantity segregated by stock UOM)
     - **Production Achievement** (percentage completed with color-coded status)
     - **Overdue Work Orders** (active orders past target completion date)
     - **Open Job Cards** (active operations on the shop floor)
     - **Material Blockers** (active orders with raw material shortages)

3. **Production Status Distribution:**
   - Interactive status bar displaying counts for `Not Started`, `In Process`, `Completed`, `Stopped`, `Draft`, and `Cancelled`.
   - Clicking any status pill toggles filter scoping across the homepage.

4. **Planned versus Actual Output by Item Table:**
   - Displays each manufactured item, stock unit, active order count, planned quantity, completed quantity, achievement percentage with a progress bar, and clickable links to ERPNext Work Order documents (`['Form', 'Work Order', name]`).
   - Keeps quantities segregated by Stock UOM without mixing incompatible units.

5. **Operational Exceptions & Deadlines Grid:**
   - **Overdue Work Orders:** Lists overdue active orders with item details, target completion dates, days overdue badges, and direct drill-downs. When zero orders are overdue, displays a clean verified success banner.
   - **Approaching Due Date (Next 7 Days):** Displays active jobs scheduled for delivery within the review window, with remaining days indicators. When zero orders are approaching due date, displays an informative status banner.

---

## 3. KPI Definitions, Source DocTypes, and Mathematical Formulas

| Metric | Source DocType & Fields | Date / Lifecycle Rules | Mathematical Formula |
| :--- | :--- | :--- | :--- |
| **Active Work Orders** | `Work Order` (`docstatus`, `status`, `company`) | `docstatus = 1` AND `status IN ('Not Started', 'In Process')` | $\sum \text{Count}(\text{Work Order})$ |
| **Planned Production** | `Work Order` (`qty`, `stock_uom`, `docstatus`) | Scoped to active orders cohort | $\sum \text{Work Order.qty}$ (grouped by `stock_uom`) |
| **Actual Production** | `Work Order` (`produced_qty`, `stock_uom`, `docstatus`) | Authoritative completed quantity on Work Order | $\sum \text{Work Order.produced\_qty}$ (grouped by `stock_uom`) |
| **Production Achievement** | `Work Order` (`qty`, `produced_qty`) | Computed per item / single UOM cohort | $\frac{\text{Produced Qty}}{\text{Planned Qty}} \times 100\%$ (handled safely if planned = 0) |
| **Overdue Work Orders** | `Work Order` (`planned_end_date`, `expected_delivery_date`, `status`) | Active jobs where `target_date < reference_date` | $\sum [\text{target\_date} < \text{ref\_date}]$ |
| **Open Job Cards** | `Job Card` (`docstatus`, `status`, `work_order`, `workstation`) | `docstatus < 2` AND `status IN ('Open', 'Work In Progress')` | $\sum \text{Count}(\text{Job Card})$ |
| **Material Blockers** | `Work Order Item` (`required_qty`, `transferred_qty`) & `Bin` (`actual_qty`, `reserved_qty`) | Active Work Orders requiring stock where shortage > 0 | $\text{Uncommitted Stock} = \max(0, \text{actual} - \text{reserved})$<br>$\text{Shortage} = \max(0, (\text{req} - \text{trans}) - \text{stock})$ |

### Target Completion Date Fallback Rule
ERPNext `Work Order` records frequently omit `planned_end_date` while storing the customer deadline in `expected_delivery_date`. The backend resolution helper `get_target_completion_date(row)` evaluates `planned_end_date or expected_delivery_date` to prevent missing overdue or approaching jobs.

---

## 4. Operational Filter Bar and Scoping Matrix

| Filter Control | Parameter Key | Data Type / Validation | Scope & Affected Widgets |
| :--- | :--- | :--- | :--- |
| **Organization** | `company` | Link `Company`; permission-checked via `check_record` | Scopes all KPIs, status pills, item tables, and job lists. Auto-selects single company or user default. |
| **From Date** | `from_date` | ISO Date (`YYYY-MM-DD`); ordered $\le \text{to\_date}$ | Filters Work Orders by `planned_start_date >= from_date`. |
| **To Date** | `to_date` | ISO Date (`YYYY-MM-DD`); ordered $\ge \text{from\_date}$ | Filters Work Orders by `planned_start_date <= to_date 23:59:59`. |
| **Work Order Status** | `status` | Allowlist (`Active`, `All`, `Not Started`, `In Process`, `Completed`, `Stopped`, `Overdue`, `Due soon`, `Draft`, `Cancelled`) | Filters the active cohort, item progress table, and KPI summaries. |
| **Workstation** | `workstation` | Link `Workstation`; existence and permission checked | Scopes Work Orders and Job Cards having operations assigned to the selected workstation. |
| **Project** | `project` | Link `Project`; company and customer match enforced | Scopes Work Orders linked directly to the selected Project. |
| **Customer** | `customer` | Link `Customer`; verified via Sales Order / Project | Scopes Work Orders whose parent Project or Sales Order belongs to the customer. |
| **Review Window** | `review_days` | Integer $0 \le \text{days} \le 90$ (default 7) | Defines the horizon for "Approaching Due Date" orders. |

---

## 5. Security and Permission Matrix

1. **Role Enforcement:**
   - Evaluates `require_capability("production")`.
   - Authorized roles: `Manufacturing Manager`, `Sarathi Super Admin`, `System Manager`, `Sarathi Owner`.
   - Unauthorized callers receive HTTP 403 `frappe.PermissionError`.
2. **Server-Side Enforcement:**
   - Frontend controls are purely presentational; permissions and filters are strictly validated on the server.
   - `validate_factory_filters()` enforces strict parameter allowlists, preventing SQL injection and parameter tampering.
   - `@read_errors` sanitizes database exceptions without exposing raw stack traces.
3. **Multi-Company Scoping:**
   - Multi-tenant VPS isolation ensures queries are scoped with `WHERE company = %(company)s`. Single-company setups auto-default; multi-company setups mandate company selection.

---

## 6. Responsive Behavior Across Device Tiers

Tested with automated Playwright browser tests across 9 device viewports (from 360px to 1440px):

| Device Tier | Viewport Width | Tested Metrics | Layout Behavior |
| :--- | :--- | :--- | :--- |
| **Small Mobile** | 360×800 | `scrollWidth = 360` (overflow: False) | Stacked single-column KPI cards; compact table with internal scroll; touch targets $\ge 44\text{px}$. |
| **Standard Mobile** | 390×844 | `scrollWidth = 390` (overflow: False) | Single-column KPIs; status pills wrap cleanly; touch-friendly filters; screenshot saved. |
| **Large Mobile** | 480×900 | `scrollWidth = 480` (overflow: False) | Single-column KPIs; full item descriptions readable. |
| **Mobile Threshold** | 767×1000 | `scrollWidth = 767` (overflow: False) | Single-column transition boundary verified; zero horizontal scroll. |
| **Small Tablet** | 768×1000 | `scrollWidth = 768` (overflow: False) | Two-column KPI grid; side-by-side alert boxes; screenshot saved. |
| **Standard Tablet** | 820×1180 | `scrollWidth = 820` (overflow: False) | Two-column KPI grid; spacious progress bars. |
| **Tablet Threshold** | 1023×1000 | `scrollWidth = 1023` (overflow: False) | Two-column layout boundary verified. |
| **Desktop Threshold** | 1024×1000 | `scrollWidth = 1024` (overflow: False) | Full factory overview layout; 4-column KPI cards; 2-column exception boxes. |
| **Large Desktop** | 1440×900 | `scrollWidth = 1440` (overflow: False) | Full command tower layout; all tables fully expanded; screenshot saved. |

---

## 7. Automated Test Results and Verification Evidence

### A. Unit Tests (`sarathi_visibility.tests.test_factory_overview`)
Ran 11 unit tests in container via `frappe-bench`:
```
test_factory_overview_structure_and_kpis ... ok
test_factory_overview_summary_sections ... ok
test_factory_overview_workstation_filter ... ok
test_future_reference_date_overdue_detection ... ok
test_get_target_completion_date_fallback ... ok
test_unauthorized_access_denied ... ok
test_validate_filters_allowlist ... ok
test_validate_filters_date_bounds ... ok
test_validate_filters_invalid_status ... ok
test_validate_filters_invalid_workstation ... ok
test_validate_filters_review_days_range ... ok

----------------------------------------------------------------------
Ran 11 tests in 2.326s - OK
```

### B. Regression Tests (`sarathi_visibility.tests.test_dashboard`)
Ran 15 existing test suite checks in container:
```
Ran 15 tests in 62.751s - OK (skipped=1)
```

### C. Playwright Browser Audit (`audit_factory_overview_browser_local.py`)
Tested live across 9 viewports against `http://localhost:8080/desk/sarathicontroltower`:
```json
{
  "route": "/desk/sarathicontroltower",
  "title_verified": true,
  "kpis_verified": {
    "Active Work Orders": "4",
    "Planned Production": "138.0 Nos",
    "Actual Production": "35.0 Nos",
    "Production Achievement": "25.4%",
    "Overdue Work Orders": "0",
    "Open Job Cards": "10",
    "Material Blockers": "0"
  },
  "summary_verified": {
    "status_pills": [
      "Not Started: 4",
      "Completed: 2",
      "Draft: 1"
    ],
    "item_rows_count": 3,
    "overdue_box_present": true,
    "approaching_box_present": true
  },
  "filters_tested": {
    "workstation_options": 7
  },
  "viewports_tested": 9,
  "horizontal_overflow_detected": 0,
  "javascript_errors": [],
  "http_errors": []
}
```

### D. Captured Evidence Screenshots
- `docs/factory-overview-evidence/factory-overview-390.png` (Mobile 390px)
- `docs/factory-overview-evidence/factory-overview-768.png` (Tablet 768px)
- `docs/factory-overview-evidence/factory-overview-1440.png` (Desktop 1440px)

---

## 8. Dependencies on Subsequent Child Tasks (DASH-016 through DASH-021)

To strictly enforce scope boundaries, child task responsibilities remain separated:

- **DASH-016 (Work Orders and Job Cards):** Will provide detailed paginated table views, quick search, sort by sequence, and inline operational status updates. DASH-015 provides direct links into ERPNext desk forms as entry points.
- **DASH-017 (Production Pipeline and Bottlenecks):** Will calculate cycle times, workstation queues, and process losses across the 5 flow stages.
- **DASH-018 (Material Readiness and Shortages):** Will calculate granular component-level shortages across BOM hierarchies and reserve stock per transfer batch.
- **DASH-019 (Workstation and Downtime Analytics):** Will integrate machine logs, downtime entries, and OEE calculations.
- **DASH-020 (Quality, Rework, and Subcontracting):** Will display rejected inspection trends, scrap rates, and outsourced job tracking.
- **DASH-021 (Production Exception and Escalation Queue):** Will provide supervisor escalation workflows, resolution acknowledgments, and notification triggers.
