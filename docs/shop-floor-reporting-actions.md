# DASH-025 — Shop-Floor Reporting Actions Documentation

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-022 — Shop-Floor Supervisor & Operator Dashboard  
**Task ID:** DASH-025  
**Priority:** P1 — High  
**Application:** `sarathi_visibility`  
**Frontend:** Mobile-First Shop-Floor Workboard (`sarathi_shopfloor.js`, `sarathi_shopfloor.css`)  
**Backend:** Frappe Framework + ERPNext Manufacturing (`sarathi_visibility/api/shopfloor.py`)  
**Dependencies:** DASH-023 (Workboard UI) and DASH-024 (Assigned Job & Current Operation API)  
**Status:** **Implemented & Verified**

---

## 1. Executive Summary & Objective

DASH-025 implements secure, validated, and permission-aware shop-floor production reporting actions directly within the existing Sarathi Industrial Control Tower Shop-Floor Workboard.

Shop-floor operators and supervisors can execute production actions—starting jobs, recording progress, pausing/resuming work, stopping cycles, and completing operations—without navigating through the complex ERPNext Desk interface. Every action strictly adheres to native ERPNext manufacturing logic, document lifecycle methods, permission boundaries, and audit logging.

### Key Principles Followed
1. **Zero Core Modifications:** Zero alterations to ERPNext or Frappe core files.
2. **Native Business Logic:** Utilizes native `Job Card` and `Job Card Time Log` methods (`start_timer`, `pause_job`, `resume_job`, `complete_job_card`, `validate_sequence_id`, `validate_transfer_qty`, `validate_inspection`).
3. **Strict Server-Side Authorization:** Derives caller identity solely from `frappe.session.user`. Enforces strict assignment boundaries so operators can only report against Job Cards assigned to them via Frappe ToDo assignments or active Employee linking.
4. **Idempotency & Concurrency Safety:** Safe handling of duplicate submissions, rapid button presses, and out-of-order requests without creating duplicate time logs or corrupting production quantities.
5. **Mobile-First UX:** Touch-friendly buttons (min 40-44px), double-click prevention with loading spinners, mobile input dialogs, client-side sanity checks, and automatic workboard data refreshes upon confirmed server updates.

---

## 2. Supported Reporting Actions & API Endpoints

All reporting endpoints are whitelisted for HTTP POST via `@frappe.whitelist(methods=["POST"])` and secured with `@api_error_handler` to mask internal stack traces while presenting clear, actionable validation guidance.

| Action Logical Name | Python Function | Frappe API Route | HTTP Method | ERPNext Document Methods & Logic |
| :--- | :--- | :--- | :--- | :--- |
| **Action A: Start Operation** | [`start_job`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L650-L715) | `sarathi_visibility.api.shopfloor.start_job` | POST | `start_timer()`, sets `status = "Work In Progress"`, initiates open `Job Card Time Log`. |
| **Action B: Record Progress** | [`record_job_progress`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L720-L808) | `sarathi_visibility.api.shopfloor.record_job_progress` | POST | Closes active time log with reported qty, recalculates `total_completed_qty`, re-arms open time log. |
| **Action C: Pause Operation** | [`pause_job`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L813-L865) | `sarathi_visibility.api.shopfloor.pause_job` | POST | `pause_job()`, sets `is_paused = 1`, `status = "On Hold"`, timestamps `to_time` on open log. |
| **Action C: Resume Operation** | [`resume_job`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L870-L922) | `sarathi_visibility.api.shopfloor.resume_job` | POST | `resume_job()`, sets `is_paused = 0`, `status = "Work In Progress"`, opens new time log. |
| **Action C: Stop Operation Cycle** | [`stop_job`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L927-L985) | `sarathi_visibility.api.shopfloor.stop_job` | POST | Closes open time log, updates duration, leaves job in open state ready for next shift/cycle. |
| **Action D: Complete Operation** | [`complete_job`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/shopfloor.py#L990-L1068) | `sarathi_visibility.api.shopfloor.complete_job` | POST | `validate_sequence_id()`, `validate_transfer_qty()`, `validate_inspection()`, `complete_job_card()`, submits (`docstatus = 1`). |

---

## 3. Verified ERPNext DocTypes & Document Life Cycle

### Primary DocTypes

1. **`Job Card` (Parent):**
   - **`docstatus` States:**
     - `0` (Draft / Active): Represents unsubmitted jobs (`Open`, `Work In Progress`, `On Hold`). All active reporting occurs in this state.
     - `1` (Submitted / Completed): Sealed, authoritative audit record. No further time logs or quantity adjustments permitted.
     - `2` (Cancelled): Inactive. All mutations strictly rejected.
   - **Key Fields Utilized:**
     - `name`, `work_order`, `operation`, `workstation`, `for_quantity`, `total_completed_qty`, `process_loss_qty`, `status`, `is_paused`, `total_time_in_mins`, `time_logs`, `remarks`.

2. **`Job Card Time Log` (Child Table in `Job Card`):**
   - **Fields Utilized:**
     - `from_time`: Exact start timestamp set by server (`now_datetime()`).
     - `to_time`: Closing timestamp set by server upon pause, stop, or progress reporting.
     - `time_in_mins`: Elapsed duration calculated from timestamps.
     - `completed_qty`: Incremental quantity reported during the specific time slice.
     - `employee`: Active ERPNext Employee linked to the session user.

3. **`ToDo` (Assignment Table):**
   - Maps `reference_type = "Job Card"` and `reference_name = job_card_name` to `allocated_to = user`. Enforces operator assignment boundary.

4. **`Work Order` (Upstream Document):**
   - Reference for routing validation, operation sequence (`sequence_id`), and material transfer checks (`validate_transfer_qty`).

5. **`Quality Inspection` (Prerequisite):**
   - Validated prior to Job Card completion when mandatory quality checks are configured on the operation.

---

## 4. Valid Status Transitions & Document Lifecycle

```
                 +-------------------+
                 |   Open / Waiting  | <---------------------+
                 +-------------------+                       |
                           |                                 |
                     start_job()                         stop_job()
                           |                                 |
                           v                                 |
                 +-------------------+                       |
                 |  Work In Progress | ----------------------+
                 +-------------------+
                     |           ^
          pause_job()|           | resume_job()
                     v           |
                 +-------------------+
                 |      On Hold      |
                 +-------------------+
                           |
                     complete_job()
                           |
                           v
                 +-------------------+
                 | Completed (Subm.) | (docstatus = 1)
                 +-------------------+
```

### Transition Rules

1. **Start Operation (`start_job`):**
   - **Allowed Pre-conditions:** `docstatus == 0`, `status in ["Open", "On Hold"]`.
   - **Prerequisites:** Sequence ID validation (`validate_sequence_id`) ensures prior operations on the Work Order are completed.
   - **Post-conditions:** `status = "Work In Progress"`, `is_paused = 0`. An active child record in `time_logs` is created with `from_time = now_datetime()` and `to_time = None`.
   - **Idempotency:** If already running (`status == "Work In Progress"` with an open time log), returns HTTP 200 with `idempotent: True` and existing start time without appending duplicate rows.

2. **Record Progress (`record_job_progress`):**
   - **Allowed Pre-conditions:** `docstatus == 0`, `status in ["Work In Progress", "Open"]`.
   - **Validation:** `completed_qty > 0`, non-negative, finite. Ensures `total_completed_qty + completed_qty <= for_quantity` (accounting for standard overproduction allowance).
   - **Post-conditions:** Closes current open time log with incremental reported quantity, recalculates `total_completed_qty`, and immediately starts a new open time log so operation tracking continues uninterrupted.

3. **Pause Operation (`pause_job`):**
   - **Allowed Pre-conditions:** `docstatus == 0`, `status == "Work In Progress"`.
   - **Post-conditions:** `status = "On Hold"`, `is_paused = 1`. Finds open time log, sets `to_time = now_datetime()`, and computes `time_in_mins`.
   - **Idempotency:** If already paused (`status == "On Hold"` or `is_paused == 1`), returns HTTP 200 with `idempotent: True`.

4. **Resume Operation (`resume_job`):**
   - **Allowed Pre-conditions:** `docstatus == 0`, `status in ["On Hold", "Open"]`.
   - **Post-conditions:** `status = "Work In Progress"`, `is_paused = 0`. Creates new open time log row.
   - **Idempotency:** If already in `Work In Progress`, returns HTTP 200 with `idempotent: True`.

5. **Stop Operation Cycle (`stop_job`):**
   - **Allowed Pre-conditions:** `docstatus == 0`, `status == "Work In Progress"`.
   - **Post-conditions:** Closes active time log, updates cumulative minutes and quantity, and sets `status = "Open"` so the job remains available for subsequent shifts or cycles.

6. **Complete Operation (`complete_job`):**
   - **Allowed Pre-conditions:** `docstatus == 0`.
   - **Prerequisites:** Validates material transfers (`validate_transfer_qty`), quality inspection results (`validate_inspection`), and sequence dependencies.
   - **Post-conditions:** Closes any lingering open time log, executes `complete_job_card()`, submits document (`docstatus = 1`), setting `status = "Completed"`.
   - **Idempotency:** If document is already completed (`docstatus == 1`), returns HTTP 200 with `idempotent: True`.

---

## 5. Security & Permission Architecture

Production reporting alters authoritative business records. The security model enforces multi-layer verification:

```
                            [ Client Request ]
                                    |
                            [ HTTP POST API ]
                                    |
                         derive frappe.session.user
                                    |
                     +--------------+--------------+
                     |                             |
             [ Role Check ]                [ Session Check ]
       has_capability("shop")              frappe.session.user
      or has_capability("production")      != "Guest"
                     |                             |
                     +--------------+--------------+
                                    |
                        resolve_shopfloor_context()
                                    |
                     +--------------+--------------+
                     |                             |
              [ Operator ]                  [ Supervisor ]
        Verify ToDo assignment          Verify User Permission
        or Linked Employee              for Workstation or ToDo
                     |                             |
                     +--------------+--------------+
                                    |
                         authorize_and_get_job_card()
                                    |
                         DocStatus & Record Locks
                                    |
                     [ Execute ERPNext Mutation ]
```

### Authorization Guarantees
- **No Client Spoofing:** Neither `user`, `employee`, nor `role` can be passed from the frontend. The server derives the caller exclusively from `frappe.session.user`.
- **Operator Isolation:** A Machine Operator (`is_operator=True`, `is_manager=False`) is strictly forbidden from executing any reporting action against a Job Card that is not explicitly assigned to them via open `ToDo` or linked `Employee`. Any attempt raises `frappe.PermissionError`.
- **Supervisor Scoping:** A Shop-Floor Supervisor can only report against Job Cards situated at workstations explicitly granted via Frappe `User Permission` (`allow="Workstation"`), or jobs directly assigned via `ToDo`.
- **Non-Existent & Cancelled Checks:** Non-existent documents raise `frappe.DoesNotExistError`. Cancelled documents (`docstatus == 2`) raise `frappe.ValidationError`.

---

## 6. Input Validation & Reliability Safeguards

### Quantity & UOM Validation
- **Numeric & Non-Negative:** All quantity inputs (`completed_qty`, `pending_qty`, `process_loss_qty`) are validated via `flt()`. Negative, non-numeric, `NaN`, or infinite values are rejected with `frappe.ValidationError`.
- **No Direct Inventory Table Overwrites:** Raw materials are consumed via standard ERPNext manufacturing stock entries; no direct SQL adjustments are executed against inventory tables.
- **Stock UOM Integrity:** Inherits `stock_uom` directly from the parent Job Card.

### Time Log Integrity
- **Authoritative Server Timestamps:** Client-supplied timestamps are never trusted. All start, pause, stop, and completion times use `now_datetime()` in the server's configured system timezone.
- **Duration Protection:** Negative durations and future timestamps are impossible because closing timestamps are generated server-side at the time of request.
- **Overlapping Record Prevention:** Active open logs are scanned prior to creating new ones, preventing duplicate active rows.

### Concurrency & Duplicate Request Protection
- **Client-Side Throttling:** Action buttons implement `setBtnLoading()`, which disables button clicks, displays a spinning loader, and prevents duplicate rapid submissions.
- **Server-Side Idempotency:** If network retries re-send a `start_job` or `complete_job` payload, the backend detects the current document state and returns a successful response with `idempotent: True` rather than throwing an error or creating duplicate records.
- **Database Savepoints & Rollback:** Multi-step operations leverage Frappe's database transactions. Any failure during validation or child row creation rolls back cleanly, preventing orphan reporting records.

---

## 7. Frontend Workboard Integration

The Shop-Floor Workboard (`sarathi_shopfloor.js`) integrates reporting actions directly into the operator workflow:

### Active Operation Card Actions
When an operation is in `Work In Progress`:
- **"Report Progress" Button (Blue):** Opens a prompt dialog to submit incremental completed quantities, immediately updating progress bars.
- **"Pause" Button (Amber):** Halts the active operation and stops live duration timers.
- **"Stop Cycle" Button (Secondary):** Closes the current operation cycle for shift changeovers.
- **"Complete Job" Button (Green):** Submits final quantities and submits the Job Card.

### Queued / Assigned Cards Actions
- **"Start Job Now" Button:** Exposed on eligible waiting jobs (`status == "Open"`). Clicking immediately transitions the card to `Work In Progress` and begins duration tracking.
- **"Resume" Button:** Displayed on paused jobs (`status == "On Hold"`).

### UX & Mobile Safeguards
- Touch target heights meet accessibility guidelines (min 38-44px).
- Numeric input fields have client validation for prompt responses.
- After every successful action, the workboard refreshes active operations, assigned job lists, and KPI summary counters.

---

## 8. Test Execution & Verification

### Automated Test Suites

1. **Unit & Logic Suite (`sarathi_visibility/tests/test_shopfloor_logic.py`):**
   - 25 dedicated test cases covering:
     - Allowlist parameter validation.
     - Role scoping (Operator vs. Supervisor vs. Manager).
     - Idempotent `start_job`, `pause_job`, `resume_job`, `stop_job`, and `complete_job`.
     - Quantity boundary validation and negative quantity rejection.
     - Sequence ID and prerequisite dependency checks.
     - ToDo assignment isolation.
   - **Result:** `Ran 25 tests in 0.024s — OK (All Passed)`.

2. **Integration Suite (`sarathi_visibility/tests/test_shopfloor.py`):**
   - Native Frappe bench integration test verifying:
     - `test_unauthorized_user_cannot_mutate_jobs`: Unrelated user denied access with `frappe.PermissionError`.
     - `test_operator_cannot_mutate_unassigned_job`: Operator restricted to assigned jobs only.
     - `test_mutation_rejects_nonexistent_job_card`: Non-existent IDs raise `frappe.DoesNotExistError`.
     - `test_record_progress_rejects_negative_or_invalid_quantity`: Negative quantities raise `frappe.ValidationError`.
     - `test_operator_job_lifecycle_start_pause_resume`: Full lifecycle tested with savepoints and rollback.

---

## 9. Manual Testing Instructions

### Scenario A: Operator Starts and Reports Progress
1. Log in as an operator with assigned Job Cards (or view assigned jobs on `/desk/sarathicontroltower`).
2. On an assigned waiting job (`status == "Open"`), click **"Start Job Now"**.
3. Verify that the button shows a loading spinner, disables clicks, and upon response, the job moves to **Current Operation** with `status = "Work In Progress"`.
4. Click **"Report Progress"**, enter `5`, and submit.
5. Verify that `total_completed_qty` increments by 5 and the progress bar updates.

### Scenario B: Operator Pauses and Resumes
1. On an active job, click **"Pause"**.
2. Verify that the status updates to `On Hold` and the pause timestamp is recorded.
3. Click **"Resume"**.
4. Verify that the status returns to `Work In Progress` and a new time log begins tracking.

### Scenario C: Operator Completes Job
1. Click **"Complete Job"**.
2. If final quantity prompt appears, confirm the completed quantity.
3. Verify that the Job Card transitions to `Completed` (`docstatus = 1`) and moves out of the active operations queue.

### Scenario D: Security & Isolation Verification
1. Attempt to call `POST /api/method/sarathi_visibility.api.shopfloor.start_job` via cURL or Postman with a `job_card` belonging to a different operator.
2. Verify HTTP 403 response with `frappe.PermissionError`.

---

## 10. Unsupported Actions & Configuration Dependencies

1. **Direct Stock Entry Posting:** Operators report production quantities against the Job Card. Bulk raw material issue entries (`Stock Entry` of type *Material Transfer for Manufacture*) must be processed through standard warehouse procedures before completion if strict material transfer enforcement is enabled in ERPNext Manufacturing Settings.
2. **Quality Inspection Submissions:** If an operation requires a mandatory Quality Inspection (`quality_inspection` field configured), the inspection document must be submitted prior to completing the Job Card.
3. **Subcontracted Operations:** Subcontracting purchase receipts and supplier delivery notes follow standard purchase workflows and are outside the scope of shop-floor workboard execution.
