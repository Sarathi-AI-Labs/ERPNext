# DASH-016 — Work Order and Job Card APIs

## 1. Overview & Architecture

- **Task ID:** DASH-016
- **Task Name:** Implement Work Order and Job Card APIs
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Primary Application:** `sarathi_visibility`
- **Dashboard Route:** `/desk/sarathicontroltower`
- **Source Module:** [`sarathi_visibility/sarathi_visibility/api/work_orders.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/work_orders.py)
- **Re-exported Module:** [`sarathi_visibility/sarathi_visibility/api/dashboard.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/dashboard.py)
- **Automated Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_work_orders.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_work_orders.py)

This module implements secure, role-aware, paginated, and deterministic backend APIs for retrieving Work Orders and Job Cards from live ERPNext manufacturing records (`Work Order`, `Job Card`, `Work Order Operation`, `Work Order Item`, `Job Card Time Log`, `Job Card Operation`, `Job Card Item`, and `Stock Entry`).

All endpoints enforce strict server-side validation against allowlists, zero N+1 queries, document-level security (`check_record`), and role-based field masking (such as hourly rates and operating costs for non-finance users).

---

## 2. API Endpoints

### API A: Work Order List

- **Method:** `GET`
- **Path:** `/api/method/sarathi_visibility.api.work_orders.get_work_orders` (also re-exported as `sarathi_visibility.api.dashboard.get_work_orders`)
- **Capability Required:** `production` (Roles: `Sarathi Owner`, `Manufacturing Manager`, `Manufacturing User`, `Sarathi Supervisor`, `Sarathi Operator`, `System Manager`)
- **DocType Permission:** Read permission on `Work Order`

#### Input Parameters & Supported Filters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `filters` | JSON / Dict | No | Dictionary of validated filters (see allowlist below). |
| `start` | Integer | No | Page offset, default `0`. Range: `0 <= start <= 100,000`. |
| `page_length` | Integer | No | Page limit, default `20`. Range: `1 <= page_length <= 100`. |
| `sort_by` | String | No | Sort field, default `"modified"`. Validated against allowlist. |
| `sort_order` | String | No | `"asc"` or `"desc"`, default `"desc"`. |

**Filter Allowlist (`WO_FILTER_KEYS`):**
- `company` (Link `Company`): User default company if omitted; validated against native permissions.
- `from_date` (ISO date `YYYY-MM-DD`): Lower bound on `planned_start_date`.
- `to_date` (ISO date `YYYY-MM-DD`): Upper bound on `planned_start_date`. Validated `from_date <= to_date`.
- `status` (String): `"Active"` (default), `"All"`, `"Overdue"`, `"Due soon"`, `"Draft"`, `"Completed"`, `"Cancelled"`, or exact ERPNext status.
- `production_item` / `item_code` (Link `Item`): Filter Work Orders for a specific finished item.
- `project` (Link `Project`): Filter by Project linked to Work Order.
- `customer` (Link `Customer`): Scoped via linked Project or Sales Order.
- `workstation` (Link `Workstation`): Scoped via linked Job Cards / operations.
- `operation` (Link `Operation`): Scoped via linked Job Cards / operations.
- `search` / `work_order` (String): Case-insensitive substring match on Work Order ID, item code, or item name.
- `reference_at` (ISO timestamp `YYYY-MM-DD HH:MM:SS`): Reference timestamp for overdue calculation (defaults to server now).

**Sort Field Allowlist (`WO_SORT_FIELDS`):**
- `name`, `modified`, `creation`, `planned_start_date`, `planned_end_date`, `expected_delivery_date`, `status`, `qty`, `produced_qty`, `production_item`.

#### Response Contract

```json
{
  "work_orders": [
    {
      "name": "MFG-WO-2026-00009",
      "production_item": "FG-CONV-ROLLER-01",
      "item_name": "Conveyor Drive Roller Assembly",
      "qty": 50.0,
      "produced_qty": 15.0,
      "remaining_qty": 35.0,
      "completion_percent": 30.0,
      "status": "In Process",
      "docstatus": 1,
      "company": "SarathiAILabs",
      "project": "PROJ-2026-001",
      "customer": "Apex Conveyors Ltd",
      "sales_order": "SAL-ORD-2026-00014",
      "bom_no": "BOM-FG-CONV-ROLLER-01-001",
      "stock_uom": "Nos",
      "planned_start_date": "2026-10-10 08:00:00",
      "planned_end_date": "2026-10-25 18:00:00",
      "expected_delivery_date": "2026-10-28",
      "target_completion_date": "2026-10-25",
      "is_active": true,
      "is_overdue": false,
      "days_diff": 11,
      "open_job_cards_count": 2,
      "total_job_cards_count": 5,
      "wip_warehouse": "Work In Progress - SAL",
      "fg_warehouse": "Finished Goods - SAL",
      "material_transferred_for_manufacturing": 50.0,
      "creation": "2026-10-09 14:22:10",
      "modified": "2026-10-14 06:15:30"
    }
  ],
  "total": 4,
  "start": 0,
  "page_length": 20,
  "has_next_page": false,
  "applied_filters": {
    "company": "SarathiAILabs",
    "status": "Active"
  }
}
```

---

### API B: Work Order Detail

- **Method:** `GET`
- **Path:** `/api/method/sarathi_visibility.api.work_orders.get_work_order_detail` (also re-exported as `sarathi_visibility.api.dashboard.get_work_order_detail`)
- **Capability Required:** `production`
- **DocType Permission:** Document-level read permission enforced via `check_record("Work Order", work_order, "read")`

#### Input Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `work_order` | String | Yes | Work Order ID (e.g. `"MFG-WO-2026-00009"`). |

#### Response Contract

```json
{
  "work_order": {
    "name": "MFG-WO-2026-00009",
    "production_item": "FG-CONV-ROLLER-01",
    "item_name": "Conveyor Drive Roller Assembly",
    "company": "SarathiAILabs",
    "status": "In Process",
    "docstatus": 1,
    "bom_no": "BOM-FG-CONV-ROLLER-01-001",
    "sales_order": "SAL-ORD-2026-00014",
    "project": "PROJ-2026-001",
    "customer": "Apex Conveyors Ltd",
    "stock_uom": "Nos",
    "qty": 50.0,
    "produced_qty": 15.0,
    "remaining_qty": 35.0,
    "completion_percent": 30.0,
    "planned_start_date": "2026-10-10 08:00:00",
    "planned_end_date": "2026-10-25 18:00:00",
    "expected_delivery_date": "2026-10-28",
    "target_completion_date": "2026-10-25",
    "actual_start_date": "2026-10-10 08:15:00",
    "actual_end_date": null,
    "is_overdue": false,
    "days_diff": 11,
    "wip_warehouse": "Work In Progress - SAL",
    "fg_warehouse": "Finished Goods - SAL",
    "source_warehouse": "Stores - SAL",
    "scrap_warehouse": null,
    "lead_time": 15.0,
    "material_transferred_for_manufacturing": 50.0,
    "track_semi_finished_goods": true,
    "description": "Custom roller batch for high speed conveyor line",
    "planned_operating_cost": null,
    "actual_operating_cost": null,
    "total_operating_cost": null
  },
  "operations": [
    {
      "name": "d4e5f6g7",
      "operation": "Turning & Facing",
      "workstation": "CNC Lathe 01",
      "workstation_type": "CNC Machining",
      "sequence_id": 1,
      "status": "Completed",
      "time_in_mins": 450.0,
      "completed_qty": 50.0,
      "process_loss_qty": 0.0,
      "actual_operation_time": 440.0
    }
  ],
  "required_items": [
    {
      "name": "a1b2c3d4",
      "item_code": "RAW-STL-ROD-50",
      "item_name": "EN8 Bright Steel Round Bar 50mm",
      "source_warehouse": "Stores - SAL",
      "stock_uom": "Kg",
      "required_qty": 250.0,
      "transferred_qty": 250.0,
      "consumed_qty": 75.0
    }
  ],
  "job_cards": [
    {
      "name": "PO-JOB00015",
      "operation": "Turning & Facing",
      "workstation": "CNC Lathe 01",
      "status": "Completed",
      "docstatus": 1,
      "for_quantity": 50.0,
      "total_completed_qty": 50.0,
      "transferred_qty": 50.0,
      "completion_percent": 100.0,
      "total_time_in_mins": 440.0,
      "expected_start_date": "2026-10-10 09:00:00",
      "expected_end_date": "2026-10-11 17:00:00",
      "actual_start_date": "2026-10-10 09:10:00",
      "actual_end_date": "2026-10-11 16:45:00",
      "quality_inspection": null
    }
  ],
  "stock_entries": [
    {
      "name": "MFG-STE-2026-00042",
      "posting_date": "2026-10-12",
      "fg_completed_qty": 15.0,
      "docstatus": 1,
      "target_warehouse": "Finished Goods - SAL"
    }
  ]
}
```

*Note on Financial Field Masking:* `planned_operating_cost`, `actual_operating_cost`, and `total_operating_cost` evaluate to `null` unless the authenticated user possesses the `finance` capability (`can_finance()` is true).

---

### API C: Job Card List

- **Method:** `GET`
- **Path:** `/api/method/sarathi_visibility.api.work_orders.get_job_cards` (also re-exported as `sarathi_visibility.api.dashboard.get_job_cards`)
- **Capability Required:** `production`
- **DocType Permission:** Read permission on `Job Card`

#### Input Parameters & Supported Filters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `filters` | JSON / Dict | No | Dictionary of validated filters. |
| `start` | Integer | No | Page offset, default `0`. Range: `0 <= start <= 100,000`. |
| `page_length` | Integer | No | Page limit, default `20`. Range: `1 <= page_length <= 100`. |
| `sort_by` | String | No | Sort field, default `"modified"`. Validated against allowlist. |
| `sort_order` | String | No | `"asc"` or `"desc"`, default `"desc"`. |

**Filter Allowlist (`JC_FILTER_KEYS`):**
- `company` (Link `Company`): User default company if omitted; validated against native permissions.
- `work_order` (Link `Work Order`): Associated parent Work Order ID.
- `operation` (Link `Operation`): Operation name.
- `workstation` (Link `Workstation`): Assigned workstation ID.
- `status` (String): `"Open"`, `"Work In Progress"`, `"Completed"`, `"Cancelled"`, or `"All"`.
- `from_date` / `to_date` (ISO date `YYYY-MM-DD`): Bound on `posting_date`.
- `production_item` (Link `Item`): Item code.
- `project` (Link `Project`): Associated Project ID.
- `employee` (Link `Employee`): Assigned employee filter.
- `search` (String): Case-insensitive substring match on Job Card ID, Work Order ID, operation, or item.

**Sort Field Allowlist (`JC_SORT_FIELDS`):**
- `name`, `modified`, `creation`, `expected_start_date`, `actual_start_date`, `for_quantity`, `total_completed_qty`, `status`, `operation`, `workstation`.

#### Response Contract

```json
{
  "job_cards": [
    {
      "name": "PO-JOB00015",
      "work_order": "MFG-WO-2026-00009",
      "production_item": "FG-CONV-ROLLER-01",
      "item_name": "Conveyor Drive Roller Assembly",
      "stock_uom": "Nos",
      "operation": "Turning & Facing",
      "workstation": "CNC Lathe 01",
      "status": "Completed",
      "docstatus": 1,
      "company": "SarathiAILabs",
      "project": "PROJ-2026-001",
      "for_quantity": 50.0,
      "total_completed_qty": 50.0,
      "transferred_qty": 50.0,
      "completion_percent": 100.0,
      "expected_start_date": "2026-10-10 09:00:00",
      "expected_end_date": "2026-10-11 17:00:00",
      "actual_start_date": "2026-10-10 09:10:00",
      "actual_end_date": "2026-10-11 16:45:00",
      "total_time_in_mins": 440.0,
      "quality_inspection": null,
      "is_corrective_job_card": false,
      "creation": "2026-10-09 15:00:00",
      "modified": "2026-10-11 17:00:00"
    }
  ],
  "total": 15,
  "start": 0,
  "page_length": 20,
  "has_next_page": false,
  "applied_filters": {
    "company": "SarathiAILabs"
  }
}
```

---

### API D: Job Card Detail

- **Method:** `GET`
- **Path:** `/api/method/sarathi_visibility.api.work_orders.get_job_card_detail` (also re-exported as `sarathi_visibility.api.dashboard.get_job_card_detail`)
- **Capability Required:** `production`
- **DocType Permission:** Document-level read permission enforced via `check_record("Job Card", job_card, "read")`

#### Input Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `job_card` | String | Yes | Job Card ID (e.g. `"PO-JOB00015"`). |

#### Response Contract

```json
{
  "job_card": {
    "name": "PO-JOB00015",
    "work_order": "MFG-WO-2026-00009",
    "production_item": "FG-CONV-ROLLER-01",
    "item_name": "Conveyor Drive Roller Assembly",
    "stock_uom": "Nos",
    "operation": "Turning & Facing",
    "workstation": "CNC Lathe 01",
    "workstation_type": "CNC Machining",
    "status": "Completed",
    "docstatus": 1,
    "company": "SarathiAILabs",
    "project": "PROJ-2026-001",
    "for_quantity": 50.0,
    "total_completed_qty": 50.0,
    "transferred_qty": 50.0,
    "completion_percent": 100.0,
    "expected_start_date": "2026-10-10 09:00:00",
    "expected_end_date": "2026-10-11 17:00:00",
    "actual_start_date": "2026-10-10 09:10:00",
    "actual_end_date": "2026-10-11 16:45:00",
    "total_time_in_mins": 440.0,
    "wip_warehouse": "Work In Progress - SAL",
    "quality_inspection": null,
    "is_corrective_job_card": false,
    "remarks": null,
    "hour_rate": null
  },
  "time_logs": [
    {
      "name": "e5f6g7h8",
      "employee": "EMP-0012",
      "from_time": "2026-10-10 09:10:00",
      "to_time": "2026-10-10 17:30:00",
      "time_in_mins": 440.0,
      "completed_qty": 50.0
    }
  ],
  "sub_operations": [],
  "items": [],
  "parent_work_order": {
    "work_order": "MFG-WO-2026-00009",
    "status": "In Process",
    "planned_qty": 50.0,
    "produced_qty": 15.0,
    "stock_uom": "Nos"
  }
}
```

*Note on Financial Field Masking:* `hour_rate` is masked to `null` unless the authenticated user possesses the `finance` capability.

---

## 3. Quantity Semantics & Derived Formulas

A critical requirement of DASH-016 is establishing and enforcing verified manufacturing quantity semantics:

### 1. Work Order Quantities (Finished Goods Level)
- `qty`: Total planned production quantity of the finished item for this Work Order.
- `produced_qty`: Actual finished items received into the finished goods warehouse via submitted `Stock Entry` (Purpose: `"Manufacture"`).
- `remaining_qty = max(0.0, qty - produced_qty)`: Remaining finished goods to be manufactured. Always bounded at `>= 0.0`.
- `completion_percent = round((produced_qty / qty) * 100.0, 1)` (if `qty > 0`, else `0.0`). Bounded at `0.0% to 100.0%`.

### 2. Job Card Quantities (Operation / Workstation Level)
- `for_quantity`: The quantity planned for *this specific operation* at this workstation.
- `total_completed_qty`: The quantity completed through *this specific operation*.
- **Crucial Rule:** Job Card quantities represent individual operation volume. They must **never** be summed across different operations to represent finished goods output, as the same physical part passes through multiple sequential operations (which would cause massive double-counting).
- Total finished output is sourced strictly from `Work Order.produced_qty` and `Stock Entry (Manufacture).fg_completed_qty`.

### 3. Target Completion Date & Overdue Detection
- In ERPNext, `Work Order.planned_end_date` can be empty depending on routing configuration, while `Work Order.expected_delivery_date` holds customer delivery commitments.
- Formula:
  $$\text{Target Date} = \text{planned\_end\_date} \lor \text{expected\_delivery\_date}$$
- A Work Order is marked `is_overdue = true` if and only if:
  1. `docstatus == 1` (Submitted).
  2. `status in ("Not Started", "In Process")` (Active).
  3. $\text{Target Date} < \text{Reference Date}$.

---

## 4. Zero N+1 Query Architecture

To ensure high performance when paginating Work Orders, all associated data is resolved using batch queries rather than per-record lookups:

1. **Customer Resolution:**
   - On the current page slice of Work Orders (max 100 items), all distinct `project` and `sales_order` identifiers are gathered.
   - Two batch queries fetch project customers (`frappe.get_all("Project", filters={"name": ["in", proj_names]}, fields=["name", "customer"])`) and sales order customers (`frappe.get_all("Sales Order", filters={"name": ["in", so_names]}, fields=["name", "customer"])`).
   - Customer names are mapped in memory in $O(1)$ time per row.

2. **Job Card Counts:**
   - A single aggregated batch query fetches all open and total Job Cards for the Work Orders on the current page:
     ```python
     jcs = frappe.get_all(
         "Job Card",
         filters={"work_order": ["in", paged_wo_names], "docstatus": ["<", 2]},
         fields=["work_order", "status"],
         limit_page_length=5000,
     )
     ```
   - Total queries per list request: strictly 3 queries, regardless of page size.

---

## 5. Security & Permission Enforcement

Every endpoint in `work_orders.py` adheres to the Sarathi AI Labs security framework:

1. **Authentication & Capability Check:**
   - All 4 endpoints invoke `require_capability("production")`.
   - Users without production capabilities (such as guests or accounts-only users) receive an immediate `frappe.PermissionError` (HTTP 403).
2. **Company Isolation:**
   - Multi-tenant ERPNext instances have dedicated companies.
   - `validate_work_order_filters` and `validate_job_card_filters` call `_company()` to verify user permissions on the requested company.
   - Queries strictly filter on `company == user_authorized_company`.
   - Direct record queries verify `record.company == authorized_company`.
3. **Record-Level Security (`check_record`):**
   - Individual Work Order and Job Card detail endpoints use `check_record(doctype, name, "read")`.
   - If a record does not exist or belongs to an unauthorized company/scope, it throws `frappe.PermissionError`, preventing enumeration attacks.
4. **Input Sanitization & Allowlists:**
   - Filter keys, sort fields, sort order (`"asc"`, `"desc"`), pagination (`start >= 0`, `1 <= page_length <= 100`), and identifiers (`len <= 140`, no control characters) are validated against strict allowlists.
5. **Financial Field Masking:**
   - Manufacturing costs (`planned_operating_cost`, `actual_operating_cost`, `total_operating_cost`) on Work Orders and `hour_rate` on Job Cards are masked to `null` unless `can_finance()` is true.

---

## 6. Test Suite & Verification Results

The automated test suite in [`sarathi_visibility/sarathi_visibility/tests/test_work_orders.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_work_orders.py) covers 45 distinct test cases inheriting from native `PermissionTests`.

### Test Execution Command
```bash
docker exec -w /home/frappe/frappe-bench/sites -u frappe frappe_docker_main-backend-1 \
  /home/frappe/frappe-bench/env/bin/python -c "
import frappe; frappe.init(site='frontend'); frappe.connect(); import unittest;
from sarathi_visibility.tests.test_work_orders import TestWorkOrderAndJobCardAPIs;
suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkOrderAndJobCardAPIs);
res = unittest.TextTestRunner(verbosity=2).run(suite);
print('Ran:', res.testsRun, 'Errors:', len(res.errors), 'Failures:', len(res.failures))"
```

### Actual Test Results
```
----------------------------------------------------------------------
Ran 45 tests in 7.375s

OK
Ran: 45 Errors: 0 Failures: 0
```

### Full Regression Check (DASH-015 Factory Overview + DASH-006 Data Helpers)
```bash
docker exec -w /home/frappe/frappe-bench/sites -u frappe frappe_docker_main-backend-1 \
  /home/frappe/frappe-bench/env/bin/python -c "
import frappe; frappe.init(site='frontend'); frappe.connect(); import unittest;
from sarathi_visibility.tests.test_factory_overview import TestFactoryOverview;
from sarathi_visibility.tests.test_data_helpers import DataHelperTests;
suite = unittest.TestSuite();
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFactoryOverview));
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(DataHelperTests));
res = unittest.TextTestRunner(verbosity=1).run(suite);
print('Ran:', res.testsRun, 'Errors:', len(res.errors), 'Failures:', len(res.failures))"
```

### Regression Results
```
----------------------------------------------------------------------
Ran 50 tests in 9.748s

OK
Ran: 50 Errors: 0 Failures: 0
```

---

## 7. Known Limitations & Dependencies for Future Tasks

1. **DASH-017 — Production Pipeline and Bottleneck Views:**
   - Future pipeline views can reuse `get_work_orders` with `status="Active"` and sort by `completion_percent` or `target_completion_date`.
   - Workstation queues can query `get_job_cards` filtered by `workstation` and `status="Open"`.
2. **DASH-018 — Material Readiness and Shortages:**
   - `get_work_order_detail` already exposes `required_items` with `required_qty`, `transferred_qty`, and `consumed_qty`. DASH-018 will build warehouse bin balance reconciliation on top of these fields.
3. **DASH-019 — Workstation and Downtime Views:**
   - `Job Card.total_time_in_mins` and `time_logs` child table provide operator logged time for utilization calculations.
4. **DASH-020 — Quality, Rework, and Subcontracting:**
   - `is_corrective_job_card` and `quality_inspection` are exposed on Job Cards to support rework tracking in DASH-020.
