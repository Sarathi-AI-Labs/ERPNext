# DASH-012: Manufacturing and Inventory Summary

## 1. Executive Summary

| Attribute | Specification |
|:---|:---|
| **Task ID** | DASH-012 |
| **Task Name** | Implement Manufacturing and Inventory Summary |
| **Parent Epic** | DASH-007 — Owner & Executive Dashboard |
| **Primary App** | `sarathi_owner` |
| **Expected Route** | `/desk/sarathiownertower` |
| **Target Role** | Owner / Executive (`Sarathi Owner`, `System Manager`) |
| **Objective** | Provide executive management with reliable, permission-aware manufacturing and inventory summary KPIs using actual ERPNext manufacturing transactions and stock valuation ledger logic. |

---

## 2. KPI Dictionary & Business Rules

### Feature A & B — Manufacturing Overview and Production Output

| KPI | Label | Source DocType & Fields | Formula / Definition | Inclusion / Exclusion Rules | Grouping Grain |
|:---|:---|:---|:---|:---|:---|
| **Active Work Orders** | Active Work Orders | `Work Order`: `status`, `docstatus` | `COUNT(*)` where `docstatus = 1` and `status IN ('Not Started', 'In Process', 'Submitted')` | Draft (`docstatus=0`), Cancelled (`docstatus=2`), Stopped, and Completed are excluded. | Distinct Work Order |
| **Completed Work Orders** | Completed Work Orders | `Work Order`: `status`, `docstatus` | `COUNT(*)` where `docstatus = 1` and `status = 'Completed'` | Draft, active, cancelled, and stopped are excluded. | Distinct Work Order |
| **Overdue Work Orders** | Overdue Work Orders | `Work Order`: `planned_end_date`, `expected_delivery_date`, `status` | Active Work Orders where `target_completion_date < reference_date` (`target_completion_date = planned_end_date or expected_delivery_date`) | Completed, cancelled, and stopped orders excluded. Orders without expected dates are marked "Unknown", never assumed overdue. | Distinct Work Order |
| **Jobs Due Soon** | Jobs Approaching Completion | `Work Order`: `planned_end_date`, `expected_delivery_date`, `status` | Active Work Orders where `reference_date <= target_completion_date <= reference_date + review_days` | Review window defaults to 7 days (configurable 0–90 days). | Distinct Work Order |
| **Planned Production Qty** | Planned Production Quantity | `Work Order`: `qty`, `stock_uom` | `SUM(qty)` grouped strictly by `stock_uom` | Excludes Draft and Cancelled orders. **Never sums unlike UOMs (e.g. Kg + Nos).** | `stock_uom` and `production_item` |
| **Actual Produced Qty** | Actual Produced Quantity | `Work Order`: `produced_qty`, `stock_uom` | `SUM(produced_qty)` grouped strictly by `stock_uom` | Verified cumulative output updated by submitted manufacture Stock Entries. | `stock_uom` and `production_item` |
| **Production Variance** | Production Variance | Derived | `produced_qty - planned_qty` | Positive indicates output ahead of target; negative indicates remaining output. | `stock_uom` and `production_item` |
| **Production Achievement** | Production Achievement (%) | Derived | `(produced_qty / planned_qty) * 100` if `planned_qty > 0` else `0.0%` | Safe division by zero handling. Evaluated strictly within compatible UOMs. | `stock_uom` and `production_item` |

---

### Feature C — Inventory Valuation

| Metric | Source DocType & Engine | Formula / Valuation Logic | Currency & Warehouse Scope | Strict Business Rule |
|:---|:---|:---|:---|:---|
| **Total Inventory Valuation** | `Bin`: `stock_value` for leaf warehouses (`Warehouse.is_group = 0`). Historical: `erpnext.stock.report.stock_balance.stock_balance`. | `SUM(Bin.stock_value)` across company leaf warehouses. When historical `to_date` is specified in the past, executes standard ERPNext Stock Balance report. | Company default currency (e.g. `INR`). Scoped to company leaf warehouses or filtered warehouse. | **CRITICAL:** Inventory value is NEVER calculated as naive `qty * latest purchase price`. Valuation strictly uses ERPNext perpetual inventory valuation. |
| **Total Items in Stock** | `Bin`: `item_code` | `COUNT(DISTINCT item_code)` | Non-group leaf warehouses belonging to company. | Group warehouses excluded to prevent duplicate counting. |

---

### Feature D — Stock Availability and Inventory Risk

| Stock Concept | Field / Calculation | Business Definition |
|:---|:---|:---|
| **Actual Stock** | `Bin.actual_qty` | Physical recorded stock balance in warehouse under ERPNext stock ledger. |
| **Reserved Stock** | `Bin.reserved_qty` | Stock committed to open Sales Orders, Work Orders, or Subcontracting. |
| **Available Stock** | `max(0.0, actual_qty - reserved_qty)` | Immediately usable stock balance after accounting for committed reservations. |
| **Projected Quantity** | `Bin.projected_qty` | ERPNext native projected stock including incoming POs/WOs minus outgoing demands. |
| **Low-Stock Item** | `Item Reorder.warehouse_reorder_level` or `Item.safety_stock` | Flagged when `available_qty <= threshold` or `projected_qty <= threshold`. Items without thresholds are explicitly classified as `No threshold configured` (never assigned an invented threshold). |
| **Negative Projected** | `Bin.projected_qty < 0` | Demand commitments exceed on-hand stock plus incoming purchase/production orders. |
| **Zero Stock with Demand** | `actual_qty <= 0 and reserved_qty > 0` | Stockouts where active demand or customer commitments exist. |

---

### Feature E — Material Shortages Affecting Production

| Element | Calculation & Source | Logic |
|:---|:---|:---|
| **Scope** | Active Work Orders (`docstatus = 1` and `status IN ('Not Started', 'In Process')`) | Only evaluates open manufacturing orders requiring raw material issuance. |
| **Remaining Requirement** | `Work Order Item`: `max(0.0, required_qty - transferred_qty)` | Raw material still needed to transfer to WIP for this Work Order. If already transferred, requirement is zero. |
| **Available in Warehouse** | `Bin`: `max(0.0, actual_qty - reserved_qty)` in `source_warehouse` | Available uncommitted stock in the specific warehouse assigned to provide the material. |
| **Shortage Quantity** | `max(0.0, remaining_requirement - available_in_warehouse)` | Deficit preventing Work Order material transfer. |
| **Affected Records** | Work Order link, Assembling Item, Raw Material, Source Warehouse, Target Completion Date | Links management directly to the source Work Order and Item documents in ERPNext. |

---

## 3. Architecture & API Implementation

### Backend Module: `sarathi_owner/sarathi_owner/api/manufacturing_inventory.py`
- Exposes `@frappe.whitelist(methods=["GET"]) @read_errors def get_manufacturing_inventory_summary(filters=None, **extra)`
- Role check: `require_capability("owner")` ensures only authorized executives (`Sarathi Owner`, `System Manager`) can execute.
- Strict filter allowlist: `FEATURE_KEYS = {"warehouse", "mfg_status", "shortage_only", "reference_at", "review_days", "wo_start", "wo_page_length", "stock_start", "stock_page_length", "shortage_start", "shortage_page_length"}` and `BASE_KEYS = {"company", "customer", "project", "from_date", "to_date"}`.
- Bounded pagination: `wo_page_length`, `stock_page_length`, `shortage_page_length` (default 25, bounded up to 100).
- Safe parameterization: All queries use ORM (`frappe.get_all`, `frappe.get_list`) or parameterized SQL (`frappe.db.sql`) with explicit company boundary filters.

### Homepage Adapter Integration: `sarathi_owner/sarathi_owner/api/homepage.py`
- Integrated `FEATURE_KEYS as MFG_KEYS` into `get_homepage` allowed filters.
- Invokes `get_manufacturing_inventory_summary({**mfg_filters, "company": company})` and attaches payload under `data.manufacturing_inventory`.
- Added `warehouses` to `options` endpoint with company validation.

### UI Homepage Adapter: `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js`
- Integrated responsive `renderManufacturingInventory` section:
  1. **Manufacturing Overview:** 6 KPI cards (Active, Completed, Overdue, Due Soon, Draft, Cancelled), UOM Output breakdown cards, Work Order progress list with pagination.
  2. **Inventory Valuation & Stock Availability:** 4 KPI cards (Total Valuation with Stock Balance drill-down, Actual Stock, Reserved Stock, Projected Stock), 4 Stock Risk count cards, Stock items risk list.
  3. **Material Shortages:** 3 KPI cards (Affected Work Orders, Shortage Items, Shortage Lines), Material requirements table highlighting shortage quantities and source warehouses.
- Filter Bar integration: Added `warehouse`, `mfg_status`, and `shortage_only` controls with live option search.

---

## 4. Live Reconciliation Evidence

Executed via `sarathi_owner/sarathi_owner/tests/reconcile_manufacturing_inventory.py` against live database records in `SarathiAILabs`:

| Dimension | Dashboard Metric | Dashboard Value | ERPNext Native DB / Report Value | Variance / Difference | Status |
|:---|:---|:---|:---|:---|:---|
| **Work Orders** | Total Work Orders | 7 | 7 (`tabWork Order`) | 0 | **Reconciled** |
| | Active Work Orders | 4 | 4 (`docstatus=1, status in ('Not Started', 'In Process')`) | 0 | **Reconciled** |
| | Completed Work Orders | 2 | 2 (`docstatus=1, status='Completed'`) | 0 | **Reconciled** |
| | Draft Work Orders | 1 | 1 (`docstatus=0`) | 0 | **Reconciled** |
| | Overdue Work Orders | 0 | 0 (No active WO has completion date < 2026-10-14) | 0 | **Reconciled** |
| **Inventory** | Total Stock Valuation | 32,536,350.00 INR | 32,536,350.00 INR (`tabBin.stock_value`) | 0.00 | **Reconciled** |
| | ERPNext Stock Balance Report | 32,536,350.00 INR | 32,536,350.00 INR (`erpnext.stock.report.stock_balance`) | 0.00 | **Reconciled** |
| | Total Actual Stock Qty | 44,478.00 | 44,478.00 (`tabBin.actual_qty`) | 0.00 | **Reconciled** |
| | Total Reserved Stock Qty | 158.00 | 158.00 (`tabBin.reserved_qty`) | 0.00 | **Reconciled** |
| | Total Projected Stock Qty | 25,991.00 | 25,991.00 (`tabBin.projected_qty`) | 0.00 | **Reconciled** |
| | Distinct Stock Items | 10 | 10 distinct items in `tabBin` | 0 | **Reconciled** |
| **Stock Risks** | Negative Projected Items | 5 | 5 (`AERO-MOUNT-01`, `DIE-FIXTURE-01`, `EV-BATTPACK-01`, `EV-CHASSIS-01`, `ROBOT-ARM-01`) | 0 | **Verified** |
| | Zero Stock with Demand | 5 | 5 items | 0 | **Verified** |
| **Material Shortages** | Shortage Lines (Active WOs) | 0 | 0 (Current raw material inventory in `Stores - S` exceeds requirements) | 0 | **Reconciled** |

---

## 5. Automated Test Suite Results

### 1. `test_manufacturing_inventory.py`
- Executed inside container `frappe_docker_main-backend-1`:
  - **Tests Run:** 28
  - **Failures:** 0
  - **Errors:** 0
  - **Result:** `OK (100% Passed)`
- Test Coverage:
  - Security gating: Non-owners (`manager`, `operator`, `supervisor`, `unrelated`, `finance_only`) denied with `PermissionError`.
  - Multi-company isolation: Mismatched companies denied.
  - Strict input validation: Bad dates, reversed date bounds, malformed `reference_at`, invalid `review_days`, invalid `mfg_status`, invalid `warehouse` rejected with `ValidationError`.
  - Work Order lifecycle & health classification: Draft, Cancelled, Stopped, Completed, Overdue, Due Soon, On Track, Unknown.
  - UOM integrity: Production planned vs actual output aggregated per UOM, never mixed.
  - Inventory valuation: Matches native `Bin.stock_value` for leaf warehouses.
  - Stock risk distinction: Physical, reserved, available, projected stock verified.
  - Shortage calculation: Remaining requirement vs warehouse available stock verified.

### 2. `test_homepage.py`
- Executed inside container `frappe_docker_main-backend-1`:
  - **Tests Run:** 27
  - **Failures:** 0
  - **Errors:** 0
  - **Result:** `OK (100% Passed)`

---

## 6. Mobile Responsiveness & Browser Audit

Executed via Playwright in `sarathi_owner/sarathi_owner/tests/audit_manufacturing_inventory_browser_local.py`:

| Viewport Tested | Window Width | Window Scroll Width | Dashboard Container Overflow | Status |
|:---|:---|:---|:---|:---|
| **Mobile Phone (Compact)** | 360 px | 360 px | None (`[]`) | **PASS** |
| **iPhone 12 / 13 / 14** | 390 px | 390 px | None (`[]`) | **PASS** |
| **Large Mobile Phone** | 480 px | 480 px | None (`[]`) | **PASS** |
| **Small Tablet (Portrait)** | 767 px | 767 px | None (`[]`) | **PASS** |
| **iPad (Portrait)** | 768 px | 768 px | None (`[]`) | **PASS** |
| **Tablet (Landscape)** | 1023 px | 1023 px | None (`[]`) | **PASS** |
| **Desktop (Small)** | 1024 px | 1024 px | None (`[]`) | **PASS** |
| **Desktop (Large 1080p/2K)** | 1440 px | 1440 px | None (`[]`) | **PASS** |
| **Mobile Landscape** | 844 px | 844 px | None (`[]`) | **PASS** |

### Visual Artifacts Captured:
- `docs/manufacturing-inventory-evidence/mfg-inventory-390.png` (Mobile Phone)
- `docs/manufacturing-inventory-evidence/mfg-inventory-768.png` (Tablet)
- `docs/manufacturing-inventory-evidence/mfg-inventory-1440.png` (Desktop)
- `docs/manufacturing-inventory-evidence/inv-summary-390.png` (Mobile Phone)
- `docs/manufacturing-inventory-evidence/inv-summary-768.png` (Tablet)
- `docs/manufacturing-inventory-evidence/inv-summary-1440.png` (Desktop)
- `docs/manufacturing-inventory-evidence/browser-results.json` (Full audit execution log: 0 JS errors, 0 HTTP errors).

---

## 7. Files Created or Modified

| File Path | Type | Action | Purpose |
|:---|:---|:---|:---|
| `sarathi_owner/sarathi_owner/api/manufacturing_inventory.py` | Python Backend | **Created** | Core business logic, status rules, stock valuation, risk metrics, shortages, and `@frappe.whitelist` endpoint. |
| `sarathi_owner/sarathi_owner/api/homepage.py` | Python Backend | **Modified** | Integrated `manufacturing_inventory` into `get_homepage` and added `warehouses` to `options`. |
| `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js` | Frontend Adapter | **Modified** | Added warehouse/mfg filter controls, option loader, and `renderManufacturingInventory` UI renderer. |
| `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css` | Frontend Styling | **Modified** | Added responsive styles, UOM cards, and scrollable table regions for manufacturing/inventory. |
| `sarathi_owner/sarathi_owner/tests/test_manufacturing_inventory.py` | Automated Test | **Created** | 28 automated tests covering security, filter validations, formulas, valuations, and shortages. |
| `sarathi_owner/sarathi_owner/tests/reconcile_manufacturing_inventory.py` | Reconciliation | **Created** | Compares dashboard metrics against native `tabWork Order`, `tabBin`, and `Stock Balance` report. |
| `sarathi_owner/sarathi_owner/tests/audit_manufacturing_inventory_browser_local.py` | Playwright Audit | **Created** | Tests 9 responsive viewports, checks overflow, and generates screenshot evidence. |
| `docs/manufacturing-inventory-evidence/*` | Evidence | **Created** | 6 full-page screenshots and `browser-results.json`. |
| `docs/manufacturing-inventory-summary.md` | Deliverable Doc | **Created** | Complete task documentation, dictionary, reconciliation, and audit evidence. |

---

## 8. Strictly Maintained Constraints

1. **Strictly DASH-012 Scope:** No work performed on DASH-013 (approvals and business risks), Production Control Tower operations board, or Shop Floor.
2. **ERPNext/Frappe Core Source Untouched:** Zero edits, monkey-patches, or schema changes in `ERPNEXT_MAIN/`, `apps/erpnext/`, or `apps/frappe/`.
3. **No Naive Inventory Price Formula:** Valuation strictly derives from ERPNext perpetual inventory ledger balance (`Bin.stock_value` and `Stock Balance` report logic).
4. **Units of Measure Never Mixed:** Production output and achievement are grouped strictly by `stock_uom`.
5. **No Invented Numbers:** All KPIs, stock risks, and shortages calculate from verifiable live ERPNext records.
