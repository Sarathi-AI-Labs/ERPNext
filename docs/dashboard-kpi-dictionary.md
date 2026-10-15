# DASH-004 — Dashboard KPI dictionary and metric formulas

Status: ready for definition review, **not dashboard or financial release approval**. Verified 13 October 2026 on branch feature/Gaurav_2, site frontend, Frappe **16.31.0**, ERPNext **16.33.0**. This task adds specifications and focused validation artifacts only. No dashboard API, card, chart, layout, native accounting rule, workflow, role assignment or core source was changed.

The [structured dictionary](dashboard-kpi-dictionary.json) is the machine-readable definition source. [Validation evidence](dashboard-kpi-validation.json) records actual source/report comparisons and schema checks. This document expands every definition, including its purpose, formula, source fields, eligibility, date/filter behavior, permissions, freshness and readiness status.

Read together with [DASH-001 foundation](dashboard-foundation.md), [DASH-002 audit](dashboard-audit.md), and [DASH-003 permissions](dashboard-permission-matrix.md). Earlier audits are historical; the installed metadata and comparisons here are new DASH-004 evidence.

## Shared contracts and accounting decisions

- **Installation boundary:** one client company owns its ERPNext site/database/VPS; Customers are business parties, not separate tenants. Financial totals require Company. Cross-company consolidation/currency translation needs its own approved basis.
- **Verification has two axes:** source comparisons can be verified while dashboard implementation remains proposed. Proposed=align/implement later; blocked=missing trustworthy input/mapping/policy; not configured=required source/configuration/operational records absent. No existing card is certified merely because a source report reconciles.
- **Proposed headline sales basis:** FIN-001 is tax-exclusive net invoiced sales using submitted signed net base amounts. FIN-002 is P&L total income and is the denominator for net profit margin. Journals, adjustments and account classification can make them differ. They happen to match in this dataset; that is not universal equivalence. Orders, collections, gross invoice totals and accounting income are different measures. Business approval of headline label/basis remains outstanding.
- **Profit:** native P&L income minus expense, preserving opening/closing, finance-book, fiscal-year and dimension rules. No invoice-minus-purchase fallback, fabricated COGS share, or silent sign correction. Gross Profit is a distinct stock-cost measure.
- **Balances versus flows:** AR/AP/stock valuation are as-of balances; invoice revenue and manufacture output are posting-period flows; WO.produced_qty and operation counters are current cumulative values. A WO date cohort does not turn cumulative output into period flow.
- **Dates:** site timezone Asia/Calcutta. Inclusive local calendar dates should become a datetime window from start-of-first-day up to, but excluding, start-of-day-after-to-date. Date deadlines compare to local today; Datetime deadlines compare to server now. Include generated_at/source_as_of. Missing schedule stays Unknown, never hidden creation-date fallback.
- **Units and ratios:** group by actual item and stock UOM plus relevant company/warehouse/operation. Different items both in Nos still cannot silently become one production target. Recorded conversion factors must be valid. Good output, process loss, quality rejection, operation disposition and FG stock are distinct. Compute ratios from compatible aggregated components, not mean percentages. Denominator0=>null/N/A; meaningful negatives and overproduction/overbudget remain visible, with warnings.
- **Permissions:** apply DASH-003 capabilities AND native record/field/Company/assignment rights before aggregating, ranking, charting or drilling down. Finance separate from production. Native Desk rights remain an installation configuration responsibility. Embedded reports with unverified complex record scopes remain blocked.
- **Filters:** validate links, dates, status enums and bounded lists server-side. Unsupported Customer/Project/Warehouse/shift combinations must be rejected or explicitly unavailable per KPI, never silently ignored while the UI claims a filtered total. Shared stock/unallocated expense is not exclusively Project/customer-owned.
- **Availability:** a complete readable empty cohort yields measured0. Absent configuration/schema, failed query, incomplete scope or missing denominator yields null plus reason. Never fabricate zero profit/downtime, a budget, or healthy status from unavailable inputs.
- **Joins/performance:** aggregate each parent/child grain once. Count distinct IDs; sum header totals before line fan-out or switch to eligible line amounts. Details paginate at database (proposed25,max100); exports retain identical permissions/filters. Top-N/chart limits never cap the total KPI numerator. Batch related aggregates, avoid per-card/per-row queries, and cache only site+user/permission revision+normalized filters+currency/UOM/date basis.
- **Freshness:** existing active-visible owner/production polling is15s plus after-commit invalidation; shop-floor refresh is not built. This is ERP record refresh, not machine telemetry. Show ledger repost/reconciliation/stale/error states; a source may be older than dashboard generation time.

## Installed source and configuration evidence

All declared source fields were checked against installed metadata, not merely repository strings. The evidence artifact contains record counts, field types/options, native status enums and installed source SHA-256 fingerprints.

Site-wide observation: 2 submitted Sales Invoices, 0 submitted returns, 8 submitted Purchase Invoices, 7 Work Orders, 15 Job Cards, 0 WO Operation rows, 0 Job Card Time Logs, 0 Stock Reservation Entries, 0 Downtime Entries, 0 Subcontracting Orders/Receipts, 0 active workflows/actions, 0 ToDo assignments, 0 Employees and 0 Item Reorder rows. Shift Type is absent. Quality Inspection exists with4 records; submission/outcome rules still apply. Budget exists with1 record but was not reconciled. Missing records do not prove a feature can never be configured.

Installed source differs from ERPNEXT_MAIN checkout. Installed P&L, financial statements, Sales Register, receivables, WO Summary, Project, Job Card, stock valuation/reservation and Workflow Action were read directly. Important differences:

1. Installed Project Task Progress averages stored Task.progress; Task Weight uses stored progress and native safe division. Checkout has newer/different completed/cancelled handling. Consume native stored percent_complete/method and revalidate upgrades.
2. Installed Budget stores account/budget_amount on header, from/to fiscal year and budget start/end dates, with Budget Distribution(start_date,end_date,amount,percent). Budget.fiscal_year is absent. A legacy Budget Account DocType existing does not make it the active child relationship.
3. Physical reservations use outstanding SRE reserved_qty-delivered_qty-transferred_qty-consumed_qty. Bin demand counters are not extra physical reservations. Native reserve-availability helper locks rows; do not blindly invoke a command helper in dashboard reads.
4. WO transfer/return counters are separate; installed consumed_qty adds returned_qty. Return-aware demand needs manufacturing-mode and allocation fixtures before certification.
5. Workflow Actions are role/transition-based. Their user field and email notification recipients are not automatically approval assignees.

### Shared label mapping

| Display | Shared definition |
| --- | --- |
| Active / completed Projects | PROJ-007 / PROJ-008 |
| Net sales / customer ranking / trend | FIN-001 / SALES-001–003; distinguish FIN-002 P&L income |
| Net profit/margin; gross profit/margin | FIN-004–007, distinct denominators |
| Invoice-only positive outstanding / net exposure | Existing invoice snapshot narrower than AR-002; full signed balance AR-001 |
| Commercial gross order book / delivery backlog | Full header order total is not SALES-004/005 |
| Owner output summary and manager detail | MFG-001–005, same compatible grain/cohort or explicitly posting-flow basis |
| Active / overdue WO | MFG-006 / MFG-008 |
| Job target/output/remaining/progress | JOB-001–004, not WO target or sum of sequential stages |
| Planned / executable Job Cards | JOB-017 / JOB-016 |
| In progress / not started production cards | Distinct Project counts partitioned by PROJ-006 state; not operation counts; Unknown separate |
| Hold / blocked / waiting | JOB-015 / JOB-012 / JOB-011, not interchangeable |
| Stock value / stock row count / free / projected | INV-001 / CAT-003 / INV-004 / INV-005 |
| Potential shortage / confirmed WO blocker | INV-008 / INV-009 |
| Failed inspection / rejected units / rework | QUAL-001–003 / JOB-007 / OPS-004, distinct grains |
| Recorded state / downtime / utilization / OEE | WS-001–004, distinguish absent telemetry |
| Subcontract active/delay/supplier material | SUB-001–005 |
| Master/catalogue counts | CAT-001–011, navigation counts not throughput |

### Discrepancies: specify corrections, do not implement them in DASH-004

| Existing code evidence | Required later correction |
| --- | --- |
| owner_dashboard financial chart uses Sales Invoice.grand_total; order book sums header gross totals | Use signed net base sales and explicit delivery backlog, not tax-inclusive/transaction-currency totals |
| Owner Income/Expense GL queries restrict voucher types | Consume native P&L rules across all eligible voucher types |
| accounting zero-GL SI/PI fallback; COGS70%/operating expense30% | Missing/zero GL cannot authorize invoice-minus-purchase profit or fabricated allocations |
| accounting expects Budget.fiscal_year/Budget Account; expense×1.35 budget and expense×0.1 commitment | Use installed header/distribution model; FIN-011 blocked pending encumbrance policy |
| Current invoice outstanding fields/owner aging | Do not reconstruct historical allocations, advances or JEs from current invoice-only snapshots |
| Owner production chart filters WO.creation, sums unlike items, casts quantity to int | Separate schedule cohort from period flow, preserve item/UOM and decimal quantities |
| dashboard_data material need required-max(consumed,transferred), Bin.actual_qty | Returns/reservations/WIP/allocation unresolved; potential risk only until INV-007–009 validated |
| production.analyze empty-operation completion / progress cap | Missing expected operation rows=>Unknown, not vacuous complete; good output differs from disposition |
| Stock/name-based raw/WIP/FG buckets and default50/30/20; hardcoded pcs | Native valuation, explicit classification, Unclassified bucket and real UOM; no invented percentages |
| Non-cancelled draft QI rows in current source views | Submitted rejection metric excludes drafts; sample_size is not rejected output |
| Subcontract header deadlines / remaining quantity×order rate value | Use actual child due dates and native warehouse valuation; label rate estimate separately |
| Legacy control_tower/data and pipeline synthetic/default stage/plan paths | Demo quantities/weights are not approved facts; use real linked records or unavailable states |

Report equality is not ledger correctness or financial release sign-off. Audit company expense is negative and profit exceeds income; draft/open Job Cards lack operation/time data. These require business/data review, not sign changes or invented execution. No business records were corrected here.

## Per-KPI definitions

There are **108** definitions. Status counts: proposed=76, blocked=16, not configured=16. Source verification is recorded separately below.

| KPI | Name | Dashboard scope | Readiness |
| --- | --- | --- | --- |
| FIN-001 | Net invoiced sales (tax exclusive) | Owner | proposed |
| FIN-002 | P&L total income | Owner | proposed |
| FIN-003 | P&L total expense | Owner | proposed |
| FIN-004 | Net profit / loss | Owner | proposed |
| FIN-005 | Net profit margin | Owner | proposed |
| FIN-006 | Gross profit | Owner | proposed |
| FIN-007 | Gross profit margin | Owner | proposed |
| FIN-008 | Cash and bank balance as of date | Owner | proposed |
| FIN-009 | Approved budget | Owner | proposed |
| FIN-010 | Budget utilization | Owner | proposed |
| FIN-011 | Open procurement / budget commitment | Owner | blocked |
| FIN-012 | Customer/project net profitability | Owner | blocked |
| AR-001 | Net receivables including credits | Owner | proposed |
| AR-002 | Gross positive customer balances | Owner | proposed |
| AR-003 | Overdue receivables / invoice count | Owner | proposed |
| AR-004 | Receivables aging | Owner | proposed |
| AP-001 | Net supplier payables | Owner | proposed |
| AP-002 | Overdue supplier obligations | Owner | proposed |
| SALES-001 | Net invoiced sales by Customer | Owner | proposed |
| SALES-002 | Top customers by net sales | Owner | proposed |
| SALES-003 | Net sales trend / comparison | Owner | proposed |
| SALES-004 | Open delivery backlog quantity | Owner, Production | proposed |
| SALES-005 | Open delivery backlog value | Owner | proposed |
| SALES-006 | Open customer orders count | Owner, Production | proposed |
| SALES-007 | Allocated customer collections | Owner | proposed |
| PROJ-001 | Recorded Project progress | Owner, Production | proposed |
| PROJ-002 | Overdue projects | Owner, Production | proposed |
| PROJ-003 | Dated projects not overdue | Owner | proposed |
| PROJ-004 | Projects due soon | Owner, Production | proposed |
| PROJ-005 | Project delivery risk | Owner | blocked |
| PROJ-006 | Recorded manufacturing state by Project | Owner, Production | proposed |
| PROJ-007 | Active Projects count | Owner, Production | proposed |
| PROJ-008 | Completed Projects count | Owner, Production | proposed |
| MFG-001 | Scheduled-start planned production | Owner, Production | proposed |
| MFG-002 | Produced output to date for cohort | Owner, Production | proposed |
| MFG-003 | Production achievement (cohort) | Owner, Production | proposed |
| MFG-004 | Production variance (cohort) | Owner, Production | proposed |
| MFG-005 | Finished output posted in period | Owner, Production | proposed |
| MFG-006 | Active Work Orders | Owner, Production | proposed |
| MFG-007 | Completed Work Orders | Owner, Production | proposed |
| MFG-008 | Overdue Work Orders | Owner, Production | proposed |
| MFG-009 | Work Orders due soon | Owner, Production | proposed |
| MFG-010 | Remaining good-output target | Owner, Production | proposed |
| MFG-011 | Remaining processing quantity | Owner, Production | proposed |
| MFG-012 | Work Order completion rate | Owner, Production | proposed |
| OPS-001 | Completed recorded operations | Production | not configured |
| OPS-002 | Operation progress | Production | not configured |
| OPS-003 | Late-operation / potential bottleneck list | Production | proposed |
| OPS-004 | Corrective Job Cards / rework count | Production | proposed |
| JOB-001 | Job planned quantity | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-002 | Job recorded good output | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-003 | Job remaining processing quantity | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-004 | Job good-output progress | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-005 | Job process loss | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-006 | Recorded operation time | Production, Shop-floor supervisor, Shop-floor operator | not configured |
| JOB-007 | Job rejected quantity | Production, Shop-floor supervisor, Shop-floor operator | blocked |
| JOB-008 | Assigned operations / jobs | Shop-floor supervisor, Shop-floor operator | not configured |
| JOB-009 | Current Job Card status | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-010 | Recorded running jobs | Production, Shop-floor supervisor, Shop-floor operator | not configured |
| JOB-011 | Waiting jobs | Production, Shop-floor supervisor, Shop-floor operator | blocked |
| JOB-012 | Blocked jobs / operations | Production, Shop-floor supervisor, Shop-floor operator | blocked |
| JOB-013 | Reported production issues | Production, Shop-floor supervisor, Shop-floor operator | blocked |
| JOB-014 | Delayed Job Cards | Production | proposed |
| JOB-015 | On-hold Job Cards | Production, Shop-floor supervisor, Shop-floor operator | proposed |
| JOB-016 | Open executable Job Cards | Production | proposed |
| JOB-017 | Planned Job Cards on draft WOs | Production | proposed |
| INV-001 | Stock valuation as of date | Owner | proposed |
| INV-002 | Actual stock quantity | Owner, Production | proposed |
| INV-003 | Outstanding physical reservations | Production | not configured |
| INV-004 | Unreserved available stock | Production | blocked |
| INV-005 | Projected stock quantity | Owner, Production | proposed |
| INV-006 | Low-stock risk | Owner, Production | not configured |
| INV-007 | Outstanding material requirement | Production | blocked |
| INV-008 | Potential material shortage quantity | Owner, Production | blocked |
| INV-009 | Material-ready / affected Work Orders | Production | blocked |
| INV-010 | Excess inventory | Owner | blocked |
| INV-011 | Stock age / aging inventory | Owner | proposed |
| INV-012 | Raw/WIP/finished inventory value mix | Owner | blocked |
| QUAL-001 | Rejected inspections count | Owner, Production | proposed |
| QUAL-002 | Inspection failure rate | Owner, Production | proposed |
| QUAL-003 | Supplier rejected receipt quantity | Production | not configured |
| WS-001 | Recorded workstation state | Production | proposed |
| WS-002 | Recorded downtime minutes | Production | not configured |
| WS-003 | Measured utilization / availability | Production | blocked |
| WS-004 | OEE | Production | not configured |
| SUB-001 | Active subcontract orders | Production | not configured |
| SUB-002 | Overdue subcontract lines / orders | Production | not configured |
| SUB-003 | Subcontract quantity still to receive | Production | not configured |
| SUB-004 | Material at supplier quantity | Production | not configured |
| SUB-005 | Supplier-held material value | Owner | not configured |
| ALERT-001 | Overdue customer invoice | Owner, Production | proposed |
| ALERT-002 | Delayed Work Order | Owner, Production | proposed |
| ALERT-003 | Confirmed material blocker | Owner, Production | blocked |
| ALERT-004 | Project delivery risk | Owner, Production | blocked |
| ALERT-005 | Pending approval for current user | Owner | not configured |
| ALERT-006 | Rejected inspection | Owner, Production | proposed |
| ALERT-007 | Delayed subcontract delivery | Owner, Production | proposed |
| CAT-001 | Projects catalogue count | Owner, Production | proposed |
| CAT-002 | Items catalogue count | Owner, Production | proposed |
| CAT-003 | Warehouse stock rows catalogue count | Owner, Production | proposed |
| CAT-004 | Warehouses catalogue count | Owner, Production | proposed |
| CAT-005 | Workstations catalogue count | Owner, Production | proposed |
| CAT-006 | Operation masters catalogue count | Owner, Production | proposed |
| CAT-007 | Workstation types catalogue count | Owner, Production | proposed |
| CAT-008 | Routings catalogue count | Owner, Production | proposed |
| CAT-009 | Active BOMs catalogue count | Owner, Production | proposed |
| CAT-010 | Customers catalogue count | Owner, Production | proposed |
| CAT-011 | Suppliers catalogue count | Owner, Production | proposed |

### FIN-001 — Net invoiced sales (tax exclusive)

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-001 |
| Name | Net invoiced sales (tax exclusive) |
| Dashboard(s) | Owner |
| Section | Finance and sales |
| Business purpose | Measure submitted sales separately from commitments/cash. |
| Plain-language definition | Signed invoice net value, proposed headline sales measure, distinct from all P&L Income. |
| Exact formula/calculation | SUM(eligible invoice.base_net_total) once per invoice; Project/line filter instead SUM(line.base_net_amount). Negative return amounts included once, never double-subtracted. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, docstatus, company, posting_date, customer, project, base_net_total, base_grand_total, is_return, is_internal_customer, represents_company, currency, conversion_rate; Sales Invoice Item: parent, base_net_amount, project, income_account |
| Inclusion/exclusion rules | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Document/status requirements | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Date and period behavior | Inclusive Sales Invoice.posting_date period, never creation/modified. |
| Filters and unsupported dimensions | applicable: Company required; Customer=Sales Invoice.customer; Project via verified header or Sales Invoice Item.project with consistent parent fallback and line base_net_amount (never duplicate header totals). Warehouse unsupported without verified line allocation.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Company base_* currency; sum stored precision then round once to native currency precision. No fixed INR or mixing grand_total currencies. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive capability AND native Sales Invoice/child/Customer/Project and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Register / authorized Sales Invoice form with identical scope. |
| Validation source/scenario | invoice_net_vs_sales_register; V01-V04 returns/draft/cancel/tax/project scenarios. |
| Limitations | Accounting basis/label requires approval. Two local invoices have no tax difference, submitted returns or foreign currency; equality to grand totals does not validate those edge cases. |
| Implementation status | proposed |

### FIN-002 — P&L total income

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-002 |
| Name | P&L total income |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Supply accounting revenue and net-margin denominator. |
| Plain-language definition | Native eligible Income account net credits. |
| Exact formula/calculation | Native P&L income summary; equivalent SUM(Income GL credit-debit) under identical native filters. No invoice-only voucher restriction. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | pnl_income_vs_gl; V05-V06. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-003 — P&L total expense

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-003 |
| Name | P&L total expense |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Include accrued stock-related expenses/journals, not only purchases. |
| Plain-language definition | Native eligible Expense net debits; negative expense flagged for review. |
| Exact formula/calculation | Native P&L expense summary; equivalent SUM(Expense GL debit-credit), same report filters. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | pnl_expense_vs_gl; V05-V06. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-004 — Net profit / loss

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-004 |
| Name | Net profit / loss |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Measure accounting profitability. |
| Plain-language definition | Native total income less expense. |
| Exact formula/calculation | FIN-002 - FIN-003; consume native net_profit_loss/summary, not parent+child account sums. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | pnl_profit_vs_gl; V05-V06. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-005 — Net profit margin

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-005 |
| Name | Net profit margin |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Compare profit on the same accounting basis. |
| Plain-language definition | Net profit as percent of P&L Income, not invoice sales when they differ. |
| Exact formula/calculation | 100*FIN-004/FIN-002 if FIN-002!=0 else null. Negative revenue flagged; >100% not clipped. |
| Numerator | FIN-004, identical scope/currency. |
| Denominator | FIN-002 P&L Income, identical scope/currency. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | Native components compared; V07 zero/negative denominator arithmetic. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-006 — Gross profit

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-006 |
| Name | Gross profit |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Separate direct product profitability from net profit. |
| Plain-language definition | Native Gross Profit report selling amount less valuation-based buying amount. |
| Exact formula/calculation | Use native Gross Profit gross_profit at approved grouping; sum eligible leaf invoice/item rows once, or authoritative total. Never assign 70% of expense to COGS. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, posting_date, company, docstatus; Sales Invoice Item: parent, item_code, base_net_amount; Stock Ledger Entry: voucher_no, stock_value_difference, actual_qty |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V08 native Gross Profit returns/cost/service scenarios; NOT run. |
| Limitations | Report exists, but grouping/total extraction and Project/customer cost allocation unverified. Missing cost is Unknown. |
| Implementation status | proposed |

### FIN-007 — Gross profit margin

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-007 |
| Name | Gross profit margin |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Use the gross-profit report's own sales denominator. |
| Plain-language definition | Gross profit divided by same report selling amount. |
| Exact formula/calculation | 100*FIN-006/native Gross Profit selling_amount; null for denominator0. |
| Numerator | FIN-006 native report gross profit. |
| Denominator | Native Gross Profit selling_amount for identical eligible leaf rows. |
| ERPNext DocTypes / exact fields | Sales Invoice Item: parent, base_net_amount |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V08 not run. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-008 — Cash and bank balance as of date

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-008 |
| Name | Cash and bank balance as of date |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Show book liquidity rather than cash collections or bank statements. |
| Plain-language definition | Signed balance of authorized leaf Bank/Cash accounts. |
| Exact formula/calculation | SUM(GL debit-credit) through as_of for leaf Account.account_type in Bank,Cash; native Balance Sheet/GL balance/opening rules, not P&L closing exclusions. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | GL posting_date<=as_of, preserving opening balances; from_date cannot truncate them. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V09 General Ledger/Balance Sheet subtree; not run. |
| Limitations | Customer/Project liquidity attribution unsupported. Bank reconciliation/overdraft classification need finance review. |
| Implementation status | proposed |

### FIN-009 — Approved budget

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-009 |
| Name | Approved budget |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Use actual authorized budget, not an expense multiplier. |
| Plain-language definition | Submitted native Budget header amounts for matching Company/account/dimension and date range. |
| Exact formula/calculation | Full budget=SUM(distinct eligible Budget.budget_amount). Period allocation=installed Budget Variance Report over Budget Distribution.start_date/end_date/amount, distributing each row across its covered months. Select one non-overlapping account/dimension budget scope; never expense*1.35. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Budget: name, company, docstatus, from_fiscal_year, to_fiscal_year, budget_start_date, budget_end_date, budget_against, cost_center, project, account, budget_amount; Budget Distribution: parent, start_date, end_date, amount, percent |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Budget.budget_start_date/budget_end_date and from_fiscal_year/to_fiscal_year; native Budget Distribution month allocation. Not the obsolete fiscal_year field. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V10 known approved budget/distribution; not run. |
| Limitations | One native Budget exists, not reconciled here. Installed schema has account/budget_amount on Budget header and Budget Distribution children; no Budget.fiscal_year. Legacy Budget Account is not the active parent relationship. Overlaps need approved non-overlapping scope. Native monthly/fiscal-year report buckets do not authorize arbitrary daily budget prorating; partial-month policy unresolved. |
| Implementation status | proposed |

### FIN-010 — Budget utilization

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-010 |
| Name | Budget utilization |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Identify genuine budget overrun. |
| Plain-language definition | Actual budget-scope expense divided by corresponding allocated budget. |
| Exact formula/calculation | 100*native Budget Variance actual_expense/FIN-009; null if budget<=0, no100% cap. |
| Numerator | Native actual expense on selected budget accounts/dimensions. |
| Denominator | FIN-009 matching period allocation. |
| ERPNext DocTypes / exact fields | Budget: name, company, from_fiscal_year, to_fiscal_year, account, budget_amount, docstatus; Budget Distribution: parent, start_date, end_date, amount; GL Entry: account, posting_date, debit, credit, project, cost_center |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V10 overspend and zero-budget; not run. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### FIN-011 — Open procurement / budget commitment

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-011 |
| Name | Open procurement / budget commitment |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Distinguish commitments from recognized expense. |
| Plain-language definition | Unresolved procurement encumbrance measure. |
| Exact formula/calculation | Unavailable pending policy for undelivered vs uninvoiced POs, receipts/accruals, invoice allocations/returns/currency; never expense*0.1. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Purchase Order: name, company, docstatus, status; Purchase Order Item: parent, base_net_amount, billed_amt, received_qty, qty |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V11 partial PO/receipt/invoice with no GRNI double count; blocked. |
| Limitations | Business encumbrance definition and currency/allocation basis required. |
| Implementation status | blocked |

### FIN-012 — Customer/project net profitability

| Attribute | Definition |
| --- | --- |
| KPI ID | FIN-012 |
| Name | Customer/project net profitability |
| Dashboard(s) | Owner |
| Section | Finance and profitability |
| Business purpose | Avoid assigning unattributed overhead to customers. |
| Plain-language definition | No approved complete customer/project cost-allocation model. |
| Exact formula/calculation | Unavailable until relevant Income/Expense postings and unallocated overhead have an approved model. Native Project costing and Gross Profit remain separately labelled. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | GL Entry: company, posting_date, account, debit, credit, is_cancelled, is_opening, voucher_type, finance_book, project, cost_center; Account: name, root_type, is_group, account_type |
| Inclusion/exclusion rules | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Document/status requirements | Native P&L non-cancelled eligible GL and leaf Account rules; all eligible voucher types, exclude Period Closing Voucher; preserve native opening-entry and Finance Book behavior. |
| Date and period behavior | Native P&L Date Range period_start_date/period_end_date; non-accumulated periods summed once; native fiscal-year behavior preserved. |
| Filters and unsupported dimensions | applicable: Single Company required; native GL Project, Cost Center, Finance Book and accounting dimensions supported when configured. Customer and Warehouse P&L attribution unsupported; reject rather than silently ignore.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native company currency or explicitly selected native presentation currency; native conversion/precision. Never sum both group and leaf account amounts. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance capability plus native GL/Account/report/financial-field read; DASH-003 complex-scope report guard remains active. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Profit and Loss Statement / General Ledger with identical filters. |
| Validation source/scenario | V12 assigned/unassigned costs and mixed invoices; blocked. |
| Limitations | Customer GL party incomplete; no fabricated proportional revenue allocation. |
| Implementation status | blocked |

### AR-001 — Net receivables including credits

| Attribute | Definition |
| --- | --- |
| KPI ID | AR-001 |
| Name | Net receivables including credits |
| Dashboard(s) | Owner |
| Section | Receivables |
| Business purpose | Show net customer exposure. |
| Plain-language definition | Signed native voucher outstanding including eligible credits/advances/JEs. |
| Exact formula/calculation | SUM(native Accounts Receivable outstanding on leaf voucher rows, group_by_party=0,in_party_currency=0). No total rows added again. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Payment Ledger Entry: company, posting_date, party_type, party, account, account_type, amount, amount_in_account_currency, account_currency, delinked, voucher_type, voucher_no, against_voucher_type, against_voucher_no, due_date |
| Inclusion/exclusion rules | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Document/status requirements | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Date and period behavior | As-of report_date/to_date inclusive, not an invoice posting-date cohort. from_date must not remove older open balances. |
| Filters and unsupported dimensions | applicable: Company required; native party_type=Customer, party and party account/Cost Center filters. Installed report has no verified Project/Warehouse scope; reject unsupported combinations. in_party_currency=0 for base-currency total.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency. Account/party-currency balances separate; outstanding_amount is not universally company currency or safely conversion_rate-convertible. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native receivable report, party, invoice/PLE/financial-field read; native record restrictions verified before report use. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Receivable at identical report_date/party/account. |
| Validation source/scenario | ar_net_vs_payment_ledger and ar_current_snapshot (invoice subset); V13-V15 history/multicurrency pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### AR-002 — Gross positive customer balances

| Attribute | Definition |
| --- | --- |
| KPI ID | AR-002 |
| Name | Gross positive customer balances |
| Dashboard(s) | Owner |
| Section | Receivables |
| Business purpose | Separate collection demand from customer credits. |
| Plain-language definition | Positive receivable balances, with negative credit balances separately visible. |
| Exact formula/calculation | SUM(max(leaf outstanding,0)); credits=SUM(min(outstanding,0)); gross+credits=AR-001. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Payment Ledger Entry: company, posting_date, party_type, party, account, account_type, amount, amount_in_account_currency, account_currency, delinked, voucher_type, voucher_no, against_voucher_type, against_voucher_no, due_date |
| Inclusion/exclusion rules | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Document/status requirements | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Date and period behavior | As-of report_date/to_date inclusive, not an invoice posting-date cohort. from_date must not remove older open balances. |
| Filters and unsupported dimensions | applicable: Company required; native party_type=Customer, party and party account/Cost Center filters. Installed report has no verified Project/Warehouse scope; reject unsupported combinations. in_party_currency=0 for base-currency total.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency. Account/party-currency balances separate; outstanding_amount is not universally company currency or safely conversion_rate-convertible. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native receivable report, party, invoice/PLE/financial-field read; native record restrictions verified before report use. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Receivable at identical report_date/party/account. |
| Validation source/scenario | V13 positive invoices plus credits; all-voucher native balance compared, gross component not independently compared. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### AR-003 — Overdue receivables / invoice count

| Attribute | Definition |
| --- | --- |
| KPI ID | AR-003 |
| Name | Overdue receivables / invoice count |
| Dashboard(s) | Owner |
| Section | Receivables |
| Business purpose | Prioritize collectible overdue invoices. |
| Plain-language definition | Positive eligible Sales Invoice balances past known due dates. |
| Exact formula/calculation | SUM(outstanding) and COUNT(DISTINCT voucher_no) where voucher_type=Sales Invoice AND outstanding>0 AND known due_date<as_of. Due-today not overdue; missing dates separate. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, due_date, company, docstatus; Payment Ledger Entry: voucher_no, due_date, amount, posting_date |
| Inclusion/exclusion rules | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Document/status requirements | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Date and period behavior | As-of report_date/to_date inclusive, not an invoice posting-date cohort. from_date must not remove older open balances. |
| Filters and unsupported dimensions | applicable: Company required; native party_type=Customer, party and party account/Cost Center filters. Installed report has no verified Project/Warehouse scope; reject unsupported combinations. in_party_currency=0 for base-currency total.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency. Account/party-currency balances separate; outstanding_amount is not universally company currency or safely conversion_rate-convertible. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native receivable report, party, invoice/PLE/financial-field read; native record restrictions verified before report use. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Receivable at identical report_date/party/account. |
| Validation source/scenario | V14 due-today, partial payment, paid and missing due date boundaries; not all run. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### AR-004 — Receivables aging

| Attribute | Definition |
| --- | --- |
| KPI ID | AR-004 |
| Name | Receivables aging |
| Dashboard(s) | Owner |
| Section | Receivables |
| Business purpose | Show age of outstanding balances at the selected cutoff. |
| Plain-language definition | Native due-date aging buckets, positive balances/credits separate. |
| Exact formula/calculation | Native Accounts Receivable ranges 1-30,31-60,61-90,91-120,>120 days; not-yet-due separate. Missing due date follows explicitly labelled native posting-date fallback or Unknown. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Payment Ledger Entry: company, posting_date, party_type, party, account, account_type, amount, amount_in_account_currency, account_currency, delinked, voucher_type, voucher_no, against_voucher_type, against_voucher_no, due_date |
| Inclusion/exclusion rules | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Document/status requirements | Native Accounts Receivable / Payment Ledger Entry posted and delinked/allocation rules, no drafts/cancelled vouchers. Leaf voucher balances only, no duplicate party totals. |
| Date and period behavior | As-of report_date/to_date inclusive, not an invoice posting-date cohort. from_date must not remove older open balances. |
| Filters and unsupported dimensions | applicable: Company required; native party_type=Customer, party and party account/Cost Center filters. Installed report has no verified Project/Warehouse scope; reject unsupported combinations. in_party_currency=0 for base-currency total.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency. Account/party-currency balances separate; outstanding_amount is not universally company currency or safely conversion_rate-convertible. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native receivable report, party, invoice/PLE/financial-field read; native record restrictions verified before report use. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Receivable at identical report_date/party/account. |
| Validation source/scenario | V14-V15 exact report_date aging buckets; not run. |
| Limitations | Approve aging basis/bands. Do not offset unrelated invoice age buckets with credit silently. |
| Implementation status | proposed |

### AP-001 — Net supplier payables

| Attribute | Definition |
| --- | --- |
| KPI ID | AP-001 |
| Name | Net supplier payables |
| Dashboard(s) | Owner |
| Section | Payables |
| Business purpose | Show supplier obligations net of credits. |
| Plain-language definition | Signed native Accounts Payable balances. |
| Exact formula/calculation | SUM(native report outstanding at eligible leaf vouchers). Gross positive and supplier-credit subtotals separate. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Payment Ledger Entry: company, posting_date, party_type, party, account, account_type, amount, amount_in_account_currency, account_currency, delinked, voucher_type, voucher_no, against_voucher_type, against_voucher_no, due_date |
| Inclusion/exclusion rules | Native Accounts Payable / PLE eligibility and allocation semantics; exclude draft/cancelled vouchers; no group/subtotal duplication. |
| Document/status requirements | Native Accounts Payable / PLE eligibility and allocation semantics; exclude draft/cancelled vouchers; no group/subtotal duplication. |
| Date and period behavior | As-of report_date/to_date inclusive, preserving old unpaid obligations. |
| Filters and unsupported dimensions | applicable: Company required; native Supplier party, party account and Cost Center filters. Customer unsupported; Project/Warehouse unsupported until equivalent report scope is verified.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency; party currencies separated; keep supplier credits separate from positive obligations. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native payable report, Supplier, invoice/PLE and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Payable at identical as-of/party/account. |
| Validation source/scenario | ap_net_vs_payment_ledger and ap_current_snapshot; historical/multicurrency pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### AP-002 — Overdue supplier obligations

| Attribute | Definition |
| --- | --- |
| KPI ID | AP-002 |
| Name | Overdue supplier obligations |
| Dashboard(s) | Owner |
| Section | Payables |
| Business purpose | Identify past-due supplier invoices. |
| Plain-language definition | Positive payable invoices with known due_date before as_of. |
| Exact formula/calculation | SUM(outstanding) and COUNT(DISTINCT voucher_no) for Purchase Invoice, outstanding>0, known due_date<as_of. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Purchase Invoice: name, company, due_date, docstatus; Payment Ledger Entry: voucher_no, amount, due_date |
| Inclusion/exclusion rules | Native Accounts Payable / PLE eligibility and allocation semantics; exclude draft/cancelled vouchers; no group/subtotal duplication. |
| Document/status requirements | Native Accounts Payable / PLE eligibility and allocation semantics; exclude draft/cancelled vouchers; no group/subtotal duplication. |
| Date and period behavior | As-of report_date/to_date inclusive, preserving old unpaid obligations. |
| Filters and unsupported dimensions | applicable: Company required; native Supplier party, party account and Cost Center filters. Customer unsupported; Project/Warehouse unsupported until equivalent report scope is verified.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Native report company currency; party currencies separated; keep supplier credits separate from positive obligations. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive/finance plus native payable report, Supplier, invoice/PLE and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Accounts Payable at identical as-of/party/account. |
| Validation source/scenario | V14 payable counterpart, debit notes/due today; not run. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-001 — Net invoiced sales by Customer

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-001 |
| Name | Net invoiced sales by Customer |
| Dashboard(s) | Owner |
| Section | Finance and sales |
| Business purpose | Compare customers consistently. |
| Plain-language definition | FIN-001 partitioned by explicit parent Customer. |
| Exact formula/calculation | Group eligible FIN-001 invoice/line amounts by authorized Customer; partitions including Unassigned reconcile to FIN-001 under same scope. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, docstatus, company, posting_date, customer, project, base_net_total, base_grand_total, is_return, is_internal_customer, represents_company, currency, conversion_rate; Sales Invoice Item: parent, base_net_amount, project, income_account |
| Inclusion/exclusion rules | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Document/status requirements | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Date and period behavior | Inclusive Sales Invoice.posting_date period, never creation/modified. |
| Filters and unsupported dimensions | applicable: Company required; Customer=Sales Invoice.customer; Project via verified header or Sales Invoice Item.project with consistent parent fallback and line base_net_amount (never duplicate header totals). Warehouse unsupported without verified line allocation.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Company base_* currency; sum stored precision then round once to native currency precision. No fixed INR or mixing grand_total currencies. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive capability AND native Sales Invoice/child/Customer/Project and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Register / authorized Sales Invoice form with identical scope. |
| Validation source/scenario | invoice_net_vs_sales_register total basis; V03 grouping/joins pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-002 — Top customers by net sales

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-002 |
| Name | Top customers by net sales |
| Dashboard(s) | Owner |
| Section | Finance and sales |
| Business purpose | Rank customers without item-join inflation. |
| Plain-language definition | Top N groups from SALES-001. |
| Exact formula/calculation | Sort amount descending, stable Customer ID ties; proposed N10,max50. TopN+Other=total; negative return-only groups retained in detail. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, docstatus, company, posting_date, customer, project, base_net_total, base_grand_total, is_return, is_internal_customer, represents_company, currency, conversion_rate; Sales Invoice Item: parent, base_net_amount, project, income_account |
| Inclusion/exclusion rules | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Document/status requirements | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Date and period behavior | Inclusive Sales Invoice.posting_date period, never creation/modified. |
| Filters and unsupported dimensions | applicable: Company required; Customer=Sales Invoice.customer; Project via verified header or Sales Invoice Item.project with consistent parent fallback and line base_net_amount (never duplicate header totals). Warehouse unsupported without verified line allocation.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Company base_* currency; sum stored precision then round once to native currency precision. No fixed INR or mixing grand_total currencies. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive capability AND native Sales Invoice/child/Customer/Project and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Register / authorized Sales Invoice form with identical scope. |
| Validation source/scenario | V03 ties/returns/two lines per header; ranking not run. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-003 — Net sales trend / comparison

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-003 |
| Name | Net sales trend / comparison |
| Dashboard(s) | Owner |
| Section | Finance and sales |
| Business purpose | Compare equal sales periods. |
| Plain-language definition | FIN-001 posting-date time buckets. |
| Exact formula/calculation | SUM(FIN-001) per calendar day/week/month; delta=current-prior, change%=100*(current-prior)/abs(prior) if prior!=0 else null. Equal windows explicit; partial month labelled. |
| Numerator | Current minus prior FIN-001 amount, identical comparable windows/currency. |
| Denominator | Absolute prior FIN-001 amount; prior0=>null percentage. |
| ERPNext DocTypes / exact fields | Sales Invoice: name, docstatus, company, posting_date, customer, project, base_net_total, base_grand_total, is_return, is_internal_customer, represents_company, currency, conversion_rate; Sales Invoice Item: parent, base_net_amount, project, income_account |
| Inclusion/exclusion rules | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Document/status requirements | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Date and period behavior | Inclusive Sales Invoice.posting_date period, never creation/modified. |
| Filters and unsupported dimensions | applicable: Company required; Customer=Sales Invoice.customer; Project via verified header or Sales Invoice Item.project with consistent parent fallback and line base_net_amount (never duplicate header totals). Warehouse unsupported without verified line allocation.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Company base_* currency; sum stored precision then round once to native currency precision. No fixed INR or mixing grand_total currencies. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive capability AND native Sales Invoice/child/Customer/Project and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Register / authorized Sales Invoice form with identical scope. |
| Validation source/scenario | Native total basis checked; V04/V07 boundaries and prior0 pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-004 — Open delivery backlog quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-004 |
| Name | Open delivery backlog quantity |
| Dashboard(s) | Owner, Production |
| Section | Sales commitments |
| Business purpose | Show undelivered commitments, not revenue. |
| Plain-language definition | Remaining eligible order-line delivery quantity. |
| Exact formula/calculation | Per line max(qty-delivered_qty,0)*conversion_factor by item+stock_uom; do not subtract returned_qty again if native delivered_qty already nets returns. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Order: name, company, customer, transaction_date, status, docstatus, project; Sales Order Item: name, parent, item_code, stock_uom, uom, qty, delivered_qty, returned_qty, conversion_factor, base_net_rate, base_net_amount, delivery_date, warehouse, project |
| Inclusion/exclusion rules | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Document/status requirements | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Date and period behavior | Current backlog at generated_at; optional transaction_date cohort explicitly labelled. Due-date view uses line delivery_date; no historical backlog inferred. |
| Filters and unsupported dimensions | applicable: Company required; parent Customer; line Project with consistent parent fallback; line Warehouse; item/stock_uom/delivery_date/source ID. Mixed order header values cannot be allocated repeatedly.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Quantity by item+stock_uom using recorded conversion_factor; value in base company currency, rounded after aggregation. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Sales Order/child/Customer/Project rights; money additionally finance capability/field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Order Analysis / source order and line. |
| Validation source/scenario | V16 partial/held/closed/cancelled/UOM lifecycle; pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-005 — Open delivery backlog value

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-005 |
| Name | Open delivery backlog value |
| Dashboard(s) | Owner |
| Section | Sales commitments |
| Business purpose | Value unfulfilled delivery commitments. |
| Plain-language definition | Remaining delivery quantity at recorded tax-exclusive net base rate. |
| Exact formula/calculation | SUM(max(qty-delivered_qty,0)*base_net_rate) for SALES-004 lines. Not grand_total*(1-per_delivered%). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Order: name, company, customer, transaction_date, status, docstatus, project; Sales Order Item: name, parent, item_code, stock_uom, uom, qty, delivered_qty, returned_qty, conversion_factor, base_net_rate, base_net_amount, delivery_date, warehouse, project |
| Inclusion/exclusion rules | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Document/status requirements | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Date and period behavior | Current backlog at generated_at; optional transaction_date cohort explicitly labelled. Due-date view uses line delivery_date; no historical backlog inferred. |
| Filters and unsupported dimensions | applicable: Company required; parent Customer; line Project with consistent parent fallback; line Warehouse; item/stock_uom/delivery_date/source ID. Mixed order header values cannot be allocated repeatedly.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Quantity by item+stock_uom using recorded conversion_factor; value in base company currency, rounded after aggregation. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Sales Order/child/Customer/Project rights; money additionally finance capability/field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Order Analysis / source order and line. |
| Validation source/scenario | V16-V17 different rates/discounts/taxes/currencies; pending. |
| Limitations | Not unbilled value, recognized revenue or cash due. Service/drop-ship/direct-billing policy needs approval. |
| Implementation status | proposed |

### SALES-006 — Open customer orders count

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-006 |
| Name | Open customer orders count |
| Dashboard(s) | Owner, Production |
| Section | Sales commitments |
| Business purpose | Count orders still carrying delivery demand. |
| Plain-language definition | Eligible distinct orders with positive remaining lines. |
| Exact formula/calculation | COUNT(DISTINCT order.name with any SALES-004 remaining line>0); held demand separately labelled. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Order: name, company, customer, transaction_date, status, docstatus, project; Sales Order Item: name, parent, item_code, stock_uom, uom, qty, delivered_qty, returned_qty, conversion_factor, base_net_rate, base_net_amount, delivery_date, warehouse, project |
| Inclusion/exclusion rules | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Document/status requirements | Submitted Sales Order.docstatus=1; exclude Completed/Closed/Cancelled. Proposed policy: On Hold is held demand, not executable delivery backlog. Partial lines retained. |
| Date and period behavior | Current backlog at generated_at; optional transaction_date cohort explicitly labelled. Due-date view uses line delivery_date; no historical backlog inferred. |
| Filters and unsupported dimensions | applicable: Company required; parent Customer; line Project with consistent parent fallback; line Warehouse; item/stock_uom/delivery_date/source ID. Mixed order header values cannot be allocated repeatedly.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Quantity by item+stock_uom using recorded conversion_factor; value in base company currency, rounded after aggregation. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Sales Order/child/Customer/Project rights; money additionally finance capability/field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Order Analysis / source order and line. |
| Validation source/scenario | V16 multiple lines in one order count once; pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### SALES-007 — Allocated customer collections

| Attribute | Definition |
| --- | --- |
| KPI ID | SALES-007 |
| Name | Allocated customer collections |
| Dashboard(s) | Owner |
| Section | Finance and sales |
| Business purpose | Separate received allocations from invoices and advances. |
| Plain-language definition | Submitted Receive Payment Entry allocations. |
| Exact formula/calculation | SUM(Payment Entry Reference.allocated_amount on submitted Customer Receive entries), native account/company currency treatment; unallocated advances, refunds and JE allocations separately labelled. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Payment Entry: name, company, posting_date, docstatus, payment_type, party_type, party; Payment Entry Reference: parent, reference_doctype, reference_name, allocated_amount |
| Inclusion/exclusion rules | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Document/status requirements | Submitted Sales Invoice.docstatus=1; exclude draft/cancelled and same-company internal transfers; signed returns included once. Submitted amended replacement replaces cancelled original. |
| Date and period behavior | Payment Entry.posting_date, not invoice date. |
| Filters and unsupported dimensions | applicable: Company required; Customer=Sales Invoice.customer; Project via verified header or Sales Invoice Item.project with consistent parent fallback and line base_net_amount (never duplicate header totals). Warehouse unsupported without verified line allocation.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Company base_* currency; sum stored precision then round once to native currency precision. No fixed INR or mixing grand_total currencies. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Executive capability AND native Sales Invoice/child/Customer/Project and financial-field rights. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Sales Register / authorized Sales Invoice form with identical scope. |
| Validation source/scenario | V18 partial allocation/advance/refund/FX; not run. |
| Limitations | Not bank cash flow or complete AR movement; multicurrency/refunds unvalidated. Never subtract all receipts from invoice totals. |
| Implementation status | proposed |

### PROJ-001 — Recorded Project progress

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-001 |
| Name | Recorded Project progress |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Show configured progress rather than a new invented average. |
| Plain-language definition | Persisted Project.percent_complete and percent_complete_method. |
| Exact formula/calculation | Read stored percent_complete/method. Installed16.33: Manual retains value (Completed forces100); Task Completion=(Completed+Cancelled Tasks)/all Tasks*100; Task Progress=SUM(Task.progress)/count; Task Weight=SUM(progress*task_weight)/SUM(weights) with native safe_div. No Tasks=>native0 unless manually complete. |
| Numerator | Native Task Completion: Completed+Cancelled count; Task Progress: SUM(progress); Task Weight: SUM(progress*task_weight); Manual is a stored value. |
| Denominator | Native all-Task count or SUM(task_weight), method-dependent; display stored result rather than a new ratio. |
| ERPNext DocTypes / exact fields | Project: name, percent_complete, percent_complete_method, status; Task: project, status, progress, task_weight |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Read authorized stored percent_complete faithfully. Native no-Task or zero-weight computation can store0; disclose method/coverage. Missing permission/field=>Unknown, no new recomputation. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V19 native controller method fixtures pending; source/metadata inspected, no Tasks locally. |
| Limitations | Installed Project controller differs from checkout. Installed Task Progress/Weight do not force completed Tasks to100 as newer checkout does; always consume native stored value and revalidate upgrades. |
| Implementation status | proposed |

### PROJ-002 — Overdue projects

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-002 |
| Name | Overdue projects |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Identify open deadlines already elapsed. |
| Plain-language definition | Open/held Project past known expected end. |
| Exact formula/calculation | COUNT(DISTINCT Project.name where status in Open,On hold AND expected_end_date<today); held subset labelled. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, expected_end_date, company, customer |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V20 due-today/past/terminal/held/missing date; pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### PROJ-003 — Dated projects not overdue

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-003 |
| Name | Dated projects not overdue |
| Dashboard(s) | Owner |
| Section | Project and delivery health |
| Business purpose | Avoid claiming forecast confidence from a due date. |
| Plain-language definition | Open dated projects whose due date has not passed. |
| Exact formula/calculation | COUNT(Project status=Open AND known expected_end_date>=today). Label Not overdue, not guaranteed On track. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, expected_end_date |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V20 same cohort as PROJ-002. |
| Limitations | Undated/held projects separate; Open does not prove on-track production. |
| Implementation status | proposed |

### PROJ-004 — Projects due soon

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-004 |
| Name | Projects due soon |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Highlight approaching deadlines. |
| Plain-language definition | Open dated projects within an approved configurable horizon H. |
| Exact formula/calculation | COUNT(Project status=Open AND today<=expected_end_date<=today+H); proposed H7 days, awaiting approval. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, expected_end_date |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V20 H boundaries and invalid horizon; pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### PROJ-005 — Project delivery risk

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-005 |
| Name | Project delivery risk |
| Dashboard(s) | Owner |
| Section | Project and delivery health |
| Business purpose | Expose supported delivery exceptions. |
| Plain-language definition | Unapproved rule-based risk, not an AI prediction. |
| Exact formula/calculation | Proposed: overdue OR (due-soon AND remaining required production>0) OR confirmed unresolved critical material/quality blocker. Missing delivery/schedule mapping=>Unknown, not Low risk. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, expected_end_date; Work Order: name, project, qty, produced_qty, planned_end_date |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V21 multi-delivery commitment/critical blocker; blocked. |
| Limitations | Approve severity/horizon and verified Sales Order delivery-line -> required WO mapping; no critical-path model. |
| Implementation status | blocked |

### PROJ-006 — Recorded manufacturing state by Project

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-006 |
| Name | Recorded manufacturing state by Project |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Distinguish production state from administrative Project progress. |
| Plain-language definition | Derived lifetime production summary with explicit completeness. |
| Exact formula/calculation | Not started if no start/output evidence; In progress if started/incomplete; Finished only with >=1 eligible WO, every WO Completed and every required operation balance known and closed. Missing expected operation rows=>Unknown/incomplete configuration, never all([])=complete. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V22 no WO/missing operations/partial/stopped/closure pending. |
| Limitations | Existing analyze/live_activity derived labels need alignment; empty operation lists must not certify a complete pipeline. |
| Implementation status | proposed |

### PROJ-007 — Active Projects count

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-007 |
| Name | Active Projects count |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Distinguish nonterminal business projects from manufacturing output. |
| Plain-language definition | Current readable Project records not terminal. |
| Exact formula/calculation | COUNT(DISTINCT Project.name where status in Open,On hold); held subset disclosed. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, company, customer |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V20 current source states; no extra native lifecycle fixture. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### PROJ-008 — Completed Projects count

| Attribute | Definition |
| --- | --- |
| KPI ID | PROJ-008 |
| Name | Completed Projects count |
| Dashboard(s) | Owner, Production |
| Section | Project and delivery health |
| Business purpose | Show administrative closure separately from production completion. |
| Plain-language definition | Native Projects with status Completed. |
| Exact formula/calculation | COUNT(DISTINCT Project.name where status=Completed and docstatus<2); do not replace native status with PROJ-006. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name, status, docstatus |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current stored progress/status; expected_end_date compared to local calendar today. Optional Project.creation cohort separately labelled. |
| Filters and unsupported dimensions | applicable: Company required; explicit Project.customer and Project ID; no name inference. Warehouse unsupported. Date/status filters must use the declared cohort/deadline basis.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Integer counts; native percent precision, display 2 decimals; no currency or aggregation of unlike production. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V20 Completed Project vs finished production/closure pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-001 — Scheduled-start planned production

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-001 |
| Name | Scheduled-start planned production |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Show a declared schedule cohort target. |
| Plain-language definition | Planned WO quantity per item/UOM schedule-start cohort. |
| Exact formula/calculation | SUM(WO.qty) for eligible planned_start_date cohort, by company+production_item+stock_uom. Missing planned start is Unknown schedule, not allocated to period. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | work_order_qty_vs_report verifies submitted-ID checksum, not planned-date target; V23-V25 cohort fixtures pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-002 — Produced output to date for cohort

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-002 |
| Name | Produced output to date for cohort |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Compare exactly the same jobs against target. |
| Plain-language definition | Current cumulative WO.produced_qty for MFG-001 IDs. |
| Exact formula/calculation | SUM(WO.produced_qty) for exact MFG-001 cohort and item/UOM; never SUM(Job Card outputs across operations). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | work_order_produced_vs_report; four real item cohorts partial/complete. Planned-period attribution pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-003 — Production achievement (cohort)

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-003 |
| Name | Production achievement (cohort) |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Compare good output with compatible target. |
| Plain-language definition | Good finished output percentage at item/UOM cohort grain. |
| Exact formula/calculation | 100*MFG-002/MFG-001 if target>0 else null; allow >100 with overproduction warning. No scalar across different items/UOMs without approved normalization. |
| Numerator | MFG-002, same IDs/item/UOM. |
| Denominator | MFG-001, same IDs/item/UOM. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | Real item ratios25%,62.962963%,90%,100%; V24-V25 zero/mixed UOM. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-004 — Production variance (cohort)

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-004 |
| Name | Production variance (cohort) |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Show unit-specific shortfall or overproduction. |
| Plain-language definition | Signed produced minus planned cohort quantity. |
| Exact formula/calculation | MFG-002-MFG-001 per same company+item+stock_uom. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | V24 arithmetic: planned10/produced6=>-4; produced12=>+2, not native lifecycle tests. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-005 — Finished output posted in period

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-005 |
| Name | Finished output posted in period |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Measure posting flow separately from lifetime cohort progress. |
| Plain-language definition | Net finished-item Manufacture stock movement in period. |
| Exact formula/calculation | SUM(signed SLE.actual_qty for designated finished Stock Entry Detail rows of submitted Stock Entry.purpose=Manufacture linked to WO), grouping actual finished item+stock_uom. Exclude transfer-only/scrap; native actual movement direction handles returns, not a guessed sign from quantity. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Stock Entry: name, company, purpose, docstatus, posting_date, posting_time, work_order, is_return; Stock Entry Detail: name, parent, item_code, is_finished_item, transfer_qty, stock_uom, t_warehouse, s_warehouse; Stock Ledger Entry: voucher_no, voucher_detail_no, actual_qty, item_code, warehouse, is_cancelled |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | Stock Entry/SLE posting_date+posting_time local period; not WO.creation. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | V26 partial manufacture/transfer/cancel/return/disassembly/alternative FG; not run. |
| Limitations | Achievement against schedule needs matching cohort attribution. Return/alternative-FG native fixtures pending. |
| Implementation status | proposed |

### MFG-006 — Active Work Orders

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-006 |
| Name | Active Work Orders |
| Dashboard(s) | Owner, Production |
| Section | Work Order status and deadlines |
| Business purpose | Coordinate current factory workload and deadlines. |
| Plain-language definition | Active Work Orders by native state/known expected completion. |
| Exact formula/calculation | COUNT(DISTINCT eligible active WO.name). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Document/status requirements | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Date and period behavior | Current state; planned_end_date is Datetime and overdue compares to server now in site timezone. Missing schedule unknown; no historical status reconstruction. |
| Filters and unsupported dimensions | applicable: Company required; authorized WO/Project and verified Customer path; source/WIP/FG warehouse dimension explicitly chosen; optional deadline window.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct document counts; compatible item/UOM for any quantities, not currency. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native and dashboard WO scope as mfg; no factory scope for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Work Order list/form with same status/deadline predicate. |
| Validation source/scenario | V27 active statuses including reserved; stopped/closed/draft/cancelled excluded. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-007 — Completed Work Orders

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-007 |
| Name | Completed Work Orders |
| Dashboard(s) | Owner, Production |
| Section | Work Order status and deadlines |
| Business purpose | Coordinate current factory workload and deadlines. |
| Plain-language definition | Completed Work Orders by native state/known expected completion. |
| Exact formula/calculation | COUNT(DISTINCT WO.name where docstatus=1 AND status=Completed). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Document/status requirements | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Date and period behavior | Current state; planned_end_date is Datetime and overdue compares to server now in site timezone. Missing schedule unknown; no historical status reconstruction. |
| Filters and unsupported dimensions | applicable: Company required; authorized WO/Project and verified Customer path; source/WIP/FG warehouse dimension explicitly chosen; optional deadline window.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct document counts; compatible item/UOM for any quantities, not currency. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native and dashboard WO scope as mfg; no factory scope for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Work Order list/form with same status/deadline predicate. |
| Validation source/scenario | V27 completed versus cancelled replacement. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-008 — Overdue Work Orders

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-008 |
| Name | Overdue Work Orders |
| Dashboard(s) | Owner, Production |
| Section | Work Order status and deadlines |
| Business purpose | Coordinate current factory workload and deadlines. |
| Plain-language definition | Overdue Work Orders by native state/known expected completion. |
| Exact formula/calculation | COUNT(DISTINCT active WO.name with known planned_end_date<now). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Document/status requirements | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Date and period behavior | Current state; planned_end_date is Datetime and overdue compares to server now in site timezone. Missing schedule unknown; no historical status reconstruction. |
| Filters and unsupported dimensions | applicable: Company required; authorized WO/Project and verified Customer path; source/WIP/FG warehouse dimension explicitly chosen; optional deadline window.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct document counts; compatible item/UOM for any quantities, not currency. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native and dashboard WO scope as mfg; no factory scope for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Work Order list/form with same status/deadline predicate. |
| Validation source/scenario | V28 due-now/overdue/missing end/terminal. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-009 — Work Orders due soon

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-009 |
| Name | Work Orders due soon |
| Dashboard(s) | Owner, Production |
| Section | Work Order status and deadlines |
| Business purpose | Coordinate current factory workload and deadlines. |
| Plain-language definition | Work Orders due soon by native state/known expected completion. |
| Exact formula/calculation | COUNT(DISTINCT active WO.name where now<=planned_end_date<=now+H); proposed configurable H7 days. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Document/status requirements | Submitted WO only; active statuses Submitted/Not Started/In Process/Stock Reserved/Stock Partially Reserved. Completed/Stopped/Closed/Cancelled/Draft not active. |
| Date and period behavior | Current state; planned_end_date is Datetime and overdue compares to server now in site timezone. Missing schedule unknown; no historical status reconstruction. |
| Filters and unsupported dimensions | applicable: Company required; authorized WO/Project and verified Customer path; source/WIP/FG warehouse dimension explicitly chosen; optional deadline window.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct document counts; compatible item/UOM for any quantities, not currency. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native and dashboard WO scope as mfg; no factory scope for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Work Order list/form with same status/deadline predicate. |
| Validation source/scenario | V28 both time bounds/horizon/timezone. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-010 — Remaining good-output target

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-010 |
| Name | Remaining good-output target |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Retain unproduced good-output commitment even when loss closes processing. |
| Plain-language definition | Remaining good target, separate from remaining processing. |
| Exact formula/calculation | Per WO max(qty-produced_qty,0), grouped compatible item/UOM. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | V29 qty10/good8/loss2=>good target remaining2. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-011 — Remaining processing quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-011 |
| Name | Remaining processing quantity |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Show quantity not disposed as good output or process loss. |
| Plain-language definition | Remaining processing obligation. |
| Exact formula/calculation | Per WO max(qty-produced_qty-process_loss_qty,0), known counters only. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | V29 qty10/good8/loss2=>processing0; good achievement80%, not100%. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### MFG-012 — Work Order completion rate

| Attribute | Definition |
| --- | --- |
| KPI ID | MFG-012 |
| Name | Work Order completion rate |
| Dashboard(s) | Owner, Production |
| Section | Manufacturing output |
| Business purpose | Compare completed document count within one cohort. |
| Plain-language definition | Completed WOs divided by all eligible submitted cohort WOs. |
| Exact formula/calculation | 100*COUNT(cohort status=Completed)/COUNT(eligible cohort IDs); empty cohort=>null. |
| Numerator | Completed distinct WOs in cohort. |
| Denominator | All eligible submitted cohort WOs, including completed. |
| ERPNext DocTypes / exact fields | Work Order: name, company, production_item, stock_uom, qty, produced_qty, process_loss_qty, docstatus, status, planned_start_date, planned_end_date, project, sales_order, fg_warehouse |
| Inclusion/exclusion rules | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Document/status requirements | Work Order.docstatus=1; schedule-start cohort excludes cancelled/stopped/closed, includes completed. Exclusion of abandoned targets is proposed policy needing approval. |
| Date and period behavior | planned_start_date selects schedule-start cohort; produced_qty is current cumulative output of those exact IDs, not posting-period flow. |
| Filters and unsupported dimensions | applicable: Company required; Work Order.project; Customer only verified Project/Sales Order link (conflicts unknown); production_item+stock_uom and fg_warehouse for output. Source/WIP warehouse views separate. Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group company+production_item+stock_uom; never sum different items even with same UOM. Native quantity precision; ratios rounded after aggregation, no silent 100% cap. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production native WO and linked records/fields; supervisor/operator related assigned jobs only per DASH-003. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Work Order Summary / WO form; align exact IDs, date basis, age and draft exclusions. |
| Validation source/scenario | V27 one of two WOs=>50%; counts not quantity weights. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### OPS-001 — Completed recorded operations

| Attribute | Definition |
| --- | --- |
| KPI ID | OPS-001 |
| Name | Completed recorded operations |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Avoid counting split Job Cards as routing stages. |
| Plain-language definition | Distinct native WO Operation rows completed with known quantity. |
| Exact formula/calculation | COUNT(distinct WO Operation with eligible parent,status=Completed, completed_qty+process_loss_qty>=verified operation plan). Ordinary plan=WO.qty; semi-FG conversion requires compatible verified basis. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order Operation: name, parent, operation, status, completed_qty, process_loss_qty, pending_qty, finished_good; Work Order: name, qty, stock_uom, docstatus, status |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V30 split/corrective jobs/missing operations. |
| Limitations | Zero WO Operation rows despite15 Job Cards. Missing child table is not a complete pipeline; semi-FG conversions unvalidated. |
| Implementation status | not configured |

### OPS-002 — Operation progress

| Attribute | Definition |
| --- | --- |
| KPI ID | OPS-002 |
| Name | Operation progress |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Measure a routing operation at its own grain. |
| Plain-language definition | Good completion ratio at one WO Operation. |
| Exact formula/calculation | 100*WO Operation.completed_qty/verified planned operation quantity; plan<=0 or unknown mapping/UOM=>null. Loss separate; sequential operations not added. |
| Numerator | Good completed_qty at operation row. |
| Denominator | Verified compatible per-operation plan. |
| ERPNext DocTypes / exact fields | Work Order Operation: name, parent, completed_qty, process_loss_qty, finished_good; Work Order: name, qty, stock_uom |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V30 target10/good8/loss2=>80%; no operation rows. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### OPS-003 — Late-operation / potential bottleneck list

| Attribute | Definition |
| --- | --- |
| KPI ID | OPS-003 |
| Name | Late-operation / potential bottleneck list |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Prioritize observed schedule exceptions without false capacity optimization. |
| Plain-language definition | Ranked delayed jobs, not measured bottleneck probability. |
| Exact formula/calculation | Sort JOB-014 records by now-expected_end_date descending; show per-record remaining quantity/time/Workstation. True capacity bottleneck unavailable without schedule, queue and capacity coverage. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V31 multiple workstations, preserve per-job unit; pending. |
| Limitations | Lateness proxy only; no machine utilization or critical-path claim. |
| Implementation status | proposed |

### OPS-004 — Corrective Job Cards / rework count

| Attribute | Definition |
| --- | --- |
| KPI ID | OPS-004 |
| Name | Corrective Job Cards / rework count |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Expose recorded corrective work without inventing rejection units. |
| Plain-language definition | Non-cancelled corrective job records. |
| Exact formula/calculation | COUNT(DISTINCT Job Card.name where is_corrective_job_card=1); disclose draft/submitted and for_job_card link. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, docstatus, is_corrective_job_card, for_job_card, work_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V32 original+two corrective jobs=>2 rework jobs, not3 FG outputs. |
| Limitations | Not rework units or defect rate; native corrective fixture not run. |
| Implementation status | proposed |

### JOB-001 — Job planned quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-001 |
| Name | Job planned quantity |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make current assigned work and next action understandable. |
| Plain-language definition | Job planned quantity for the authorized job. |
| Exact formula/calculation | Read Job Card.for_quantity for authorized current job. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V33 split batch plan differs from full WO.qty. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-002 — Job recorded good output

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-002 |
| Name | Job recorded good output |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make current assigned work and next action understandable. |
| Plain-language definition | Job recorded good output for the authorized job. |
| Exact formula/calculation | Read Job Card.total_completed_qty; provisional if draft, authoritative submitted counter separately. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V33 do not add employee/time-log completed_qty to already totalled header. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-003 — Job remaining processing quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-003 |
| Name | Job remaining processing quantity |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make current assigned work and next action understandable. |
| Plain-language definition | Job remaining processing quantity for the authorized job. |
| Exact formula/calculation | max(for_quantity-total_completed_qty-process_loss_qty,0), all fields/UOM known. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V29/V33 plan10/good8/loss1=>1; missing field=>Unknown. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-004 — Job good-output progress

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-004 |
| Name | Job good-output progress |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Separate successful output from processing disposition. |
| Plain-language definition | Good-output ratio for one job. |
| Exact formula/calculation | 100*total_completed_qty/for_quantity if plan>0 else null; overproduction flagged, no silent cap. |
| Numerator | Same Job Card.total_completed_qty. |
| Denominator | Same Job Card.for_quantity/UOM. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V29/V33 loss may close processing with good progress<100. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-005 — Job process loss

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-005 |
| Name | Job process loss |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make current assigned work and next action understandable. |
| Plain-language definition | Job process loss for the authorized job. |
| Exact formula/calculation | Read Job Card.process_loss_qty, separate from good/rejected quantities. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V29 loss is not quality rejection and never deducted twice. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-006 — Recorded operation time

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-006 |
| Name | Recorded operation time |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Show logged work rather than measured machine runtime. |
| Plain-language definition | Closed log durations clipped to selected actual interval; lifetime header separately. |
| Exact formula/calculation | SUM(overlap([from_time,to_time],[period_start,period_end])) in minutes for valid closed Job Card Time Logs. Lifetime control=total_time_in_mins. Concurrent employee logs are labour-minutes, not machine elapsed time; open logs not finalized minutes. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, total_time_in_mins, work_order; Job Card Time Log: parent, from_time, to_time, time_in_mins, employee, completed_qty |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Actual log intervals, clipped in site timezone; not Job Card.posting_date. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V35 midnight/two employees/open/invalid log; no native logs. |
| Limitations | No Employee or time-log rows; header/log consistency and elapsed-versus-labour interpretation need native fixture. |
| Implementation status | not configured |

### JOB-007 — Job rejected quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-007 |
| Name | Job rejected quantity |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Prevent process loss/sample size masquerading as rejected output. |
| Plain-language definition | No verified per-job rejected-good-output source. |
| Exact formula/calculation | Unavailable. Job Card has process_loss_qty, no rejected_qty. Quality Inspection.sample_size is not rejected units. Requires approved linked rejected-output source/UOM. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, process_loss_qty, quality_inspection; Quality Inspection: sample_size, status, reference_type, reference_name |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V36 rejected sample does not imply rejected batch; blocked. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | blocked |

### JOB-008 — Assigned operations / jobs

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-008 |
| Name | Assigned operations / jobs |
| Dashboard(s) | Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Restrict work to current user/team scope. |
| Plain-language definition | Distinct readable assigned/explicitly authorized Job Cards. |
| Exact formula/calculation | COUNT(DISTINCT readable Job Card IDs after check_shop_job). Operator uses open ToDo(reference_type=Job Card,allocated_to=current_user,status=Open); supervisor may union explicit applicable Workstation User Permission jobs; deduplicate. Valid configured scope with no assignments=>[]/0. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | ToDo: reference_type, reference_name, allocated_to, status; Job Card: name, workstation, work_order, docstatus; User Permission: user, allow, for_value, applicable_for |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V37 another user/team/closed ToDo/empty list. DASH-003 guards previously tested, not rerun as KPI validation; no live assignments. |
| Limitations | Employee child table is not assignment. Workboard does not exist; no inferred shift/current job. |
| Implementation status | not configured |

### JOB-009 — Current Job Card status

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-009 |
| Name | Current Job Card status |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make current assigned work and next action understandable. |
| Plain-language definition | Current Job Card status for the authorized job. |
| Exact formula/calculation | Read exact Job Card.status/docstatus and parent status; derive recorded-running separately from open time log. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V34 native Open/Work In Progress/Partially Transferred/Material Transferred/On Hold/Submitted/Completed/Cancelled; no invented Blocked status. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-010 — Recorded running jobs

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-010 |
| Name | Recorded running jobs |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Show actual ERP start evidence, not live machine state. |
| Plain-language definition | Executable authorized jobs with an open time log. |
| Exact formula/calculation | COUNT(DISTINCT job with log.from_time set,to_time empty), excluding Completed/Cancelled/On Hold jobs and completed/stopped/closed/cancelled parent WOs. Label Recorded running and show start timestamp. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, work_order, status, docstatus; Job Card Time Log: parent, from_time, to_time; Work Order: name, status, docstatus |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V35 held/completed/stopped parents excluded; no logs. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### JOB-011 — Waiting jobs

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-011 |
| Name | Waiting jobs |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Separate ready waiting work from unknown readiness. |
| Plain-language definition | Proposed assigned executable job not started and actually ready. |
| Exact formula/calculation | COUNT(authorized executable jobs with no log start, no actual_start_date,total_completed_qty=0), only after verified material/sequence readiness. Otherwise label Not started/readiness unknown, not Waiting ready. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V38 unknown materials/predecessor/held/empty assignment. |
| Limitations | No complete readiness or sequencing model; Open alone does not prove ready. |
| Implementation status | blocked |

### JOB-012 — Blocked jobs / operations

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-012 |
| Name | Blocked jobs / operations |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Expose confirmed blockers, not an invented native status. |
| Plain-language definition | Distinct authorized jobs with an explicit unresolved blocker. |
| Exact formula/calculation | Unavailable until verified job-linked blocker source exists; future COUNT(DISTINCT nonterminal job with confirmed unresolved blocker). On Hold/is_paused/material risk are separate proxies. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, is_paused, status, work_order; Issue: name, status, project, company |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V38-V39 confirmed/inferred/resolved/private blocker; blocked. |
| Limitations | Issue exists but has no Job Card reference; no verified mapping or new blocker DocType created. |
| Implementation status | blocked |

### JOB-013 — Reported production issues

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-013 |
| Name | Reported production issues |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Make production problems auditable. |
| Plain-language definition | No configured issue-to-job relationship. |
| Exact formula/calculation | Unavailable; future COUNT(DISTINCT unresolved linked issue ID for authorized Job Card), approved resolution statuses; never parse remarks into counts. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Issue: name, status, project, company; Job Card: name, remarks |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V39 multi-job/private/resolved issue; blocked. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | blocked |

### JOB-014 — Delayed Job Cards

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-014 |
| Name | Delayed Job Cards |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Identify unfinished scheduled operations already late. |
| Plain-language definition | Executable nonterminal job past known expected end. |
| Exact formula/calculation | COUNT(DISTINCT job with known expected_end_date<now AND status not Completed,Cancelled AND active submitted parent AND known JOB-003>0). On Hold subset labelled; missing schedule/remaining=>Unknown. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V28/V34 due boundary/stale status/held/missing date. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-015 — On-hold Job Cards

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-015 |
| Name | On-hold Job Cards |
| Dashboard(s) | Production, Shop-floor supervisor, Shop-floor operator |
| Section | Operations and shop-floor |
| Business purpose | Show recorded holds separately from blocker causes. |
| Plain-language definition | Authorized executable native On Hold jobs. |
| Exact formula/calculation | COUNT(DISTINCT eligible job where status=On Hold). is_paused separately disclosed, not a new workflow status. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V34 On Hold and paused flag; pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-016 — Open executable Job Cards

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-016 |
| Name | Open executable Job Cards |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Avoid treating draft-parent planning as executable work. |
| Plain-language definition | Nonterminal Job Cards on active submitted WOs. |
| Exact formula/calculation | COUNT(DISTINCT job docstatus!=2,status not Completed,Cancelled,parent in MFG-006). Submitted-but-incomplete disclosed; docstatus1 alone does not mean completed. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V34 parent draft/completed/stopped and Submitted vs Completed. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### JOB-017 — Planned Job Cards on draft WOs

| Attribute | Definition |
| --- | --- |
| KPI ID | JOB-017 |
| Name | Planned Job Cards on draft WOs |
| Dashboard(s) | Production |
| Section | Operations and shop-floor |
| Business purpose | Keep planning separate from live production. |
| Plain-language definition | Non-cancelled Job Cards with draft parent WO. |
| Exact formula/calculation | COUNT(DISTINCT job with parent WO.docstatus=0 and job.docstatus!=2); exclude from JOB-016/assigned executable counts. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Job Card: name, company, work_order, for_quantity, total_completed_qty, process_loss_qty, stock_uom, status, docstatus, operation_id, workstation, expected_end_date, is_corrective_job_card, total_time_in_mins; Work Order: name, docstatus, status, company, project, sales_order |
| Inclusion/exclusion rules | Job Card.docstatus!=2, non-cancelled submitted parent WO unless explicitly a planned/draft metric. Draft Job Card output is provisional; corrective work separate. |
| Document/status requirements | Parent WO.docstatus=0 only; Job Card.docstatus!=2. Planning metric, not recognized production. |
| Date and period behavior | Current job state; posting_date cohort, expected_end_date deadline and actual log intervals are distinct time bases. |
| Filters and unsupported dimensions | applicable: Company required on job and parent; exact native job/WO/operation_id/operation_row_id/Workstation; verified Project/Customer path. Source/WIP/target warehouse explicit. Current-user assignment required for shop. Shift unavailable.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Per job/operation/item+stock_uom, field/UOM precision. Sequential operation quantities never summed as finished goods. Time/percent display 2 decimals. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Production/owner native scope; supervisor/operator check_shop_job + native Company/WO/Workstation/Job read. Operator open ToDo allocated_to=current user; supervisor additionally explicit applicable Workstation User Permission. Never trust supplied operator identity. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Job Card / related WO operation; KPI read grants no action permission. |
| Validation source/scenario | V34 draft vs submitted parent. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### INV-001 — Stock valuation as of date

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-001 |
| Name | Stock valuation as of date |
| Dashboard(s) | Owner |
| Section | Inventory and materials |
| Business purpose | Use authoritative inventory carrying value. |
| Plain-language definition | Native Stock Balance closing value. |
| Exact formula/calculation | SUM(native Stock Balance.bal_val on eligible leaf item/warehouse rows), no totals repeated. Current Bin.stock_value is current control only, not historical valuation or latest purchase price. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Stock Ledger Entry: item_code, warehouse, posting_date, posting_time, stock_value, stock_value_difference, qty_after_transaction, actual_qty, is_cancelled; Bin: item_code, warehouse, stock_uom, actual_qty, stock_value, valuation_rate, projected_qty, reserved_stock; Item: name, stock_uom; Warehouse: name, company, is_group |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | stock_value_current_vs_report and stock_item_warehouse_balances; V40-V42 historical/reposting pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### INV-002 — Actual stock quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-002 |
| Name | Actual stock quantity |
| Dashboard(s) | Owner, Production |
| Section | Inventory and materials |
| Business purpose | Show recorded on-hand in the correct warehouse. |
| Plain-language definition | Quantity per item/warehouse/UOM. |
| Exact formula/calculation | Current=Bin.actual_qty; historical=native Stock Balance.bal_qty. Known permitted pair with complete source and no Bin=>0; missing source/access=>Unknown. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Stock Ledger Entry: item_code, warehouse, posting_date, posting_time, stock_value, stock_value_difference, qty_after_transaction, actual_qty, is_cancelled; Bin: item_code, warehouse, stock_uom, actual_qty, stock_value, valuation_rate, projected_qty, reserved_stock; Item: name, stock_uom; Warehouse: name, company, is_group |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | 14 exact item/warehouse pairs compared; V40-V42 historical/reservations pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### INV-003 — Outstanding physical reservations

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-003 |
| Name | Outstanding physical reservations |
| Dashboard(s) | Production |
| Section | Inventory and materials |
| Business purpose | Separate physical reservation from planning demand. |
| Plain-language definition | Native outstanding Stock Reservation Entry pool. |
| Exact formula/calculation | SUM(reserved_qty-delivered_qty-transferred_qty-consumed_qty) by item/warehouse under installed eligibility docstatus1 and delivered_qty<reserved_qty. Validate negative/inconsistent residuals; do not deduct both SRE and demand counters. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Stock Reservation Entry: docstatus, item_code, warehouse, reserved_qty, delivered_qty, transferred_qty, consumed_qty, voucher_type, voucher_no, voucher_detail_no; Bin: reserved_stock, reserved_qty, reserved_qty_for_production |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V43 competing WOs/partial transfer/consume/cancel/own reservation; no SRE rows. |
| Limitations | Bin.reserved_qty/reserved_qty_for_production are demand, not independent SRE allocations. Native availability helper uses FOR UPDATE; dashboard must not uncritically call a locking command helper. |
| Implementation status | not configured |

### INV-004 — Unreserved available stock

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-004 |
| Name | Unreserved available stock |
| Dashboard(s) | Production |
| Section | Inventory and materials |
| Business purpose | Avoid promising reserved stock twice. |
| Plain-language definition | Current eligible unreserved on-hand, not projected supply. |
| Exact formula/calculation | Simple non-batch/non-serial pool A=INV-002-INV-003; keep deficit warning. Own-job availability may add back its own outstanding reservation once. Serial/batch/expiry/WIP constraints or incomplete competing reservation visibility=>Unknown. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Bin: actual_qty, reserved_stock, item_code, warehouse; Stock Reservation Entry: item_code, warehouse, reserved_qty, delivered_qty, transferred_qty, consumed_qty |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V43 stock10,total reservation7=>free3; own4 inside total7=>own7, not11. Native allocation fixtures absent. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | blocked |

### INV-005 — Projected stock quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-005 |
| Name | Projected stock quantity |
| Dashboard(s) | Owner, Production |
| Section | Inventory and materials |
| Business purpose | Separate planning projection from immediately usable stock. |
| Plain-language definition | Native maintained Bin.projected_qty. |
| Exact formula/calculation | Read Bin.projected_qty per item/warehouse; native planning formula actual+ordered+indented+planned minus demand-reservation categories. Never subtract physical reserved_stock again without native basis. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Bin: item_code, warehouse, actual_qty, projected_qty, ordered_qty, indented_qty, planned_qty, reserved_qty, reserved_qty_for_production, reserved_qty_for_sub_contract, reserved_qty_for_production_plan |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V44 projected positive while free negative; native event lifecycle pending. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### INV-006 — Low-stock risk

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-006 |
| Name | Low-stock risk |
| Dashboard(s) | Owner, Production |
| Section | Inventory and materials |
| Business purpose | Use actual warehouse reorder settings. |
| Plain-language definition | Stock below configured warehouse reorder threshold. |
| Exact formula/calculation | Proposed Bin.projected_qty<matching Item Reorder.warehouse_reorder_level (<= only if approved), exact Warehouse/native warehouse_group expansion. No matching rule=>Not configured; show actual/free/projected separately. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Item Reorder: parent, warehouse, warehouse_group, warehouse_reorder_level, warehouse_reorder_qty; Bin: item_code, warehouse, actual_qty, projected_qty |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V44 per-warehouse/equality/no setting; Item Reorder0 rows. |
| Limitations | Approve projected-vs-free and equality policy. Existing Item.safety_stock/global pcs labelling is not canonical. |
| Implementation status | not configured |

### INV-007 — Outstanding material requirement

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-007 |
| Name | Outstanding material requirement |
| Dashboard(s) | Production |
| Section | Inventory and materials |
| Business purpose | Show material still needing supply in actual transfer mode. |
| Plain-language definition | Outstanding component demand, with returns and direct consumption distinguished. |
| Exact formula/calculation | Proposed normal transfer=max(required_qty-(transferred_qty-returned_qty),0). skip_transfer/direct consumption=max(required_qty-(consumed_qty-returned_qty),0), only after native counter/return reconciliation. Installed consumed_qty adds returned_qty; do not count returns twice. WIP available is separate from source need. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, docstatus, status, skip_transfer, wip_warehouse; Work Order Item: parent, item_code, stock_uom, required_qty, transferred_qty, consumed_qty, returned_qty, source_warehouse, include_item_in_manufacturing |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V45 required10,transfer10,return4=>resupply4; direct/alternative/additional items pending. |
| Limitations | Source fields verified, native lifecycle fixtures missing. Existing required-max(consumed,transferred) ignores returns and cannot certify readiness. |
| Implementation status | blocked |

### INV-008 — Potential material shortage quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-008 |
| Name | Potential material shortage quantity |
| Dashboard(s) | Owner, Production |
| Section | Inventory and materials |
| Business purpose | Expose shared stock-demand risk without false allocation. |
| Plain-language definition | Unallocated pool shortage at one item/source-warehouse/UOM. |
| Exact formula/calculation | For fully known pool max(SUM(INV-007 demand)-eligible shared stock,0), stock counted once. On-hand-only variant must be labelled Potential on-hand shortage, not complete readiness. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order Item: parent, item_code, source_warehouse, stock_uom, required_qty, transferred_qty, returned_qty, consumed_qty; Bin: item_code, warehouse, actual_qty, reserved_stock |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V43/V45 demands8+8,shared stock10=>pool short6, not two full allocations. |
| Limitations | Demand/mode/reservation inputs unresolved; never sum shortage across items/UOMs. Project demand subset does not own shared stock. |
| Implementation status | blocked |

### INV-009 — Material-ready / affected Work Orders

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-009 |
| Name | Material-ready / affected Work Orders |
| Dashboard(s) | Production |
| Section | Inventory and materials |
| Business purpose | Identify jobs that can actually proceed. |
| Plain-language definition | WO readiness after an approved complete material allocation. |
| Exact formula/calculation | Ready only when every required row has known shortage0 after warehouse/serial/batch/reservation/priority allocation. Affected count=distinct WOs with confirmed allocated shortage>0. Unknown inputs=>Unknown count, not Ready. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name, reserve_stock, status, docstatus; Work Order Item: parent, item_code, source_warehouse, stock_uom, required_qty, stock_reserved_qty |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V43/V45 competing jobs/mixed unknown rows; blocked. |
| Limitations | No approved allocation queue/priority or reservation fixture. Pool shortage alone cannot identify precisely which WO is blocked. |
| Implementation status | blocked |

### INV-010 — Excess inventory

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-010 |
| Name | Excess inventory |
| Dashboard(s) | Owner |
| Section | Inventory and materials |
| Business purpose | Avoid arbitrary excess-stock declarations. |
| Plain-language definition | Stock above approved max/coverage policy. |
| Exact formula/calculation | Unavailable until target/max stock, demand horizon and usable-quantity policy approved. Then max(usable_qty-approved_target_qty,0), item/warehouse/UOM; value uses native valuation. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Bin: item_code, warehouse, actual_qty, projected_qty, stock_value |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V46 slow-moving vs strategic stock; blocked. |
| Limitations | No verified maximum-stock/forecast coverage policy; no invented threshold. |
| Implementation status | blocked |

### INV-011 — Stock age / aging inventory

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-011 |
| Name | Stock age / aging inventory |
| Dashboard(s) | Owner |
| Section | Inventory and materials |
| Business purpose | Use actual stock layers for aging analysis. |
| Plain-language definition | Native Stock Ageing FIFO-layer age as of selected date. |
| Exact formula/calculation | Native Stock Ageing quantity/value/average_age by exact item/warehouse/as-of, preserving serial/batch/opening rules. Approved aging thresholds required; never Item.creation or last purchase alone. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Stock Ledger Entry: item_code, warehouse, posting_date, posting_time, actual_qty, stock_value_difference |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V47 receipts/issues/returns/opening layers; report exists, not run. |
| Limitations | FIFO analytical age may differ from financial valuation method. Approve bucket thresholds/opening-stock treatment. |
| Implementation status | proposed |

### INV-012 — Raw/WIP/finished inventory value mix

| Attribute | Definition |
| --- | --- |
| KPI ID | INV-012 |
| Name | Raw/WIP/finished inventory value mix |
| Dashboard(s) | Owner |
| Section | Inventory and materials |
| Business purpose | Explain working capital without guessed bucket percentages. |
| Plain-language definition | Native stock valuation partitioned by approved explicit classification. |
| Exact formula/calculation | Group INV-001 using approved item/warehouse classification. share%=100*bucket_value/total if total!=0 else null; include Unclassified. No warehouse-name substring guess or default50/30/20. |
| Numerator | Native bucket stock value. |
| Denominator | Same complete INV-001 value; signed deficits flagged. |
| ERPNext DocTypes / exact fields | Stock Ledger Entry: item_code, warehouse, posting_date, posting_time, stock_value, stock_value_difference, qty_after_transaction, actual_qty, is_cancelled; Bin: item_code, warehouse, stock_uom, actual_qty, stock_value, valuation_rate, projected_qty, reserved_stock; Item: name, stock_uom; Warehouse: name, company, is_group |
| Inclusion/exclusion rules | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Document/status requirements | Native non-cancelled stock ledger/submitted document eligibility. Material demand from eligible submitted WOs; reservation scope must be complete, not just visible own jobs. |
| Date and period behavior | Stock Balance as-of to_date for historical valuation/quantity. Bin/current WO/reservations are current-only; no historical reservation inference. |
| Filters and unsupported dimensions | applicable: Company via authorized Warehouse required; exact leaf warehouses or native group expansion; item/UOM and stock dimensions. General Customer/Project allocation unsupported for shared stock. Demand can be Project-filtered but stock remains explicitly shared.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Qty company+item+warehouse+stock_uom; native company-currency valuation, not latest purchase price. Do not sum unrelated units/items. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Warehouse/Item/Bin/SLE and linked document rights; money also finance. Partial reservation visibility => Unknown availability, not extra free stock. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Stock Balance / Stock Ledger same as-of, item, warehouse and dimensions; WO.required_items for demand. |
| Validation source/scenario | V48 unclassified/zero-stock cases; mapping unverified. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | blocked |

### QUAL-001 — Rejected inspections count

| Attribute | Definition |
| --- | --- |
| KPI ID | QUAL-001 |
| Name | Rejected inspections count |
| Dashboard(s) | Owner, Production |
| Section | Quality and rework |
| Business purpose | Count actual failed inspections, not imagined rejected units. |
| Plain-language definition | Submitted inspections with status Rejected. |
| Exact formula/calculation | COUNT(DISTINCT eligible Quality Inspection.name where status=Rejected). |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Quality Inspection: name, company, docstatus, status, report_date, sample_size, reference_type, reference_name, item_code |
| Inclusion/exclusion rules | Submitted QI.docstatus=1, status Accepted/Rejected; exclude drafts/cancelled and cancelled originals of amendments. |
| Document/status requirements | Submitted QI.docstatus=1, status Accepted/Rejected; exclude drafts/cancelled and cancelled originals of amendments. |
| Date and period behavior | Quality Inspection.report_date selected period; current status is not an historical event timeline. |
| Filters and unsupported dimensions | applicable: Company directly or verified reference; item/reference/inspection type; Customer/Project/Warehouse only explicit verified reference paths.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Inspection counts are not rejected-unit counts. Ratios per inspection; unit quantities require an actual compatible source. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native QI/reference rights, owner/production scope; shop only inspections linked to authorized assigned work. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Quality Inspection Summary / source inspection/reference. |
| Validation source/scenario | V49 draft rejection excluded; sample-size not rejected output. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### QUAL-002 — Inspection failure rate

| Attribute | Definition |
| --- | --- |
| KPI ID | QUAL-002 |
| Name | Inspection failure rate |
| Dashboard(s) | Owner, Production |
| Section | Quality and rework |
| Business purpose | Compare outcomes at inspection-document grain. |
| Plain-language definition | Rejected share of eligible completed inspections. |
| Exact formula/calculation | 100*QUAL-001/COUNT(eligible submitted Accepted or Rejected inspections); empty=>null. |
| Numerator | Rejected submitted inspection count. |
| Denominator | Submitted Accepted+Rejected count, identical scope. |
| ERPNext DocTypes / exact fields | Quality Inspection: name, company, docstatus, status, report_date, sample_size, reference_type, reference_name, item_code |
| Inclusion/exclusion rules | Submitted QI.docstatus=1, status Accepted/Rejected; exclude drafts/cancelled and cancelled originals of amendments. |
| Document/status requirements | Submitted QI.docstatus=1, status Accepted/Rejected; exclude drafts/cancelled and cancelled originals of amendments. |
| Date and period behavior | Quality Inspection.report_date selected period; current status is not an historical event timeline. |
| Filters and unsupported dimensions | applicable: Company directly or verified reference; item/reference/inspection type; Customer/Project/Warehouse only explicit verified reference paths.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Inspection counts are not rejected-unit counts. Ratios per inspection; unit quantities require an actual compatible source. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native QI/reference rights, owner/production scope; shop only inspections linked to authorized assigned work. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Quality Inspection Summary / source inspection/reference. |
| Validation source/scenario | V49 accepted3/rejected1=>25%; no unit rejection inferred. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### QUAL-003 — Supplier rejected receipt quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | QUAL-003 |
| Name | Supplier rejected receipt quantity |
| Dashboard(s) | Production |
| Section | Subcontracting |
| Business purpose | Distinguish supplier rejects from Job Card loss. |
| Plain-language definition | Recorded rejected_qty of submitted subcontract receipts. |
| Exact formula/calculation | SUM(signed Subcontracting Receipt Item.rejected_qty) per item+stock_uom on eligible receipts, native return/correction semantics. Not per-Job Card rejection. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Receipt: name, company, docstatus, posting_date, is_return; Subcontracting Receipt Item: parent, item_code, stock_uom, rejected_qty, qty, subcontracting_order |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Subcontracting Receipt.posting_date period, not order due date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V50 accepted/rejected/return; no receipt rows. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### WS-001 — Recorded workstation state

| Attribute | Definition |
| --- | --- |
| KPI ID | WS-001 |
| Name | Recorded workstation state |
| Dashboard(s) | Production |
| Section | Recorded workstation information |
| Business purpose | Show ERP-entered status honestly. |
| Plain-language definition | Native recorded Workstation.status and modified time. |
| Exact formula/calculation | Read exact Production/Off/Idle/Problem/Maintenance/Setup; independently show JOB-010 recorded running jobs. Neither proves physical machine runtime. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Workstation: name, status, modified |
| Inclusion/exclusion rules | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Document/status requirements | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Date and period behavior | Recorded Workstation.status/modified, or downtime from_time/to_time clipped to period. No telemetry observation timestamp exists. |
| Filters and unsupported dimensions | applicable: Workstation authorized through actual WO/Job links; no assumed Company field/physical plant mapping. Customer/Project downtime allocation unsupported without explicit links. Warehouse/Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Text state; recorded minutes, 2 decimals; utilization needs validated schedule/coverage denominator. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Workstation/Downtime Entry read; shop only its authorized workstation and assigned jobs. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Workstation / Downtime Entry / Downtime Analysis. |
| Validation source/scenario | V51 statusProduction with no open log must not claim measured running. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### WS-002 — Recorded downtime minutes

| Attribute | Definition |
| --- | --- |
| KPI ID | WS-002 |
| Name | Recorded downtime minutes |
| Dashboard(s) | Production |
| Section | Recorded workstation information |
| Business purpose | Show logged interruptions, not inferred idle time. |
| Plain-language definition | Closed valid downtime intervals clipped to period. |
| Exact formula/calculation | SUM(max(0,min(to_time,period_end)-max(from_time,period_start))) in minutes. Flag overlap/duplicates; machine elapsed downtime requires union per workstation, not overlapping record-minute sum. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Downtime Entry: name, workstation, from_time, to_time, downtime, stop_reason |
| Inclusion/exclusion rules | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Document/status requirements | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Date and period behavior | Recorded Workstation.status/modified, or downtime from_time/to_time clipped to period. No telemetry observation timestamp exists. |
| Filters and unsupported dimensions | applicable: Workstation authorized through actual WO/Job links; no assumed Company field/physical plant mapping. Customer/Project downtime allocation unsupported without explicit links. Warehouse/Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Text state; recorded minutes, 2 decimals; utilization needs validated schedule/coverage denominator. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Workstation/Downtime Entry read; shop only its authorized workstation and assigned jobs. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Workstation / Downtime Entry / Downtime Analysis. |
| Validation source/scenario | V52 overlap/midnight/open/invalid intervals; no rows. |
| Limitations | Manual record-time, not telemetry. Approve overlap, planned-break exclusion and elapsed-time interpretation. |
| Implementation status | not configured |

### WS-003 — Measured utilization / availability

| Attribute | Definition |
| --- | --- |
| KPI ID | WS-003 |
| Name | Measured utilization / availability |
| Dashboard(s) | Production |
| Section | Recorded workstation information |
| Business purpose | Prevent fabricated machine utilization. |
| Plain-language definition | Unavailable without reliable run/down observations and approved schedule. |
| Exact formula/calculation | Future utilization=100*union(measured run minutes)/approved available minutes; availability=100*(planned-unplanned downtime)/planned, same machine/time window. Missing coverage=>Unavailable. |
| Numerator | Validated measured runtime or planned-minus-downtime minutes. |
| Denominator | Approved available schedule minutes with measurement coverage. |
| ERPNext DocTypes / exact fields | Workstation: name, working_hours; Downtime Entry: workstation, from_time, to_time |
| Inclusion/exclusion rules | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Document/status requirements | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Date and period behavior | Recorded Workstation.status/modified, or downtime from_time/to_time clipped to period. No telemetry observation timestamp exists. |
| Filters and unsupported dimensions | applicable: Workstation authorized through actual WO/Job links; no assumed Company field/physical plant mapping. Customer/Project downtime allocation unsupported without explicit links. Warehouse/Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Text state; recorded minutes, 2 decimals; utilization needs validated schedule/coverage denominator. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Workstation/Downtime Entry read; shop only its authorized workstation and assigned jobs. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Workstation / Downtime Entry / Downtime Analysis. |
| Validation source/scenario | V53 breaks/overlap/zero schedule/no telemetry; blocked. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | blocked |

### WS-004 — OEE

| Attribute | Definition |
| --- | --- |
| KPI ID | WS-004 |
| Name | OEE |
| Dashboard(s) | Production |
| Section | Recorded workstation information |
| Business purpose | Keep unsupported advanced intelligence out of core metrics. |
| Plain-language definition | No validated availability/performance/quality telemetry dataset. |
| Exact formula/calculation | Future OEE=Availability*Performance*Quality as fractions. Performance=ideal_cycle_time*total_count/runtime; Quality=good_count/total_count. Any component unavailable=>Unavailable. |
| Numerator | Three independently validated component fractions. |
| Denominator | Declared denominator for each component; no Job Card count substitute. |
| ERPNext DocTypes / exact fields | Workstation: name |
| Inclusion/exclusion rules | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Document/status requirements | Native Workstation records; downtime closed valid intervals only. No assumed Submitted state for non-submittable records. |
| Date and period behavior | Recorded Workstation.status/modified, or downtime from_time/to_time clipped to period. No telemetry observation timestamp exists. |
| Filters and unsupported dimensions | applicable: Workstation authorized through actual WO/Job links; no assumed Company field/physical plant mapping. Customer/Project downtime allocation unsupported without explicit links. Warehouse/Shift unsupported.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Text state; recorded minutes, 2 decimals; utilization needs validated schedule/coverage denominator. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native Workstation/Downtime Entry read; shop only its authorized workstation and assigned jobs. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Workstation / Downtime Entry / Downtime Analysis. |
| Validation source/scenario | V53 ideal cycle/good-reject counts/schedule; blocked. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### SUB-001 — Active subcontract orders

| Attribute | Definition |
| --- | --- |
| KPI ID | SUB-001 |
| Name | Active subcontract orders |
| Dashboard(s) | Production |
| Section | Subcontracting |
| Business purpose | Coordinate outsourced commitments. |
| Plain-language definition | Distinct native submitted active orders. |
| Exact formula/calculation | COUNT(DISTINCT eligible Subcontracting Order.name) in active native status set. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order: name, company, status, docstatus, supplier |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Current order/receipt state; due uses item schedule_date or explicitly agreed expected_delivery_date; receipt outcomes use posting_date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V54 draft/open/transferred/partial/completed/cancelled; no orders. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### SUB-002 — Overdue subcontract lines / orders

| Attribute | Definition |
| --- | --- |
| KPI ID | SUB-002 |
| Name | Overdue subcontract lines / orders |
| Dashboard(s) | Production |
| Section | Subcontracting |
| Business purpose | Locate exact late supplier item commitments. |
| Plain-language definition | Positive remaining line receipt quantity past known line due date. |
| Exact formula/calculation | Line remaining=max(qty-received_qty,0) with verified net-return semantics; overdue lines=count distinct line names with remaining>0 AND schedule_date<today; affected orders=count distinct parents separately. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order: name, docstatus, status, company; Subcontracting Order Item: name, parent, qty, received_qty, returned_qty, schedule_date, expected_delivery_date, item_code, stock_uom |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Current order/receipt state; due uses item schedule_date or explicitly agreed expected_delivery_date; receipt outcomes use posting_date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V54 different line deadlines/partial receipt/returns; none configured. |
| Limitations | Existing code uses header schedule_date; native child schedule_date required. Native receipt/return counter semantics need fixture. |
| Implementation status | not configured |

### SUB-003 — Subcontract quantity still to receive

| Attribute | Definition |
| --- | --- |
| KPI ID | SUB-003 |
| Name | Subcontract quantity still to receive |
| Dashboard(s) | Production |
| Section | Subcontracting |
| Business purpose | Show outsourced output remainder per item. |
| Plain-language definition | Remaining native receipt quantity. |
| Exact formula/calculation | max(qty-received_qty,0) per eligible order item, native net receipt basis. If returns separate, reconcile signed receipt history before adding returned_qty. Group item+stock_uom, not services+outputs. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order Item: name, parent, item_code, stock_uom, qty, received_qty, returned_qty |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Current order/receipt state; due uses item schedule_date or explicitly agreed expected_delivery_date; receipt outcomes use posting_date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V54 partial receipt/return/replacement; no native fixture. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### SUB-004 — Material at supplier quantity

| Attribute | Definition |
| --- | --- |
| KPI ID | SUB-004 |
| Name | Material at supplier quantity |
| Dashboard(s) | Production |
| Section | Subcontracting |
| Business purpose | Track raw material not consumed or returned. |
| Plain-language definition | Net supplied materials by item/UOM/supplier warehouse. |
| Exact formula/calculation | Per distinct supplied-item row max(total_supplied_qty-consumed_qty-returned_qty,0), authoritative counters verified first; negative residual flags inconsistency. Never add supplied_qty and total_supplied_qty. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order Supplied Item: name, parent, rm_item_code, stock_uom, total_supplied_qty, consumed_qty, returned_qty; Subcontracting Order: name, company, supplier, supplier_warehouse, docstatus |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Current order/receipt state; due uses item schedule_date or explicitly agreed expected_delivery_date; receipt outcomes use posting_date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V55 supply/consume/return; no orders. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### SUB-005 — Supplier-held material value

| Attribute | Definition |
| --- | --- |
| KPI ID | SUB-005 |
| Name | Supplier-held material value |
| Dashboard(s) | Owner |
| Section | Subcontracting |
| Business purpose | Separate official carrying stock from an order-rate estimate. |
| Plain-language definition | Native stock valuation in mapped supplier warehouses. |
| Exact formula/calculation | SUM(native Stock Balance.bal_val for explicitly mapped supplier warehouses); SUB-004*order rate is only a separate labelled estimate, not certified inventory carrying value. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order: name, supplier, supplier_warehouse, company; Stock Ledger Entry: warehouse, item_code, stock_value_difference |
| Inclusion/exclusion rules | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Document/status requirements | Submitted active Subcontracting Order: Open/Partially Received/Material Transferred/Partial Material Transferred; exclude Completed/Closed/Cancelled/Draft. Receipts submitted; signed returns. |
| Date and period behavior | Current order/receipt state; due uses item schedule_date or explicitly agreed expected_delivery_date; receipt outcomes use posting_date. |
| Filters and unsupported dimensions | applicable: Company; Supplier; explicit child Project/customer path; verified supplier/receipt Warehouse; item+stock_uom. Distinguish service items from manufactured output.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Group supplier+item+stock_uom+warehouse; native company currency for value, never sum services and outputs. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Native order/receipt/children/Supplier/Warehouse; finance for money. No factory list for operator. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Subcontracting Order/Receipt native lists/forms; no installed Subcontracting Order Summary report. |
| Validation source/scenario | V55 supplier warehouse valuation vs rate estimate; no records. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | not configured |

### ALERT-001 — Overdue customer invoice

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-001 |
| Name | Overdue customer invoice |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from AR-003. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Sales Invoice: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate AR-003 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | proposed |

### ALERT-002 — Delayed Work Order

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-002 |
| Name | Delayed Work Order |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from MFG-008. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate MFG-008 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | proposed |

### ALERT-003 — Confirmed material blocker

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-003 |
| Name | Confirmed material blocker |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from INV-009. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Work Order: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate INV-009 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | blocked |

### ALERT-004 — Project delivery risk

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-004 |
| Name | Project delivery risk |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from PROJ-005. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate PROJ-005 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | blocked |

### ALERT-005 — Pending approval for current user

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-005 |
| Name | Pending approval for current user |
| Dashboard(s) | Owner |
| Section | Exceptions and management decisions |
| Business purpose | Show only native decisions this user can take. |
| Plain-language definition | Open native Workflow Actions with a current eligible transition for authenticated user. |
| Exact formula/calculation | Count distinct reference_doctype+reference_name+workflow_state after Workflow Action/native reference permissions, permitted-role intersection, active state/conditions and self-approval checks. Workflow Action.user is not assumed an assignee; multiple permitted roles count once. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Workflow Action: name, status, reference_doctype, reference_name, workflow_state, permitted_roles, user; Workflow Action Permitted Role: parent, role; Workflow: name, is_active, document_type |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V57 two roles/denied reference/self-approval/completed action; no active workflow/actions. |
| Limitations | Notification recipients from get_users_next_action_data differ from approval eligibility; ToDo ownership is not approval. All actions remain native workflow, no KPI approval command. |
| Implementation status | not configured |

### ALERT-006 — Rejected inspection

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-006 |
| Name | Rejected inspection |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from QUAL-001. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Quality Inspection: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate QUAL-001 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | proposed |

### ALERT-007 — Delayed subcontract delivery

| Attribute | Definition |
| --- | --- |
| KPI ID | ALERT-007 |
| Name | Delayed subcontract delivery |
| Dashboard(s) | Owner, Production |
| Section | Exceptions and management decisions |
| Business purpose | Route a supported exception to a concrete authorized record. |
| Plain-language definition | Exact trigger inherited from SUB-002. |
| Exact formula/calculation | Generate one unresolved alert per inherited trigger/dedup key; proposed severity High (configurable, needs approval). Count distinct keys; resolve on predicate clear; child/item/warehouse key for material issues. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Subcontracting Order: name |
| Inclusion/exclusion rules | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Document/status requirements | Inherit referenced metric source eligibility. Resolve when trigger clears; deduplicate Company+type+doctype+name (+child/item/warehouse where needed). |
| Date and period behavior | Trigger as-of/generated_at with inherited source cutoff. Historical cutoff must not masquerade as now. |
| Filters and unsupported dimensions | applicable: Authorized affected Company/Customer/Project/Warehouse links; current user only for approvals; source ID, trigger and severity.; unsupported: Reject unsupported filter combinations or explicitly mark unavailable per KPI; never silently imply the filter applied.; shift: Unsupported: Shift Type absent and no job/shift mapping verified. |
| Currency/UOM/rounding | Distinct issue keys; money only under the referenced financial permission; not a sum of overlapping issue quantities. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Same native record/metric rights as trigger; approval requires current-user native workflow transition eligibility. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized affected source form/report preserving filters. |
| Validation source/scenario | V56 duplicate refresh/resolution/permission denial; validate SUB-002 first. |
| Limitations | No persistence/notification/new workflow implemented. Money only when source financial permissions permit. |
| Implementation status | proposed |

### CAT-001 — Projects catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-001 |
| Name | Projects catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Project.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Project: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-002 — Items catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-002 |
| Name | Items catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Item.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Item: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-003 — Warehouse stock rows catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-003 |
| Name | Warehouse stock rows catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Bin.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Bin: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-004 — Warehouses catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-004 |
| Name | Warehouses catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Warehouse.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Warehouse: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-005 — Workstations catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-005 |
| Name | Workstations catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Workstation.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Workstation: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-006 — Operation masters catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-006 |
| Name | Operation masters catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Operation.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Operation: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-007 — Workstation types catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-007 |
| Name | Workstation types catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Workstation Type.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Workstation Type: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-008 — Routings catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-008 |
| Name | Routings catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Routing.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Routing: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-009 — Active BOMs catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-009 |
| Name | Active BOMs catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT BOM.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | BOM: name, docstatus, is_active |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-010 — Customers catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-010 |
| Name | Customers catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Customer.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Customer: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

### CAT-011 — Suppliers catalogue count

| Attribute | Definition |
| --- | --- |
| KPI ID | CAT-011 |
| Name | Suppliers catalogue count |
| Dashboard(s) | Owner, Production |
| Section | Existing navigation counters |
| Business purpose | Make existing navigation counters auditable, not throughput KPIs. |
| Plain-language definition | Unique permitted records in corresponding current catalogue. |
| Exact formula/calculation | COUNT(DISTINCT Supplier.name) in declared native scope; BOM additionally docstatus1/is_active1. Bin means item/warehouse rows, not units/value. Project catalogue limits to verified linked IDs, union/deduplicated. |
| Numerator | Not a ratio. |
| Denominator | Not a ratio. |
| ERPNext DocTypes / exact fields | Supplier: name |
| Inclusion/exclusion rules | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Document/status requirements | Project.docstatus<2, exact native Open/On hold/Completed/Cancelled statuses. Open deadline metrics exclude terminal records; held subset disclosed. |
| Date and period behavior | Current catalogue. Project.creation cohort only for Projects, not historical linked masters. |
| Filters and unsupported dimensions | company: Only source Company field or verified linkage; no assumed Company on Customer/Item/Routing.; customer: Only explicit authorized Project/job/order relationships.; project: Existing get_project_resource_ids actual relationship closure, union/deduplicate IDs.; warehouse: Direct for Bin/Warehouse; others verified linkage only.; other: Native source rights; active/disabled flags disclosed. |
| Currency/UOM/rounding | Integer distinct count, not currency/production quantity. |
| Missing/empty/zero handling | Measured empty permitted cohort => count/sum0. Missing source/permission/field/date => null with reason. Ratio denominator0 => null/N/A. Query errors never become0. |
| Required permissions | Owner/production plus native Project/Task/Customer; shop users only related authorized job context. |
| Refresh and freshness | Existing owner/production active-visible poll15s plus after-commit invalidation. Contract: generated_at, source_as_of, applied filters, coverage and availability. Shop-floor refresh not implemented; stale errors retain only explicitly labelled old data. |
| Drill-down | Authorized Project, Tasks and related Work Orders. |
| Validation source/scenario | V58 restricted records/duplicate links/empty Project; inventory of existing APIs, no new count code. |
| Limitations | Specified contract, not certified dashboard implementation; see discrepancy register. |
| Implementation status | proposed |

## Actual validation against the installed ERPNext site

Read-only Administrator audit, one company anonymized as C1, company currency INR, P&L/invoice period 2026-04-01 through 2026-10-13. AR/AP/SLE cutoff uses the same as-of date without dropping earlier balances. All12 source/report comparisons passed within0.01 base-currency units (counts exact). These are source controls, not dashboard API reconciliation or cross-role certification. Customer/project filters, multiple currencies and historical allocation/reposting remain unverified.

| Check / KPI IDs | Source control expected | Native report actual | Difference | Records | Result / limit |
| --- | --- | --- | --- | --- | --- |
| invoice_net_vs_sales_register / FIN-001, SALES-001, SALES-002, SALES-003 | 17699999.5 | 17699999.5 | 0.0 | 2 | verified; External net invoiced sales, not P&L total income. No submitted return or foreign-currency fixture exists on this site. |
| pnl_income_vs_gl / FIN-002 | 17699999.5 | 17699999.5 | 0.0 | 73 | verified;  |
| pnl_expense_vs_gl / FIN-003 | -31995000.5 | -31995000.5 | 0.0 | 73 | verified;  |
| pnl_profit_vs_gl / FIN-004, FIN-005 | 49695000.0 | 49695000.0 | 0.0 | 73 | verified; Default finance book, non-consolidated company currency; alternative books/dimensions and fiscal-year boundaries not exercised. |
| ar_current_snapshot / AR-001 | 4200000.5 | 4200000.5 | 0.0 | 2 | verified; Invoice-voucher subset at current audit date only. Historical allocations, advances and Journal Entry balances are not reconciled by this comparison. |
| ar_net_vs_payment_ledger / AR-001 | -3559999.5 | -3559999.5 | 0.0 | 8 | verified; Current base-currency all-party balance only. Historical delinking/reallocation and party/finance-book filters require separate report fixtures. |
| ap_current_snapshot / AP-001 | 638793.0 | 638793.0 | 0.0 | 8 | verified; Invoice-voucher subset at current audit date only. Historical allocations, advances and Journal Entry balances are not reconciled by this comparison. |
| ap_net_vs_payment_ledger / AP-001 | 638793.0 | 638793.0 | 0.0 | 8 | verified; Current base-currency all-party balance only. Historical delinking/reallocation and party/finance-book filters require separate report fixtures. |
| stock_value_current_vs_report / INV-001 | 32536350.0 | 32536350.0 | 0.0 | 14 | verified; Current snapshot only, no stock-closing/repost/foreign-company or historical valuation fixture. A difference must be investigated, never replaced with purchase-price valuation. |
| stock_item_warehouse_balances / INV-001, INV-002 | 0.0 | 0.0 | 0.0 | 14 | verified; Counts mismatched item/warehouse pairs; missing zero-balance rows treated as zero. |
| work_order_qty_vs_report / MFG-001, MFG-002 | 233.0 | 233.0 | 0.0 | 6 | verified; Source-to-report total check only: quantities must be split by item/UOM in dashboard output, never expose this cross-item audit checksum as a KPI. |
| work_order_produced_vs_report / MFG-002 | 130.0 | 130.0 | 0.0 | 6 | verified; Same exact submitted IDs and creation-date cohort; group dashboard quantities by item/UOM. |

The WO planned/produced totals above are **audit checksums across exact IDs**, not displayable mixed-item KPIs. Native Work Order Summary defaults include drafts and apply creation/planned/actual date and age filters. The control deliberately supplied Creation Date1900-01-01 through audit date, age=-100000, then retained only matching submitted IDs to compare the same current source cohort. An initial comparison without its required dates returned no rows; correcting the validation scope made the comparison match. That is not a dashboard or native-report code change.

Native item cohorts (names anonymized, no aggregation across items):

| Item group | UOM | Planned | Produced | Achievement |
| --- | --- | --- | --- | --- |
| item_group_1 | Nos | 68.0 | 17.0 | 25.000000% |
| item_group_2 | Nos | 135.0 | 85.0 | 62.962963% |
| item_group_3 | Nos | 20.0 | 18.0 | 90.000000% |
| item_group_4 | Nos | 10.0 | 10.0 | 100.000000% |

AR all-voucher net balance=-3559999.5, while the matching invoice-only positive balance=4200000.5. The difference is eligible non-invoice/credit balances, not a rounding adjustment. AP all-voucher balance=638793.0. Net margin from native P&L components=280.7627197955571%; negative net expense is preserved and flagged for finance review. Report agreement does not validate the business postings themselves.

### Scenario catalogue: expected behavior, not unrun native-test claims

Only the explicit comparisons above executed against native records. The scenarios below are precise acceptance fixtures for later implementation; numeric examples are expected arithmetic, **not** newly posted ERPNext transactions or claims of native lifecycle coverage.

| Scenario | Required fixture | Expected result | Native execution |
| --- | --- | --- | --- |
| V01 | Tax/return sales | Net100+credit note-20=>80 net sales; taxes excluded; signed return not subtracted twice. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V02 | Document states/amendment | Submitted100,draft50,cancelled70=>100; cancelled original excluded, submitted replacement once. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V03 | Invoice/project fan-out | Invoice lines60/40 on A/B: customer100,A60,B40, not200 after join. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V04 | Dates/trends | Posting Jan31 remains January even if creation Feb1; explicit comparable windows and partial-month label. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V05 | P&L accrual | Income100,expense60,expense JE10=>profit30 regardless purchase-invoice-only total. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V06 | Opening/closing/finance book | Same native report flags/books; no closing entry doubles P&L; fiscal-year boundary tested. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V07 | Zero/negative ratios | Income0=>null margin; prior0=>null change%; over100 and negative values retained with warning. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V08 | Gross Profit | Selling100,native buying60=>gross40; cost missing=>Unknown, not expense70%. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V09 | Cash book | Opening50+receipts20-payments10=>60; bank-statement unreconciled items separate. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V10 | Budget | Approved100,actual120=>120% used; missing budget=>Unavailable, not expense*1.35. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V11 | Procurement encumbrance | Partial PO/receipt/invoice must not double-count GRNI in actuals+commitments; blocked policy. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V12 | Customer profitability | Unallocated overhead remains unallocated; no invented proportional customer profit. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V13 | AR credits/advances | Positive invoices100 and eligible credit-30=>gross100,credits-30,net70. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V14 | Due-date boundaries | Due today not overdue; overdue1day eligible positive residual only; missing due separate. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V15 | Historical allocations | Payment after cutoff cannot reduce earlier outstanding; delinking/reallocation and currencies tested. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V16 | Order states/partial fulfillment | Qty10,delivered4=>remaining6; closed/cancelled excluded, held separately. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V17 | Backlog pricing | Remaining6*base_net_rate10=>60, excluding tax; heterogeneous line rates not header percentage. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V18 | Collections | Invoice100,allocated receipt40,unallocated advance10: collection allocation40,advance10 separate. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V19 | Project methods | Use installed controller Manual/Task Completion/Task Progress/Task Weight; task cancelled handling native. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V20 | Project deadlines/states | Missing date Unknown, due-today not overdue; Completed/Cancelled excluded, held separately. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V21 | Delivery-risk policy | Multiple commitments and one critical blocker require approved mapping/horizon/severity. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V22 | Project production completeness | No WO is not Finished; missing expected operation rows is Unknown, not all([])=complete. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V23 | Planned cohort | WO started before selected period does not become new target; missing start not creation fallback. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V24 | Partial/overproduction | Plan10,produced6=>achievement60%,variance-4; produced12=>120%,variance+2. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V25 | UOM/item grain | 10kg and5Nos never total15; two different Nos items remain separate; invalid conversion Unknown. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V26 | Manufacture flow | Manufacture FG movements count once; transfer-only/cancelled excluded, returns/disassembly explicit. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V27 | WO states | Only submitted active native statuses; completion rate1of2=>50%; drafts/stopped/closed not active. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V28 | Datetime deadlines | Overdue1minute, due-now and H boundary distinct; missing planned end Unknown. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V29 | Loss vs good output | Plan10,good8,loss2=>good remainder2,processing0,good achievement80%. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V30 | Operation grouping | Split/corrective Job Cards do not multiply one routing operation; semi-FG plan/UOM verified. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V31 | Bottleneck proxy | Rank late jobs by elapsed delay; no unsupported machine capacity prediction. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V32 | Rework | Original+two corrective jobs=>2 corrective jobs, not3 finished outputs or rejected units. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V33 | Job output counters | Read one job target/completed; do not add employee logs again to total_completed_qty. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V34 | Job states/parent eligibility | Draft parent planned only; active submitted parent executable; Submitted != Completed. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V35 | Time logs | Clip midnight intervals; two concurrent employee logs are labour-minutes; open log not finalized. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V36 | Rejected units | Rejected inspection sample1 does not imply planned batch rejected; process_loss not rejection. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V37 | Assignment | Other user's job denied; supervisor explicit scope only; closed ToDo excluded; empty assignments[]/0. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V38 | Waiting/blocker | No start evidence plus unknown materials is Not started/readiness unknown, not Ready/Blocked. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V39 | Issue mapping | Linked open issue counted once; private/resolved excluded; remarks not an issue registry. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V40 | Stock as of | Current Bin cannot answer earlier dates; native stock closing/reposting semantics tested. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V41 | Warehouse scope | Same item at warehouse A/B counted only in authorized selected pool; no global stock reuse. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V42 | Valuation | Qty*latest purchase price not carrying value; zero-qty valuation adjustments/native report respected. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V43 | Reservations | Stock10,reserved7=>free3; own4 within total7=>own available7, not11; shared demands8+8=>pool short6. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V44 | Reorder/projected | Warehouse-specific configured threshold, equality rule approved; no rule Not configured. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V45 | Material return/mode | Required10,transferred10,returned4=>resupply4 in transfer mode; direct-consumption/backflush fixtures separate. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V46 | Excess | Strategic safety stock not excess until maximum/coverage policy approved. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V47 | Stock age | Receipt/issue FIFO layers, opening stock and return age; Item.creation is not age. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V48 | Inventory mix | Unclassified bucket preserved; total0=>null shares, not50/30/20. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V49 | Inspection rate | Submitted Accepted3,Rejected1=>25%; draft rejected excluded; sample_size not rejected units. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V50 | Supplier rejects | Receipt rejected_qty distinct from accepted qty/process loss; return correction verified. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V51 | Recorded workstation state | Production status/no open log is not measured machine running. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V52 | Downtime | Overlapping closed logs flag duplicates; elapsed machine time unions intervals; open/invalid Unknown. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V53 | Utilization/OEE | No schedule/telemetry/cycle/good-reject coverage=>Unavailable; zero denominator not0% health. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V54 | Subcontract deadlines | Partial item receipts with different line due dates; affected order distinct from late line count. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V55 | Supplier material | Supplied10,consumed3,returned2=>quantity5; authoritative value from supplier-warehouse stock ledger. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V56 | Alert idempotence | Repeated refresh same unresolved key=>one alert; resolved trigger disappears; unauthorized record omitted. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V57 | Approvals | Two eligible roles=>one reference/state; native conditions/self-approval/reference permission enforced. | Not run as a new lifecycle fixture; see limited source comparisons above |
| V58 | Catalogue counts | Duplicate relationship links count one permitted master; no linked records=>0, not company-wide masters. | Not run as a new lifecycle fixture; see limited source comparisons above |

## Business decisions and handoff

- Confirm FIN-001 headline label/accounting basis and retain a distinct P&L Income measure for net margin. Approve finance-book/dimension/presentation-currency policy.
- Approve AR gross/net/credit presentation, aging bands and overdue thresholds; historical/multicurrency allocation fixtures remain required.
- Approve planned-start cohort versus time-phased target and posted-period output. Define treatment of stopped/closed commitments and alternative finished goods. No mixed-item scalar achievement without approved normalization.
- Approve due-soon horizon (proposed7days), risk severity and delivery-to-production mapping. No invented forecast or critical path.
- Validate transfer/direct-consumption/return/reservation and shared-stock allocation policy before claiming material readiness. Approve warehouse reorder basis/equality, excess/age thresholds and raw/WIP/FG classification.
- Approve native budget overlap/distribution and procurement encumbrance model; current Budget schema needs correction in later finance code.
- Configure real operator assignment, Employee/time logs and issue/rejection linkage before shop-floor metrics. Do not create transactions/workflows for the sake of a KPI.
- Telemetry, OEE/capacity optimization and predictive analysis remain unsupported later enhancements.

## Changed files and validation commands

Only these files belong to DASH-004:

- docs/dashboard-kpi-dictionary.md — this expanded contract, discrepancy register and handoff.
- docs/dashboard-kpi-dictionary.json —108 structured, explicit definitions.
- docs/dashboard-kpi-validation.json — actual read-only native comparisons and installed schema evidence.
- sarathi_visibility/sarathi_visibility/tests/test_kpi_sources.py — read-only native report/source collector, not a whitelisted API.
- sarathi_visibility/sarathi_visibility/tests/test_kpi_dictionary.py — definition/evidence completeness checks.

Native collection command (inside an initialized administrator bench console, not a production API):

    from sarathi_visibility.tests.test_kpi_sources import collect, describe_sources
    result = collect(company=<authorized_company>, from_date='2026-04-01', to_date='2026-10-13')

The executed local harness streamed these calls into Docker backend's bench Python with frappe.init('frontend'), connect(), set_user('Administrator'), then finally rollback()/destroy(). Company default selection was audit-only (most submitted invoice data), not a dashboard tenant default. The final collector also passed all declared source fields to describe_sources. No fixtures, business writes, migrations, permission changes or core patches were performed. Native report deprecation warnings were retained in local audit logs; no dependency changes made.

Definition checks: python -m unittest discover -s sarathi_visibility/sarathi_visibility/tests -p test_kpi_dictionary.py -v. Static checks: python -m ruff check --select F401,F821 on the two new validation modules; Python AST parse; git diff --check; pre-task hash comparison to prove earlier work/core unchanged. Actual final results are recorded in the completion evidence below.

Recommended next task: **DASH-005 — Build shared responsive UI components**. Formula implementation/corrections belong to subsequent KPI/API/finance tasks (especially DASH-006/DASH-009), not this definition task. No subsequent backlog task was started.

### Completion evidence

- Native collector rerun against the installed Docker site: **12/12 source/report comparisons verified**, all declared source fields present. This validates the explicitly listed scope only, not every proposed metric or lifecycle scenario.
- Definition/evidence unittest command above: **7 tests passed**, no skips, final run0.041s.
- Ruff F401/F821 checks and AST parsing on both new Python modules passed; git diff --check passed (existing CRLF conversion notices only).
- Pre-task hashes of6,339 existing files matched after this task: **no existing file changed or removed**; exactly the five listed deliverables were created. Core source and earlier dashboard/security/UI/Docker work are unchanged.
- No dependencies, production business transactions, database configuration, roles, workflows, native schema or VPS deployment changed. Later tasks must implement/reconcile proposed formulas and configure missing sources before display approval.
