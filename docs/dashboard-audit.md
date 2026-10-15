# DASH-002 — Audit Existing Dashboard Apps and Routes

Audit date: 13 October 2026 (Asia/Calcutta). Branch: `feature/Gaurav_2`. Scope: inspect, trace and document only. Status: **source audit ready for review; current runtime and device verification unavailable**. No dashboard implementation, permission/schema changes, builds, migrations, deployment or GitHub changes were performed.

## 1. Executive summary

Both expected dashboards have source implementations, Page metadata, initialization scripts, frontend assets, API services and navigation links. They are not blank scaffolds. The owner app provides executive and accounting subviews; the production app provides organization/customer/project navigation, operational reports, accounting and subcontracting views. Both use a shared runtime/assistant hosted by `sarathi_visibility`. A dedicated assignment-scoped shop-floor Page was **not found**.

The main risks are inconsistent company/document authorization, directly interpolated owner SQL filters, mismatched financial definitions and filter scope, approximate material readiness, unbounded reads before pagination, hardcoded legacy blueprint data, and an existing image-build step that patches Frappe core. These findings are source evidence, not claims of a newly reproduced exploit or reconciled business totals.

The current local HTTP and Docker requests timed out. Consequently this audit does **not** certify that either route currently renders, that installed metadata matches local files, or that layouts work on actual desktop/tablet/phone screens. Earlier successful runtime tests remain historical evidence only.

This report extends [DASH-001 architecture](dashboard-foundation.md), preserving its two-app/three-experience design and read-only ERPNext/Frappe boundary. It does not replace the [7 October audit](sarathi-dashboard-audit-2026-10-07.md), [navigation notes](dashboard-navigation-cache.md), or [loader repair notes](owner-blank-page-fix.md).

## 2. Repository and application structure

Root: `D:/SarathiAiLabs/Industrial_Projects/Frappe_docker_main`. `ERPNEXT_MAIN/` contains upstream code and is read-only. Custom app sources are in `sarathi_owner/` and `sarathi_visibility/`; `ERPNext_Agent/` is a separate existing assistant dependency. `docs/` is the established documentation location. Audit utilities/raw evidence are local, git-ignored files in `scratch/dash-002/`.

Inventory: **109 non-bytecode app files; 62 Python, 10 JavaScript, 11 JSON**. The file and function inventories below include line references from this snapshot. Line numbers may change after later implementation.

Git state at entry: eight modified tracked files — `pwd.yml`; owner dashboard CSS, controller JS, page HTML and page JS; production dashboard CSS, controller JS and page JS. Existing untracked work: `.agents/`, `docs/dashboard-foundation.md`, `docs/dashboard-navigation-cache.md`, `docs/owner-blank-page-fix.md`, production assistant CSS/JS and shared runtime JS. Preserved without reset/revert/branch switch/staging.

Initial `git status --short` failed reading ignore files. Read-only command override `git -c core.excludesFile=/dev/null status --short` succeeded; no Git configuration was edited. No `AGENTS.md` was found in the scoped repository search. Applied the [Sarathi dashboard skill](../.agents/skills/sarathi-erpnext-dashboards/SKILL.md) and the supplied task instructions.

Configured version: `sarathi_visibility/Containerfile:1` defaults to ERPNext `v16.33.0`. Both app `__init__.py` files declare `0.0.1`; packaging requires Python >=3.10. DASH-001 observed bench ERPNext 16.33.0/Frappe 16.31.0. **Current installed versions could not be reverified** because Docker/bench requests timed out; the earlier observation is not presented as a new runtime result.

## 3. Owner Dashboard route audit

Expected route: `/desk/sarathiownertower`.

| Item | Evidence / result |
| --- | --- |
| Page registration source | `sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.json:1`; name and page_name `sarathiownertower`, standard Desk Page, module Sarathi Owner |
| Page entry and lifecycle | Same directory `sarathiownertower.js:1`; shared initializing promise, `on_page_load`, `on_page_show`, `on_page_hide`; initializes `frappe.SarathiOwnerDashboard` |
| Template | Page `.html` exists, but controller also assigns `frappe.templates["sarathiownertower"]` inside constructor at `public/js/sarathi_owner_dashboard.js:68` before rendering at line 235. Controller template changes can shadow the page HTML |
| CSS/controller | `public/css/sarathi_owner_dashboard.css`; `public/js/sarathi_owner_dashboard.js`; also globally included by `hooks.py:15` |
| Shared dependencies | Entry loads visibility runtime first, then assistant CSS/JS and owner CSS/JS using runtime loader |
| Page Python | `sarathiownertower.py:1` sets `context.no_cache`; data APIs are separate |
| Navigation | `hooks.py:18` app-screen entry; `desktop_icon/owner.json`; `setup/install.py:_ensure_owner_page` and `after_install`/`after_migrate`; production/owner controller view-switch buttons |
| Page roles | Sarathi Owner, System Manager, Manufacturing Manager in JSON and setup; Administrator special handling in Python helper |
| Source status | **Confirmed in source**; linked code/files found, JavaScript parses |
| Current installed/HTTP/render status | **Unable to verify**; HTTP timed out, Docker bench unavailable. No successful browser/render result in this run |

Owner controller offers 17 page keys: home, projects, project_detail, customers, sales_orders, manufacturing, stock_quality, invoicing, payments, financial_reports, accounts_setup, taxes, banking, budget, share_management, subscription, reports. This is a broader existing accounting navigation than the future eight-section executive sidebar; preserve useful behavior and map it deliberately in DASH-008 rather than deleting it as duplication.

## 4. Production Control Tower route audit

Expected route: `/desk/sarathicontroltower`.

| Item | Evidence / result |
| --- | --- |
| Page registration source | `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.json:1`; name/page_name `sarathicontroltower`, module Sarathi Visibility |
| Page entry and lifecycle | Same directory `sarathicontroltower.js:1`; shared promise and runtime, initializes `frappe.SarathiIndustrialDashboard` |
| Template | Page `sarathicontroltower.html:1`, rendered by `public/js/sarathi_dashboard.js:64` |
| Active assets | `public/js/sarathi_dashboard.js`, `public/css/sarathi_dashboard.css`, runtime/assistant assets |
| Global hook assets | `hooks.py:12` prefill JS and `hooks.py:14` `sarathi_control_tower.css`; this stylesheet is distinct from the active page CSS |
| Page Python | `sarathicontroltower.py:1` sets `context.no_cache`; active reads use `api/dashboard.py`, not the page Python |
| Navigation | `hooks.py:18`, `desktop_icon/production_manager.json`, setup desktop icons/page links; workspace JSON contains Page shortcut and `is_hidden:1`. A source shortcut does not prove visible live navigation |
| Page roles | Manufacturing User, Manufacturing Manager, System Manager, Sarathi Super Admin |
| Source status | **Confirmed in source**; referenced files found, JavaScript parses |
| Current installed/HTTP/render status | **Unable to verify**; runtime unavailable. No current tablet/mobile rendering claim |

Active navigation tabs: overview, sales, production, engineering, materials, procurement, quality, fulfillment, reports, integrations (`sarathi_dashboard.js:105`). Accounting/subcontracting are separate views in this controller. URL context includes company, customer, project, dates, status, tab and view (`readUrl`/`writeUrl`, lines 321–342). The dedicated shop-floor Page is **not found**; a Job Cards report and native form links are existing functionality, not the planned operator workboard.

## 5. File and function inventory

The appendices provide the complete non-cache file list and Python definitions/JavaScript method candidates with source line numbers. The architectural entry points are:

| Area | Files/functions to retain and trace |
| --- | --- |
| Owner data | `api/owner_dashboard.py`: `get_owner_context` (85), `get_owner_summary` (113), `get_live_report_data` (1250), `get_page_data` (1484); `_get_*_page` and chart helpers |
| Owner detail/catalog | `api/quick_details.py:get_details` (148); `api/module_catalog.py:get_catalog` (231), `get_entry` (307); `api/detail_analytics.py:describe` (8) |
| Owner pipeline | `api/pipeline.py:get_project_pipeline`; explicit BOM/Production Plan/Work Order/Job Card/Stock Entry relationships and ancillary sales/payment/delivery/quality records |
| Active production reads | `api/dashboard.py:get_summary` (1055), `get_report` (1529), `get_record` (1549), `export_report` (1658); `REPORTS` (47), `report_data` (907) |
| Shared production data | `api/dashboard_data.py:readable` (44), `rows` (48), `children` (62), `check_link` (94), `parse_filters` (99), `load` (174) |
| Derived production | `api/production.py:analyze` (6), `live_activity` (129); `api/pipeline.py:resolve_project`, `load_pipeline` |
| Finance/subcontracts | `api/accounting.py:get_accounting_card_summary` (149), `get_accounting_dashboard` (325); `api/subcontracting.py:get_subcontracting_card_summary` (38), `get_subcontracting_dashboard` (133) |
| Legacy/alternate services | `api/control_tower.py` read/form/update/sync endpoints; `api/data.py` defaults/blueprints; `public/js/sarathi_website_tower.js` calls these alternate APIs |
| Shared lifecycle/assistant | `public/js/sarathi_dashboard_runtime.js`, `sarathi_dashboard_assistant.js`; `api/agent_chat.py:send_message` (42), `get_suggestions` (81) |
| Lifecycle setup | Both `hooks.py` and `setup/install.py`; visibility `setup/dashboard.py` relationship fields/backfills/validations/notification; `setup/rename_legacy.py` existing migration |
| Native report | `sarathi_visibility/.../report/sarathi_industrial_analysis/`: `execute` loads same dataset and returns `REPORTS` columns, data and scope note |

Five custom DocTypes (51 declared fields total): Sarathi Customer Organization (2), Sarathi Project Controller (11), Sarathi Material Requirement (14), Sarathi Production Tracker (13), Sarathi Machine Integration Log (11). Metadata JSON contains permissions; simple controllers do not establish data quality or operational use. Installed fields/roles remain unknown this run.

### Dependencies and duplicated behavior

Owner already calls visibility accounting and production summary services (`owner_dashboard.py:594`, `610`, `1535`, `1539`), and both pages load visibility shared assets. Preserve the direction owner -> visibility -> ERPNext/Frappe; avoid circular imports or a third app. Owner package metadata does not declare the full install/runtime dependency contract. Assistant imports `ERPNext_Agent` graph/client modules (`agent_chat.py:13`–15); provisioning and provider behavior are not verified.

Two production API/UI families coexist: active `dashboard.py` + `dashboard_data.py` + `sarathi_dashboard.js`, and alternate `control_tower.py` + blueprint `data.py` + `sarathi_website_tower.js`. Owner has its own financial/chart aggregations in addition to reused visibility accounting, plus both class and prototype quick-detail implementations (`sarathi_owner_dashboard.js:4103`, `5006` vicinity). Do not remove either family without caller tracing; the later prototype assignment replaces the earlier class method at runtime. Icon SVG selection logic is duplicated across frontend controllers. Shared runtime/assistant assets are already reusable, while a common KPI/filter/table component system is not yet established.

## 6. Frontend-to-backend data-flow map

| UI path | Backend path | Source / relevant behavior |
| --- | --- | --- |
| Owner filter context | `loadContext` / `refreshFilterDropdownsOnly` -> `get_owner_context` | Company, Customer, Project through `get_all`; returns permission context and date |
| Owner homepage | `refreshCurrentPage` / `smoothRefresh` -> `get_owner_summary` | Project, Sales Order/Invoice, Bin/Item/Warehouse, GL/Account, Work Orders; pipeline helper; reused accounting and industrial summaries |
| Owner subview | `get_page_data(page_name, filters)` -> relevant `_get_*_page` | Corresponding ERPNext records, tables/charts and native form/report routes; unknown page returns empty result rather than explicit rejection |
| Owner reports | `executeLiveReport` -> `get_live_report_data` | Frappe report runner with financial-report gating and report-specific filters; execution/reconciliation not retested |
| Owner details/catalog | `showQuickDetails` -> `quick_details.get_details`; optional module browser -> catalog/get_entry | Native route resolution, permitted fields/document reads, paginated list/detail/report wrappers |
| Production summary | `load` -> `dashboard.get_summary` -> `dashboard_data.load` | Permission-aware parent reads and child attribution; `production.analyze`/`live_activity`; pipeline helper; finance/subcontract summaries |
| Production report/table/card | `call` / report render -> `get_report` -> `load` + `report_data` | Applies selected subset/search, then slices full in-memory result; page size clamped 1–100 |
| Production record | `get_record` -> `load` -> selected dataset membership + `check_permission('read')` | Rejects out-of-selection documents; related rows truncated to 100 |
| Production export | `export_report` -> `load`/`report_data` + export permission | CSV; no database-level pagination established |
| Accounting/subcontracting view | Separate whitelisted `get_accounting_dashboard` / `get_subcontracting_dashboard` | Own parsers, SQL/ORM reads and result schemas, not the active production parser |
| Legacy surface | `sarathi_website_tower.js` -> `control_tower.*` | Different defaults/form schemas/derived states and update/sync methods |
| Assistant | Shared assistant -> `agent_chat.send_message` -> existing agent graph/client | Conversational transactional capability; separate from dashboard read APIs and future operator commands |

### Filters, states and refresh

Owner `getFilters` (`sarathi_owner_dashboard.js:1283`) supplies company/customer/project/status/date preset/manual dates/search. Summary/page loaders accept dict/JSON and often turn malformed JSON into empty filters; they do not share the production relationship validator. Summary chart helpers receive only company (`owner_dashboard.py:437` vicinity), so Customer/Project/date filters do not consistently constrain charts. Nested industrial summary receives company/manual dates/status/search but omits selected Customer/Project (`owner_dashboard.py:613`–620).

Production `parse_filters` validates date order, supported project status and read access to Company/Customer/Project, rejects inconsistent selected relationships, and resolves company/customer from Project. `rows` uses `frappe.get_list`; `children` checks permitted fields and restricts to permission-filtered parent names. Missing/unreadable sources can return empty lists; the summary also supplies a `restricted` list. Finance and subcontracting parsers do not inherit all these checks.

Owner requests use a sequence/page guard (`refreshCurrentPage`/`smoothRefresh`, lines 1343/1396), a loading panel, refresh-success text and failure panel (`setLiveStatus`, 1331). The displayed success time is browser callback time, not a server generation timestamp, and failure replaces content. Production uses request sequence/visible checks, `aria-busy`, server `generated_at`, explicit error/stale text and previous-data retention (`load`, 415). Both poll at 15 seconds in current source (`show`, owner 4940 and production 343), despite older documentation mentioning 30 seconds. Custom hooks publish payload-free record invalidations after commit; open Job Card time logs indicate recorded running work, not live physical machine state.

Runtime loader deduplicates assets/promises and attaches one assistant to the active host. Router-based deactivation complements page hide callbacks. Owner manual Refresh invokes `clear_owner_cache`, which deletes a broad key family and clears site cache (`owner_dashboard.py:25`); this is a maintenance side effect, not a pure read. It was not invoked in this audit.

## 7. Existing KPI and widget inventory

This is an **implementation inventory**, not the approved KPI dictionary or an endorsement of formulas. Exact helper/function line references are in Appendix B. Data below is source-derived unless explicitly marked static. No business amounts were exported into this report.

### Owner homepage

All items below are assembled by `sarathi_owner/sarathi_owner/api/owner_dashboard.py:get_owner_summary` (113–702), rendered by `sarathi_owner_dashboard.js:renderOwnerHome` (1444) and `renderHomeCharts` (1764).

| KPI/widget | Current source/formula | Concern / follow-up |
| --- | --- | --- |
| Active Manufacturing Projects | Count Projects with Open/Ongoing/Active status from `docstatus != 2` selection | Date/status/search semantics differ from transactional period scope |
| Commercial Order Book | Sum `Sales Order.grand_total` for statuses other than Completed/Closed/Cancelled; parent query `docstatus != 2` | Can include drafts; raw document currency totals; distinct from recognized revenue |
| Accounts Receivable / overdue | Positive current `Sales Invoice.outstanding_amount`, `docstatus != 2`; overdue due_date before today | Draft inclusion and current balance are not historical as-of AR; posting-period filter may omit older unpaid invoices |
| Inventory Working Capital | Current `Bin.stock_value`, fallback actual_qty × valuation_rate; authorized warehouse scope not enforced uniformly | Not historical valuation; company with no warehouses leaves Bin filter unrestricted; Customer/Project do not allocate stock |
| Total Expenses / Net Profit | Expense debit-credit and income credit-debit from selected GL voucher types/root accounts; net income minus expenses | Not full standard P&L logic; interpolated filters; Customer/Project ignored in these GL sums |
| Cash/bank snapshot | Noncancelled GL debit-credit over Bank/Cash account types | No selected date/as-of cutoff; company restriction is interpolated |
| RM/WIP/FG allocation | Item-group/warehouse-name heuristics; percentage of current total | Zero stock falls back to static 50/20/30 percent; quantities in low-stock strings use fixed `pcs` |
| Strategic manufacturing pipelines | First 10 Projects -> `api/pipeline.py:get_project_pipeline` | Bounded display but per-project queries; stage model is custom, needs configured-process validation |
| Financial trend | `_get_financial_chart_data` (1553): six current months, submitted invoice grand_total versus GL expense; difference labeled profit | Revenue basis differs from GL snapshot and date/filter selection; tax/currency treatment needs reconciliation |
| Order-book trend | `_get_order_book_chart_data` (1642): Sales Order monthly query | Commitments, company-only filter; not revenue |
| Production trend / output | `_get_production_chart_data` (1706): Work Order qty/produced_qty grouped by creation month, cast to integers | Combines output units/items and truncates fractions; not output by actual completion date |
| AR aging | `_get_ar_aging_chart_data` (1770): current submitted invoice outstanding by today/due_date | Not historical AR; label hardcodes rupees |
| Capital doughnut | `_get_working_capital_chart_data` (1635), derived from inventory classification above | Shares classification/valuation limitations |
| Risks/actions | Overdue receivables, low stock and delayed submitted WOs | Delayed query limited to 5, so displayed count is capped; not a factory-wide delay count; Customer not applied |
| Activity and portfolio table | `_get_live_activity` (705), Project fields plus per-project Sales Order lookup/WO SQL | N+1 reads; record modifications are activity, not a telemetry feed |
| Accounts advance/invoicing flow | Sales Order advance versus grand_total, invoice/receivable aggregates | `advance_paid` is used but absent from the selected SO fields; named in-charge/step values are hardcoded, not workflow assignments (`get_owner_summary`, 559–590) |
| Embedded accounting/industrial data | Visibility accounting and production summary calls | Duplicate work and incomplete filter forwarding; no automatic guarantee finance permissions apply to every returned raw dataset |

### Owner detail views and native report widgets

| Page/helper | Major data widgets and sources |
| --- | --- |
| `_get_projects_page` (1816) / `_get_project_detail_page` (1969) | Project portfolio/progress/cost/billed/sales fields, schedule and budget/cost variance; linked Tasks/Sales Orders/Work Orders and project pipeline |
| `_get_customers_page` (2211) | Customer list; Sales Order commitments; invoice totals/outstanding by Customer; customer table/concentration. Restricted-user and currency correctness unverified |
| `_get_sales_orders_page` (2317) | Orders, grand_total, delivered/billed percentages, outstanding fulfillment and order-book chart; no recognized-revenue claim should be inferred |
| `_get_manufacturing_page` (2437) | Active/completed WO counts; sum planned/produced, output ratio; WO table and production chart. Limit 50 before displayed metrics; not complete factory totals |
| `_get_stock_quality_page` (2564) | Warehouse/Bin/current inventory and stock distribution; a page name containing quality is not proof of full quality/rework analytics |
| `_get_invoicing_page` (2657), finance alias | Invoice/billing/AR/AP-oriented widgets from invoice records with finance gate; selected-period/outstanding semantics need agreed definitions |
| `_get_payments_page` (2847) | Payment Entry rows/totals and native payment/journal/reconciliation/GL routes |
| `_get_financial_reports_page` (2997) | Standard Balance Sheet/P&L/Cash Flow/Trial Balance/GL/AR/AP controls; execution and reconciliation remain unverified this run |
| `_get_accounts_setup_page` (3134) / `_get_taxes_page` (3224) | Account/master/template counts and native setup/tax reports; operational settings, not computed financial performance |
| `_get_banking_page` (3311) / `_get_budget_page` (3410) | Bank/master/payment-clearance and Budget records; flags/checklist text must not be treated as reconciled accounts or approvals |
| `_get_share_management_page` (3504) / `_get_subscription_page` (3588) | Shareholder/subscription records and native actions; ancillary existing features to preserve |
| `_get_reports_page` (3680) / `get_live_report_data` (1250) | Nine definitions: AR, P&L, Gross and Net Profit, Sales Order Analysis, Warehouse Wise Stock Balance, Production Analytics, Work Order Summary, Financial Ratios, Project Summary |
| `quick_details.get_details`, `detail_analytics.describe`, module catalog | Record fields, scoped lists, calculations/charts/report wrappers. Lists use permission-aware paths in places; do not generalize their safety to owner summary SQL |

### Production overview, charts and details

`sarathi_visibility/sarathi_visibility/api/dashboard.py:get_summary` (1055) builds KPIs from `len(report_data(...))`, with `load` in `dashboard_data.py:174` supplying datasets. Counts describe records, not quantities. Default KPI labels and mapped reports:

| KPI(s) | Dataset/subset |
| --- | --- |
| Total projects/items; warehouse stock; warehouses | projects; items; inventory (Bin row count, not stock quantity); warehouses |
| Workstations; operations; workstation types; routings; active BOMs | workstations; operations_catalogue; workstation_types; routings; boms |
| Customers; suppliers | customers; suppliers |
| Open orders; active Work Orders | orders/open; work_orders/open: submitted, not cancelled/completed/closed/stopped |
| Executable Job Cards; planned Job Cards | job_cards/open filtered by `production_phase == 'Executable pending'`; job_cards/planned |
| Completed/in-progress/not-started/delayed projects | projects/completed; production_summary/in_progress; production_summary/not_started; projects/delayed |
| Selected Project status, due date and progress | Project.status, expected_end_date, percent_complete |
| Selected Project resources/items + open orders/WOs/Job Cards | Resource attribution via `get_project_resource_ids`/`report_data`; no assignment-to-user implication |
| Selected Project material shortages | Count materials where known shortage_qty > 0 |

Major charts (same function): recorded live production status; Project status/progress; Sales Order status; deadline days remaining; planned versus produced grouped by item/UOM; planned versus actual Job Card hours; submitted order value by currency/month; selected Project task/Job Card pipeline progress; operation completed/remaining grouped by unit; ordered/received procurement; recorded output parts; finished receipts by item/unit/date; potential shortages by item/unit; projects by Customer. First-12/first-6 limits are display sampling, not full analytics. Production's item/UOM grouping is a useful pattern missing from owner combined output.

Major tables/widgets use these sources:

- Project health/current/next operations, operation balances and production summary: `dashboard.py:get_summary`, `production.py:analyze` (6), `live_activity` (129), Work Order Operation completion/loss/schedule and Job Card open time logs. Remaining = max(WO qty − operation completed − process loss, 0), unknown when fields unavailable. These are recorded states, not machine uptime.
- Material readiness: `dashboard_data.py:load` (660–728), remaining requirement = max(required − max(consumed, transferred), 0), grouped by item/source warehouse/company; shortage = max(remaining − current Bin actual, 0). Reservation fields are loaded, but not deducted in this shortage formula; future projected/reserved-stock readiness is incomplete.
- Stock history, reservations, quality, finished output and procurement pipeline: explicit parent/child relationships in `load`, `api/pipeline.py:resolve_project`/`load_pipeline`; ledger/reservation/inspection records are distinct datasets. Inspection sample size is explicitly labeled not rejected quantity in `REPORTS`.
- Workstation resources/workload, BOM revisions/components/operations, routing/plant-floor/master tables: `load`, `get_project_resource_ids`, `REPORTS`/`report_data`. Resource catalog scope is not the operator assignment policy.
- Quality/rework: Quality Inspection results plus corrective Job Cards/time logs/suboperations; no proof of reconciled rejected output for every installation.
- Alerts/data quality: `load` issues and procurement exceptions; summary limits displayed lists to 20 while retaining separate counts.
- Machine integration logs: existing app-owned log records only; physical integrations were not exercised.

Appendix C lists all **39 current `REPORTS` definitions**, their source DocType and line. The older audit mentioned 45 industrial reports; this run's source inventory establishes 39 dictionary keys and does not reuse the older count.

### Shared accounting and subcontracting widgets

| Service/widget | Existing implementation and unresolved semantics |
| --- | --- |
| Accounting overview nine KPIs | `accounting.py:get_accounting_dashboard` (325), return at 1260: revenue, expense, net profit/margin, cash, bank, receivables, payables, tax liability, budget used. GL/Account, Sales/Purchase Invoice, Payment Entry, Budget/Cost Center sources; no current reconciliation performed |
| Accounting charts/detail panels | Same function: current/prior-period change, income mix/customer/project revenue, expense account/cost-center categories, monthly revenue/expense trends, profitability waterfall, cash/liquidity, AR/AP aging/top parties, taxes/budget, Project/Customer/Supplier finance, month-end checklist |
| Accounting estimates/fallbacks | Zero GL revenue/expense -> invoice base_grand_total; expense split 70/30; absent budget -> actual expense × 1.35; commitment -> expense × 0.1; average monthly revenue -> revenue/6. Fixed review-checklist conditions do not prove completed reconciliation |
| Accounting card summary | `get_accounting_card_summary` (149) uses separate query/budget logic; earlier audit reported summary/detail divergence. Source duplication confirmed; divergence not remeasured |
| Subcontracting eight KPIs | `subcontracting.py:get_subcontracting_dashboard` (133; calculations 354–466): total orders; active submitted statuses; material remaining at suppliers × rate; pending supplied-material reconciliation count; orders pending receipt; on-time rate; service + consumed-material spend; receipt rejected_qty |
| Subcontracting caveats | On-time uses order modified date versus schedule (missing date counts on time), and no completed orders yields 100%; pending scrap is outstanding material-line count, not a validated scrap workflow. UOM/currency/grain correctness requires definition and reconciliation |
| Subcontracting major panels | Same function: procurement/transfer/receipt lifecycle counts, status distribution, service/material/total cost trends, supplier/project costs, material reconciliation, order/receipt tables, quality and delays. Card summary at line 38 is a separate calculation path |

### Static, computed and live-source distinctions

Active pages mostly read live ERPNext records and calculate dashboard responses; that is different from validated accounting meaning. Owner hardcoded allocation fallbacks/in-charge names, accounting assumptions, and subcontracting empty-sample defaults are not measured facts. Legacy `api/data.py` contains fixed company/project/order identifiers, engineering component rows, pipeline weights and task blueprints. `control_tower.py` consumes those defaults/fallbacks (`resolve_project`, `get_project_tasks`, `get_pipeline_weights`, `get_material_rows`, and response engineering_components). Do not classify these as live operational data merely because other fields come from ERPNext.

## 8. Permissions and security observations

Source-verified existing safeguards: owner context/summary/page-data/quick-details explicitly gate owner access; finance helpers distinguish capabilities; production selected links use document read checks; active parent reads use permission-aware `get_list`; child reads constrain permitted parent names/fields; record detail verifies dataset membership and read permission; report subsets and page sizes are allowlisted/bounded; catalog requires a signed-in System User and checks permitted fields/documents. Normal Frappe whitelist authentication still matters, but Page roles alone do not secure an API.

Important gaps:

- Owner context `get_all` and owner/finance/subcontract SQL aggregates do not consistently apply Company/User Permissions or record scope. `accounting._check_read` and subcontracting equivalent check only DocType read capability. Earlier company-leak reproduction is historical; current source still contains the implicated query patterns.
- Owner summary interpolates client-derived company/date strings into GL SQL (`owner_dashboard.py:377`–421). No preceding company Link validation is present in this method. This is a concrete unsafe construction; no injection payload was sent.
- Owner summary computes/returns company-only raw chart datasets unconditionally after the finance-gated GL block and also calls shared accounting. Formatting selected strings as Restricted does not prove that the full response protects financial values. Restricted-role exploit/runtime behavior was not tested.
- `clear_owner_cache` has no explicit owner/maintenance role check in its body. Normal authentication is not equivalent to authorization for site-wide cache clearing.
- Legacy mutations `update_project`/`update_task` call `require_super_admin`, but accept any existing DocType field rather than a business-action allowlist; endpoint-specific HTTP method, state and mutation scope need follow-up. They were not called.
- Assistant state is fetched by supplied `session_id` from `sarathi_agent_graph_state`; `_get_agent_state` does not visibly compare cached state's user to authenticated user before returning it (`agent_chat.py:18`–38). Cross-user access is a source-level concern, not tested behavior. Do not reuse this session model for shop-floor actions without review.
- Supervisor/operator assignment restrictions are not established. Four custom operational DocTypes declare only System Manager access; their presence does not create safe worker access.

No user/role fixtures, permission changes, schema modifications, business submissions or transaction mutations were performed. Tenant model remains one client-company installation with many Customer records.

## 9. Responsive design observations

**Source observations only.** Current browser rendering at 1440, 820, 390 and landscape 844 px could not be verified because runtime/session preparation did not return. No screenshots or overflow measurements from this run are claimed.

| Area | Existing source behavior | Remaining verification |
| --- | --- | --- |
| Owner navigation/cards | CSS breakpoints 1200/820/480–820 and later 1100/700/380; sidebar becomes horizontal scroll navigation at <=820; KPI grids reduce columns | Phone first-action visibility, scrolling/menu usability, filter fit and long names |
| Owner filter/charts/tables | Searchable combo/date controls; resize-aware Frappe charts; overflow containers; multiple overlapping rule blocks | Chart labels, card/table readability, dialogs and no page-level overflow |
| Production header/filter/cards | CSS <=768 stacks hero and filters, clips horizontal overflow on root; later rules use minmax KPI grids and single-column cards | `overflow-x:hidden` can hide content rather than fix it; actual clipping must be measured |
| Production navigation/tables | Compact tabs, table/card modes and contained table wrappers; URL-backed filter/view context | Back/reload/filter persistence and report/detail behavior on real devices |
| Touch/accessibility | Status text with badges, labeled filters, aria-busy, error/status roles, reduced-motion styles | Not full accessibility compliance. Production mobile hero refresh min-height 36px (`sarathi_dashboard.css:700` vicinity) is below the intended 44–48px touch target; focus/contrast/glove use unverified |
| States | Both have loading/failure/empty patterns; production retains stale data; owner failure replaces content | Offline, denied access, slow/racing requests, empty/large data and responsive error panels |
| Shared pieces | Runtime/assistant, icon/status patterns, basic wrappers and filters | Formal shared responsive design system remains DASH-005; shop-floor minimal/touch layout remains future work |

## 10. Tests and runtime verification performed

| Check | Actual result / limit |
| --- | --- |
| Branch and status | Branch `feature/Gaurav_2`; initial ignore-file error, read-only `/dev/null` override succeeded |
| Source inventory | 109 app files read; AST/JSON inventory captured locally; no application imports/mutations required |
| Python syntax | All 62 app Python files parsed with `ast.parse`: passed; syntax is not business correctness |
| JSON metadata syntax | All 11 JSON files parsed: passed; installed schema not established |
| JavaScript syntax | `node --check` for all 10 JS files: all exit 0 |
| Runtime HTTP | Initial owner request timed out after 8 seconds. Subsequent bounded requests to **both** expected routes each returned TimeoutError (5-second timeout); no successful response/render result |
| Docker / bench | Bounded `docker version --format '{{.Server.Version}}'` and `docker exec ... bench version`: each timed out after 12 seconds. Earlier `docker ps` listed services; listing alone did not prove availability |
| Runtime metadata/API/served assets | Prepared and launched local read-only probe, but no completed results artifact returned; unavailable, not passed |
| Authenticated browser/device probes | Playwright import available; audit launch did not complete session preparation or produce browser results/screenshots. No authenticated route/layout success claimed |
| Existing business tests | Six modules, 61 test methods in source: owner 15/14/9; production 15/4/4. Not executed; some create transactional fixtures or assume site `frontend`; runtime unavailable |
| CI source review | `linters.yml`: pre-commit, ERPNext `yarn test:js`, custom-app Semgrep; server MariaDB workflow and pre-commit inspected. No fresh CI result. Pre-commit includes autofix hooks, deliberately not run across local work |
| Preservation/report checks | See final validation record below; only audit documentation is a new non-ignored deliverable |

Audit scripts and baseline/inventory/static-check evidence are under git-ignored `scratch/dash-002/`. Runtime scripts were designed to summarize keys/counts rather than dump business values and to revoke any generated audit session in a finally block; session creation/cleanup completion cannot be certified when Docker does not return. No credential/session value was printed in this report or tool output. Do not revoke other users' sessions to compensate for unavailable verification.

## 11. Findings and gap analysis

Severity reflects source risk and required follow-up, not a newly established production incident. Expected behavior comes from the approved dashboard requirements/core boundary.

| ID / priority / area | Current behavior and exact evidence | Expected behavior / risk | Follow-up task(s) |
| --- | --- | --- | --- |
| AUD-01 / High / owner, finance | `owner_dashboard.py:get_owner_context:85` uses get_all (91–102); accounting `_check_read:26`, `_sum_field:121`; subcontracting `_check_read:16` and unrestricted reads | All options/aggregates obey underlying Company/User/document permissions; current paths can expose restricted scope | DASH-003, DASH-006, DASH-032 |
| AUD-02 / High / owner SQL | `owner_dashboard.py:get_owner_summary:377`–421 interpolates company/date clauses | Validate Link filters and parameterize SQL, including access constraints; unsafe query construction | DASH-006, DASH-032 |
| AUD-03 / High / finance responses | `get_owner_summary:435`–442 computes company-only chart helpers; embedded accounting at 594; can_view_finance formatting does not guard every returned dataset | Uniform financial capabilities on server response, not client labels | DASH-003, DASH-006, DASH-009, DASH-032 |
| AUD-04 / High / finance meaning | `accounting.py:get_accounting_dashboard:443`–470, 757, 1253, 1329: invoice fallback, 70/30, synthetic budget/commitment, /6 | Reconciled accounting/report definitions; zero is valid, estimates must not masquerade as actuals | DASH-004, DASH-009, DASH-031 |
| AUD-05 / High / filter consistency | `get_owner_summary` chart calls company-only; nested industrial filters 613–620 omit Customer/Project; historical AR uses current balances | Selected filters consistently constrain applicable widgets or explicitly disclose unsupported dimensions | DASH-004, DASH-006, DASH-008–012 |
| AUD-06 / Medium / manufacturing quantity | Owner `_get_manufacturing_page:2457` limit 50 and aggregate unlike UOM; `_get_production_chart_data:1747` groups by WO creation and int-casts | Full scope totals by compatible grain/UOM and defined completion-period basis | DASH-004, DASH-012, DASH-015–016 |
| AUD-07 / High / material readiness | `dashboard_data.py:load:698`–728 loads reservation fields but shortage uses current actual stock only | Respect warehouse/transfers/consumption/reservations/projected context; avoid overpromising shared stock | DASH-004, DASH-018 |
| AUD-08 / Medium / query efficiency | `dashboard_data.rows:53` limit_page_length=0; `dashboard.get_report:1529` loads all then slices; owner pipeline/per-project queries | Bounded detail reads and aggregation without N+1, measured representative volumes | DASH-006, DASH-016, DASH-034 |
| AUD-09 / High / core boundary | `sarathi_visibility/Containerfile:10` runs `patch_socket_backend.py:5`–35 against installed Frappe realtime source | No ERPNext/Frappe source modifications; current recipe conflicts with rule and cannot be treated as approved release | DASH-035 (remediation required before release) |
| AUD-10 / Medium / hardcoded source | `api/data.py:1`–33 defaults/blueprints; `control_tower.resolve_project:313`, `get_project_tasks:560`, `get_pipeline_weights:629`, `get_material_rows:736`; owner accounts_flow:559 | Site configuration and real source-backed stages/assignments; label blueprints unavailable rather than actual | DASH-002 finding; DASH-004, DASH-017, DASH-035 |
| AUD-11 / High / cache maintenance | `owner_dashboard.py:clear_owner_cache:25` clears site cache without explicit role check; manual refresh caller JS:788 | Read refresh remains scoped; maintenance separately authorized | DASH-006, DASH-036, DASH-032 |
| AUD-12 / High / assistant session | `agent_chat.py:_get_agent_state:18` uses caller session_id, no visible cached-user ownership check | Enforce user ownership and scope before restoring a conversation; effect unverified | DASH-003, DASH-006, DASH-032; keep assistant separate from DASH-025 |
| AUD-13 / Medium / supplier analytics | `subcontracting.py:354`–466 on-time uses modified date; no completions ->100%; unreconciled material lines labeled scrap/reconciliation | KPI grain/date/source agreed, empty states distinguish no evidence from perfect performance | DASH-004, DASH-020, DASH-031 |
| AUD-14 / Medium / mobile | Owner CSS:2706 and production CSS:660/5856/5868 overlapping breakpoints; 36px mobile refresh target | Tested layouts, no clipping/overflow, readable charts, accessible touch/focus | DASH-005, DASH-028–029 |
| AUD-15 / High / shop floor | Only two Page directories found; no dedicated assignment-scoped workboard/action contract | Scoped operator/supervisor pages and validated independent backend actions | DASH-003, DASH-023–026 |
| AUD-16 / Medium / maintainability | Shared visibility assets and services consumed by owner; dual production families; owner runtime template and later prototype override | Explicit dependency/ownership and caller-aware refactor, preserve routes | DASH-005, DASH-006, DASH-035 |
| AUD-17 / Medium / runtime evidence | Current HTTP/Docker timeouts; no fresh metadata/browser/role test results | Live route/source matching/device behavior verified separately; source existence is insufficient | Follow-up verification for DASH-002; DASH-028, DASH-032–034 |

Paths abbreviated in finding rows refer to the app/package API paths identified in Sections 5–7 and Appendices A/B, not upstream ERPNext files.

## 12. Recommendations mapped to existing GitHub tasks

1. **DASH-003 next:** define owner/finance versus manufacturing capabilities, allowed company/customer/record scope, and supervisor/operator assignments. Audit evidence shows the need; do not simply mirror current broad roles.
2. **DASH-004:** formalize all metric grains/date/currency/UOM/filter meanings and reconciliation sources, prioritizing financial fallbacks, AR cutoffs, mixed units and readiness.
3. **DASH-006:** apply permission-aware validation/aggregation consistently, parameterize unsafe SQL, bound queries, protect cache/session scope. Coordinate with DASH-003/004 rather than implementing UI-only restrictions.
4. **DASH-005:** consolidate existing reusable lifecycle/status/filter/table patterns incrementally with responsive tokens, avoiding route/controller rewrites and global Desk CSS effects.
5. **DASH-008–013, 015–021, 023–026:** implement only the relevant approved business/operational gaps; existing charts and record links should be retained where correct. Do not treat legacy blueprint data as configured manufacturing or native Job Card access as the completed workboard.
6. **DASH-028–036:** execute device/role/integration/performance evidence and fix release recipes before release approval. Restore runtime availability to finish the outstanding DASH-002 runtime probes first.

No duplicate GitHub tasks were created; existing backlog IDs are recommendations only and no status was changed.

## 13. Questions and items that could not be verified

- Why are local port 8080 and Docker server unresponsive? No restart, daemon reconfiguration or infrastructure repair was attempted under this audit scope.
- Do installed Page roles, Custom Fields, workspace/icon records, whitelisted callable resolution and served asset hashes match this working tree? Prepared probe did not complete.
- What exact Company/User Permission restrictions and real non-admin accounts are intended for owner, manager, supervisor and operator? No role fixture was created or permission changed.
- Which assignment, shift, production area and telemetry sources are configured? No assumptions of digital assignment or live machines are made.
- What revenue/P&L/valuation/AR reconciliation basis and reservation semantics should be approved? Current formulas are inventoried, not agreed.
- Does the deployed site provision `ERPNext_Agent` and required dependencies safely, and which alternate/legacy callers remain in use? Source references do not establish end-to-end provider or external integration operation.
- Can existing raw response financial data and assistant session concerns be reproduced with a properly scoped test user? No exploit, cross-user data retrieval or business mutation was performed.
- Current desktop/tablet/mobile clipping, chart readability, touch behavior, filter return navigation, accessibility, slow/offline/error behavior and concurrency remain unverified. A recorded empty/error/denied source branch is not a tested state.

### Validation and task handoff

Source inspection, route wiring, file/function inventory, data-flow/widget inventory, source-level permission/mobile risks and backlog mapping are documented. Current runtime availability is the outstanding verification limitation, explicitly allowed to be reported as unavailable by this audit task. **Do not mark runtime/device/role acceptance passed or claim the dashboard release complete.** This audit is reviewable with that limitation; live verification remains pending.

Final validation: SHA-256 comparison of **6,333 baseline files** (tracked source including ERPNext core, both custom apps, and existing documentation/skills) found **zero changed or missing existing files**. All report-relative Markdown links resolve; no trailing whitespace was found. `git diff --check` passed with existing app-file CRLF conversion warnings; untracked report whitespace was checked separately. Final Git status has only `docs/dashboard-audit.md` added to the pre-existing non-ignored change list. Targeted process inspection found no remaining incomplete audit jobs.

Only `docs/dashboard-audit.md` is the new non-ignored repository deliverable. Local ignored evidence created in `scratch/dash-002/`: `source_audit.py`, `runtime_audit.py`, `browser_audit.py`, `baseline.json`, `source-inventory.json`, `static-results.json`, `http-results.json`, `validation-results.json`, `job-cleanup.json`. No completed runtime/browser result files or screenshots were produced. These utilities are audit evidence, not product implementation, and none of the existing documentation was overwritten.


## Appendix A. Complete application file inventory

Sizes are snapshot bytes; line counts apply to inspected text extensions. Generated bytecode/cache files are excluded.

| File | Bytes | Lines |
| --- | --- | --- |
| [sarathi_owner/pyproject.toml](../sarathi_owner/pyproject.toml) | 393 | 16 |
| [sarathi_owner/README.md](../sarathi_owner/README.md) | 460 | 8 |
| [sarathi_owner/sarathi_owner/__init__.py](../sarathi_owner/sarathi_owner/__init__.py) | 22 | 1 |
| [sarathi_owner/sarathi_owner/api/__init__.py](../sarathi_owner/sarathi_owner/api/__init__.py) | 32 | 1 |
| [sarathi_owner/sarathi_owner/api/detail_analytics.py](../sarathi_owner/sarathi_owner/api/detail_analytics.py) | 5959 | 210 |
| [sarathi_owner/sarathi_owner/api/module_catalog.py](../sarathi_owner/sarathi_owner/api/module_catalog.py) | 12780 | 450 |
| [sarathi_owner/sarathi_owner/api/owner_dashboard.py](../sarathi_owner/sarathi_owner/api/owner_dashboard.py) | 94467 | 3756 |
| [sarathi_owner/sarathi_owner/api/permissions.py](../sarathi_owner/sarathi_owner/api/permissions.py) | 1139 | 50 |
| [sarathi_owner/sarathi_owner/api/pipeline.py](../sarathi_owner/sarathi_owner/api/pipeline.py) | 39101 | 1225 |
| [sarathi_owner/sarathi_owner/api/quick_details.py](../sarathi_owner/sarathi_owner/api/quick_details.py) | 10272 | 316 |
| [sarathi_owner/sarathi_owner/desktop_icon/owner.json](../sarathi_owner/sarathi_owner/desktop_icon/owner.json) | 490 | 20 |
| [sarathi_owner/sarathi_owner/hooks.py](../sarathi_owner/sarathi_owner/hooks.py) | 1643 | 64 |
| [sarathi_owner/sarathi_owner/modules.txt](../sarathi_owner/sarathi_owner/modules.txt) | 14 | 0 |
| [sarathi_owner/sarathi_owner/public/css/sarathi_module_browser.css](../sarathi_owner/sarathi_owner/public/css/sarathi_module_browser.css) | 6860 | 391 |
| [sarathi_owner/sarathi_owner/public/css/sarathi_owner_dashboard.css](../sarathi_owner/sarathi_owner/public/css/sarathi_owner_dashboard.css) | 97679 | 4914 |
| [sarathi_owner/sarathi_owner/public/icons/desktop_icons/solid/owner.svg](../sarathi_owner/sarathi_owner/public/icons/desktop_icons/solid/owner.svg) | 651605 | 0 |
| [sarathi_owner/sarathi_owner/public/icons/desktop_icons/subtle/owner.svg](../sarathi_owner/sarathi_owner/public/icons/desktop_icons/subtle/owner.svg) | 651605 | 0 |
| [sarathi_owner/sarathi_owner/public/icons/owner.png](../sarathi_owner/sarathi_owner/public/icons/owner.png) | 488510 | 0 |
| [sarathi_owner/sarathi_owner/public/icons/owner.svg](../sarathi_owner/sarathi_owner/public/icons/owner.svg) | 651605 | 0 |
| [sarathi_owner/sarathi_owner/public/js/sarathi_module_browser.js](../sarathi_owner/sarathi_owner/public/js/sarathi_module_browser.js) | 16021 | 445 |
| [sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js](../sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js) | 191717 | 5235 |
| [sarathi_owner/sarathi_owner/sarathi_owner/__init__.py](../sarathi_owner/sarathi_owner/sarathi_owner/__init__.py) | 35 | 1 |
| [sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/__init__.py](../sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/__init__.py) | 37 | 1 |
| [sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.html](../sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.html) | 8489 | 167 |
| [sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.js](../sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.js) | 1795 | 39 |
| [sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.json](../sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.json) | 354 | 20 |
| [sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.py](../sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.py) | 48 | 2 |
| [sarathi_owner/sarathi_owner/setup/__init__.py](../sarathi_owner/sarathi_owner/setup/__init__.py) | 34 | 1 |
| [sarathi_owner/sarathi_owner/setup/install.py](../sarathi_owner/sarathi_owner/setup/install.py) | 2200 | 92 |
| [sarathi_owner/sarathi_owner/setup/populate_10_projects.py](../sarathi_owner/sarathi_owner/setup/populate_10_projects.py) | 31578 | 950 |
| [sarathi_owner/sarathi_owner/setup/populate_full_industrial_lifecycle.py](../sarathi_owner/sarathi_owner/setup/populate_full_industrial_lifecycle.py) | 16471 | 554 |
| [sarathi_owner/sarathi_owner/tests/__init__.py](../sarathi_owner/sarathi_owner/tests/__init__.py) | 33 | 1 |
| [sarathi_owner/sarathi_owner/tests/test_module_catalog.py](../sarathi_owner/sarathi_owner/tests/test_module_catalog.py) | 5107 | 132 |
| [sarathi_owner/sarathi_owner/tests/test_owner_dashboard.py](../sarathi_owner/sarathi_owner/tests/test_owner_dashboard.py) | 14279 | 399 |
| [sarathi_owner/sarathi_owner/tests/test_quick_details.py](../sarathi_owner/sarathi_owner/tests/test_quick_details.py) | 4577 | 120 |
| [sarathi_owner/sarathi_owner.pth](../sarathi_owner/sarathi_owner.pth) | 45 | 0 |
| [sarathi_visibility/Containerfile](../sarathi_visibility/Containerfile) | 1401 | 0 |
| [sarathi_visibility/DASHBOARD.md](../sarathi_visibility/DASHBOARD.md) | 12705 | 211 |
| [sarathi_visibility/INSTALL.md](../sarathi_visibility/INSTALL.md) | 2324 | 65 |
| [sarathi_visibility/MANIFEST.in](../sarathi_visibility/MANIFEST.in) | 233 | 0 |
| [sarathi_visibility/patch_socket_backend.py](../sarathi_visibility/patch_socket_backend.py) | 979 | 30 |
| [sarathi_visibility/pyproject.toml](../sarathi_visibility/pyproject.toml) | 398 | 19 |
| [sarathi_visibility/README.md](../sarathi_visibility/README.md) | 653 | 22 |
| [sarathi_visibility/sarathi_visibility/__init__.py](../sarathi_visibility/sarathi_visibility/__init__.py) | 22 | 1 |
| [sarathi_visibility/sarathi_visibility/api/__init__.py](../sarathi_visibility/sarathi_visibility/api/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/api/accounting.py](../sarathi_visibility/sarathi_visibility/api/accounting.py) | 43924 | 1473 |
| [sarathi_visibility/sarathi_visibility/api/agent_chat.py](../sarathi_visibility/sarathi_visibility/api/agent_chat.py) | 3654 | 96 |
| [sarathi_visibility/sarathi_visibility/api/control_tower.py](../sarathi_visibility/sarathi_visibility/api/control_tower.py) | 66827 | 2327 |
| [sarathi_visibility/sarathi_visibility/api/dashboard.py](../sarathi_visibility/sarathi_visibility/api/dashboard.py) | 50288 | 1693 |
| [sarathi_visibility/sarathi_visibility/api/dashboard_data.py](../sarathi_visibility/sarathi_visibility/api/dashboard_data.py) | 30638 | 1144 |
| [sarathi_visibility/sarathi_visibility/api/data.py](../sarathi_visibility/sarathi_visibility/api/data.py) | 4844 | 188 |
| [sarathi_visibility/sarathi_visibility/api/permissions.py](../sarathi_visibility/sarathi_visibility/api/permissions.py) | 932 | 34 |
| [sarathi_visibility/sarathi_visibility/api/pipeline.py](../sarathi_visibility/sarathi_visibility/api/pipeline.py) | 13696 | 487 |
| [sarathi_visibility/sarathi_visibility/api/production.py](../sarathi_visibility/sarathi_visibility/api/production.py) | 7285 | 231 |
| [sarathi_visibility/sarathi_visibility/api/subcontracting.py](../sarathi_visibility/sarathi_visibility/api/subcontracting.py) | 28360 | 1006 |
| [sarathi_visibility/sarathi_visibility/config/__init__.py](../sarathi_visibility/sarathi_visibility/config/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/config/desktop.py](../sarathi_visibility/sarathi_visibility/config/desktop.py) | 27 | 2 |
| [sarathi_visibility/sarathi_visibility/desktop_icon/production_manager.json](../sarathi_visibility/sarathi_visibility/desktop_icon/production_manager.json) | 541 | 20 |
| [sarathi_visibility/sarathi_visibility/hooks.py](../sarathi_visibility/sarathi_visibility/hooks.py) | 3311 | 108 |
| [sarathi_visibility/sarathi_visibility/modules.txt](../sarathi_visibility/sarathi_visibility/modules.txt) | 19 | 0 |
| [sarathi_visibility/sarathi_visibility/public/css/sarathi_control_tower.css](../sarathi_visibility/sarathi_visibility/public/css/sarathi_control_tower.css) | 93588 | 4574 |
| [sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css](../sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css) | 135057 | 6128 |
| [sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard_assistant.css](../sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard_assistant.css) | 25317 | 1102 |
| [sarathi_visibility/sarathi_visibility/public/icons/desktop_icons/solid/production_manager.svg](../sarathi_visibility/sarathi_visibility/public/icons/desktop_icons/solid/production_manager.svg) | 398861 | 0 |
| [sarathi_visibility/sarathi_visibility/public/icons/desktop_icons/subtle/production_manager.svg](../sarathi_visibility/sarathi_visibility/public/icons/desktop_icons/subtle/production_manager.svg) | 398861 | 0 |
| [sarathi_visibility/sarathi_visibility/public/icons/production_manager.png](../sarathi_visibility/sarathi_visibility/public/icons/production_manager.png) | 298952 | 0 |
| [sarathi_visibility/sarathi_visibility/public/icons/production_manager.svg](../sarathi_visibility/sarathi_visibility/public/icons/production_manager.svg) | 398861 | 0 |
| [sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js](../sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js) | 230283 | 6075 |
| [sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_assistant.js](../sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_assistant.js) | 36370 | 987 |
| [sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_runtime.js](../sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_runtime.js) | 2691 | 71 |
| [sarathi_visibility/sarathi_visibility/public/js/sarathi_desk_prefill.js](../sarathi_visibility/sarathi_visibility/public/js/sarathi_desk_prefill.js) | 13770 | 504 |
| [sarathi_visibility/sarathi_visibility/public/js/sarathi_website_tower.js](../sarathi_visibility/sarathi_visibility/public/js/sarathi_website_tower.js) | 86854 | 2551 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/sarathi_customer_organization.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/sarathi_customer_organization.json) | 1108 | 53 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/sarathi_customer_organization.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/sarathi_customer_organization.py) | 640 | 23 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/sarathi_machine_integration_log.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/sarathi_machine_integration_log.json) | 2277 | 109 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/sarathi_machine_integration_log.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_machine_integration_log/sarathi_machine_integration_log.py) | 97 | 5 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/sarathi_material_requirement.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/sarathi_material_requirement.json) | 2806 | 133 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/sarathi_material_requirement.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_material_requirement/sarathi_material_requirement.py) | 95 | 5 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/sarathi_production_tracker.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/sarathi_production_tracker.json) | 2740 | 128 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/sarathi_production_tracker.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_production_tracker/sarathi_production_tracker.py) | 93 | 5 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/sarathi_project_controller.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/sarathi_project_controller.json) | 2506 | 116 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/sarathi_project_controller.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_project_controller/sarathi_project_controller.py) | 93 | 5 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html) | 5690 | 151 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.js](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.js) | 1758 | 39 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.json) | 422 | 23 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.py) | 48 | 2 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/report/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/report/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/__init__.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.js](../sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.js) | 2234 | 51 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.json) | 443 | 17 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.py](../sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.py) | 766 | 17 |
| [sarathi_visibility/sarathi_visibility/sarathi_visibility/workspace/sarathi_visibility/sarathi_visibility.json](../sarathi_visibility/sarathi_visibility/sarathi_visibility/workspace/sarathi_visibility/sarathi_visibility.json) | 3100 | 108 |
| [sarathi_visibility/sarathi_visibility/setup/__init__.py](../sarathi_visibility/sarathi_visibility/setup/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/setup/dashboard.py](../sarathi_visibility/sarathi_visibility/setup/dashboard.py) | 8386 | 238 |
| [sarathi_visibility/sarathi_visibility/setup/install.py](../sarathi_visibility/sarathi_visibility/setup/install.py) | 10807 | 426 |
| [sarathi_visibility/sarathi_visibility/setup/rename_legacy.py](../sarathi_visibility/sarathi_visibility/setup/rename_legacy.py) | 1905 | 62 |
| [sarathi_visibility/sarathi_visibility/tests/__init__.py](../sarathi_visibility/sarathi_visibility/tests/__init__.py) | 0 | 0 |
| [sarathi_visibility/sarathi_visibility/tests/test_accounting.py](../sarathi_visibility/sarathi_visibility/tests/test_accounting.py) | 3009 | 97 |
| [sarathi_visibility/sarathi_visibility/tests/test_dashboard.py](../sarathi_visibility/sarathi_visibility/tests/test_dashboard.py) | 19218 | 544 |
| [sarathi_visibility/sarathi_visibility/tests/test_subcontracting.py](../sarathi_visibility/sarathi_visibility/tests/test_subcontracting.py) | 2990 | 88 |

## Appendix B. Function and frontend-method inventory

Python names come from AST definitions, including nested functions and test methods. `*` marks a whitelisted definition; it does not certify authorization. JavaScript entries are source method/function candidates extracted by syntax pattern, including nested callbacks; this is an index for inspection, not a complete call graph. Line numbers are one-based.

### sarathi_owner/sarathi_owner/api/detail_analytics.py

`describe:8`.

### sarathi_owner/sarathi_owner/api/module_catalog.py

`_require_desk:40`; `versions:48`; `_revision:55`; `_options:90`; `_route:100`; `_build_modules:139`; `_modules:221`; `get_catalog:231 *`; `_entry:246`; `_fields:258`; `_schema:279`; `get_entry:307 *`; `broadcast_change:396`; `after_migrate:421`; `inventory:425`.

### sarathi_owner/sarathi_owner/api/owner_dashboard.py

`broadcast_live_event:18`; `clear_owner_cache:25 *`; `_get_date_bounds:35`; `get_owner_context:85 *`; `get_owner_summary:113 *`; `_get_live_activity:705`; `get_live_report_data:1250 *`; `_get_dynamic_module_sections:1428`; `get_page_data:1484 *`; `_get_financial_chart_data:1553`; `_get_working_capital_chart_data:1635`; `_get_order_book_chart_data:1642`; `_get_production_chart_data:1706`; `_get_ar_aging_chart_data:1770`; `_get_projects_page:1816`; `_get_project_detail_page:1969`; `_get_customers_page:2211`; `_get_sales_orders_page:2317`; `_get_manufacturing_page:2437`; `_get_stock_quality_page:2564`; `_get_invoicing_page:2657`; `_get_finance_page:2843`; `_get_payments_page:2847`; `_get_financial_reports_page:2997`; `_get_accounts_setup_page:3134`; `_get_taxes_page:3224`; `_get_banking_page:3311`; `_get_budget_page:3410`; `_get_share_management_page:3504`; `_get_subscription_page:3588`; `_get_reports_page:3680`; `fmt_money:140`.

### sarathi_owner/sarathi_owner/api/permissions.py

`can_access_owner:19`; `can_view_finance:27`; `get_permission_context:41`.

### sarathi_owner/sarathi_owner/api/pipeline.py

`get_project_pipeline:39`; `_resolve_project_boms:1135`; `_resolve_production_plans:1176`; `_get_op_status:266`.

### sarathi_owner/sarathi_owner/api/quick_details.py

`get_details:148 *`.

### sarathi_owner/sarathi_owner/public/js/sarathi_module_browser.js

`constructor:3`; `esc:33`; `visible:36`; `icon:39`; `refreshCatalog:42`; `renderLauncher:77`; `renderOwnerNav:85`; `openAction:89`; `open:114`; `renderModuleMenu:160`; `setStatus:176`; `selectModule:179`; `selectEntry:213`; `loadDetail:223`; `renderDetail:265`; `value:355`; `table:365`; `openNative:386`; `refreshDetails:418`.

### sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js

`workspaceIcon:8`; `constructor:51`; `initElements:389`; `initRealtimeListener:670`; `handleLiveSocketChange:717`; `refreshFilterDropdownsOnly:732`; `showLiveToast:746`; `bindEvents:760`; `setupSearchableCombos:901`; `setupDateRangeFilters:1033`; `goToPageByKey:1131`; `renderNav:1138`; `loadContext:1215`; `populateFilterDropdowns:1228`; `getFilters:1282`; `selectPage:1301`; `setLiveStatus:1331`; `refreshCurrentPage:1342`; `smoothRefresh:1394`; `renderOwnerHome:1444`; `renderHomeCharts:1763`; `renderFrappeChart:1806`; `updateOwnerHomeSmoothly:1834`; `renderReportsPage:1870`; `bindReportRunnerEvents:1975`; `executeLiveReport:2006`; `renderLiveReportTable:2050`; `filterReportRows:2163`; `exportReportToCSV:2186`; `slugifyDoctype:2225`; `renderGenericPage:2238`; `getMaster24Stages:2816`; `resolvePipelineStages:3114`; `isManufacturingPipelineReady:3170`; `renderPipelineMarkup:3178`; `getAvatarGradient:3421`; `renderStrategicPipelineSheet:3439`; `renderManufacturingDeliverySheet:3682`; `bindPipelineClicks:4014`; `showQuickDetails:4102`; `showCardDetailModal:4316`; `showStageModal:4869`; `show:4939`; `hide:4986`.

### sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.py

`get_context:1`.

### sarathi_owner/sarathi_owner/setup/install.py

`before_install:4`; `after_install:8`; `after_migrate:20`; `ensure_role:32`; `_ensure_owner_page:41`; `remove_manufacturing_sidebar_links:70`.

### sarathi_owner/sarathi_owner/setup/populate_10_projects.py

`populate:18`.

### sarathi_owner/sarathi_owner/setup/populate_full_industrial_lifecycle.py

`populate_full_lifecycle:21`.

### sarathi_owner/sarathi_owner/tests/test_module_catalog.py

`setUpClass:12`; `setUp:17`; `tearDown:21`; `test_guest_denied:26`; `test_native_invoicing_coverage:31`; `test_external_and_recursive_routes_not_embedded:41`; `test_entry_cannot_be_forged:46`; `test_new_sidebar_entry_appears_without_code_changes:50`; `test_new_field_detected_without_frontend_change:69`; `test_records_and_children_are_permission_checked:91`; `test_restricted_user_catalog:104`; `test_events_are_payload_free_and_post_commit:127`.

### sarathi_owner/sarathi_owner/tests/test_owner_dashboard.py

`setUpClass:18`; `setUp:22`; `test_permission_checks:25`; `test_owner_summary_aggregation:36`; `test_owner_endpoints_reject_users_without_owner_access:58`; `test_page_loaders_all_views:73`; `test_accounting_modules_all_views:98`; `test_reports_page_executive_focus:128`; `test_pipeline_states_and_options:147`; `test_production_manager_dashboard_isolation:202`; `test_multiple_work_orders_and_stock_entry:210`; `test_live_report_runner:303`; `test_all_executive_reports_execute_without_error:325`; `test_live_notifications_wait_for_commit:332`; `test_executive_reports_with_selected_project:346`; `test_chart_data_generation:370`; `test_date_bounds_parsing:387`.

### sarathi_owner/sarathi_owner/tests/test_quick_details.py

`setUpClass:12`; `setUp:16`; `tearDown:19`; `test_external_routes_rejected:22`; `test_unlisted_doctype_rejected:26`; `test_guest_cannot_read:30`; `test_document_read_permission_enforced:35`; `test_new_action_is_read_only_list:40`; `test_credit_notes_preserve_route_filter:45`; `test_record_detail_is_safe:50`; `test_nested_workspace_and_tool_keep_their_identity:58`; `test_financial_report_stays_inside_dashboard:71`; `test_every_finance_entry_has_an_in_dashboard_response:76`; `test_search_scopes_calculations_and_chart:99`; `test_forged_nested_entry_is_rejected:105`; `test_invoice_child_tables_are_visible:109`; `test_invoice_calculations_keep_return_filter:116`.

### sarathi_visibility/sarathi_visibility/api/accounting.py

`_check_read:26`; `_parse_filters:30`; `_resolve_period_dates:50`; `_sum_field:121`; `_get_company_currency:140`; `get_accounting_card_summary:149`; `get_accounting_dashboard:325 *`.

### sarathi_visibility/sarathi_visibility/api/agent_chat.py

`_get_agent_state:18`; `_persist_agent_state:33`; `send_message:42 *`; `get_suggestions:81 *`.

### sarathi_visibility/sarathi_visibility/api/control_tower.py

`envelope:159`; `doctype_exists:168`; `has_field:172`; `safe_fields:191`; `get_all_safe:195`; `count_safe:213`; `split_select_options:225`; `get_link_options:229`; `form_field_payload:257`; `form_wrapper_schema:288`; `route_slug:309`; `resolve_project:313`; `project_payload:358`; `apply_production_completion:398`; `get_project_cards:425`; `get_company_options:475`; `get_default_company_from_erp:535`; `find_sales_order:552`; `get_project_tasks:560`; `is_delayed:591`; `get_pipeline:599`; `get_pipeline_weights:629`; `get_work_orders_for_project:664`; `get_job_cards_for_work_orders:700`; `get_material_rows:736`; `get_bom_material_rows:792`; `get_available_qty:844`; `get_project_item_codes:864`; `append_linked_bom_names:908`; `get_project_bom_names:932`; `get_all_work_orders:974`; `get_all_bom_rows:1006`; `get_bom_rows:1090`; `get_bom_operation_rows:1138`; `get_component_counts:1180`; `get_workstation_rows:1195`; `status_from_workstation:1250`; `get_stock_entry_rows:1256`; `get_finished_goods_rows:1289`; `get_live_analysis:1307`; `get_alert_rows:1435`; `get_manufacturing_process:1522`; `project_process_records:1588`; `project_process_row:1755`; `process_filters:1773`; `process_recent_records:1791`; `process_progress:1831`; `process_status:1870`; `get_integration_rows:1882`; `organization_summary:1920`; `count_delayed_projects:1989`; `get_dashboard:2007 *`; `get_organization_summary:2098 *`; `get_project_summary:2186 *`; `get_project_boms:2199 *`; `get_project_materials:2206 *`; `get_project_production:2214 *`; `get_workstations:2226 *`; `get_stock_entries:2234 *`; `get_finished_goods:2241 *`; `get_form_schema:2248 *`; `update_project:2253 *`; `update_task:2264 *`; `recalculate_progress:2275 *`; `sync_integration:2294`; `sync_tubepro:2316 *`; `sync_cypcut:2321 *`; `sync_tally:2326 *`.

### sarathi_visibility/sarathi_visibility/api/dashboard.py

`associate_customer:16 *`; `col:41`; `get_project_resource_ids:634`; `report_data:907`; `get_summary:1055 *`; `get_report:1529 *`; `get_record:1549 *`; `export_allowed:1644`; `export_report:1658 *`; `matches_project:833`; `kpi:1128`.

### sarathi_visibility/sarathi_visibility/api/dashboard_data.py

`readable:44`; `rows:48`; `children:62`; `check_link:94`; `parse_filters:99`; `delayed:144`; `status_matches:152`; `in_period:162`; `load:174`; `grouped:1140`; `_in_project_date_range:197`.

### sarathi_visibility/sarathi_visibility/api/permissions.py

`is_super_admin:8`; `require_super_admin:16`; `permission_payload:24`.

### sarathi_visibility/sarathi_visibility/api/pipeline.py

`resolve_project:56`; `load_pipeline:76`.

### sarathi_visibility/sarathi_visibility/api/production.py

`analyze:6`; `live_activity:129`.

### sarathi_visibility/sarathi_visibility/api/subcontracting.py

`_check_read:16`; `_parse_filters:20`; `get_subcontracting_card_summary:38`; `get_subcontracting_dashboard:133 *`.

### sarathi_visibility/sarathi_visibility/config/desktop.py

`get_data:1`.

### sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js

`workspaceIcon:2`; `constructor:45`; `el:271`; `esc:274`; `num:277`; `link:282`; `empty:291`; `statusColor:294`; `badge:310`; `call:313`; `readUrl:321`; `writeUrl:332`; `show:343`; `hide:370`; `navigate:377`; `filterChanged:393`; `applyDateFilter:398`; `clearDateFilter:411`; `load:419`; `render:452`; `pagination:596`; `renderCustomerTable:608`; `renderProjectTable:757`; `updateViewToggleButtons:910`; `renderCards:919`; `renderTabs:995`; `chart:1005`; `liveCards:1090`; `pipelineOverview:1176`; `projectHealth:1338`; `productionOverview:1514`; `setupOverview:1588`; `renderContent:1695`; `chartsForTab:1797`; `chartGrid:1812`; `cell:1828`; `loadReport:1845`; `openReport:1899`; `getDocTypeForReport:1911`; `formatCellValue:1956`; `showCardDetailsModal:2016`; `renderCardDetailsTable:2066`; `showRecordFormModal:2316`; `filterTable:2587`; `click:2635`; `inspect:2796`; `creationMenu:2861`; `create:2911`; `formatCompact:2990`; `renderSubcontractingCard:3000`; `showSubcontractingView:3030`; `hideSubcontractingView:3057`; `openSubcontractingView:3083`; `closeSubcontractingView:3090`; `subFilterChanged:3100`; `applySubFilters:3104`; `resetSubFilters:3114`; `setQuickDate:3132`; `setCostGranularity:3162`; `setPipeStage:3167`; `setSubStatusFilter:3173`; `setSubSupplierFilter:3179`; `setSubProjectFilter:3185`; `loadSubcontractingData:3191`; `renderSubcontractingDetailView:3218`; `renderSubDonutChart:3736`; `renderSubCostChart:3787`; `renderSubMaterialsTable:3838`; `renderSubOrdersTable:3918`; `renderAccountingCard:4043`; `showAccountingView:4118`; `hideAccountingView:4145`; `openAccountingView:4171`; `closeAccountingView:4178`; `accFilterChanged:4188`; `applyAccFilters:4192`; `resetAccFilters:4208`; `setAccPeriod:4224`; `setAccTab:4233`; `selectAccKpi:4239`; `loadAccountingData:4256`; `updateAccountingDetailViewSmoothly:4301`; `renderAccountingDetailView:4377`; `renderActiveKpiBanner:4602`; `renderOverviewDashboard:4688`; `renderRevenueExpenseAnalytics:4764`; `renderProfitabilityCashTower:4977`; `renderReceivablesPayablesBanking:5050`; `renderTaxesBudgetTower:5059`; `renderProjectCustomerSupplierFinance:5155`; `renderAccountingKpis:5277`; `renderProfitWaterfall:5448`; `renderRevenueExpenseTrend:5522`; `renderExpenseCategories:5623`; `renderCashLiquidity:5654`; `renderAgeingSection:5751`; `renderBudgetTaxes:5888`; `renderProjectFinance:5971`; `renderAuditChecklist:6037`; `initAiAssistant:6068`; `toggleAiChat:6072`.

### sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_assistant.js

`esc:20`; `el:21`; `load:22`; `initAiAssistant:36`; `clearAiConversation:160`; `toggleAiChat:190`; `triggerLiveBanner:202`; `highlightDashboardEntity:227`; `refreshAiChips:253`; `appendAiMessage:292`; `sendAiMessage:870`; `renderMarkdownLite:957`.

### sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard_runtime.js

`evict:8`; `load:15`; `activate:31`; `deactivate:40`; `activity:46`.

### sarathi_visibility/sarathi_visibility/public/js/sarathi_desk_prefill.js

`$:117`; `onload:341`; `refresh:344`; `setup:347`; `onload:360`; `refresh:363`; `after_save:366`; `onload:372`; `refresh:383`; `onload:397`; `after_save:409`; `onload:425`; `before_save:439`; `items_add:448`; `project:462`; `before_save:471`; `items_add:492`.

### sarathi_visibility/sarathi_visibility/sarathi_visibility/doctype/sarathi_customer_organization/sarathi_customer_organization.py

`autoname:8`; `validate:11`.

### sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.py

`get_context:1`.

### sarathi_visibility/sarathi_visibility/sarathi_visibility/report/sarathi_industrial_analysis/sarathi_industrial_analysis.py

`execute:5`.

### sarathi_visibility/sarathi_visibility/setup/dashboard.py

`install:7`; `validate_project:110`; `validate_bom:126`; `on_bom_submit:140`; `allowed_project_bom:149`; `validate_item_projects:175`; `validate_transaction:196`; `notify_dashboard:236`.

### sarathi_visibility/sarathi_visibility/setup/install.py

`before_install:6`; `after_install:10`; `after_migrate:22`; `ensure_frappe_framework_icon:33`; `ensure_desk_icons:71`; `extend_bootinfo_desktop_icons:156`; `ensure_role:229`; `ensure_module_profile_page:239`; `_ensure_control_tower_page:243`; `ensure_workspace_shortcuts:273`; `_ensure_shortcut:302`; `_ensure_content_shortcut:333`; `_remove_content_shortcut:353`; `remove_manufacturing_sidebar_links:364`; `_remove_manufacturing_workspace_card_link:390`; `_reindex_rows:410`; `_refresh_card_break_counts:415`.

### sarathi_visibility/sarathi_visibility/setup/rename_legacy.py

`execute:9`; `_rename:49`.

### sarathi_visibility/sarathi_visibility/tests/test_accounting.py

`test_period_date_resolution:14`; `test_accounting_card_summary_structure:24`; `test_accounting_dashboard_structure:41`; `test_main_dashboard_summary_integration:91`.

### sarathi_visibility/sarathi_visibility/tests/test_dashboard.py

`run:538`; `test_project_health_is_scoped_and_uses_recorded_operations:18`; `test_pipeline_line_attribution_and_completed_materials:34`; `test_mixed_project_purchase_items:86`; `test_live_activity_reads_permission_scoped_time_logs:129`; `test_live_running_and_completion_exclusion:165`; `test_operation_balances_and_shared_stock:208`; `test_project_status_cards_and_lifetime_operations:281`; `test_project_date_filter_by_creation_date:303`; `setUp:328`; `tearDown:369`; `test_customer_and_project_isolation:374`; `test_same_item_does_not_leak_boms:393`; `test_reports_and_summary_agree:421`; `test_validation_and_guest_permissions:432`; `test_pagination_export_and_native_report:451`; `test_company_user_permission:481`; `test_project_resource_scoping_isolation:509`.

### sarathi_visibility/sarathi_visibility/tests/test_subcontracting.py

`test_subcontracting_card_summary_structure:13`; `test_subcontracting_dashboard_structure:24`; `test_dashboard_get_summary_integration:69`; `test_subcontracting_filter_handling:77`.

## Appendix C. Current industrial report registry

Source: `sarathi_visibility/sarathi_visibility/api/dashboard.py:REPORTS`; data construction in `dashboard_data.load`, derivative helpers in `production.py`/`pipeline.py`, subset selection in `report_data`. The Source DocType is the registry declaration; derived reports can combine several DocTypes as described in Section 7.

| Key | Display title | Registry source DocType | Line |
| --- | --- | --- | --- |
| `items` | Items catalogue | Item | 48 |
| `inventory` | Warehouse stock & inventory balance | Bin | 62 |
| `procurement_exceptions` | Unassigned / conflicting procurement | Purchase Order | 76 |
| `material_history` | Lifetime material consumption | Work Order | 87 |
| `stock_details` | Lifetime stock movement items | Stock Entry | 102 |
| `stock_ledger` | Project voucher stock ledger | Stock Ledger Entry | 120 |
| `reservations` | Project stock reservations | Stock Reservation Entry | 135 |
| `quality` | Project quality inspections | Quality Inspection | 153 |
| `job_logs` | Job Card time history | Job Card | 168 |
| `job_suboperations` | Job Card sub-operations | Job Card | 182 |
| `tracking_setup` | Project part tracking setup | Project | 194 |
| `part_production` | Recorded operation output parts | Stock Entry | 205 |
| `live_activity` | Live project activity | Job Card | 222 |
| `operation_balance` | Lifetime operation balances | Work Order | 241 |
| `production_summary` | Project production summary | Project | 266 |
| `wip_stock` | Semi-finished shared warehouse stock | Bin | 286 |
| `deadlines` | Upcoming and overdue deadlines | Project | 299 |
| `projects` | Project portfolio | Project | 311 |
| `orders` | Sales orders | Sales Order | 325 |
| `order_items` | Order items and delivery | Sales Order | 341 |
| `work_orders` | Work orders | Work Order | 354 |
| `job_cards` | Job cards / shop floor | Job Card | 370 |
| `boms` | Engineering / BOM revisions | BOM | 390 |
| `components` | Engineering components / purchased parts | BOM | 405 |
| `operations` | Planned BOM operations | BOM | 417 |
| `materials` | Material requirements / shared warehouse stock | Work Order | 428 |
| `stock` | Stock movements | Stock Entry | 442 |
| `finished` | Finished production receipts | Stock Entry | 454 |
| `tasks` | Project tasks / pipeline | Task | 467 |
| `integrations` | Machine integration logs | Sarathi Machine Integration Log | 481 |
| `issues` | Data quality and alerts | Project | 496 |
| `workstations` | Workstations & workload | Workstation | 506 |
| `operations_catalogue` | Operations catalogue | Operation | 522 |
| `warehouses` | Warehouses catalogue | Warehouse | 532 |
| `customers` | Customers catalogue | Customer | 543 |
| `suppliers` | Suppliers catalogue | Supplier | 554 |
| `workstation_types` | Workstation types | Workstation Type | 565 |
| `plant_floors` | Plant floors | Plant Floor | 573 |
| `routings` | Routings | Routing | 583 |
