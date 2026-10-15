# DASH-026 — Shop-Floor Supervisor Team Overview Documentation

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-022 — Shop-Floor Supervisor & Operator Dashboard  
**Task ID:** DASH-026  
**Priority:** P1 — High  
**Application:** `sarathi_visibility`  
**Dashboard Route:** `/desk/sarathishopfloor`  
**Frontend:** Subview Switcher, Supervisor Team Toolbar, 9-KPI Grid, Team Workload Grid, Active Floor Operations Table, Completed Work Table, Supervisor Attention Queue, Workstations Health (`sarathishopfloor.html`, `sarathi_shopfloor.js`, `sarathi_shopfloor.css`)  
**Backend:** Frappe Framework + ERPNext Manufacturing (`sarathi_visibility/api/shopfloor.py`)  
**Dependencies:** DASH-023 (Mobile-First Workboard), DASH-024 (Assigned Job APIs), and DASH-025 (Validated Reporting Actions)  
**Status:** **Implemented & Verified**

---

## 1. Executive Summary & Objective

DASH-026 implements the **Supervisor Team Overview** inside the Sarathi Industrial Control Tower Shop-Floor Dashboard (`/desk/sarathishopfloor`).

This operational cockpit empowers factory supervisors and production managers to oversee their authorized floor team, monitor live operations, balance machine operator workloads, catch overdue/delayed operations, track completions, and resolve critical blockers (downtime breakdowns, quality rework, paused jobs) directly from one unified screen.

### Core Questions Answered by the Overview:
1. **Which operators are assigned to work today?** Surfaces all team operators with their active status (`Working`, `Assigned`, `No Active Job`).
2. **Which Job Cards and operations are waiting, in progress, or completed?** Categorized across summary KPIs and real-time lists.
3. **Which operations are overdue or delayed?** Overdue operations are detected when `expected_end_date < today` and highlighted in attention notices with delay days and links.
4. **Which operators have multiple active jobs or no eligible work?** Flags multiple concurrent WIP jobs as a high-severity workload alert, and clearly identifies operators with no assigned active/waiting work.
5. **Which production jobs have blockers?** Aggregates workstation breakdown downtimes, quality rework holds, and paused operations with suggested actions.
6. **What work has been reported as completed during the selected period?** Tracks finished Job Cards with completed quantities, stock UOMs, duration, and completion timestamps.
7. **Which jobs require supervisor attention?** Consolidated Attention Queue prioritizing issues by severity (`Critical`, `High`, `Medium`).
8. **Which ERPNext document should the supervisor open?** Direct authorized Frappe Desk drill-down links to Job Cards, Work Orders, Employees, Workstations, and Downtime Entries.

---

## 2. Dashboard Layout & Route

- **Desk Route:** `/desk/sarathishopfloor`
- **Dynamic Role-Based Gating:**
  - **Machine Operator:** Sees only the Mobile-First Operator Workboard (Current Operation + Assigned Queue). The Subview Switcher is hidden. Attempts to call the supervisor endpoint return HTTP 403 `PermissionError`.
  - **Shop-Floor Supervisor & Production Manager:** The Subview Switcher appears at the top of the page, defaulting to the **Supervisor Team Overview** while permitting instant toggling to the Operator Workboard.

### Dashboard Sections

```
+----------------------------------------------------------------------------------------------------+
|  Top Header: Shop-Floor Workboard | User Badge (Role + Name) | CT Link | Refresh Button             |
+----------------------------------------------------------------------------------------------------+
|  Subview Switcher: [ * Supervisor Team Overview ]  [   Operator Workboard ]                        |
+----------------------------------------------------------------------------------------------------+
|  Supervisor Scope & Filters Toolbar: Date Bounds | Operator | Workstation | Status | Search | Reset |
+----------------------------------------------------------------------------------------------------+
|  Team Summary 9-KPI Grid:                                                                          |
|  [ Team Members ] [ Working Now ] [ Queued/Assigned ] [ No Work ] [ Active JCs ]                   |
|  [ Waiting JCs ] [ Completed JCs ] [ Blocked JCs ] [ Overdue JCs ]                                 |
+----------------------------------------------------------------------------------------------------+
|  Team Workload & Operator Status (Operator Cards with avatars, job counts, active operation)       |
+----------------------------------------------------------------------------------------------------+
|  Live Floor Operations (Work In Progress table with elapsed time, station, operator, progress bar) |
+----------------------------------------------------------------------------------------------------+
|  Supervisor Attention & Production Blockers (Downtime breakdowns, quality rework, overdue, alerts) |
+----------------------------------------------------------------------------------------------------+
|  Completed Production Work (Completed Job Cards in period with quantities, duration, date)         |
+----------------------------------------------------------------------------------------------------+
|  Permitted Workstations Status (Station cards: status Running/Idle/Breakdown, active & queued JCs)|
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Verified DocTypes & Supervisor-to-Team Relationships

The supervisor scope and team membership are derived authoritatively on the server via [`resolve_supervisor_team_scope(user)`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L1110-L1352):

```
                                  [ Authenticated Caller ]
                                             |
                                    frappe.session.user
                                             |
                         +-------------------+-------------------+
                         |                                       |
                [ Sarathi Supervisor ]                 [ Production Manager ]
                         |                                       |
          +--------------+--------------+             Full Company Manufacturing Scope
          |                             |             (All active employees & JCs)
     Direct Reports             Permitted Workstations
 (Employee.reports_to)         (User Permission: allow="Workstation")
          |                             |
          +--------------+--------------+
                         |
           [ Discover Active Floor Team ]
           - Job Card child Time Log operators
           - Open ToDo task assignments
                         |
           [ Authorized Team Overview ]
```

### Verified Relationships:
1. **Direct Reports (`Employee.reports_to`):** Active employees whose `reports_to` links to the supervisor's active `Employee` record.
2. **Workstation Team Scope (`User Permission`):** Workstations explicitly granted to the supervisor via Frappe `User Permission` (`allow="Workstation"`). Any operators executing work or assigned to Job Cards at those workstations are included in the supervisor's team.
3. **Frappe Task Assignments (`ToDo`):** Direct Job Card assignments linking `reference_type="Job Card"` to team member user IDs (`allocated_to`).
4. **Active Child Time Logs (`Job Card Time Log`):** Operators clocking active time on operations at the supervisor's workstations.
5. **Production Manager Scope:** Full company-wide visibility across all workstations and manufacturing personnel.
6. **Unconfigured State:** If a supervisor has no direct reports, no workstation permissions, and no assigned Job Cards, the API returns `unconfigured_reason` with clear administrative setup guidance instead of fabricating artificial teams.

---

## 4. KPI Definitions & Mathematical Consistency

All 9 summary KPIs are derived from verified ERPNext manufacturing data:

| Metric | Field & Entity Counted | Statuses Included | Formula / Deduplication |
| :--- | :--- | :--- | :--- |
| **Team Members** | `Employee.name` / user ID | Active team operators | Distinct count of authorized team operators. |
| **Working Now** | `team_workload.in_progress_count` | `Work In Progress` | Count of operators with $\ge 1$ active WIP operation. |
| **Assigned / Queued** | `team_workload` job counts | `Open` or `Work In Progress` | Count of operators with $\ge 1$ active or waiting job. |
| **No Eligible Work** | `team_workload` idle | 0 active and 0 waiting | `total_team_members - operators_with_jobs`. |
| **Active JCs** | `Job Card.name` | `Work In Progress` | Count of eligible Job Cards currently in WIP. |
| **Waiting JCs** | `Job Card.name` | `Open` | Count of eligible Job Cards ready to start. |
| **Completed JCs** | `Job Card.name` | `Completed` (`docstatus = 1`) | Count of eligible Job Cards completed in selected period. |
| **Blocked JCs** | `Job Card.has_blocker` | Any active status | Count of Job Cards with active downtime, rework, or paused status. |
| **Overdue JCs** | `Job Card.is_overdue` | Uncompleted | Count of Job Cards where `expected_end_date < today`. |

> **Consistency Guarantee:**  
> `operators_with_jobs + operators_without_work == total_team_members`.  
> Active Job Cards matches the number of operations in the Live Floor Operations table.

---

## 5. Workload, Completion, and Blocker Rules

### Workload Classification
- **`Working`:** Operator has $\ge 1$ Job Card in `Work In Progress`.
- **`Assigned`:** Operator has 0 WIP jobs but $\ge 1$ waiting Job Card in `Open`.
- **`No Active Job`:** Operator has 0 WIP and 0 waiting Job Cards.
- **`Multiple Active Jobs Alert`:** Flagged when an operator has $> 1$ concurrent WIP operations. Surfaced as a High-severity notice so supervisors can ensure idle jobs are paused for accurate duration logging.

### Completion Tracking
- Completed work reflects sealed Job Cards (`docstatus == 1`, `status == "Completed"`).
- Uses `actual_end_date` (or `modified` fallback) to match the supervisor's date bounds.
- Quantities reflect standard Job Card `total_completed_qty` and `stock_uom`.

### Blocker Severity Hierarchy
1. **Critical:** Active Workstation breakdown (`Downtime Entry` with `to_time is null`).
2. **High:** Quality rework holds (`is_corrective_job_card = 1`), Overdue operations (`delay_days > 0`), and Multiple Active Jobs.
3. **Medium:** Paused operations (`On Hold`), and Unassigned waiting work.

---

## 6. Supported Filters & Security Enforcement

All filters are strictly allowlisted and validated via [`validate_shopfloor_filters`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L58-L106):

- `from_date` / `to_date`: Validated date bounds (`from_date <= to_date`).
- `employee` / `employee_id`: Validated alphanumeric identifier matching authorized team members.
- `workstation`: Validated workstation identifier scoped to permitted supervisor workstations.
- `status`: One of `All`, `Work In Progress`, `Open`, `Blocked`, `Completed`.
- `search`: Case-insensitive search across Job Card ID, Work Order, Item, Operation, Workstation, and Operator Name.

### Permission Enforcement
- Derives identity exclusively from `frappe.session.user`.
- Rejects callers lacking `Sarathi Supervisor`, `Production Manager`, or `System Manager` with HTTP 403 `frappe.PermissionError`.
- Supervisors cannot expand their visibility by manipulating workstation or employee parameters; server-side scoping filters records to their permitted scope.

---

## 7. API Endpoints

| Endpoint | Method | Python Handler | Return Data |
| :--- | :--- | :--- | :--- |
| **Supervisor Team Overview** | GET | [`get_supervisor_team_overview`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L1355-L1615) | Single round-trip JSON payload containing `user_context`, `team_summary` (9 KPIs), `team_workload`, `active_operations`, `completed_work`, `blockers`, `workstations`, and `filters_applied`. |
| **Shop-Floor Workboard** | GET | [`get_shopfloor_workboard`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L579-L681) | Operator workboard payload declaring `"supervisor_team_overview": True`. |

---

## 8. Test Execution & Verification

### Unit & Business Logic Test Suite:
```bash
python -m unittest sarathi_visibility.tests.test_shopfloor_logic
```
**Results:**
```text
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.024s

OK
```
All **29 tests PASSED (0 failures, 0 errors)**:
- Filter allowlist & invalid status rejection.
- Unauthorized operator role rejection on supervisor overview (`PermissionError`).
- Unconfigured supervisor returns truthful explanation (`unconfigured_reason`).
- Supervisor overview with direct reports computes correct 9 KPIs and workload distribution.
- Multiple active jobs detection and alert generation.
- Overdue jobs and downtime stops surfacing in blockers.
- Operator assignment isolation and ToDo discovery.
- All DASH-023, DASH-024, DASH-025, and DASH-026 test cases passing simultaneously.

### Bench Integration Suite (`test_shopfloor.py`):
- `test_operator_cannot_access_supervisor_team_overview`: Verified HTTP 403 `PermissionError`.
- `test_supervisor_can_access_supervisor_team_overview`: Verified schema and 9 KPIs.
- `test_production_manager_can_access_supervisor_team_overview`: Verified company-wide visibility.

---

## 9. Manual Testing Instructions

### Scenario 1: Supervisor Accesses Team Overview
1. Log in as a user with `Sarathi Supervisor` role.
2. Navigate to `/desk/sarathishopfloor`.
3. Verify that the **Subview Switcher Bar** appears showing `Supervisor Team Overview` (active) and `Operator Workboard`.
4. Verify that the 9 summary KPI cards display non-negative counts.
5. In the **Team Workload** section, inspect operator cards: verify operator names, designations, status badges (`Working`, `Assigned`, `No Active Job`), and active operation banners.
6. In the **Live Floor Operations** section, verify active WIP Job Cards with live elapsed duration timers and output progress bars.

### Scenario 2: Blocker & Alert Investigation
1. If an operator has 2 active WIP jobs, verify that the **Supervisor Attention** queue shows a High-severity "Multiple Active Jobs" alert with a suggested action.
2. If a workstation has an active breakdown, verify that the notice shows "Workstation Breakdown" with a direct link to the Downtime Entry.
3. Click the drill-down link; verify that it opens the authorized Frappe Desk document.

### Scenario 3: Operator Access Isolation
1. Log in as an operator with only `Sarathi Operator` role.
2. Navigate to `/desk/sarathishopfloor`.
3. Verify that the Subview Switcher Bar is hidden and only the Operator Workboard is rendered.
4. Attempt to query `GET /api/method/sarathi_visibility.api.shopfloor.get_supervisor_team_overview` directly via browser/Postman.
5. Verify HTTP 403 response with `frappe.PermissionError`.

---

## 10. Known Limitations & Configuration Dependencies

1. **Shift Management:** If an ERPNext installation has not configured `Shift Type` and `Shift Assignment` doctypes, the overview scopes by date range (`from_date` / `to_date`) rather than shift schedules.
2. **Supervisor Linking:** Supervisors without `Employee.reports_to` links or `User Permission` on `Workstation` will see the clean unconfigured state banner explaining the necessary setup.
3. **Attendance Integration:** Operators are described as having "No Active Job" rather than "Idle/Absent", as attendance records may not be tracked in manufacturing.
