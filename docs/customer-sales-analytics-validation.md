# DASH-010 — Customer and sales analytics validation

## Pre-implementation audit and decisions

Reviewed actual DASH-001–009 foundation/audit, permissions, KPI dictionary, shared UI/data helpers, homepage and finance implementation on feature/Gaurav_2. Existing unrelated changes are preserved using scratch/dash-010/baseline.json. Installed Frappe 16.31.0 / ERPNext 16.33.0 is available locally. Installed source differs from ERPNEXT_MAIN; native accounting filters and Sales Order Analysis were inspected inside the container.

| Component | Decision |
| --- | --- |
| Homepage, shared filters/cards/tables/chart wrapper | Retain and extend the overview only |
| Finance normalize/native report/complete-scope gate | Reuse; add source-specific sales/customer field and complete-read checks |
| Legacy sales totals based on invoice grand total | Do not reuse; they disagree with the DASH-009 basis |
| P&L income | Same FIN-002 basis for customer attribution and trends; retain signed GL credit minus debit |
| Customer attribution | Submitted Sales Invoice voucher -> invoice Customer; other Income entries -> explicit GL Customer party; otherwise separate Unattributed accounting income bucket |
| Native financial_statements additional conditions | Reuse opening/closing/book/project/cost-center semantics; reconcile full included income to native P&L |
| Sales Order Analysis | Its pending_amount is unbilled, not delivery backlog; validate delivery qty fields but use remaining delivery net value, distinctly labelled |

Revenue attribution never distributes unassigned journal income across customers. Customer share denominator is the signed sum of included attributed customer income (not top-N, and excludes Unattributed); zero denominator -> N/A. Negative shares or shares above 100% are mathematically possible. Customer-filtered totals represent the attributed subset; native P&L itself does not support Customer filtering. Top-N and paginated customer detail use amount descending, Customer ID ascending to break ties.

Backlog contract: current submitted Sales Orders, excluding Closed/Stopped, Cancelled, Completed, To Bill (delivery complete), and drafts. On Hold appears separately as held demand, excluded from executable totals. Per line remaining=max(qty-delivered_qty,0); stock quantity=remaining*conversion_factor, grouped by item+stock_uom; delivery net value=remaining*base_net_rate. This excludes taxes, retains recorded net-rate discounts and company-currency conversion, and is independent of billed amount. No mixed item/UOM grand quantity. Global dates select order transaction-date cohort; optional delivery bounds select line delivery_date and exclude unknown dates when a bound is selected. Otherwise missing dates remain Unknown. Overdue means delivery_date before site today. Project scope uses line Project with order-header fallback only when the line is blank. Returns use native current delivered_qty without subtracting returned_qty twice; amendments contribute only the active submitted replacement. Current backlog is not a historical as-of snapshot.

Only read APIs and UI are in scope. Core/configuration/history remain unchanged. Validation results and limitations will be appended after execution.


## Implemented definitions and reconciliation behavior

Customer analytics and the trend are labelled **accounting income (FIN-002)**, exactly the DASH-009 P&L basis. The proposed DASH-004 SALES-001–003 definitions reference FIN-001 invoice net sales; those are not silently redefined or claimed equivalent. DASH-010's explicit requirement to retain DASH-009's financial basis governs this implementation. Approval of a separate FIN-001 headline remains an existing business decision.

One Income GL row contributes its signed company-currency `credit-debit` once. A one-to-one submitted Sales Invoice voucher join supplies Customer; other vouchers use an explicit GL Customer party when present. Unlinked income remains Unattributed. No invoice-item/payment joins can multiply income. Native `financial_statements.apply_additional_conditions` and account-filter logic supply company/account root, closing-voucher, finance-book, project and cost-center behavior. Opening-entry behavior follows the installed P&L defaults, with no extra exclusion. Draft and cancelled invoices contribute no active GL income; active submitted amendments and signed returns follow native postings. Taxes follow their actual account classification, not invoice grand totals. Recorded base GL amounts preserve historical currency conversion.

Before returning attribution, its complete full-scope sum must match native P&L at configured currency precision. A mismatch returns an unavailable section; the service never manufactures a balancing amount. Customer selection is applied to the verified attribution, so selected-customer income is a subset of P&L, and the UI explains that the native report drill-down shows full equivalent company/dimension scope. Customer shares divide by all included attributed customer income, independent of page/Top-N; Unattributed is excluded. Zero denominator returns null/N/A; negative amounts and percentages remain signed. Comparison bars explicitly show absolute magnitude with signed text.

Monthly periods use calendar YYYY-MM keys, including partial first/last months and year transitions. Daily periods use posting date, limited to 93 inclusive calendar days. Monthly supports the same ordered maximum five-year period as finance. Complete readable empty periods are measured zero; failure or unavailable scope is never zero. Weekly/comparison series are not implemented.

Backlog follows SALES-004/005 delivery formulas documented above. It aggregates net delivery value before detail pagination, counts distinct orders by status, and keeps held demand separate. Quantity conversion must be positive and stock UOM/net base rate must exist, otherwise the section is unavailable. Header totals, billed percentages and unbilled amounts do not substitute for delivery commitments. Native Sales Order Analysis validates remaining delivery quantity, but its `pending_amount` is unbilled and is intentionally not our delivery-value reference. Values at recorded net-rate precision can differ from a rounded header amount; no hidden adjustment is applied. Unknown delivery dates remain visible unless a delivery-date bound excludes them.

## API and UI contracts

GET `/api/method/sarathi_owner.api.sales_analytics.get_sales_analytics`, with a JSON `filters` object:

| Input | Contract |
| --- | --- |
| company | Authorized Company; unique readable Company may resolve automatically |
| from_date / to_date | ISO YYYY-MM-DD, inclusive; defaults company fiscal-year start/site today |
| customer / project | Readable native links, consistent company/customer relationships |
| cost_center / finance_book | Native P&L dimensions through the sales API; backlog explicitly unavailable; not added to the homepage form |
| interval | Monthly (default) or Daily, maximum 93 daily points |
| top_limit | Integer 1–20, default 5 |
| start / page_length | Customer detail offset and size; defaults 0/25; size maximum 100, offset maximum 100000 |
| backlog_start / backlog_page_length | Independent detail pagination, same bounds |
| order_status | Installed open Sales Order status; closed/completed/cancelled/To Bill rejected; On Hold selects held demand |
| delivery_from / delivery_to | Ordered ISO delivery-date bounds, only backlog |

Unknown fields, arbitrary identity/DocType/SQL, invalid links/dates/status/limits and unsupported intervals are rejected. Global dates select income posting dates and backlog order transaction dates; the UI labels both meanings. The existing homepage passes sales-only parameters to analytics, retaining the original five operational/finance filter keys for prior sections. Apply resets pagination; Reset retains Company. Customer, Project and Company option searches continue through the existing native permission-aware helpers.

Response: `applied_filters`, `currency`, `generated_at`, and independent `revenue`/`backlog` sections. Available revenue contains paginated `rows`, `top_customers`, `customer_count`, `has_next`, full `customer_total`, `unattributed`, selected `included_income`, reference-scope `company_accounting_income`, `trend`, `reference_filters` and basis descriptions. Available backlog contains paginated line `rows`, `has_next`, complete monetary/overdue/held totals, distinct order counts/status breakdown, item/stock-UOM quantities and `source_as_of`. Ordered/delivered quantities are in the returned line `uom`; remaining quantities use `stock_uom` and recorded `conversion_factor`.

Database grouping precedes customer ranking/detail pagination; backlog details paginate in SQL. There is no per-customer/card query. At most 20000 customer/date or backlog grouping rows are accepted; larger sets return unavailable and request a narrower scope, not partial totals. Item/UOM summary displays the first 100 stable groups with explicit coverage/count; monetary totals remain complete. Customer sorting is amount descending, ID ascending; backlog sorting is order ID then line ID ascending. Only fixed field/DocType expressions and bound query-builder values are used.

Errors follow DASH-006: validation HTTP 417, denied API HTTP 403, unexpected read failure sanitized HTTP 500. Expected permission/fiscal/configuration limitations yield section-level `available:false` and a safe reason. There is no cross-user sales result cache. Homepage loading, same-scope stale/offline recovery, permission-denied cache clearing and stale-response guards are retained. Customer and order forms use native Desk permissions. Customer income detail applies a validated Customer filter; the P&L drill-down carries equivalent native filters.

Authorization requires executive and finance capabilities, native Company/link/field access, native P&L Report roles/ref-DocType report permission, and complete readable financial/sales scope before aggregation. Native role read must be unrestricted; shared/owner-only access, non-Company User Permissions and relevant custom permission hooks fail closed. Child reads are limited to wholly authorized order parents. Conservative denial also applies to a customer-limited executive selecting their permitted customer; restricted partial aggregates are not supported. No role/permission is granted to production users to render a chart.

## Executed validation — 14 October 2026

| Validation | Result |
| --- | --- |
| Combined native fixture and regression suite | 104 tests passed, zero skipped, 144.618 seconds |
| Focused DASH-010 suite after count/UOM/summary refinements | 20 tests passed, zero skipped, 23.614 seconds |
| Independent live reconciliation | 29 comparisons across three periods; zero unexplained differences |
| Direct HTTP security audit | Six checks passed; temporary User, User Permissions and session removed |
| Browser audit | Nine viewports; no page-wide overflow, JavaScript errors or unexpected HTTP errors |
| Preservation audit | Exactly three existing homepage files changed; no baseline files missing; core and prior finance source unchanged |
| Fixture cleanup | Zero temporary DASH009/010 Item, Customer, Supplier, Project, User or marked Journal Entry records remain |

Tests cover multiple customers, deterministic ties/limits/pages, duplicate-prone two-line invoices, signed returns, zero/negative shares, drafts/cancellations/amendments, unattributed journal income, daily/monthly and year boundaries, empty periods, recorded foreign-currency conversion, discounted delivery commitments, partial/full delivery, cancellation restoring delivered counters, closed/cancelled/draft/held orders, amended order replacement, project fallback, fully billed yet undelivered commitments, delivery bounds, overdue lines, stock-UOM conversion and source-reconciliation failure. Existing finance tests also retain tax/partial-settlement/historical-cutoff coverage. Test records are created only through native controllers inside rolled-back transactions; existing business records/configuration are not edited.

Permission coverage includes real owner, production manager, supervisor, operator, unrelated and finance-only roles; forged Company/Customer identifiers; real Customer User Permissions; a successful non-administrator full-company executive; simulated hidden-field helper results; input injection/limits and sanitized failures. Six HTTP checks separately verify successful non-administrator access, unexpected query fields, identity injection, Guest denial, POST denial and role revocation.

Browser coverage: widths 360, 390, 480, 767, 768, 1023, 1024, 1440 and 844×390 landscape. Verified native chart rendering, Top-N and independent backlog pagination without changing income, second customer page, date apply/reset, Company retention, existing navigation/return, offline recovery and removal of cached records after 403. Native Charts entry animation was disabled via public options to prevent an SVG race on rapid resize. Y-axis uses documented K/M abbreviations, full currency tooltips and an accessible trend-value table. Backlog tables scroll within their labelled container on larger screens and become cards on phones.

Local validation initially detected stale Nginx Socket.IO upstream connectivity after the earlier service restart. Reloading existing Nginx resolved it; the final browser run has no HTTP errors. Core source/configuration was not modified.

## Live reconciliation results

Company SarathiAILabs; INR; reporting cutoff 2026-10-14:

| Scope | Accounting income / customer+unattributed / trend sum | Executable delivery backlog |
| --- | ---: | ---: |
| Fiscal year to date: 2026-04-01–2026-10-14 | 17,699,999.50 each | 27,400,000.00 across 6 orders |
| Month to date: 2026-10-01–2026-10-14 | 9,499,999.50 each | 0.00 in this order-date cohort |
| Historical cohort: 2026-04-01–2026-06-30 | 0.00 each | 0.00 in this order-date cohort |

Fiscal-year ranking: ISRO Propulsion Complex Vendor 9,499,999.50 (53.672315%), Larsen & Toubro Heavy Engineering 8,200,000.00 (46.327685%). Unattributed income is measured 0.00 in these existing cohorts, while a rollback journal fixture verifies nonzero unattributed handling. Existing held/overdue totals are zero; native fixture tests exercise both. All source comparisons are recorded with exact filters/raw differences in [reconciliation evidence](customer-sales-evidence/reconciliation.json). This proves agreement for the tested scopes, not commercial correctness of the source books or every deployment configuration.

## Re-running and evidence

Inside the installed bench, use `bench --site frontend execute sarathi_owner.tests.test_sales_analytics.run` for the combined native fixture suite (local development site only), and `bench --site frontend execute sarathi_owner.tests.reconcile_sales_analytics.run` for the read-only comparison. From the repository root, run `python sarathi_owner/sarathi_owner/tests/audit_sales_http_local.py` and `python sarathi_owner/sarathi_owner/tests/audit_sales_browser_local.py`. These manual local audits require Docker's existing frontend site and Python Playwright/Chromium; they create and revoke native temporary audit sessions. They do not print credentials/cookies.

Evidence: [backend tests](customer-sales-evidence/test-results.txt), [focused tests](customer-sales-evidence/focused-test-results.txt), [HTTP](customer-sales-evidence/http-results.json), [browser](customer-sales-evidence/browser-results.json), [preservation](customer-sales-evidence/preservation.json), [fixture cleanup](customer-sales-evidence/fixture-cleanup.json). Screenshots: [customer overview phone](customer-sales-evidence/customer-sales-390.png), [tablet](customer-sales-evidence/customer-sales-768.png), [desktop](customer-sales-evidence/customer-sales-1440.png), [backlog phone](customer-sales-evidence/sales-backlog-390.png), [tablet](customer-sales-evidence/sales-backlog-768.png), [desktop](customer-sales-evidence/sales-backlog-1440.png), [trend desktop](customer-sales-evidence/sales-trend-1440.png).

## Exact change manifest and limits

Modified existing files only:

- `sarathi_owner/sarathi_owner/api/homepage.py` — integrates independently available sales analytics, preserves finance/operational scopes.
- `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js` — sales filters, rankings/customer detail, native chart/accessible values, commitment summaries/line cards, pagination and chart cleanup.
- `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css` — scoped sales presentation, responsive and contained backlog table styles.

New source/test files:

- `sarathi_owner/sarathi_owner/api/sales_analytics.py`
- `sarathi_owner/sarathi_owner/tests/test_sales_analytics.py`
- `sarathi_owner/sarathi_owner/tests/reconcile_sales_analytics.py`
- `sarathi_owner/sarathi_owner/tests/audit_sales_http_local.py`
- `sarathi_owner/sarathi_owner/tests/audit_sales_browser_local.py`

New documentation: this file and `docs/customer-sales-evidence/` artifacts linked above. Baseline SHA-256 checks preserve the earlier dirty DASH-001–009 implementation and ERPNext/Frappe checkout. Runtime worker/Nginx reloads only loaded the new custom-app code/restored local connectivity.

Locally ready for review. Limits: no weekly/prior-period comparison; no historical backlog reconstruction; no alternate revenue-basis approval; no partial record-limited executive aggregates; no arbitrary custom accounting dimensions, warehouse or shift filters; large grouping scopes require narrowing. Alternate finance-book/cost-center configurations, stock-item delivery-return workflows, all browser engines, production-scale performance, VPS deployment and upgrade/rollback remain outside this local certification. The populated-site reconciliation has two invoiced customers and six outstanding orders; lifecycle/negative/held cases are verified by rollback fixtures, not claimed as existing production history. Native current delivered counters are consumed; automated delivery cancellation and full delivery were exercised, but an actual stock-item return/re-delivery workflow was not. Legacy detail-page sales calculators are preserved and are not newly certified by this task. DASH-011 is the recommended next backlog task and has not been started.
