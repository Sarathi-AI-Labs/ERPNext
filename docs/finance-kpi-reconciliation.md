# DASH-009 — Finance KPIs and reconciliation

## Audit and decisions before implementation

Reviewed DASH-001–008, installed ERPNext 16.33.0 / Frappe 16.31.0 accounting report source, current permissions/APIs and KPI dictionary. Existing dirty work is preserved using `scratch/dash-009/baseline.json`. Core source and accounting configuration remain read-only.

| Existing component | Decision |
| --- | --- |
| Owner homepage and shared KPI/state components | Integrate finance without a redesign |
| DASH-006 validation/company resolution and DASH-003 capabilities | Reuse; native report scripts need a stricter complete-scope gate |
| Legacy invoice/GL finance aggregates | Do not reuse shortcuts or silently replace the existing APIs |
| Native Profit and Loss Statement | Reuse its income/expense/net-profit summaries for FIN-002–005 |
| Native Gross Profit, Invoice grouping | Reuse its authoritative Total row once; do not sum parents and items |
| Native Accounts Receivable/Payable | Reuse signed voucher outstanding rows, including credits/advances and historical allocation logic |

Definition discrepancy: DASH-004 labels FIN-001 as proposed invoice net sales and FIN-002 as P&L income, with business headline approval still outstanding. DASH-009 explicitly requests recognized accounting revenue; implement the clearly labelled FIN-002 **Accounting income (P&L)**, not a claim that FIN-001 equals it. FIN-006/007's detailed dictionary contains copied P&L date/inclusion text inconsistent with its native Gross Profit source. Follow the installed Gross Profit invoice-posting and valuation-cost logic, document this discrepancy, and keep it distinct from net profit. Negative gross-margin denominators must follow the dictionary's signed arithmetic rather than silently adopting the native displayed absolute-denominator percentage.

No financial figures or reconciliation status will be fabricated. Executed comparisons, scope limits and exact changed files are recorded below after validation.

## Implemented metric contract

| KPI | Calculation / native source | Time basis |
| --- | --- | --- |
| FIN-002 Accounting income | Profit and Loss Statement income summary | Inclusive posting-date period |
| FIN-003 Accounting expense | Profit and Loss Statement expense summary | Inclusive posting-date period |
| FIN-004 Net profit / loss | Native P&L net-profit summary | Inclusive posting-date period |
| FIN-005 Net margin | 100 × native net profit / accounting income | Same period; undefined for zero income |
| FIN-006 Gross profit | Gross Profit report, Invoice grouping, authoritative Total row | Invoice posting-date period and native cost logic |
| FIN-007 Gross margin | 100 × gross profit / native selling amount | Same period; undefined for zero selling amount |
| AR-001 Net receivables including credits | Sum native Accounts Receivable voucher outstanding, Customer party type | Historical balance as of selected date |
| AP-001 Net supplier payables | Sum native Accounts Payable voucher outstanding, Supplier party type | Historical balance as of selected date |

Amounts use company currency and native recorded exchange rates. Revenue excludes invoice taxes through the accounting report; Sales Orders are not recognized income. Neither purchase-invoice subtraction nor an invented inventory-cost estimate replaces native report logic. Signed credits and advances remain signed. Margins can be negative or exceed 100%. Native Gross Profit's displayed percentage uses an absolute denominator; our signed formula intentionally differs when selling amount is negative.

Default financial dates are the company's configured fiscal-year start through the site's current date; `as_of_date` defaults to the period end. The UI labels accounting period and balance cutoff separately from operational schedule dates. Missing fiscal-year coverage produces unavailable period metrics. Unsupported filters, missing access and undefined ratios produce `null`/N/A with reasons, never fabricated zeroes. Accounting configuration is not changed.

| Filter | P&L metrics | Gross metrics | Receivables | Payables |
| --- | --- | --- | --- | --- |
| Authorized Company | Supported | Supported | Supported | Supported |
| From/to dates | Posting period | Invoice period | Uses separate as-of date | Uses separate as-of date |
| Customer | Unavailable | Unavailable | Supported | Unavailable |
| Project / Cost Center / Finance Book | Native P&L filters | Unavailable | Unavailable | Unavailable |

Unknown fields, injected user identity, invalid dates and inconsistent linked company/customer/project values are rejected. Native report filters accompany each metric and its drill-down. Financial refresh runs server calculations; it does not claim live machine data or use a shared cross-user financial cache.

## Permission boundary

The GET-only endpoint requires both owner-dashboard and finance capabilities, authorized Company access, native Report access and underlying DocType report/read permissions. Required source fields must be readable. Because native accounting scripts aggregate without applying ordinary list predicates throughout, these calls additionally require complete readable financial scope: record-limited users, non-Company User Permissions, owner-only/share-only access and relevant custom permission hooks fail closed. This conservative restriction can make finance unavailable to otherwise partially authorized users; it must not be weakened into unrestricted aggregation.

After these checks, execution uses the installed standard Accounts report module executor. It avoids the native script executor's prepared-report timer, which can persist configuration during a read. No core patch, controller override, raw transaction write or prepared-result cache is introduced. Unexpected failures are sanitized; operational homepage sections remain available when finance cannot be shown.

## Executed validation and reconciliation

Installed versions audited: ERPNext 16.33.0 and Frappe 16.31.0. The saved comparisons cover Company **SarathiAILabs**, INR, with cutoff **2026-10-13**. These are dated evidence, not a claim that today's books have independently been approved.

| Fiscal year to date: 2026-04-01 to 2026-10-13 | Dashboard and native reference |
| --- | ---: |
| Accounting income | INR 17,699,999.50 |
| Accounting expense | INR -31,995,000.50 |
| Net profit | INR 49,695,000.00 |
| Net margin | 280.76% |
| Gross profit | INR -20,000.50 |
| Gross margin | -0.11% |
| Net receivables | INR -3,559,999.50 |
| Net supplier payables | INR 638,793.00 |

[Full reconciliation evidence](finance-kpi-evidence/reconciliation.json) includes identical native report filters and raw differences for fiscal-year-to-date, October-to-date and April–June historical periods. All 22 numeric comparisons matched at company currency precision (2 decimals) or displayed percentage precision (2 decimals). Two zero-denominator historical margins are correctly undefined. Currency raw differences are zero; tiny percentage differences arise from JSON float serialization of Decimal ratios. There are no unexplained differences. Independent GL income/expense/net-profit and Payment Ledger signed-balance checks also agree.

Negative expenses, credit receivables and unusually high margins exist in the underlying reports. They require business/accounting review; matching native reports does not certify that the underlying postings are commercially correct. This task preserves those figures and supplies review warnings and report links.

- **38 tests passed, zero skipped:** native submitted invoices, taxes, partial settlements, credits/returns, cancellation/draft exclusions, date boundaries, customer advances, project scope, recorded USD conversion to company currency, direct permission denial, company restrictions, restricted financial scope, hidden source fields and sanitized failures. Accounting fixtures use validated native controllers and transaction rollback. The hidden-field regression simulates the permission helper's restricted field result.
- **27 existing homepage regression tests passed** during implementation.
- **Six HTTP checks passed:** authorized non-administrator finance access, unknown filters, identity injection, Guest denial, POST denial and access revocation. Temporary test User, User Permissions and session were removed. See [HTTP evidence](finance-kpi-evidence/http-results.json).
- **Nine viewport checks passed:** 360, 390, 480, 767, 768, 1023, 1024 and 1440 pixel widths, plus 844×390 landscape. No page overflow, unexpected HTTP failures or JavaScript errors. Filter reset/navigation, offline recovery and permission-denied cache clearing were checked. See [browser evidence](finance-kpi-evidence/browser-results.json), [phone](finance-kpi-evidence/owner-home-390.png), [tablet](finance-kpi-evidence/owner-home-768.png) and [desktop](finance-kpi-evidence/owner-home-1440.png).

Re-run using the installed bench test runner for `sarathi_owner.tests.test_finance_kpis`; the manual reconciliation entry point is `sarathi_owner.tests.reconcile_finance_kpis.run`. Local HTTP/browser audit scripts live alongside these tests and require the documented local Docker site. They create temporary native audit sessions/users and clean up afterward. Do not run test-fixture scripts against a production site.

## Change manifest and remaining limits

Existing files changed by DASH-009 only:

- `sarathi_owner/sarathi_owner/api/homepage.py`
- `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js`
- `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css`

New implementation and verification files: `sarathi_owner/sarathi_owner/api/finance_kpis.py`, plus `test_finance_kpis.py`, `reconcile_finance_kpis.py`, `audit_finance_http_local.py` and `audit_finance_browser_local.py` under the app's `tests/` directory. This document and the six evidence files are new supporting documentation. Pre-task file hashes are checked separately from the full dirty Git diff to preserve DASH-001–008 work. ERPNext/Frappe core remains read-only.

Local DASH-009 implementation and the above validation are complete. Business approval of FIN-001 versus FIN-002 headline terminology remains outstanding. Alternate finance-book/cost-center configurations were inspected in native code but not exhaustively exercised with dedicated fixtures. Stock-manufacturing valuation/cost completeness, every company/currency, custom dimensions, large-factory performance, all browser engines, VPS deployment and upgrade/rollback are not certified by this local test set. Legacy finance APIs are not replaced by this task. DASH-010 and subsequent features are not started here.

### Continuation verification — 2026-10-14

Pre-task SHA-256 comparison found exactly the three existing files listed above changed, with no baseline files missing. Finance Python syntax and homepage JavaScript syntax passed. The six HTTP checks were rerun successfully and their temporary user/permissions/session cleanup passed. An independent read-only check found zero DASH009 fixture Items, Customers, Suppliers, Projects, Users or marked Journal Entries. The local Redis cache/queue containers had been stopped; both were started and the websocket service restarted to restore local verification. No application configuration or ERPNext/Frappe source changes were needed.
