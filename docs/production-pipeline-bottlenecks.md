# DASH-017 — Production Pipeline and Bottleneck Views

## 1. Overview & Architecture

- **Task ID:** DASH-017
- **Task Name:** Build Production Pipeline and Bottleneck Views
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Primary Application:** `sarathi_visibility`
- **Dashboard Route:** `/desk/sarathicontroltower`
- **Source Backend Module:** [`sarathi_visibility/sarathi_visibility/api/production_pipeline.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/production_pipeline.py)
- **Re-exported Module:** [`sarathi_visibility/sarathi_visibility/api/dashboard.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/dashboard.py)
- **Frontend Page View:** [`sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html)
- **Frontend UI Logic:** [`sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js)
- **CSS Styling:** [`sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css)
- **Automated Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_production_pipeline.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_production_pipeline.py)

DASH-017 implements an interactive, responsive production pipeline and bottleneck analysis view for factory and production managers. It translates live ERPNext manufacturing records into a multi-stage progression model with operation sequencing, predecessor dependency tracking, time-sensitive overdue detection, and defensible bottleneck identification.

---

## 2. Production Pipeline Visualization

The pipeline is organized into 4 verified manufacturing lifecycle stages based on actual document statuses and transaction records:

```
[1. Material Staging]  -->  [2. In Production]  -->  [3. Manufacture Receipt]  -->  [4. Completed]
  Raw materials pending       Operations active on        Partial finished goods        100% finished goods
  issue / transfer to WIP     shop-floor workstations     received via Stock Entry      produced and closed
```

### Stage Determination Rules

| Stage | Document Criteria | ERPNext Source Fields | Meaning |
| :--- | :--- | :--- | :--- |
| **1. Material Staging** | `docstatus == 1`, `status in ("Not Started", "In Process")`, `produced_qty == 0`, and `material_transferred_for_manufacturing == 0` | `Work Order.material_transferred_for_manufacturing` | Work Order is submitted and active, but raw materials have not yet been transferred from stores to the WIP warehouse. |
| **2. In Production** | `docstatus == 1`, `status in ("Not Started", "In Process")`, `produced_qty == 0`, and (`material_transferred_for_manufacturing > 0` or any Job Card has `status == "Work In Progress"` or `total_completed_qty > 0`) | `Work Order.material_transferred_for_manufacturing`, `Job Card.status`, `Job Card.total_completed_qty` | Materials are staged/transferred and operations are currently executing on the shop floor. |
| **3. Manufacture Receipt** | `docstatus == 1`, `status in ("Not Started", "In Process")`, `produced_qty > 0`, and `produced_qty < qty` | `Work Order.produced_qty`, `Stock Entry` (Purpose: `"Manufacture"`) | Partial finished goods have been manufactured, inspected, and received into the FG warehouse. |
| **4. Completed** | `status == "Completed"` or `produced_qty >= qty` | `Work Order.status`, `Work Order.produced_qty`, `Work Order.qty` | Work Order target output is 100% fulfilled. |
| **Draft / Cancelled** | `docstatus == 0` (Draft) / `docstatus == 2` (Cancelled) | `Work Order.docstatus` | Unsubmitted drafts or cancelled orders excluded from active flow. |

---

## 3. Operation Sequencing & Dependency Tracking

For Work Orders configured with operations, Job Cards are linked to operations in sequence order:

### 1. Sequence Determination
- If `Job Card.sequence_id > 0`: Sourced from `Job Card.sequence_id`.
- Else if `Work Order Operation` rows exist: Sourced from `Work Order Operation.sequence_id` or `Work Order Operation.idx`.
- Else if `Routing` is configured: Sourced from `BOM Operation.sequence_id` in Routing.
- Fallback: Sourced from deterministic Job Card creation order (`Job Card.creation asc`).

### 2. Operation State & Dependency Classification

For operation $i \in [0, N-1]$ in the ordered sequence:
- **`Completed`**: `Job Card.status == "Completed"` or `total_completed_qty >= for_quantity`.
- **`In Progress`**: `Job Card.status == "Work In Progress"`, or `0 < total_completed_qty < for_quantity`, or `actual_start_date` is recorded.
- **`Waiting on Predecessor`**: Operation has not started (`status == "Open"` and `total_completed_qty == 0`), and any upstream predecessor $j < i$ is NOT in state `Completed`.
- **`Ready to Start`**: Operation has not started, and ALL upstream predecessors $j < i$ are `Completed`.
- **`Cancelled`**: `docstatus == 2` or `status == "Cancelled"`.

Each operation node exposes:
- `sequence`: 1-based sequence index.
- `operation`: Operation name.
- `workstation`: Assigned workstation name.
- `previous_operation`: Preceding operation name ($i - 1$).
- `next_operation`: Following operation name ($i + 1$).
- `waiting_on`: Name of the predecessor operation causing starvation.

---

## 4. Delayed Jobs and Overdue Detection

### 1. Target Date Resolution
$$\text{Target Completion Date} = \text{Work Order.planned\_end\_date} \lor \text{Work Order.expected\_delivery\_date}$$
ERPNext Work Orders often omit `planned_end_date` when routings are unconfigured, while `expected_delivery_date` holds customer delivery commitments. Resolving this fallback guarantees accurate overdue tracking.

### 2. Overdue Work Order Rule
A Work Order is flagged `is_overdue = true` if and only if:
1. `docstatus == 1` (Submitted).
2. `status in ("Not Started", "In Process")` (Active).
3. $\text{Target Date} < \text{Reference Date}$.
$$\text{days\_overdue} = (\text{Reference Date} - \text{Target Date}).\text{days}$$

### 3. Overdue Operation / Job Card Rule
A Job Card is classified as overdue if and only if:
1. `docstatus < 2` (Not cancelled).
2. `status in ("Open", "Work In Progress")` (Uncompleted).
3. `expected_end_date` is in the past ($\text{expected\_end\_date.date()} < \text{Reference Date}$), or if `expected_end_date` is omitted, the parent Work Order is overdue and the operation is uncompleted.

---

## 5. Defensible Bottleneck Detection Rules

Rather than arbitrary colored cards or fabricated scores, bottlenecks are detected using 4 explicit, verifiable operational rules:

### Signal 1: Workstation Queue Accumulation (`type="queue"`)
- **Rule:** A workstation has $\ge 2$ uncompleted Job Cards (`status in ("Open", "Work In Progress")`) queued for execution.
- **Severity:** High if queue depth $\ge 4$; Medium if $\ge 2$.
- **Reason:** `"{queue_depth} jobs queued at workstation accumulating production backlog across {wos_count} Work Order(s)."`
- **Deduplication:** `affected_work_orders_count` counts distinct Work Orders (no double-counting).
- **Drilldown Records:** Links to `Workstation` form and affected `Job Card` forms.

### Signal 2: Overdue Operation Clusters (`type="overdue"`)
- **Rule:** A workstation or operation has $\ge 1$ overdue Job Cards that missed their target completion date.
- **Severity:** High if oldest overdue $\ge 7$ days; Medium otherwise.
- **Reason:** `"{overdue_count} operation(s) missed expected completion date; oldest delayed by {days} day(s)."`
- **Metric:** `overdue_operations_count`, `oldest_overdue_days`.

### Signal 3: Predecessor Dependency Lag (`type="predecessor"`)
- **Rule:** One or more operations are in state `"Waiting on Predecessor"`, where the upstream predecessor operation is incomplete or lagging.
- **Severity:** Medium.
- **Reason:** `"Downstream operations waiting on incomplete predecessor '{pred_op}' across {wos_count} Work Order(s)."`

### Signal 4: Material Staging Blocker (`type="material"`)
- **Rule:** Active Work Orders with open Job Cards where `material_transferred_for_manufacturing == 0`, meaning raw materials have not been transferred from stores to the WIP warehouse.
- **Severity:** High.
- **Reason:** `"Raw materials have not been transferred from stores to WIP warehouse for {count} active Work Order(s), holding back shop-floor execution."`

---

## 6. Backend API Contract: `get_production_pipeline`

- **Endpoint:** `/api/method/sarathi_visibility.api.production_pipeline.get_production_pipeline` (re-exported via `dashboard.py`)
- **HTTP Method:** `GET`
- **Capability Required:** `production` (Role check)
- **DocType Permission:** Read permission on `Work Order` and `Job Card`

### Supported Filters (`PIPELINE_FILTER_KEYS`)

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `company` | String | No | Company filter. User default company if omitted. |
| `status` | String | No | `"Active"` (default), `"All"`, `"Completed"`, `"Draft"`, `"Cancelled"`, or exact status. |
| `from_date` / `to_date` | Date | No | Bound on `Work Order.planned_start_date`. Validated `from_date <= to_date`. |
| `production_item` | String | No | Filter by item code. |
| `project` | String | No | Linked Project ID. Scoped to company. |
| `customer` | String | No | Filter Work Orders linked to customer via Project or Sales Order. |
| `workstation` | String | No | Filter Work Orders with operations at this workstation. |
| `operation` | String | No | Filter Work Orders with this operation. |
| `search` | String | No | Substring search on Work Order ID, item code, or item name. |
| `reference_at` | ISO Datetime | No | Simulation / reference timestamp for overdue calculations. |

### Sample Response Contract

```json
{
  "available": true,
  "reference_date": "2026-10-14",
  "summary": {
    "total_work_orders": 4,
    "material_staging": 1,
    "in_production": 0,
    "manufacture_receipt": 3,
    "completed": 0,
    "overdue_work_orders": 0,
    "overdue_operations": 0,
    "bottlenecks_detected": 7
  },
  "stages": [
    {
      "key": "Material Staging",
      "label": "1. Material Staging",
      "description": "Work Orders pending raw material issue/transfer",
      "count": 1,
      "jobs": [...]
    },
    {
      "key": "In Production",
      "label": "2. In Production",
      "description": "Active operations and Job Cards on the shop floor",
      "count": 0,
      "jobs": []
    },
    {
      "key": "Manufacture Receipt",
      "label": "3. Manufacture Receipt",
      "description": "Partial finished goods received via Stock Entry",
      "count": 3,
      "jobs": [...]
    },
    {
      "key": "Completed",
      "label": "4. Completed",
      "description": "100% finished goods produced and closed",
      "count": 0,
      "jobs": []
    }
  ],
  "pipeline_jobs": [
    {
      "work_order": "MFG-WO-2026-00009",
      "production_item": "ROBOT-ARM-01",
      "item_name": "Precision Robotic Articulated Arm",
      "customer": "Apex Robotics Ltd",
      "project": "PROJ-2026-001",
      "qty": 20.0,
      "produced_qty": 18.0,
      "remaining_qty": 2.0,
      "completion_percent": 90.0,
      "status": "Not Started",
      "docstatus": 1,
      "stage": "Manufacture Receipt",
      "is_active": true,
      "is_overdue": false,
      "days_diff": 9,
      "target_completion_date": "2026-10-23",
      "planned_start_date": "2026-09-10 00:00:00",
      "material_transferred": 0.0,
      "is_material_blocked": false,
      "is_predecessor_blocked": false,
      "current_operation": "Laser Cutting",
      "current_workstation": "Laser Cutting Shop",
      "current_op_status": "Ready to Start",
      "operations_count": 5,
      "operations": [
        {
          "job_card": "PO-JOB00005",
          "operation": "Laser Cutting",
          "workstation": "Laser Cutting Shop",
          "sequence": 1,
          "for_quantity": 20.0,
          "completed_qty": 0.0,
          "completion_percent": 0.0,
          "status": "Ready to Start",
          "is_overdue": false,
          "waiting_on": null,
          "previous_operation": null,
          "next_operation": "Bending"
        },
        {
          "job_card": "PO-JOB00006",
          "operation": "Bending",
          "workstation": "Welding Shop",
          "sequence": 2,
          "for_quantity": 20.0,
          "completed_qty": 0.0,
          "completion_percent": 0.0,
          "status": "Waiting on Predecessor",
          "is_overdue": false,
          "waiting_on": "Laser Cutting",
          "previous_operation": "Laser Cutting",
          "next_operation": "Welding"
        }
      ],
      "drilldown_route": ["Form", "Work Order", "MFG-WO-2026-00009"]
    }
  ],
  "delayed_operations": [],
  "bottlenecks": [
    {
      "id": "queue-Welding Shop",
      "type": "queue",
      "title": "Queue Backlog: Welding Shop",
      "workstation": "Welding Shop",
      "operation": "Welding",
      "severity": "medium",
      "affected_work_orders_count": 3,
      "affected_work_orders": ["MFG-WO-2026-00006", "MFG-WO-2026-00008", "MFG-WO-2026-00009"],
      "queue_depth": 3,
      "overdue_operations_count": 0,
      "oldest_overdue_days": 0,
      "reason": "3 jobs queued at workstation accumulating production backlog across 3 Work Order(s).",
      "drilldown_records": [
        {"doctype": "Workstation", "name": "Welding Shop"},
        {"doctype": "Job Card", "name": "PO-JOB00010"}
      ]
    }
  ],
  "applied_filters": {
    "company": "SarathiAILabs",
    "status": "Active"
  }
}
```

---

## 7. Performance & Zero N+1 Architecture

All data resolution is strictly batched:
1. Candidate Work Orders are retrieved in 1 query with indexed filters on `company`, `docstatus`, `planned_start_date`.
2. Job Cards are retrieved in 1 batch query: `frappe.get_all("Job Card", filters={"work_order": ["in", wo_names]})`.
3. Customer linkages are resolved in 2 batch queries on `Project` and `Sales Order`.
4. Manufacture receipts are retrieved in 1 batch query on `Stock Entry`.
5. Total database roundtrips: strictly **4 queries total**, regardless of whether the system has 10 or 5,000 Work Orders.

---

## 8. Test Execution & Validation Evidence

### DASH-017 Automated Test Suite
```bash
docker exec -w /home/frappe/frappe-bench/sites -u frappe frappe_docker_main-backend-1 \
  /home/frappe/frappe-bench/env/bin/python -c "
import frappe; frappe.init(site='frontend'); frappe.connect(); import unittest;
from sarathi_visibility.tests.test_production_pipeline import TestProductionPipeline;
suite = unittest.TestLoader().loadTestsFromTestCase(TestProductionPipeline);
res = unittest.TextTestRunner(verbosity=2).run(suite);
print('Ran:', res.testsRun, 'Errors:', len(res.errors), 'Failures:', len(res.failures))"
```
**Actual Result:**
```
Ran 33 tests in 9.781s
OK
Ran: 33 Errors: 0 Failures: 0
```

### Full Multi-Epic Regression Check (DASH-017 + DASH-016 + DASH-015)
```bash
docker exec -w /home/frappe/frappe-bench/sites -u frappe frappe_docker_main-backend-1 \
  /home/frappe/frappe-bench/env/bin/python -c "
import frappe; frappe.init(site='frontend'); frappe.connect(); import unittest;
from sarathi_visibility.tests.test_production_pipeline import TestProductionPipeline;
from sarathi_visibility.tests.test_work_orders import TestWorkOrderAndJobCardAPIs;
from sarathi_visibility.tests.test_factory_overview import TestFactoryOverview;
suite = unittest.TestSuite();
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestProductionPipeline));
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestWorkOrderAndJobCardAPIs));
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFactoryOverview));
res = unittest.TextTestRunner(verbosity=1).run(suite);
print('Ran:', res.testsRun, 'Errors:', len(res.errors), 'Failures:', len(res.failures))"
```
**Actual Result:**
```
Ran 89 tests in 13.071s
OK
Ran: 89 Errors: 0 Failures: 0
```

---

## 9. Missing Configuration & Future Dependencies

1. **DASH-018 — Material Readiness and Shortages:**
   - DASH-017 identifies `Material Staging` Work Orders where `material_transferred_for_manufacturing == 0`. DASH-018 will calculate exact warehouse item shortages and Bin balance deficits.
2. **DASH-019 — Workstation and Downtime Views:**
   - DASH-017 detects queue accumulation and overdue operations at workstations. DASH-019 will build detailed shift capacities, operational downtime, and OEE tracking.
3. **DASH-020 — Quality, Rework, and Subcontracting:**
   - DASH-017 preserves `quality_inspection` and `is_corrective_job_card` references on Job Cards to support quality holds and rework loops in DASH-020.
4. **DASH-021 — Production Exception and Escalation Queue:**
   - DASH-017 bottleneck signals (`queue`, `overdue`, `predecessor`, `material`) provide verified inputs for the exception queue and automated escalation rules.
