# DASH-014: Production Management Control Tower Architecture & Master Plan

- **Task ID:** DASH-014
- **Task Type:** Epic
- **Priority:** P1 — High
- **Module:** Production Control Tower
- **Primary Application:** `sarathi_visibility`
- **Expected Route:** `/desk/sarathicontroltower`
- **Status:** **Architecture & Requirements Established**

---

## 1. Executive Summary & Dashboard Responsibilities

The **Production Management Control Tower** is the central operational command center for Sarathi AI Labs' factory management ecosystem. It bridges executive strategy (from the Owner Dashboard) and shop-floor execution (from the Operator Dashboard), providing factory managers, production planners, and operational coordinators with real-time operational visibility across all factory operations.

```
+-----------------------------------------------------------------------------------+
|                           SARATHI AI LABS DASHBOARD SUITE                         |
+-----------------------------------------------------------------------------------+
|  1. Owner & Executive Dashboard       (/desk/sarathiownertower)                   |
|     - Financial KPIs, Cash Flow, Receivables, Sales Backlog, Executive Risks     |
|     - Target Audience: Company Owners, Managing Directors, CFOs                   |
+-----------------------------------------------------------------------------------+
|  2. Production Management Control Tower (/desk/sarathicontroltower) [DASH-014]    |
|     - Factory Output, Work Orders, Job Cards, Bottlenecks, Shortages, Quality     |
|     - Target Audience: Factory Managers, Plant Heads, Production Planners         |
+-----------------------------------------------------------------------------------+
|  3. Shop-Floor Supervisor & Operator  (/desk/sarathishopfloor)                    |
|     - Station Job Queue, Time Logs, Touch-Friendly Reporting, Operator Actions    |
|     - Target Audience: Floor Supervisors, Machine Operators, Assemblers          |
+-----------------------------------------------------------------------------------+
```

### Key Questions Answered by the Control Tower
1. **Factory Pulse:** What is happening across all workstations, departments, and lines right now?
2. **Order Velocity:** How many Work Orders are active, on track, overdue, or blocked?
3. **Plan vs. Actual:** Is daily and weekly production meeting planned throughput targets?
4. **Operation Health:** Which Job Cards are stalled, awaiting parts, or causing queue bottlenecks?
5. **Material Readiness:** Which raw material shortages are actively blocking scheduled Work Orders?
6. **Workstation Availability:** Which workstations have recorded operational stops or scheduled maintenance?
7. **Quality & Scrap:** Where are quality inspection failures and rework jobs concentrating?
8. **Subcontracting:** Which outsourced operations or supplier-held materials are delayed?
9. **Critical Exceptions:** What operational blocker or delivery commitment requires immediate management intervention?

---

## 2. Existing Application & Route Audit

### Verification Findings (Verified from Source & Live System)
| Architectural Component | Verified Implementation in Repository | Status |
| :--- | :--- | :--- |
| **Hosting Application** | `sarathi_visibility` (`apps/sarathi_visibility/`) | **Verified** |
| **Desk Route** | `/desk/sarathicontroltower` | **Verified** |
| **Page DocType Definition** | `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.json` | **Verified** |
| **Page Authorized Roles** | `Manufacturing Manager`, `Sarathi Super Admin`, `System Manager`, `Sarathi Owner` | **Verified** |
| **Page Lifecycle Script** | `sarathicontroltower.js` (uses `frappe.sarathiDashboardRuntime` to load dependencies and instantiate dashboard) | **Verified** |
| **Page HTML Template** | `sarathicontroltower.html` (mounts `.sd-dashboard` container, hero header, filter bar) | **Verified** |
| **Main JS Controller** | `public/js/sarathi_dashboard.js` (defines `frappe.SarathiIndustrialDashboard`) | **Verified** |
| **Active Stylesheets** | `public/css/sarathi_dashboard.css`, `public/css/sarathi_ui.css` | **Verified** |
| **Backend API Endpoints** | `sarathi_visibility.api.control_tower`, `sarathi_visibility.api.dashboard`, `sarathi_visibility.api.subcontracting` | **Verified** |
| **Permission Capability** | `sarathi_visibility.api.access.require_capability("production")` | **Verified** |

### Boundary Rules
- **ERPNext Core is Read-Only:** All data is queried from standard ERPNext DocTypes. Core schemas, tables, and controllers in `apps/erpnext` and `apps/frappe` must never be modified.
- **Side-Effect-Free Reads:** Fetching dashboard metrics must never trigger database writes, cache evictions, or status mutations.
- **Strict Role Scoping:** Only users with `production` capability can access Control Tower APIs.

---

## 3. ERPNext Manufacturing Data Inventory (Live System Inspection)

Inspection of the live database in the active Docker container (`frappe_docker_main-backend-1`, bench site `frontend`, ERPNext v16.33.0 / Frappe v16.31.0):

| DocType | Live Count | Purpose in Control Tower | Configuration Status |
| :--- | :---: | :--- | :--- |
| **Work Order** | **7** | Master production orders (2 Completed, 1 Draft, 4 Not Started) | **Active & Configured** |
| **Job Card** | **15** | Operation-level shop floor jobs (All 15 Open) | **Active & Configured** |
| **BOM** | **6** | Bills of Materials for robotic arms, battery packs, chassis | **Active & Configured** |
| **Routing** | **3** | Multi-operation sequence definitions | **Active & Configured** |
| **Workstation** | **6** | Bending, Coating, Finishing, Laser Cutting, Welding (2) | **Active & Configured** |
| **Workstation Type** | **6** | Workstation category mappings | **Active & Configured** |
| **Operation** | **6** | Standard manufacturing operations (Cutting, Welding, etc.) | **Active & Configured** |
| **Stock Entry** | **5** | Material issues, transfers, and manufacturing entries | **Active & Configured** |
| **Bin** | **14** | Stock balance, reserved qty, actual qty per leaf warehouse | **Active & Configured** |
| **Item** | **13** | Raw materials, subassemblies, and finished goods | **Active & Configured** |
| **Quality Inspection** | **4** | 1 Rejected (`PO-JOB00010`), 3 Accepted | **Active & Configured** |
| **Subcontracting Order** | **0** | Outsourced production orders | Schema Present (0 records) |
| **Subcontracting Receipt** | **0** | Inward receipts from subcontractors | Schema Present (0 records) |
| **Downtime Entry** | **0** | Workstation breakdown/stoppage logs | Schema Present (0 records) |
| **Plant Floor** | **0** | Factory floor structural groupings | Schema Present (0 records) |

---

## 4. Required Control Tower Sections & Functional Boundaries

The completed Control Tower Epic encompasses 7 functional areas, delivered via child tasks DASH-015 through DASH-021:

```
+-----------------------------------------------------------------------------------+
|                        CONTROL TOWER FUNCTIONAL ARCHITECTURE                      |
+-----------------------------------------------------------------------------------+
| [DASH-015] FACTORY OVERVIEW                                                       |
|  - Active WOs | Plan vs Actual | Open Job Cards | Output Velocity | Critical Blockers  |
+-----------------------------------------------------------------------------------+
| [DASH-016] PRODUCTION RECORDS (WORK ORDERS & JOB CARDS)                           |
|  - Server-side paginated, filterable Work Order grid & Job Card execution tables  |
+-----------------------------------------------------------------------------------+
| [DASH-017] PIPELINE & BOTTLENECK ANALYSIS                                         |
|  - BOM & Routing -> Material Readiness -> Job Card Execution -> Stock Entry -> FG |
+-----------------------------------------------------------------------------------+
| [DASH-018] MATERIAL READINESS & WAREHOUSE SHORTAGES                               |
|  - Work Order Item required vs. leaf warehouse available stock (actual - reserved)|
+-----------------------------------------------------------------------------------+
| [DASH-019] WORKSTATIONS & DOWNTIME                                                |
|  - Station capacity, queue depth, recorded ERPNext status, logged Downtime Entries|
+-----------------------------------------------------------------------------------+
| [DASH-020] QUALITY, REWORK & SUBCONTRACTING                                       |
|  - Inspection rejections, rework Job Cards, Subcontracting Orders & material sent |
+-----------------------------------------------------------------------------------+
| [DASH-021] PRODUCTION EXCEPTION & ESCALATION QUEUE                                |
|  - Prioritized operational alerts, overdue jobs, shortages, direct Desk drill-down|
+-----------------------------------------------------------------------------------+
```

### Detailed Functional Breakdown:

### A. Factory Overview (Child Task: DASH-015)
- **Objective:** High-level factory pulse for the manufacturing leadership team.
- **Core Metrics:**
  - `Active Work Orders`: `docstatus = 1` and `status in ('Not Started', 'In Process')`.
  - `Planned vs. Actual Production`: Aggregated planned quantity vs produced quantity across active orders.
  - `Overdue Work Orders`: Active orders where planned completion date is past the reference date.
  - `Open Job Cards`: Job Cards in `Open` or `Work in Progress` status.
  - `Material Shortage Lines`: Active Work Order requirements exceeding available stock.
  - `Critical Operational Exceptions`: Count of critical blocker alerts requiring supervisor/manager action.
- **Filter Controls:** Company (mandatory/scoped), Date Range, Project, Customer, Status, Workstation.

### B. Work Orders and Job Cards (Child Task: DASH-016)
- **Objective:** Comprehensive, permission-aware production transaction records.
- **Work Order Fields:** `name`, `production_item`, `item_name`, `qty`, `produced_qty`, `status`, `planned_start_date`, `planned_end_date`, `expected_delivery_date`, `project`, `sales_order`, `wip_warehouse`, `fg_warehouse`.
- **Job Card Fields:** `name`, `work_order`, `operation`, `workstation`, `for_quantity`, `total_completed_qty`, `transferred_qty`, `status`, `actual_start_date`, `total_time_in_mins`, `quality_inspection`.
- **Requirements:** Server-side pagination (default 25 rows), sorting, quick search, and direct Form drill-down.

### C. Production Pipeline and Bottlenecks (Child Task: DASH-017)
- **Objective:** End-to-end manufacturing flow visibility.
- **Flow Stages:**
  1. `BOM & Routing`: Engineering verification and standard cycle times.
  2. `Material Readiness`: Raw material staging in WIP/Source warehouses.
  3. `Operation Progress`: Sequential workstation progress via Job Cards.
  4. `Stock Entry (Manufacture)`: Work Order completion postings.
  5. `Finished Goods Receipt`: Staging in Target Warehouse.
- **Bottleneck Detection:** Identifies operations with high queue depth, overdue execution, or high process loss.

### D. Material Readiness and Shortages (Child Task: DASH-018)
- **Objective:** Prevent line stoppages by identifying material shortages before work starts.
- **Formula:**
  $$\text{Uncommitted Available Stock} = \max(0, \text{Bin.actual\_qty} - \text{Bin.reserved\_qty})$$
  $$\text{Net Shortage} = \max(0, (\text{Required Qty} - \text{Transferred Qty}) - \text{Uncommitted Available Stock})$$
- **Rules:** Evaluated per leaf warehouse and stock UOM. Never mix distinct UOMs or aggregate company-wide inventory indiscriminately.

### E. Workstations and Downtime (Child Task: DASH-019)
- **Objective:** Station loading, capacity utilization, and logged operational stops.
- **ERPNext Status:** Sourced from `tabWorkstation.status` and `tabWorkstation.disabled`.
- **Downtime Logs:** Sourced from `tabDowntime Entry` (`from_time`, `to_time`, `downtime`, `workstation`).
- **Telemetry Boundary:** Clearly distinguishes ERPNext-recorded data from real-time IoT/PLC sensor feeds. Telemetry is never fabricated.

### F. Quality, Rework, and Subcontracting (Child Task: DASH-020)
- **Quality & Rework:**
  - Sourced from `tabQuality Inspection` (`status = 'Rejected'`).
  - Linked to corrective Job Cards (`is_corrective_job_card = 1`).
- **Subcontracting:**
  - Sourced from `tabSubcontracting Order` and `tabSubcontracting Receipt`.
  - Tracks materials transferred to subcontractors (`supplied_items`) vs pending finished goods receipts.

### G. Production Exceptions and Escalations (Child Task: DASH-021)
- **Objective:** Prioritized operational exception triage.
- **Severity Levels:** `Critical` (line stoppage, severe overdue delivery), `High` (overdue Job Card, raw material shortage), `Medium` (upcoming deadline), `Informational`.
- **Actions:** Every exception links to the corresponding ERPNext record (`Work Order`, `Job Card`, `Quality Inspection`, `Subcontracting Order`).

---

## 5. Navigation & Sidebar Architecture

The completed Control Tower navigation will provide structured access to factory management views:

```
+-----------------------------------------------------------------------------------+
|                     CONTROL TOWER NAVIGATION STRUCTURE                            |
+-----------------------------------------------------------------------------------+
|  1. Factory Overview            (/desk/sarathicontroltower?tab=overview)          |
|  2. Work Orders                 (/desk/sarathicontroltower?tab=work_orders)       |
|  3. Job Cards & Operations      (/desk/sarathicontroltower?tab=job_cards)         |
|  4. Production Pipeline         (/desk/sarathicontroltower?tab=pipeline)          |
|  5. Materials & Shortages       (/desk/sarathicontroltower?tab=materials)         |
|  6. Workstations & Downtime     (/desk/sarathicontroltower?tab=workstations)      |
|  7. Quality & Rework            (/desk/sarathicontroltower?tab=quality)           |
|  8. Subcontracting              (/desk/sarathicontroltower?tab=subcontracting)   |
|  9. Finished Goods & Transfers  (/desk/sarathicontroltower?tab=transfers)         |
| 10. Production Reports          (/desk/sarathicontroltower?tab=reports)           |
+-----------------------------------------------------------------------------------+
```

### Implementation Rules
- Tabs are activated only when their backing child task implementation is complete.
- No dead links or non-functional placeholder tabs.
- Navigation state preserved across refreshes via clean URL query parameters.

---

## 6. Permissions, Multi-Company Scoping & Security

1. **Role Enforcement:**
   - Evaluates `require_capability("production")`.
   - Permitted roles: `Manufacturing Manager`, `Sarathi Super Admin`, `System Manager`, `Sarathi Owner`.
   - Unauthorized users receive HTTP 403 `PermissionError`.
2. **Company Scoping:**
   - Every database query enforces `WHERE company = %(company)s`.
   - Single-company deployments auto-select the company. Multi-company installations require explicit selection.
3. **Record-Level Field Masking:**
   - Operational users lacking financial permissions must not see financial totals, cost valuations, or profit margins on Work Orders or Job Cards (`can_finance()` check enforced).
4. **Input Sanitization:**
   - All filter parameters parsed and strictly validated against allowlists. Internal database exceptions sanitized via `@read_errors` without traceback leakage.

---

## 7. Responsive Design Requirements

Tested viewports and layout behavior across device tiers:

| Device Tier | Viewport Width | Layout Behavior & Constraints |
| :--- | :--- | :--- |
| **Mobile** | `360px` – `767px` | Stacked single-column cards; critical blockers at top; collapsible filter panel; touch targets $\ge 44\text{px}$; **0 page-wide horizontal scroll**. |
| **Tablet** | `768px` – `1023px` | Two-column grid layouts; touch-friendly filters; tabular data horizontally scrollable within container only. |
| **Desktop** | `1024px` – `1440px+`| Factory-wide command overview; 4-column KPI rows; persistent filter bar; rich operational detail tables. |

---

## 8. Child-Task Implementation Sequence

To maintain controlled, incremental progress and prevent monolithic code changes, DASH-014 must be implemented through its dedicated child tasks:

| Sequence | Task ID | Task Title | Primary Deliverables | Target Scope |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **DASH-015** | Build Factory Overview KPIs and Filters | Homepage KPI cards, global production filter bar, summary counters. | `sarathi_visibility` |
| **2** | **DASH-016** | Implement Work Order and Job Card APIs | Paginated Work Order & Job Card list APIs, status badges, drill-downs. | `sarathi_visibility` |
| **3** | **DASH-017** | Build Production Pipeline & Bottleneck Views | Stage-by-stage pipeline flow, operation balance, cycle time delays. | `sarathi_visibility` |
| **4** | **DASH-018** | Implement Material Readiness & Shortages | Leaf warehouse stock vs Work Order Item demand, UOM group cards. | `sarathi_visibility` |
| **5** | **DASH-019** | Build Workstation & Downtime Views | Workstation load, active jobs, recorded status, Downtime Entry logs. | `sarathi_visibility` |
| **6** | **DASH-020** | Implement Quality, Rework & Subcontracting | Quality Inspection rejections, rework jobs, Subcontracting Orders. | `sarathi_visibility` |
| **7** | **DASH-021** | Build Production Exception & Escalation Queue | Prioritized exception queue, severity rules, manager action links. | `sarathi_visibility` |

---

## 9. Acceptance Criteria for DASH-014 Epic

The complete DASH-014 Epic will be deemed complete when all child tasks (DASH-015 through DASH-021) have been implemented, tested, and verified against these criteria:

1. **Functional Homepage:** Factory Overview displays verified active, planned, and completed production totals.
2. **Accurate Transactions:** Work Orders and Job Cards accurately represent ERPNext database state with 0 discrepancies.
3. **Verified Formulas:** Material readiness, shortages, and output metrics adhere to documented formulas without UOM mixing.
4. **Honest Data Sourcing:** Station status reflects ERPNext records; no fabricated IoT/PLC real-time claims.
5. **Quality & Outsourcing:** Rejected quality inspections and subcontracted operations are visible with correct linkages.
6. **Exception Triage:** Production exceptions have deterministic triggers and direct Desk drill-down routes.
7. **Security & Permissions:** `production` capability strictly enforced; multi-company scoping enforced fail-closed.
8. **Responsive Excellence:** Zero page-wide horizontal scroll across mobile (360px), tablet (768px), and desktop (1440px).
9. **Automated Verification:** Comprehensive test suite passes with 0 failures; browser Playwright audit verifies clean rendering.
10. **Preserved Integrity:** Existing Owner Dashboard and Shop-Floor Dashboard remain completely unaffected.

---

## 10. Known Gaps & Unconfigured Features

1. **Downtime Entry Logs:** `Downtime Entry` DocType exists in ERPNext v16, but currently has 0 rows in the test database. Empty states must be cleanly handled.
2. **Subcontracting Transactions:** `Subcontracting Order` has 0 records currently. Test fixtures or seed data will be required during DASH-020 validation.
3. **Plant Floor DocType:** `Plant Floor` has 0 rows. Station grouping must default to `workstation_type` or factory department until plant floors are populated.
4. **Independent Work Orders:** Some Work Orders are created directly for stock without a linked `Project` or `Sales Order`. Dashboards must support both project-linked and standalone manufacturing orders.
