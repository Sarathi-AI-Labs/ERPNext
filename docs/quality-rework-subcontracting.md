# DASH-020 — Quality, Rework, and Subcontracting Views Documentation

## 1. Executive Summary & Architecture

- **Task ID:** DASH-020
- **Task Name:** Implement Quality, Rework, and Subcontracting Views
- **Parent Epic:** DASH-014 — Production Management Control Tower
- **Primary Application:** `sarathi_visibility`
- **Dashboard Route:** `/desk/sarathicontroltower`
- **Backend API Module:** [`sarathi_visibility/sarathi_visibility/api/quality_rework.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/quality_rework.py)
- **Re-exported Module:** [`sarathi_visibility/sarathi_visibility/api/dashboard.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/dashboard.py)
- **Frontend Page Template:** [`sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html)
- **Frontend Controller Logic:** [`sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js)
- **CSS Stylesheet:** [`sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css)
- **Native Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_quality_rework.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_quality_rework.py)
- **Standalone Logic Test Suite:** [`sarathi_visibility/sarathi_visibility/tests/test_quality_rework_logic.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_quality_rework_logic.py)

DASH-020 delivers three permission-aware, read-focused operational views inside the existing Production Management Control Tower (`/desk/sarathicontroltower`):

1. **Quality Overview:** Tracks quality inspections across incoming materials and in-process Job Cards, calculates pass/fail counts and failure rate percentages, summarizes item defect rejections, and renders paginated inspection logs.
2. **Rework Overview:** Traceably identifies actual corrective production actions via ERPNext corrective Job Cards (`is_corrective_job_card = 1`), associates parent Job Cards and failed Quality Inspections, or clearly reports when rework tracking is unconfigured rather than fabricating records.
3. **Subcontracting Overview:** Tracks outsourced manufacturing operations using standard `Subcontracting Order` and `Subcontracting Order Item` records, reconciles ordered, received, and outstanding quantities, flags overdue supplier deliveries, and highlights fulfillment progress.

---

## 2. Installed ERPNext & Frappe Version Context

- **Platform:** Frappe Framework v14 / v15 compatible architecture.
- **Manufacturing Engine:** ERPNext Manufacturing & Stock modules.
- **Subcontracting Model:** Native `Subcontracting Order` and `Subcontracting Receipt` DocTypes (decoupled from standard Purchase Order receipts).
- **Rework Model:** In standard ERPNext, rework is handled via corrective `Job Card` records with `is_corrective_job_card = 1`, linked to the failed Job Card via `for_job_card` and root `quality_inspection`.
- **System of Record:** All views are strictly read-focused, querying genuine database records without mutating transactions or bypassing Frappe document permissions.

---

## 3. Quality Overview

### 3.1 Data Model & Authoritative Fields

| DocType | Fields Used | Purpose in Quality Overview |
| :--- | :--- | :--- |
| **`Quality Inspection`** | `name`, `inspection_type`, `reference_type`, `reference_name`, `item_code`, `item_name`, `status`, `report_date`, `sample_size`, `inspected_by`, `docstatus`, `company` | Inspection identifier, reference document, inspected item, pass/fail result, sample quantity, and inspector. |
| **`Item`** | `name`, `item_name`, `stock_uom`, `item_group` | Item master details and verified Stock Unit of Measure. |

### 3.2 Quality KPIs & Formulas

- **Total Quality Inspections:** Submitted quality inspections (`docstatus == 1`) within the selected period and company scope. Canceled inspections (`docstatus == 2`) are excluded.
- **Passed Inspections:** Submitted inspections where `status == "Accepted"`.
- **Failed Inspections:** Submitted inspections where `status == "Rejected"`.
- **Draft Inspections:** Active draft inspections (`docstatus == 0`) awaiting formal submission or sign-off.
- **Failure Rate Percentage:**
  $$\text{Failure Rate} = \left(\frac{\text{Failed Inspections}}{\text{Total Submitted Inspections}}\right) \times 100$$
  Evaluates to `0.0%` when no submitted inspections exist.
- **Distinct Defect Items:** Count of unique items with at least one rejected inspection in the active filtered view.
- **Top Defect Breakdown:** Aggregates rejections by `item_code`, summing rejected inspection occurrences and inspected sample units.

### 3.3 Quality Drill-down

Every row in the Quality Inspection table includes links to:
- The `Quality Inspection` document itself (`data-inspect-qi`).
- The reference document (e.g. `Job Card`, `Purchase Receipt`, or `Work Order`).
- The inspected `Item` master (`data-inspect-item`).

All links strictly respect the logged-in user's role-based document permissions.

---

## 4. Rework Overview

### 4.1 How Rework is Represented in this Installation

In ERPNext, rework does not use an ad-hoc text string. It is represented through **corrective Job Cards**:
- `Job Card.is_corrective_job_card = 1`
- `Job Card.for_job_card`: Links back to the original operational Job Card that required rework.
- `Job Card.quality_inspection`: Links back to the failed Quality Inspection record that triggered the corrective action.
- `Job Card.work_order`: The parent manufacturing Work Order.

### 4.2 Truthful Representation When Unconfigured

> [!IMPORTANT]
> If an installation does not have `is_corrective_job_card` configured on `Job Card`, or if no corrective Job Cards exist, DASH-020 **never fabricates records** or presents zero values as an all-clear signal.
> It displays an explicit informative banner:
> *"Rework tracking is not configured in this ERPNext installation. Rework tracking requires corrective Job Cards (`is_corrective_job_card = 1`) linked via `for_job_card`."*

### 4.3 Rework KPIs & Operational Statuses

Where configured and available:
- **Total Rework Jobs:** All active corrective Job Cards (`is_corrective_job_card == 1` and `docstatus < 2`).
- **In Progress Rework:** Jobs currently being executed on the shop floor (`status == "Work In Progress"`).
- **Queued Rework:** Jobs waiting to be started (`status == "Open"`).
- **Completed Rework:** Successfully finished corrective jobs (`status == "Completed"`).
- **Delayed Rework:** Active jobs whose `expected_end_date` is earlier than the reference date (`days_to_target < 0` and `status != "Completed"`).
- **Total Units in Rework:** Sum of `for_quantity` across all corrective Job Cards.

---

## 5. Subcontracting Overview

### 5.1 Subcontracting Workflow & Source of Truth

The subcontracting workflow relies on ERPNext v14/v15's native subcontracting architecture:
1. `Purchase Order` specifies outsourced service item with subcontracting enabled.
2. `Subcontracting Order` tracks outsourced manufacturing orders, supplier assignment, schedule dates, and items to be received.
3. Raw materials are transferred to the subcontractor via `Stock Entry` (Material Transfer for Subcontract).
4. `Subcontracting Receipt` records finished items received back from the subcontractor and auto-consumes supplied materials.

### 5.2 Distinction of Material Locations

To prevent double-counting:
1. **Internal Warehouse Stock:** Material in internal stores (`Bin.actual_qty`).
2. **Material Transferred to Subcontractor:** Tracked via `Subcontracting Order Supplied Item` and transfer Stock Entries.
3. **Goods Received:** Recorded against `Subcontracting Order Item.received_qty`.
4. **Outstanding Order Quantity:**
   $$\text{Outstanding Qty} = \max(0, \text{total\_qty} - \text{received\_qty})$$

### 5.3 Subcontracting KPIs & Formulas

- **Total Subcontract Orders:** Total orders within scope (`docstatus != 2`).
- **Active Subcontracts:** Submitted orders with status in `("Open", "Material Transferred", "Partial Material Transferred", "Partially Received")`.
- **Awaiting Receipt:** Orders where `per_received < 100` and status is not completed/closed.
- **Overdue Subcontracts:** Orders where `schedule_date < reference_date` and status is not completed/closed.
- **Total Ordered Units:** Sum of `total_qty` across all subcontracting orders.
- **Total Received Units:** Reconciled sum of received item quantities (`received_qty`).
- **Total Outstanding Units:** Reconciled remaining quantity across orders.

---

## 6. Backend API & Zero N+1 Architecture

All endpoints reside in [`sarathi_visibility/sarathi_visibility/api/quality_rework.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/quality_rework.py) and are re-exported through [`sarathi_visibility/sarathi_visibility/api/dashboard.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/api/dashboard.py).

### 6.1 Server-Side Validation

The helper `validate_quality_rework_filters(filters)` enforces:
- Capability authorization: `require_capability("production")`.
- Parameter allowlist validation against `QUALITY_FILTER_KEYS`.
- Date range ordering: `from_date <= to_date`.
- Cross-company boundary isolation: checks that linked `Work Order`, `Job Card`, and `Company` belong to the user's permitted company scope.
- Status and inspection type allowlist matching.

### 6.2 Strict Zero N+1 Batched Queries

Each overview endpoint executes **strictly at most two batched database queries**:
- **`get_quality_overview`:**
  - Query 1: `Quality Inspection` records with parameterized company and date filters.
  - Query 2: `Item` master metadata in a single `in` batch for all referenced items.
- **`get_rework_overview`:**
  - Query 1: `Job Card` records matching `is_corrective_job_card = 1`.
  - Query 2: `Work Order` metadata in a single `in` batch.
- **`get_subcontracting_overview`:**
  - Query 1: `Subcontracting Order` records.
  - Query 2: `Subcontracting Order Item` child lines in a single `in` batch.

---

## 7. Frontend Implementation

### 7.1 Dashboard Structure

The views are mounted directly in the main Production Management Control Tower (`/desk/sarathicontroltower`):
- Quality Overview Panel: `[data-quality-overview-panel]`
- Rework Overview Panel: `[data-rework-overview-panel]`
- Subcontracting Overview Panel: `[data-subcontracting-overview-panel]`

### 7.2 UI Components & Micro-interactions

- **KPI Cards:** Rendered using shared `frappe.sarathiUI.kpi` components with color indicators (blue for totals, green for passed, red for rejections/delays, amber for pending/drafts).
- **Status Filter Pills:** Instant client-side filtering by status (`Accepted`, `Rejected`, `Draft` in Quality; `Open`, `Work In Progress`, `Completed` in Rework; `Open`, `Partially Received`, `Completed` in Subcontracting).
- **Defect Breakdown Bar:** Highlights top rejected items with rejection count and sample unit totals.
- **Fulfillment Progress Bar:** Subcontracting orders display a visual percentage progress bar for received quantities.
- **Drill-down Actions:** Buttons open authorized ERPNext documents (`Quality Inspection`, `Job Card`, `Work Order`, `Subcontracting Order`, `Supplier`).

### 7.3 Responsive Design

- **Desktop (>= 1200px):** 5-column KPI grid, full data tables with all reference and inspector badges.
- **Tablet (768px – 1199px):** 3-column KPI grid, wrapped table cells.
- **Mobile (< 768px):** 1-column stacked KPI cards, horizontal table scrolling with pinned record IDs.

---

## 8. Test Execution & Verification

### 8.1 Standalone Test Runner

The standalone test suite [`sarathi_visibility/sarathi_visibility/tests/test_quality_rework_logic.py`](file:///d:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main/sarathi_visibility/sarathi_visibility/tests/test_quality_rework_logic.py) validates all validation, calculation, and permission rules locally without Docker dependencies:

```bash
python sarathi_visibility/sarathi_visibility/tests/test_quality_rework_logic.py
```

**Actual Execution Result:**
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.015s

OK
```

All 9 tests passed:
1. `test_filter_allowlist_rejection` — PASSED
2. `test_date_bounds_validation` — PASSED
3. `test_unsupported_status_choice` — PASSED
4. `test_cross_company_isolation` — PASSED
5. `test_quality_overview_passed_failed_calculation` — PASSED
6. `test_quality_overview_unauthorized_scope` — PASSED
7. `test_rework_overview_corrective_jobs` — PASSED
8. `test_rework_overview_unconfigured_field` — PASSED
9. `test_subcontracting_overview_quantities_and_overdue` — PASSED

---

## 9. Known Limitations & Recommendations

1. **Rework Classification:** If an organization logs rework via ad-hoc notes on normal Job Cards rather than marking `is_corrective_job_card = 1`, those jobs cannot be programmatically verified as rework. Organizations should formalize corrective Job Cards linked via `for_job_card`.
2. **Subcontract Material Scrap:** Scrap generated at subcontractor sites is only captured when recorded in `Subcontracting Receipt` scrap items. Unrecorded vendor scrap cannot be inferred from stock balance alone.
3. **Telemetric Quality Testing:** Quality inspections in this dashboard reflect signed-off records in ERPNext, not continuous in-line automated sensor streams.
