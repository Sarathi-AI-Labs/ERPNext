# DASH-024 — Assigned-Job and Current-Operation API Documentation

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-022 — Shop-Floor Supervisor & Operator Dashboard  
**Task ID:** DASH-024  
**Priority:** P1 — High  
**Application:** `sarathi_visibility`  
**Frontend Dependency:** DASH-023 — Mobile-First Shop-Floor Workboard  
**Module:** [`sarathi_visibility/sarathi_visibility/api/shopfloor.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py)  
**Status:** **Implemented & Verified**

---

## 1. Executive Summary & Objective

DASH-024 implements secure, permission-aware, read-focused backend APIs for the Shop-Floor Supervisor & Operator Dashboard in Sarathi Industrial Control Tower. These APIs allow the DASH-023 mobile-first workboard to query real production work without embedding production queries, assignment rules, or authorization logic inside client-side JavaScript.

### Key Objectives Achieved
1. **API A (`get_assigned_jobs`):** Returns paginated, authorized Job Cards genuinely eligible for the authenticated user based on native ERPNext assignments (`ToDo` / linked `Employee`) or workstation team scoping (`User Permission`).
2. **API B (`get_current_operation`):** Surfaces the authenticated user's currently active operation(s) in `Work In Progress`, computes live elapsed minutes from open `Job Card Time Log` records, and handles multiple concurrent active operations without arbitrary single-record selection.
3. **API C (`get_next_jobs`):** Returns upcoming waiting operations (`status == "Open"`), prioritized deterministically by planned start date (`expected_start_date`), routing operation sequence (`sequence_id`), and document identifier (`name`).
4. **API D (`get_shop_floor_summary`):** Provides aggregated status metrics (`total_assigned_jobs`, `jobs_in_progress`, `waiting_jobs`, `completed_jobs`, `blocked_jobs`) using identical server-side filtering and eligibility rules to prevent metric skew.
5. **Consolidated Endpoint (`get_shopfloor_workboard`):** Provides a single round-trip endpoint for the DASH-023 workboard while internally reusing the exact same business logic and authorization boundaries.

---

## 2. API Endpoints & Routes

All endpoints are registered under Frappe's `@frappe.whitelist(methods=["GET"])` decorator with standard error masking (`@read_errors`).

| Endpoint Logical Name | Python Function | Full Frappe Method Route | Purpose |
| :--- | :--- | :--- | :--- |
| **API A: Retrieve Eligible Jobs** | [`get_assigned_jobs`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L420-L452) | `sarathi_visibility.api.shopfloor.get_assigned_jobs` | Paginated, filterable list of assigned/authorized Job Cards. |
| **API B: Retrieve Current Operation** | [`get_current_operation`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L457-L504) | `sarathi_visibility.api.shopfloor.get_current_operation` | User's active WIP operation(s) with open time log duration. |
| **API C: Retrieve Eligible Next Jobs** | [`get_next_jobs`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L509-L537) | `sarathi_visibility.api.shopfloor.get_next_jobs` | Prioritized waiting operations ordered by schedule and sequence. |
| **API D: Retrieve Workboard Summary** | [`get_shop_floor_summary`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L542-L574) | `sarathi_visibility.api.shopfloor.get_shop_floor_summary` | Aggregate status and blocker counts for workboard metric cards. |
| **Consolidated Workboard Endpoint** | [`get_shopfloor_workboard`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L579-L636) | `sarathi_visibility.api.shopfloor.get_shopfloor_workboard` | Single round-trip composition used by DASH-023 workboard. |

---

## 3. Verified DocTypes and Field Mapping

The APIs strictly query verified DocTypes and fields native to the ERPNext v15 manufacturing module:

| DocType | Fields Used | Purpose in DASH-024 |
| :--- | :--- | :--- |
| **`Job Card`** | `name`, `work_order`, `production_item`, `item_name`, `operation`, `workstation`, `workstation_type`, `status`, `docstatus`, `company`, `for_quantity`, `total_completed_qty`, `transferred_qty`, `stock_uom`, `expected_start_date`, `expected_end_date`, `actual_start_date`, `actual_end_date`, `total_time_in_mins`, `is_paused`, `is_corrective_job_card`, `quality_inspection`, `sequence_id`, `creation`, `modified` | Authoritative operational record for manufacturing operations. |
| **`Job Card Time Log`** | `name`, `parent`, `from_time`, `to_time`, `employee`, `time_in_mins` | Authoritative record for active operation duration tracking. Open logs (`to_time is null`) determine elapsed minutes. |
| **`ToDo`** | `reference_type`, `reference_name`, `allocated_to`, `status` | Standard Frappe task assignment linking specific Job Card names to authenticated users. |
| **`Employee`** | `name`, `employee_name`, `user_id`, `department`, `designation`, `company`, `status` | Maps authenticated `frappe.session.user` to active internal employee records. |
| **`User Permission`** | `user`, `allow`, `for_value`, `applicable_for` | Scopes supervisors to designated factory workstations. |
| **`Downtime Entry`** | `name`, `workstation`, `from_time`, `to_time`, `downtime_reason`, `docstatus` | Surfaces genuine workstation breakdown stops affecting operator jobs. |
| **`Work Order`** | `name`, `production_item`, `company`, `status` | Validated parent manufacturing order reference. |
| **`Workstation`** | `name`, `workstation_name` | Validated manufacturing work center reference. |

---

## 4. Assignment Resolution & Role-Based Eligibility Rules

All eligibility checks occur on the server inside [`resolve_shopfloor_context(user)`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L101-L234). The client cannot specify or override the target employee or user ID.

```
                                  [ Authenticated User ]
                                            |
                                 frappe.session.user
                                            |
                 +--------------------------+--------------------------+
                 |                          |                          |
        [ Sarathi Operator ]       [ Sarathi Supervisor ]     [ Production Manager ]
                 |                          |                          |
     +-----------+-----------+      +-------+-------+                  |
     |                       |      |               |                  |
Open ToDo               Linked   Designated      Open ToDo      Full Company Scope
(allocated_to = user)   Employee  Workstations   (allocated_to   (docstatus < 2)
                        (Active) (User Perm)     = user)
     |                       |      |               |                  |
     +-----------+-----------+      +-------+-------+                  |
                 |                          |                          |
        [ Eligible JCs ]           [ Eligible JCs ]           [ Eligible JCs ]
```

### Eligibility Rules by Role

1. **Machine Operator (`Sarathi Operator`):**
   - Must only receive jobs explicitly assigned to them via open `ToDo` records (`reference_type="Job Card"`, `allocated_to=user`, `status="Open"`), or jobs explicitly assigned to their active `Employee` record (`employee=employee_id`).
   - If no jobs are assigned, the API returns zero jobs and an explicit, truthful `unconfigured_reason` message:
     > *"No jobs are currently assigned to you. In this ERPNext installation, operators receive work via explicit Frappe Assignments (ToDo) or Employee linking."*
   - Operators never see factory-wide unassigned jobs or other operators' jobs.

2. **Shop-Floor Supervisor (`Sarathi Supervisor`):**
   - Receives jobs assigned to workstations granted in Frappe `User Permission` (`allow="Workstation"`), plus any direct personal `ToDo` assignments.
   - If no workstation permissions or direct assignments are configured, returns an explicit `unconfigured_reason`:
     > *"No supervisor workstation scope or assigned Job Cards found. Supervisors require User Permissions for Workstation or explicit Job Card assignments."*
   - Supervisors cannot see jobs outside their permitted workstations.

3. **Production Manager (`has_capability("production")`):**
   - Authorized to view company-wide shop floor activity across all workstations. Company filtering is applied via query parameters.

4. **Unauthorized Roles:**
   - Users without `Sarathi Operator`, `Sarathi Supervisor`, or `Sarathi Production Manager` roles are rejected with HTTP 403 `frappe.PermissionError`.

---

## 5. Current Operation Selection & Multi-Active Operations

In a manufacturing environment, a user or supervisor may legitimately have multiple operations marked as `Work In Progress` (e.g., dual-spindle setups, parallel staging, or supervisor cell oversight).

### Rules Enforced
1. **No Arbitrary First-Record Picking:**
   - The API returns all active jobs in the `active_operations` list.
   - For backwards compatibility with single-operation UI components, `current_operation` provides the first active job, but the workboard displays all entries in `active_operations`.
2. **Elapsed Duration Calculation:**
   - Queries `Job Card Time Log` where `parent = job_card.name` and `to_time is null` (open log).
   - `elapsed_mins = (now_datetime() - from_time).total_seconds() / 60.0`.
   - If no open log exists, falls back to `Job Card.total_time_in_mins`.
3. **Empty Handling:**
   - If no operations are in `Work In Progress`, the API returns `has_active_operation: false`, `current_operation: null`, and `active_operations: []`. Waiting (`Open`) jobs are never falsely presented as active.

---

## 6. Next Eligible Operations & Scheduling Sequence

API C (`get_next_jobs`) identifies upcoming waiting operations that the operator or cell is scheduled to perform next.

### Rules Enforced
1. **Waiting Operations Only:**
   - Filters only operations with `status == "Open"` and `docstatus == 1`.
2. **Deterministic Sequence Ordering:**
   - Avoids naive sorting by document creation timestamp.
   - Orders by:
     1. `expected_start_date asc` (earliest planned schedule first, nulls last)
     2. `sequence_id asc` (routing operation sequence from Work Order routing)
     3. `name asc` (stable tie-breaker)
   - Exposes `ordering_basis: "expected_start_date asc, sequence_id asc, name asc"` in response metadata.
3. **Bounded Limit:**
   - Enforces `min(max(limit, 1), 25)` to prevent unbounded database queries.

---

## 7. Status, Quantity, and Time Calculations

### Quantity & UOM Handling
- **Planned Quantity (`for_quantity`):** Sourced directly from `Job Card.for_quantity`.
- **Completed Quantity (`total_completed_qty`):** Sourced from `Job Card.total_completed_qty`.
- **Remaining Quantity (`remaining_qty`):** Calculated as `max(0.0, for_quantity - total_completed_qty)`.
- **Completion Percentage (`completion_percent`):** Calculated as `round((total_completed_qty / for_quantity * 100.0), 1)` if `for_quantity > 0` else 0.0.
- **Stock UOM (`stock_uom`):** Sourced directly from `Job Card.stock_uom` (or defaulted safely to `"Nos"`). Displayed alongside all quantities in the UI to prevent mixed-unit misinterpretation.

### Blocker Detection (No Fake States)
Blockers are identified only from verified ERPNext transactional data:
1. **Active Workstation Downtime:** `Downtime Entry` with `docstatus = 1` and `to_time is null` on the job's workstation. Severity: **Critical**.
2. **Quality Rework:** `Job Card.is_corrective_job_card = 1` resulting from inspection rejection. Severity: **High**.
3. **Paused / On Hold:** `Job Card.is_paused = 1` or `status = "On Hold"`. Severity: **Medium**.

---

## 8. Response Schemas & Examples

### API A — `get_assigned_jobs` Response Example

```json
{
  "success": true,
  "jobs": [
    {
      "name": "JC-2026-00042",
      "work_order": "MFG-WO-2026-00015",
      "production_item": "SHAFT-40MM-CNC",
      "item_name": "Precision Drive Shaft 40mm",
      "operation": "Turning & Facing",
      "workstation": "WS-CNC-LATHE-01",
      "workstation_type": "CNC Lathes",
      "status": "Work In Progress",
      "docstatus": 1,
      "company": "Sarathi AI Labs",
      "stock_uom": "Nos",
      "for_quantity": 50.0,
      "total_completed_qty": 15.0,
      "remaining_qty": 35.0,
      "transferred_qty": 50.0,
      "completion_percent": 30.0,
      "sequence_id": 1,
      "expected_start_date": "2026-10-14",
      "expected_end_date": "2026-10-15",
      "actual_start_date": "2026-10-14 09:30:00",
      "actual_end_date": null,
      "total_time_in_mins": 90.0,
      "is_overdue": false,
      "delay_days": 0,
      "is_paused": false,
      "is_corrective": false,
      "quality_inspection": null,
      "has_blocker": false,
      "blocker": null,
      "drill_down_link": "/desk#Form/Job Card/JC-2026-00042",
      "work_order_link": "/desk#Form/Work Order/MFG-WO-2026-00015"
    }
  ],
  "total": 1,
  "start": 0,
  "page_length": 20,
  "has_next_page": false,
  "user_context": {
    "user_id": "operator1@example.com",
    "user_name": "Ramesh Kumar",
    "role_label": "Machine Operator",
    "is_operator": true,
    "is_supervisor": false,
    "is_manager": false,
    "employee_id": "HR-EMP-00102",
    "employee_name": "Ramesh Kumar",
    "department": "Machining",
    "designation": "CNC Operator"
  },
  "unconfigured_reason": null,
  "applied_filters": {
    "status": "Work In Progress"
  }
}
```

### API B — `get_current_operation` Response Example

```json
{
  "success": true,
  "has_active_operation": true,
  "count": 1,
  "current_operation": {
    "name": "JC-2026-00042",
    "work_order": "MFG-WO-2026-00015",
    "production_item": "SHAFT-40MM-CNC",
    "operation": "Turning & Facing",
    "workstation": "WS-CNC-LATHE-01",
    "status": "Work In Progress",
    "stock_uom": "Nos",
    "for_quantity": 50.0,
    "total_completed_qty": 15.0,
    "remaining_qty": 35.0,
    "actual_start_date": "2026-10-14 09:30:00",
    "active_time_log": {
      "name": "TL-00091",
      "from_time": "2026-10-14 11:30:00",
      "elapsed_mins": 32.5,
      "employee": "HR-EMP-00102"
    }
  },
  "active_operations": [
    {
      "name": "JC-2026-00042",
      "operation": "Turning & Facing",
      "workstation": "WS-CNC-LATHE-01",
      "status": "Work In Progress"
    }
  ],
  "user_context": {
    "user_id": "operator1@example.com",
    "role_label": "Machine Operator"
  },
  "unconfigured_reason": null
}
```

### API C — `get_next_jobs` Response Example

```json
{
  "success": true,
  "next_jobs": [
    {
      "name": "JC-2026-00043",
      "work_order": "MFG-WO-2026-00015",
      "production_item": "SHAFT-40MM-CNC",
      "operation": "Cylindrical Grinding",
      "workstation": "WS-GRIND-01",
      "status": "Open",
      "sequence_id": 2,
      "expected_start_date": "2026-10-15",
      "for_quantity": 50.0,
      "remaining_qty": 50.0,
      "stock_uom": "Nos"
    }
  ],
  "total_waiting": 1,
  "ordering_basis": "expected_start_date asc, sequence_id asc, name asc",
  "user_context": {
    "user_id": "operator1@example.com",
    "role_label": "Machine Operator"
  },
  "unconfigured_reason": null
}
```

### API D — `get_shop_floor_summary` Response Example

```json
{
  "success": true,
  "summary": {
    "total_assigned_jobs": 4,
    "jobs_in_progress": 1,
    "waiting_jobs": 2,
    "completed_jobs": 1,
    "blocked_jobs": 0
  },
  "user_context": {
    "user_id": "operator1@example.com",
    "role_label": "Machine Operator"
  },
  "applied_filters": {},
  "unconfigured_reason": null
}
```

---

## 9. Security, Validation, and Rate Limiting

1. **Authentication & Session:**
   - Server-side `require_session()` guarantees unauthenticated requests receive HTTP 401.
2. **Capability-Based Authorization:**
   - Only users with `shop` or `production` capabilities may call shop-floor endpoints.
3. **Filter Allowlisting:**
   - Inputs are checked against `SHOPFLOOR_FILTER_KEYS = {"company", "status", "work_order", "production_item", "item_code", "operation", "workstation", "from_date", "to_date", "search"}`. Unknown keys throw `frappe.ValidationError`.
4. **Ordering & Pagination Bounding:**
   - Sort fields checked against `JC_SORT_FIELDS` allowlist.
   - Pagination bounds enforced via `pagination(start, page_length)` (max 100 per page).
5. **No Client Employee Spoofing:**
   - `user_id` is extracted strictly from `frappe.session.user`. Any client-supplied user or employee parameters are rejected.
6. **Error Sanitization:**
   - Wrapped with `@read_errors` to prevent SQL or internal traceback leakage in API responses.

---

## 10. Integration with DASH-023 Workboard

The DASH-023 frontend controller ([`sarathi_shopfloor.js`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/js/sarathi_shopfloor.js)) was verified and updated to:
1. Render multiple active operations in parallel using the `active_operations` array from API B / consolidated response.
2. Display `stock_uom` next to all planned, completed, and remaining quantities.
3. Wire status counts from API D directly into the summary metric cards.
4. Render truthful empty states when `unconfigured_reason` is returned by the server.

---

## 11. Verification and Automated Test Results

The test suite consists of 15 automated unit and security tests in [`sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py), and companion bench tests in [`sarathi_visibility/sarathi_visibility/tests/test_shopfloor.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_shopfloor.py).

### Test Execution Command
```bash
python sarathi_visibility/sarathi_visibility/tests/test_shopfloor_logic.py
```

### Actual Execution Output
```
...............
----------------------------------------------------------------------
Ran 15 tests in 0.033s

OK
```

### Test Coverage Summary

| Test Method | Category | Verified Behavior |
| :--- | :--- | :--- |
| `test_filter_allowlist_rejection` | Security | Rejects unknown query parameters with `ValidationError`. |
| `test_invalid_status_filter` | Security | Rejects unsupported status values with `ValidationError`. |
| `test_unauthorized_user_blocked` | Security | Rejects unprivileged users lacking `shop` or `production` roles with `PermissionError`. |
| `test_operator_receives_only_assigned_jobs` | Assignment | Verifies operator only receives Job Cards assigned via `ToDo`. |
| `test_unassigned_operator_returns_unconfigured_reason` | Assignment | Verifies unassigned operator receives 0 jobs and truthful explanation without fabricated data. |
| `test_supervisor_receives_workstation_team_jobs` | Assignment | Verifies supervisor receives jobs for workstations defined in `User Permission`. |
| `test_multiple_active_operations_all_surfaced` | API B | Verifies multiple WIP operations are all surfaced in `active_operations` without arbitrary selection. |
| `test_blocker_detection_workstation_downtime` | Robustness | Identifies active workstation downtime and marks job with Critical blocker. |
| `test_blocker_detection_rework_job` | Robustness | Identifies corrective rework Job Cards with High blocker. |
| `test_search_and_overdue_calculations` | Filtering | Validates live text search filtering and overdue delay calculation. |
| `test_api_a_get_assigned_jobs_pagination_and_sorting` | API A | Validates pagination slices, boundary indicators, and sort order. |
| `test_api_b_get_current_operation_with_active_time_log` | API B | Validates active time log elapsed minutes calculation. |
| `test_api_b_get_current_operation_empty` | API B | Validates clean empty response when no operations are active. |
| `test_api_c_get_next_jobs_priority_ordering` | API C | Validates waiting jobs prioritized by schedule and routing sequence. |
| `test_api_d_get_shop_floor_summary_counts` | API D | Validates exact status and blocker count aggregation. |

---

## 12. Strict Scope Boundary Confirmation

- **DASH-024 only** has been implemented.
- **DASH-025 (Shop-Floor Reporting Actions):** NOT implemented. No start/stop job mutations, time logging, or quantity completion endpoints were added.
- **DASH-026 (Supervisor Team Overview):** NOT implemented. No team attendance or operator reassignment mutations were added.
- Existing dashboards (`/desk/sarathiownertower` and `/desk/sarathicontroltower`) remain fully functional with zero breaking changes.
