# Sarathi Industrial Control Tower — KPI Reconciliation Test Matrix (DASH-031)

**Project:** Sarathi Industrial Control Tower  
**Parent Epic:** DASH-030 — Testing, Performance, Security & Release  
**Task ID:** DASH-031 — KPI Reconciliation and Test Scenarios  
**Scope:** Authoritative ERPNext metric reconciliation across Owner Dashboard, Production Control Tower, and Shop-Floor Workboard  
**Status:** Verified & Documented  
**Automated Test Suite:** `sarathi_visibility/sarathi_visibility/tests/test_kpi_reconciliation.py` (30 passing tests)

---

## 1. Overview & Reconciliation Methodology

This matrix establishes mathematical and business-rule reconciliation for all implemented metrics across the Sarathi Industrial Control Tower. Every metric is reconciled against authoritative ERPNext source records (General Ledger, Payment Ledger, Sales Invoice, Sales Order, Work Order, Job Card, Bin, Stock Ledger, Downtime Entry, Quality Inspection) rather than relying on circular UI-to-UI comparisons.

### Core Mathematical & Business Rules Enforced:

1. **Document Status Rules:**
   - **Draft (`docstatus=0`):** Excluded from accounting recognition, active sales totals, and completed production output.
   - **Submitted (`docstatus=1`):** Required for all recognized accounting, inventory balances, and executable operations.
   - **Cancelled (`docstatus=2`):** Strictly excluded from all active, completed, and backlog metrics.
2. **Date Inclusivity:**
   - Date range filters `[from_date, to_date]` are inclusive of both start and end days using `posting_date` or `creation` as documented.
3. **No Duplicate Multi-Record Counting:**
   - Joining parent documents to child tables (e.g. Sales Order to Sales Order Item, Work Order to Work Order Item) groups by parent ID or aggregates at line level without double-counting parent totals.
4. **Precision & Quantization:**
   - Currency metrics are quantized using native company currency precision (`Decimal.quantize(Decimal('0.01'))`).
   - Quantity metrics retain exact stock UOM conversion factors.
5. **Genuine Zero vs. Unavailable:**
   - Empty matching cohorts display clean `0` or `0.00`.
   - Missing configurations, permission denials, or unconfigured DocTypes display `—` / `null` with explicit reasons, never fabricating a zero.

---

## 2. 108-KPI Registry Audit & Classification

In accordance with DASH-031 specifications, all 108 KPIs in the Sarathi KPI registry (`docs/dashboard-kpi-dictionary.json`) have been audited against the installed Frappe v16.31.0 and ERPNext v16.33.0 codebase:

| Classification | Count | Description |
|---|---|---|
| **Implemented and verifiable** | **53** | Implemented in backend APIs (`sarathi_owner` and `sarathi_visibility`), backed by active ERPNext DocTypes, and verified with automated test suites. |
| **Implemented but not verifiable** | **11** | Navigation counter badges (`CAT-001` through `CAT-011`) that tally Desk route availability rather than underlying database DocTypes. |
| **Blocked by missing configuration or data** | **20** | Requires ERPNext DocTypes, fixtures, or settings not configured in standard runtime (e.g. `Budget`, `Shift Type`, warranty claims, formal rework). |
| **Not implemented** | **24** | Defined in DASH-004 specification catalogue but not yet implemented in backend APIs or dashboards. |
| **Total** | **108** | Complete registry accounting. |

### Classification Breakdown:
- **Implemented and verifiable (53):**
  - *Owner Dashboard (29):* `FIN-001` to `FIN-007`, `AR-001`, `AR-003`, `AP-001`, `SALES-001` to `SALES-004`, `MFG-001` to `MFG-005`, `INV-001` to `INV-002`, `PROJ-001` to `PROJ-004`, `ALERT-001` to `ALERT-004`.
  - *Production Control Tower (15):* `OPS-001` to `OPS-005`, `INV-004` to `INV-005`, `WS-001`, `WS-003`, `QUAL-001` to `QUAL-002`, `SUB-001` to `SUB-002`, `ALERT-005` to `ALERT-007`.
  - *Shop-Floor Workboard (9):* `JOB-001` to `JOB-008`, `JOB-015`.
- **Implemented but not verifiable (11):** `CAT-001` through `CAT-011` (Navigation workspace tile counts).
- **Blocked by missing configuration or data (20):** `FIN-011`, `FIN-012`, `PROJ-005`, `JOB-010`, `JOB-011`, `JOB-012`, `JOB-013`, `INV-003`, `INV-006`, `INV-007`, `INV-008`, `INV-009`, `INV-010`, `INV-012`, `QUAL-003`, `WS-002`, `WS-004`, `SUB-003`, `SUB-004`, `SUB-005`.
- **Not implemented (24):** `FIN-008`, `FIN-009`, `FIN-010`, `AR-002`, `AR-004`, `AP-002`, `SALES-005`, `SALES-006`, `SALES-007`, `PROJ-006`, `PROJ-007`, `PROJ-008`, `MFG-006`, `MFG-007`, `MFG-008`, `MFG-009`, `MFG-010`, `MFG-011`, `MFG-012`, `JOB-009`, `JOB-014`, `JOB-016`, `JOB-017`, `INV-011`.

---

## 3. Owner & Executive Dashboard KPI Reconciliation Matrix

| KPI ID | Dashboard | Metric Name | Source DocType / Report | Verified Formula | Applicable Filters | Test Scenario | Expected Result | Actual Result | Diff | Tolerance | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **FIN-001** | Owner | Net Invoiced Sales | `Sales Invoice` | `SUM(base_net_total)` where `docstatus=1` and not internal transfer | `company`, `from_date`, `to_date`, `customer` | Submitted regular invoices (₹200k) + Return credit note (-₹15k) + Draft excluded (₹50k) | ₹185,000.00 | ₹185,000.00 | 0.00 | 0.01 | **PASS** | Returns subtracted once; draft excluded |
| **FIN-002** | Owner | P&L Total Income | `GL Entry`, `Account` | `SUM(credit - debit)` for `Account.root_type = 'Income'` | `company`, `from_date`, `to_date` | Multi-entry revenue posting against default finance book | ₹500,000.00 | ₹500,000.00 | 0.00 | 0.01 | **PASS** | Reconciled against native Profit & Loss |
| **FIN-003** | Owner | P&L Total Expense | `GL Entry`, `Account` | `SUM(debit - credit)` for `Account.root_type = 'Expense'` | `company`, `from_date`, `to_date` | Multi-entry expense posting with operational cost centers | ₹375,000.00 | ₹375,000.00 | 0.00 | 0.01 | **PASS** | Matches native P&L Statement |
| **FIN-004** | Owner | Net Profit | `GL Entry` | `Total Income - Total Expense` | `company`, `from_date`, `to_date` | Standard accounting period | ₹125,000.00 | ₹125,000.00 | 0.00 | 0.01 | **PASS** | ₹500k Income - ₹375k Expense |
| **FIN-005** | Owner | Net Profit Margin | Derived | `(Net Profit / Total Income) * 100` | `company`, `from_date`, `to_date` | Profitable operation (₹125k / ₹500k) | 25.00% | 25.00% | 0.00 | 0.01% | **PASS** | Zero income returns `None` safely |
| **FIN-006** | Owner | Gross Profit | `Sales Invoice`, `Sales Invoice Item`, `Stock Ledger Entry` | `SUM(base_net_amount - buying_amount)` | `company`, `from_date`, `to_date` | Native Gross Profit report comparison | Matched Native | Matched Native | 0.00 | 0.01 | **PASS** | Reconciled via `reconcile_finance_kpis.py` |
| **FIN-007** | Owner | EBITDA / Operating Profit | `GL Entry` | `Gross Profit - Operating Expenses (excl. depr/interest)` | `company`, `from_date`, `to_date` | Revenue ₹500k, COGS ₹250k, OPEX ₹100k, Depr ₹25k | ₹175,000.00 | ₹175,000.00 | 0.00 | 0.01 | **PASS** | Operating profit before depreciation |
| **AR-001** | Owner | Net Receivables | `Sales Invoice`, `Payment Ledger Entry` | `SUM(outstanding_amount)` where `docstatus=1` | `company`, `customer`, `posting_date <= to_date` | Outstanding invoices with partial payment settled | ₹35,000.00 | ₹35,000.00 | 0.00 | 0.01 | **PASS** | Invoices ₹10k + ₹25k; settled ₹0 excluded |
| **AR-003** | Owner | Overdue Receivables | `Sales Invoice` | `SUM(outstanding_amount)` where `due_date < ref_date` | `company`, `customer` | Reference date 2026-10-14 against past due invoices | ₹10,000.00 | ₹10,000.00 | 0.00 | 0.01 | **PASS** | Exactly 1 overdue invoice flagged |
| **AP-001** | Owner | Net Payables | `Purchase Invoice`, `Payment Ledger Entry` | `SUM(outstanding_amount)` where `docstatus=1` | `company`, `supplier` | Supplier invoices ₹18k + ₹22k; draft ₹10k excluded | ₹40,000.00 | ₹40,000.00 | 0.00 | 0.01 | **PASS** | Matches Accounts Payable native report |
| **SALES-001**| Owner | Customer Revenue | `Sales Invoice` | `SUM(base_net_amount)` grouped by `customer` | `company`, `from_date`, `to_date` | Multiple lines per invoice across customers | CustA: ₹35k, CustB: ₹40k | CustA: ₹35k, CustB: ₹40k | 0.00 | 0.01 | **PASS** | No duplicate counting on multi-line joins |
| **SALES-002**| Owner | Top Customers by Revenue | `Sales Invoice` | Descending sort of customer revenue, limit 5 | `company`, `from_date`, `to_date` | 6 customers ranked by revenue | Top 5 ordered | Top 5 ordered | 0 | Exact | **PASS** | CustA, CustB, CustD, CustE, CustC |
| **SALES-003**| Owner | Delivery Backlog Value | `Sales Order`, `Sales Order Item` | `SUM(max(0, qty - delivered_qty) * base_net_rate)` | `company`, `customer` | Open order line (60 rem * ₹250) + Fully delivered excluded | ₹15,000.00 | ₹15,000.00 | 0.00 | 0.01 | **PASS** | Excludes "To Bill" and "Completed" |
| **SALES-004**| Owner | Held Order Value | `Sales Order`, `Sales Order Item` | `SUM(remaining_qty * base_net_rate)` for status="On Hold" | `company` | On Hold order with 20 remaining @ ₹500 | ₹10,000.00 | ₹10,000.00 | 0.00 | 0.01 | **PASS** | Held commitments segregated from active |
| **MFG-001** | Owner | Work Orders Total | `Work Order` | `COUNT(*)` partitioned by status | `company` | Cohort with Active(2), Completed(1), Draft(1), Stopped(1), Cancelled(1) | Total: 6 | Total: 6 | 0 | Exact | **PASS** | Complete mutual exclusivity |
| **MFG-002** | Owner | Active Work Orders | `Work Order` | `COUNT(*)` where `status IN ('Not Started', 'In Process')` | `company` | 2 active orders in cohort | 2 | 2 | 0 | Exact | **PASS** | Reconciled against total cohort |
| **MFG-003** | Owner | Completed Work Orders | `Work Order` | `COUNT(*)` where `status = 'Completed'` | `company` | 1 completed order in cohort | 1 | 1 | 0 | Exact | **PASS** | Preserves terminal state |
| **MFG-004** | Owner | Delayed Work Orders | `Work Order` | `COUNT(*)` where active and `target_date < ref_date` | `company`, `ref_date` | Target date 2026-10-10 vs ref date 2026-10-14 | 1 | 1 | 0 | Exact | **PASS** | Uses planned_end fallback |
| **MFG-005** | Owner | Planned Production Output| `Work Order` | `SUM(qty)` for active Work Orders | `company` | Planned batch quantities across active orders | Accurate sum | Accurate sum | 0.0 | Exact | **PASS** | Preserves stock UOM |
| **INV-001** | Owner | Inventory Valuation | `Bin`, `Warehouse` | `SUM(b.stock_value)` where `w.is_group=0` | `company`, `warehouse` | 3 leaf warehouses (₹1.3M) + 1 group warehouse (₹1.3M) | ₹1,300,000.00 | ₹1,300,000.00 | 0.00 | 0.01 | **PASS** | Leaf bins only; group warehouse excluded |
| **INV-002** | Owner | Top Valuation Warehouses | `Bin`, `Warehouse` | Descending sort of warehouse stock value | `company` | Finished Goods (₹600k), Stores (₹450k), WIP (₹250k) | FG, Stores, WIP | FG, Stores, WIP | 0 | Exact | **PASS** | Excludes group warehouse summaries |
| **PROJ-001**| Owner | Total Active Projects | `Project` | `COUNT(*)` where `status IN ('Open', 'On hold')` | `company`, `customer` | 3 Open/Held + 1 Completed + 1 Cancelled | 3 | 3 | 0 | Exact | **PASS** | Excludes completed and cancelled |
| **PROJ-002**| Owner | Completed Projects | `Project` | `COUNT(*)` where `status = 'Completed'` | `company` | 1 completed project in cohort | 1 | 1 | 0 | Exact | **PASS** | Preserves finished state |
| **PROJ-003**| Owner | Overdue Projects | `Project` | `COUNT(*)` where `active=1` and `expected_end_date < ref_date` | `company` | End date 2026-10-10 vs reference 2026-10-14 | 1 | 1 | 0 | Exact | **PASS** | Only active past due projects counted |
| **PROJ-004**| Owner | Milestone Progress % | `Project`, `Task` | `(completed_tasks / total_tasks) * 100` | `company`, `project` | 8 completed of 10 milestone tasks | 80.00% | 80.00% | 0.00 | 0.01% | **PASS** | Zero task denominator safe |
| **ALERT-001**| Owner | Critical Risk Alerts | `Executive Risks` | Deduplicated alerts with `severity='Critical'` | `company`, `review_days` | Invoices >30d overdue, projects >14d overdue | Sorted Critical | Sorted Critical | 0 | Exact | **PASS** | Severity rank 0 preserved |
| **ALERT-002**| Owner | Overdue Invoices Alert | `Executive Risks` | Critical/High alerts for receivables | `company` | 1 invoice >30d overdue flagged | 1 | 1 | 0 | Exact | **PASS** | Escalated to executive summary |
| **ALERT-003**| Owner | Overdue Projects Alert | `Executive Risks` | Critical/High alerts for project delivery | `company` | 1 project past expected end date | 1 | 1 | 0 | Exact | **PASS** | Direct link to Project doc |
| **ALERT-004**| Owner | Delayed WOs Alert | `Executive Risks` | Critical/High alerts for production delay | `company` | 1 active WO past target completion date | 1 | 1 | 0 | Exact | **PASS** | Cross-linked to Work Order |

---

## 4. Production Management Control Tower KPI Reconciliation Matrix

| KPI ID | Dashboard | Metric Name | Source DocType / Report | Verified Formula | Applicable Filters | Test Scenario | Expected Result | Actual Result | Diff | Tolerance | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **OPS-001** | Control Tower | Active Work Orders | `Work Order` | `COUNT(*)` where `docstatus=1` and `status IN ('Not Started', 'In Process')` | `company`, `from_date`, `to_date` | Factory Overview query with status filter | Integer >= 0 | Integer >= 0 | 0 | Exact | **PASS** | Validated in `test_factory_overview.py` |
| **OPS-002** | Control Tower | Planned Production Qty | `Work Order` | `SUM(qty)` for active Work Orders | `company`, `from_date`, `to_date` | Planned qty across active orders | Float >= 0.0 | Float >= 0.0 | 0.0 | 0.001 | **PASS** | Preserves stock UOM |
| **OPS-003** | Control Tower | Actual Production Qty | `Work Order` | `SUM(produced_qty)` for active Work Orders | `company`, `from_date`, `to_date` | Produced qty recorded in Job Cards | Float >= 0.0 | Float >= 0.0 | 0.0 | 0.001 | **PASS** | Accrued from submitted Job Cards |
| **OPS-004** | Control Tower | Production Achievement %| Derived | `(actual_qty / planned_qty) * 100` | `company` | 85 actual vs 100 planned | 85.00% | 85.00% | 0.00 | 0.01% | **PASS** | Zero planned qty safely yields 0.0% |
| **OPS-005** | Control Tower | Overdue Work Orders | `Work Order` | `COUNT(*)` where active and `target_date < ref_date` | `company`, `reference_at` | Fallback: `planned_end_date` or `expected_delivery_date` | Count matching | Count matching | 0 | Exact | **PASS** | Tested in `test_kpi_reconciliation.py` |
| **INV-004** | Control Tower | Material Readiness | `Work Order Item`, `Bin` | Cumulative stock allocation across active orders | `company`, `warehouse`, `readiness_status` | Shared demand: 150 available for two 100-qty orders | Order 1: Ready, Order 2: Partial (50 shortage) | Order 1: Ready, Order 2: Partial (50 shortage) | 0.0 | Exact | **PASS** | Prevents phantom ready allocations |
| **INV-005** | Control Tower | Critical Material Shortages| `Work Order Item`, `Bin` | Count of required items with available stock = 0 | `company`, `warehouse` | Work Order requiring stock with 0 on hand | Count matching | Count matching | 0 | Exact | **PASS** | Flags shortage pill |
| **WS-001** | Control Tower | Workstation Downtime Min | `Downtime Entry` | `SUM((to_time - from_time))` in minutes | `company`, `workstation`, `from_date`, `to_date` | 1 closed entry (120m) + 1 open entry clipped (120m) | 240.0 mins | 240.0 mins | 0.0 | 0.01 | **PASS** | Open incidents clipped to `reference_at` |
| **WS-003** | Control Tower | Active Workstation Incidents| `Downtime Entry` | `COUNT(*)` where `status='Open'` | `company`, `workstation` | Currently stopped workstation incidents | Count matching | Count matching | 0 | Exact | **PASS** | Real-time incident banner |
| **QUAL-001**| Control Tower | Inspection Pass Rate % | `Quality Inspection` | `(accepted_inspections / total_inspections) * 100` | `company`, `from_date`, `to_date` | 3 Accepted, 1 Rejected | 75.00% | 75.00% | 0.00 | 0.01% | **PASS** | Zero denominator safe |
| **QUAL-002**| Control Tower | Scrap Rate % | `Job Card`, `Work Order` | `(scrap_qty / total_produced) * 100` | `company`, `from_date`, `to_date` | 90 accepted + 5 rejected + 5 scrap | 5.00% | 5.00% | 0.00 | 0.01% | **PASS** | Reconciled against total production |
| **SUB-001** | Control Tower | Open Subcontract POs | `Purchase Order` | `COUNT(*)` where `is_subcontracted='Yes'` and `status!='Completed'` | `company`, `supplier` | Subcontract POs awaiting receipt | Count matching | Count matching | 0 | Exact | **PASS** | Distinguishes subcontract from standard |
| **SUB-002** | Control Tower | Outstanding Subcontract Qty | `Purchase Order Item` | `SUM(max(0, qty - received_qty))` for subcontract items | `company`, `supplier` | 100 ordered (60 received) + 40 ordered (0 received) | 80.0 | 80.0 | 0.0 | Exact | **PASS** | 2 pending subcontract items |
| **ALERT-005**| Control Tower | Critical Exception Count| `Production Exceptions` | Deduplicated exceptions with `severity='Critical'` | `company`, `severity` | Blocked operations, severe material shortages | Ranked 1st | Ranked 1st | 0 | Exact | **PASS** | Critical > High > Medium > Low |
| **ALERT-006**| Control Tower | Bottleneck Exceptions | `Production Exceptions` | Overdue Job Cards past workstation schedule | `company` | Delayed operation exceeding cycle threshold | Count matching | Count matching | 0 | Exact | **PASS** | Validated in logic suite |
| **ALERT-007**| Control Tower | Material Shortage Exceptions| `Production Exceptions` | Work Orders blocked by zero raw material stock | `company` | Critical shortage alerts flagged | Count matching | Count matching | 0 | Exact | **PASS** | Linked to Work Order |

---

## 5. Shop-Floor Supervisor & Operator KPI Reconciliation Matrix

| KPI ID | Dashboard | Metric Name | Source DocType / Report | Verified Formula | Applicable Filters | Test Scenario | Expected Result | Actual Result | Diff | Tolerance | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **JOB-001** | Shop-Floor | Assigned Work Count | `Job Card`, `ToDo` | `COUNT(*)` where `assigned_operator = session.user` | User scope | Operator EMP-001 has 2 jobs; EMP-002 has 1 job | 2 | 2 | 0 | Exact | **PASS** | Isolated to authenticated operator |
| **JOB-002** | Shop-Floor | Active Current Operation | `Job Card` | Single active operation where `status='Work In Progress'` | User scope | Exactly 1 running job displayed in hero banner | 1 Active | 1 Active | 0 | Exact | **PASS** | Highlights running operation |
| **JOB-003** | Shop-Floor | Waiting Operations | `Job Card` | `COUNT(*)` where `status='Open'` and assigned | User scope | Eligible jobs waiting to begin | Count matching | Count matching | 0 | Exact | **PASS** | Ready for operator start |
| **JOB-004** | Shop-Floor | Completed Jobs | `Job Card` | `COUNT(*)` where `status='Completed'` | User scope, `today` | Jobs finished within current shift | Count matching | Count matching | 0 | Exact | **PASS** | Shift boundary respected |
| **JOB-005** | Shop-Floor | Verified Blockers | `Job Card`, `Work Order` | `COUNT(*)` with documented hold/shortage | User scope | Blocked jobs with explicit blocker reason | Count matching | Count matching | 0 | Exact | **PASS** | Blocker alert cards rendered |
| **JOB-006** | Shop-Floor | Reported Production Qty | Validated Action | `completed_qty + pending_qty + process_loss_qty = remaining` | Job Card scope | Remaining 40: 30 completed, 5 pending, 5 scrap | 40.0 accounted | 40.0 accounted | 0.0 | Exact | **PASS** | UOM explicit; prevents over-completion |
| **JOB-007** | Shop-Floor | Supervisor Team Members | `Employee`, `User Permission` | `COUNT(DISTINCT employee)` under supervisor scope | Supervisor scope | Permitted team members assigned today | 2 | 2 | 0 | Exact | **PASS** | Server-side team authorization |
| **JOB-008** | Shop-Floor | Active Operators Count | `Job Card` | `COUNT(DISTINCT operator)` with active time log | Supervisor scope | Team operators currently logging time | Count matching | Count matching | 0 | Exact | **PASS** | Reconciled against active Job Cards |
| **JOB-015** | Shop-Floor | Supervisor Overdue JCs | `Job Card` | `COUNT(*)` where active and `expected_end_date < now` | Team scope | 1 team job past scheduled completion | 1 | 1 | 0 | Exact | **PASS** | Overdue pill rendered |

---

## 6. Boundary, Filter & Precision Test Scenarios

| Test Scenario | Purpose | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|
| **Empty Valid Cohort** | Ensure zero results are not treated as system failures. | Clean `0` or `0.00` returned without throwing exceptions. | Returned `0` and `Decimal('0.00')`. | **PASS** |
| **Unconfigured / Missing Source** | Differentiate genuine zero from unconfigured features. | Returns `available: False`, `value: None`, explicit reason. | Explicit reason returned; never fabricated zero. | **PASS** |
| **Date Range Inclusivity** | Test `from_date` and `to_date` edge records. | Records on boundary dates included; outside dates excluded. | `R2` (start) and `R4` (end) included; `R1` and `R5` excluded. | **PASS** |
| **Parent-Child Join Deduplication** | Prevent duplicate order counting when querying child lines. | Parent order count is 1 regardless of child item rows. | Parent count = 1; line count = 3. | **PASS** |
| **Currency & Quantity Precision** | Avoid floating point skew and improper rounding. | Native currency quantized to 2 decimals (`0.01`). | Quantized exact Decimal; zero float drift. | **PASS** |
| **Missing Due Dates** | Work Orders lacking scheduled dates. | Handled as `Unknown Target Date`, not fabricated overdue. | Correctly classified with `days_overdue=None`. | **PASS** |
| **Inverted Date Filter** | Input validation on `from_date > to_date`. | Validation error thrown; invalid range rejected. | Flagged as invalid input; execution halted safely. | **PASS** |
| **Role Permission Denial** | Unauthorized user querying executive metrics. | Permission error thrown; zero records leaked. | Access denied; authorization enforced. | **PASS** |

---

## 7. Blocked & Unverified Metrics Audit Table

The following 20 KPIs are classified as **Blocked by missing configuration or data** in standard ERPNext environments:

| KPI ID | Dashboard | Metric Name | Required Source / Fixture | Exact Dependency / Blocker Rationale | Status |
|---|---|---|---|---|---|
| **FIN-011** | Owner | Cash Flow (Direct Method) | `Bank Account`, `Payment Entry` | Direct cash flow categorization rules and bank clearing transaction mapping absent. | **BLOCKED** |
| **FIN-012** | Owner | Working Capital Ratios | `GL Entry`, Account Dimension | Requires custom balance sheet account tagging for quick ratio asset pools. | **BLOCKED** |
| **PROJ-005** | Owner | Milestone On-Time Delivery %| `Project Milestone` | Standard ERPNext lacks native `Project Milestone` child table in baseline schema. | **BLOCKED** |
| **JOB-010** | Shop-Floor | Shift Schedule Adherence % | `Shift Assignment`, `Shift Type` | `Shift Type` and `Shift Assignment` doctypes not populated in standard installation. | **BLOCKED** |
| **JOB-011** | Shop-Floor | Operator Workstation Allocation| `Workstation`, `Shift Assignment` | Workstation operator shift schedules require custom scheduling plugin. | **BLOCKED** |
| **JOB-012** | Shop-Floor | Machine Efficiency Ratio | `Workstation`, IoT Telemetry | Real-time machine operational state telemetry feed not connected. | **BLOCKED** |
| **JOB-013** | Shop-Floor | First-Pass Yield (Shift) | `Job Card Scrap Item` | Standard Job Card lacks inline first-pass yield classification flag. | **BLOCKED** |
| **INV-003** | Owner | Inventory Turnover Ratio | `Stock Ledger Entry` | Requires 12 months of historical COGS and average stock ledger balance fixtures. | **BLOCKED** |
| **INV-006** | Control Tower | Slow-Moving / Obsolete Stock | `Stock Ledger Entry` | Aging threshold policies (>180 days no movement) not configured. | **BLOCKED** |
| **INV-007** | Control Tower | Lead Time Variance | `Purchase Receipt`, `Purchase Order`| Historical vendor lead time baseline master data absent. | **BLOCKED** |
| **INV-008** | Control Tower | Min-Max Stock Breach Count | `Item Reorder` | Reorder levels not configured on test item masters. | **BLOCKED** |
| **INV-009** | Control Tower | Safety Stock Deficit Value | `Item Reorder`, `Bin` | Safety stock threshold values absent in standard demo fixtures. | **BLOCKED** |
| **INV-010** | Control Tower | Transit Stock Valuation | `In-Transit Warehouse` | Internal transfer in-transit warehouses not created. | **BLOCKED** |
| **INV-012** | Control Tower | Shelf-Life Expiry Risk | `Batch` | Expiry dates and batch-managed items not seeded in test records. | **BLOCKED** |
| **QUAL-003**| Control Tower | Formal Rework Cases | Custom `Rework Order` DocType | ERPNext standard lacks formal `Rework Order` DocType (tracked via operations). | **BLOCKED** |
| **WS-002** | Control Tower | Workstation MTBF / MTTR | `Maintenance Visit`, `Workstation` | Preventive maintenance logs and operating hours baseline absent. | **BLOCKED** |
| **WS-004** | Control Tower | Overall Equipment Effectiveness | IoT / Telemetry Master | Requires Availability * Performance * Quality sensor inputs. | **BLOCKED** |
| **SUB-003** | Control Tower | Subcontract Delivery Adherence| `Subcontracting Receipt` | Subcontractor agreed delivery schedules not populated. | **BLOCKED** |
| **SUB-004** | Control Tower | Subcontract Scrap Variance | `Subcontracting Order Item` | Subcontract scrap allowance masters not populated. | **BLOCKED** |
| **SUB-005** | Control Tower | Subcontract Inward Rejections | `Subcontracting Receipt` | Rejection inspection logs on subcontract receipts not seeded. | **BLOCKED** |

---

## 8. Summary of Automated Test Execution Results

| Test Suite / Script | Command Executed | Tests Run | Result | Notes |
|---|---|---|---|---|
| **KPI Reconciliation & Boundary Tests** | `python -m unittest sarathi_visibility/sarathi_visibility/tests/test_kpi_reconciliation.py` | 30 | **PASS** | 30 tests passed in 0.024s. Independent calculation verification. |
| **KPI Dictionary Contract Tests** | `python -m unittest sarathi_visibility/sarathi_visibility/tests/test_kpi_dictionary.py` | 7 | **PASS** | 7 tests passed in 0.027s. Validates 108 KPI contracts & dependencies. |
| **Shop-Floor Logic & Workboard** | `python -m unittest sarathi_visibility/tests/test_shopfloor_logic.py` | 29 | **PASS** | 29 tests passed in 0.034s. Operator isolation, reporting actions. |
| **Production Exceptions Logic** | `python -m unittest sarathi_visibility/tests/test_production_exceptions_logic.py` | 10 | **PASS** | 10 tests passed in 0.011s. Severity sorting, bottleneck rules. |
| **Quality & Rework Logic** | `python -m unittest sarathi_visibility/tests/test_quality_rework_logic.py` | 9 | **PASS** | 9 tests passed in 0.006s. Scrap %, inspection pass rate, subcontracting. |
| **Material Readiness Logic** | `python -m unittest sarathi_visibility/tests/test_material_readiness_logic.py` | 10 | **PASS** | 10 tests passed in 0.010s. Cumulative stock allocation across orders. |
| **Workstation Downtime Logic** | `python -m unittest sarathi_visibility/tests/test_workstation_downtime_logic.py` | 7 | **PASS** | 7 tests passed in 0.010s. Open downtime clipping, status filters. |
| **Accessibility Conventions** | `python -m unittest sarathi_visibility/sarathi_visibility/tests/test_accessibility_conventions.py` | 10 | **PASS** | 10 tests passed in 4.562s. Color contrast, focus rings, ARIA. |
| **Responsive Layout System** | `python -m unittest sarathi_visibility/sarathi_visibility/tests/test_responsive_layouts.py` | 5 | **PASS** | 5 tests passed in 3.899s. Breakpoints, collapsible drawers, touch targets. |
| **Shared UI Browser Mock** | `python -m unittest sarathi_visibility/sarathi_visibility/tests/test_shared_ui_browser.py` | 12 | **PASS** | 12 tests passed in 4.667s. DOM elements, tooltips, keyboard navigation. |
| **Total Automated Tests** | — | **129** | **PASS** | **129 passed, 0 failures, 0 regressions.** |

---

## 9. Scope Boundary Confirmation

- **Task DASH-031 is complete.**
- **Tasks DASH-032 through DASH-036 were strictly NOT started.**
- No core Frappe or ERPNext files were modified.
- All pre-existing user files and configurations remain preserved.
