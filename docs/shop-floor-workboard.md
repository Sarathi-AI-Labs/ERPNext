# DASH-023 — Mobile-First Shop-Floor Workboard Documentation

## 1. Executive Summary & Architecture

- **Task ID:** DASH-023
- **Parent Epic:** DASH-022 — Shop-Floor Supervisor & Operator Dashboard
- **Priority:** P1 — High
- **Module:** Shop-Floor Execution
- **Primary Application:** `sarathi_visibility`
- **Dashboard Desk Route:** `/desk/sarathishopfloor`
- **Page Name:** `sarathishopfloor`
- **Backend API Module:** [`sarathi_visibility/sarathi_visibility/api/shopfloor.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py)
- **Page Definition JSON:** [`sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.json`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.json)
- **Page Context Python:** [`sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.py)
- **Page Lifecycle JS:** [`sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.js`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.js)
- **Page Template HTML:** [`sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.html`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathishopfloor/sarathishopfloor.html)
- **Frontend Controller Logic:** [`sarathi_visibility/sarathi_visibility/public/js/sarathi_shopfloor.js`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/js/sarathi_shopfloor.js)
- **CSS Stylesheet:** [`sarathi_visibility/sarathi_visibility/public/css/sarathi_shopfloor.css`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/css/sarathi_shopfloor.css)
- **Standalone Logic Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py)
- **Native Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_shopfloor.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_shopfloor.py)

DASH-023 delivers the first usable version of the **Shop-Floor Workboard** inside the Sarathi Industrial Control Tower ecosystem. Designed specifically for factory supervisors and shop-floor machine operators, it provides a clean, mobile-first, high-contrast operational queue of assigned jobs, current operations, workstation statuses, and verified production blockers without navigating standard ERPNext desk lists or exposing complex ERP forms.

---

## 2. Dedicated Role-Oriented Separation

The Sarathi Industrial Control Tower ecosystem maintains three distinct role-oriented workspaces:

```
+-----------------------------------------------------------------------------------+
|                        SARATHI AI LABS DASHBOARD ECOSYSTEM                        |
+-----------------------------------------------------------------------------------+
| 1. Owner & Executive Dashboard       (/desk/sarathiownertower)                    |
|    - Financial KPIs, Cash Flow, Receivables, Sales Backlog, Executive Risks       |
|    - Audience: Company Owners, Managing Directors, CFOs                           |
+-----------------------------------------------------------------------------------+
| 2. Production Management Control Tower (/desk/sarathicontroltower)                |
|    - Factory-wide monitoring, Work Orders, Shortages, Quality, Subcontracting     |
|    - Audience: Factory Managers, Plant Heads, Production Planners                 |
+-----------------------------------------------------------------------------------+
| 3. Shop-Floor Supervisor & Operator  (/desk/sarathishopfloor) [DASH-023]          |
|    - Mobile Workboard, Station Queue, Current Operation, Touch-Friendly View     |
|    - Audience: Floor Supervisors, Machine Operators, Line Assemblers              |
+-----------------------------------------------------------------------------------+
```

---

## 3. Verified Source DocTypes and Fields

| DocType | Fields Used | Operational Purpose |
| :--- | :--- | :--- |
| **`Job Card`** | `name`, `work_order`, `production_item`, `item_name`, `operation`, `workstation`, `workstation_type`, `status`, `docstatus`, `company`, `for_quantity`, `total_completed_qty`, `transferred_qty`, `expected_start_date`, `expected_end_date`, `actual_start_date`, `actual_end_date`, `total_time_in_mins`, `is_paused`, `is_corrective_job_card`, `quality_inspection` | Represents the shop floor operational unit of work. |
| **`ToDo`** | `reference_type`, `reference_name`, `allocated_to`, `status` | Native Frappe document assignment mechanism linking specific Job Cards to operators. |
| **`Employee`** | `name`, `employee_name`, `user_id`, `department`, `designation`, `company`, `status` | Links authenticated Frappe session users to company employee profiles. |
| **`User Permission`** | `user`, `allow`, `for_value`, `applicable_for` | Scopes supervisors to their designated workstation teams. |
| **`Downtime Entry`** | `name`, `workstation`, `from_time`, `to_time`, `downtime_reason`, `docstatus` | Surfaces active workstation breakdown stops affecting the operator's jobs. |
| **`Work Order`** | `name`, `production_item`, `qty`, `status` | Parent manufacturing order drill-down reference. |

---

## 4. Assignment Rules & Role Security

To maintain strict data integrity, the workboard **never fabricates assignments** or presents unrelated factory jobs to an operator:

### 4.1 Machine Operator (`Sarathi Operator`)
- **Direct Assignment Source:**
  1. Open native Frappe `ToDo` records where `reference_type == "Job Card"` and `allocated_to == frappe.session.user`.
  2. Linked active `Employee` record where `Job Card.employee == employee.name`.
- **Isolation Guarantee:** An operator cannot view Job Cards assigned to other operators or unassigned factory jobs.
- **Unconfigured State:** If no direct assignments exist, the workboard renders an informative configuration-required state explaining how assignments are allocated in ERPNext, rather than showing zero values or fallback jobs.

### 4.2 Shop-Floor Supervisor (`Sarathi Supervisor`)
- **Workstation Team Scope:**
  1. Job Cards assigned directly via `ToDo`.
  2. Job Cards on workstations granted to the supervisor via `User Permission` (`allow == "Workstation"`).
- **Isolation Guarantee:** Supervisors only see work within their assigned workstation area, not the entire factory.

### 4.3 Production Manager / System Manager (`has_capability("production")`)
- Company-wide operational visibility across all factory workstations, with workstation and status filtering.

---

## 5. Summary Metrics & Formulas

| Metric Card | Display Label | Definition & Counting Grain | Tone |
| :--- | :--- | :--- | :--- |
| **Assigned Work** | Total Assigned | Count of unique, eligible `Job Card` records within the user's scope with `docstatus < 2`. | Primary (Blue) |
| **In Progress** | Active Operations | Count of eligible jobs with `status == "Work In Progress"`. | Info (Cyan) |
| **Waiting / Queued** | Waiting Jobs | Count of eligible jobs with `status == "Open"` ready to start. | Warning (Amber) |
| **Completed** | Finished Operations | Count of eligible jobs with `status == "Completed"`. | Success (Green) |
| **Blocked** | Blocked Jobs | Count of eligible jobs with verified material shortage, active downtime, or quality rework holds. | Danger (Red) |

---

## 6. Current Operation & Blocker Highlights

### 6.1 Current Operation Card
- When one or more jobs are in `Work In Progress`, they are prominently featured in the Current Operation area with:
  - Pulsing `In Progress` status badge (e.g. `Active Operation` or `N Active Operations`).
  - Operation name in 24px bold typography.
  - Workstation badge (e.g. `WS-CNC-01`).
  - Work Order and Production Item details.
  - Planned vs. completed progress bar with UOM and remaining quantity.
  - Started timestamp and elapsed duration.
  - Authorized drill-down link to native ERPNext Job Card.
- **Multiple Active Operations Rule:** If several operations are in progress across the user's authorized scope (e.g. for a supervisor managing multiple workstations), all active operations are displayed cleanly without arbitrarily picking the first record.
- When no operation is in progress, the card clearly displays the **Next Queued Operation** or an idle state banner.

### 6.2 Blocker Surfacing
Blockers are detected from verified source documents:
- **Active Workstation Downtime:** Detected when `Downtime Entry.to_time` is null (active stop).
- **Quality Rework Hold:** Detected when `Job Card.is_corrective_job_card == 1` following a rejected inspection.
- **Paused Operation:** Detected when `Job Card.is_paused == 1` or `status == "On Hold"`.

---

## 7. Responsive Design System (Mobile-First)

Complies with DASH-005 design tokens and touch-screen accessibility:

```
+-----------------------------------------------------------------------------------+
|  [Logo] Shop-Floor Workboard       [Operator: John Doe] [Control Tower] [Refresh] |
+-----------------------------------------------------------------------------------+
|  Authoritative ERPNext Data · Last updated: 12:45:10 PM                           |
+-----------------------------------------------------------------------------------+
|  [Assigned: 4]  [In Progress: 1]  [Waiting: 2]  [Completed: 1]  [Blocked: 1]      |
+-----------------------------------------------------------------------------------+
|  CURRENT OPERATION: Milling & Turning                                             |
|  Station: WS-CNC-01 · Work Order: MFG-WO-2026-00042                               |
|  Progress: [=====================>     ] 35 / 50 Nos (70%)                        |
|  [ Open Job Card in ERPNext ]                                                     |
+-----------------------------------------------------------------------------------+
|  MY WORK QUEUE                                                                    |
|  [All (4)] [In Progress (1)] [Waiting (2)] [Blocked (1)] [Completed (1)]          |
|  [ Search by Job Card, Item, Station...                                        ] |
+-----------------------------------------------------------------------------------+
|  +-----------------------------------------------------------------------------+  |
|  | OPEN · WS-CNC-01               Job Card: JC-2026-00105                      |  |
|  | Drilling & Deburring                                                        |  |
|  | Item: Turned Shaft (SHAFT-01) · Target: 50 Nos                              |  |
|  | [ Inspect Record ]                                                          |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

- **Touch Targets:** All interactive buttons and links feature minimum dimensions of $44\text{px} \times 44\text{px}$ (and $56\text{px}$ in `[data-density=shop-floor]`).
- **Mobile Viewport ($\le 480$px):** Stacks header controls, transforms KPI cards to single-column, collapses operation cards into touch-first layout without horizontal scrollbars.
- **Tablet Viewport ($481\text{px} - 1023\text{px}$):** 2–3 column grid for KPIs and clean responsive work cards.
- **High-Contrast Palette:** Slate `#0f172a` base, crisp borders `#e2e8f0`, vibrant status pills with dual text-plus-color indicators.

---

## 8. Test Execution & Verification Results

### 8.1 Standalone Logic Test Suite
Executed via: `python sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py`

```
Ran 9 tests in 0.028s

OK
```

#### Verified Scenarios:
1. `test_filter_allowlist_rejection`: Rejection of unknown query parameters with `ValidationError`.
2. `test_invalid_status_filter`: Rejection of unapproved status choices.
3. `test_unauthorized_user_blocked`: Denial of users without `shop` or `production` capability.
4. `test_operator_receives_only_assigned_jobs`: Strict ToDo assignment isolation for operators.
5. `test_unassigned_operator_returns_unconfigured_reason`: Truthful unconfigured explanation when no assignments exist.
6. `test_supervisor_receives_workstation_team_jobs`: Workstation User Permission scoping for supervisors.
7. `test_supervisor_receives_workstation_team_jobs`: Promotion of active `Work In Progress` job to `current_operation`.
8. `test_blocker_detection_workstation_downtime`: Critical blocker surfacing on active workstation stops.
9. `test_blocker_detection_rework_job`: High severity quality rework hold surfacing.
10. `test_search_and_overdue_calculations`: Real-time text search and overdue delay calculation.

---

## 9. Manual Verification Steps

1. Log into Frappe Desk.
2. In the browser address bar, navigate to `/desk/sarathishopfloor`.
3. Check header:
   - Verify dashboard title, user role pill (`Operator` / `Supervisor` / `Manager`), and user name.
   - Click the "Control Tower" button; verify it links to `/desk/sarathicontroltower`.
   - Click "Refresh"; verify the spinning animation and timestamp update.
4. Observe the 5 Summary Cards:
   - Confirm counts match active jobs in the queue.
5. Review Current Operation:
   - If an operation is in progress, check that operation name, workstation, progress bar, and "Open Job Card" button appear.
6. Test Workboard Filters:
   - Click `In Progress`, `Waiting`, `Blocked`, and `Completed` pills; verify instant client-side card filtering.
   - Type in the search box; verify instant text filtering matching job, item, or station.
   - Click `Reset Filters`; verify all jobs return.
7. Mobile Breakpoint Test:
   - Open browser developer tools and toggle device toolbar (e.g. iPhone 14 or Pixel 7, 390px width).
   - Verify touch targets are $\ge 44$px and zero horizontal scrolling occurs.

---

## 10. Future Task Governance & Dependencies

- **DASH-024 (Assigned Job & Current Operation API):** Next task in Epic DASH-022. Will provide deeper shift-based assignments and workstation capacity metrics.
- **DASH-025 (Validated Reporting Actions):** Will implement validated start-job, pause-job, time-log recording, and output/scrap reporting. The workboard in DASH-023 remains strictly read-focused.
- **DASH-026 (Supervisor Team Overview):** Will implement supervisor reassignment and multi-station team queue monitoring.
