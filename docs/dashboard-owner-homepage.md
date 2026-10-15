# DASH-007 epic / DASH-008 homepage and filters

Scope: implement DASH-008 only, as explicitly instructed in the DASH-007 attachment. DASH-009 through DASH-013 remain separate. Inspected architecture, audit, role matrix, KPI dictionary, shared UI and data-helper documentation plus active owner controller/template, route loader and APIs. Baseline hashes retained in `scratch/dash-008/baseline.json`; previous dirty work is preserved.

| Existing surface | Retain / improve decision |
| --- | --- |
| Desk route, owner controller, sidebar and detail/report pages | Retain; add an app-owned homepage adapter rather than rewriting the application |
| Shared runtime and `frappe.sarathiUI` | Reuse layout/header, filters, actions, record lists, badges and state patterns |
| DASH-006 data helpers and DASH-003 owner capability | Reuse native record/field/company permissions and bounded option/record reads |
| Legacy homepage aggregate | Keep source and legacy detail views; stop presenting its unreconciled metrics as the new homepage. DASH-004 already records finance/filter defects |
| Legacy global filters | Preserve on existing detail pages. New homepage gets explicit Company/date/Customer/Project controls and clear applied-scope text |
| Company selection | Add real authorized selection; the old controller currently returns `company: ""` regardless of context |
| Unsupported financial/trend/risk features | Clearly mark unavailable pending child-task validation; do not fabricate numbers/charts or implement their formulas here |

Homepage previews will show native Project and Work Order records only, with documented date bases. Customer-only manufacturing scope is unavailable without a verified allocation relationship; selecting a matching Project permits its direct Work Order scope. No KPI formula or workflow is added.

## Implemented behavior

The existing `/desk/sarathiownertower` now opens the new owner homepage. An app-owned adapter loads after the original controller and before its first instance is created. The original controller, inline template, sidebar, report runner, record modals and legacy detail pages remain intact. No ERPNext/Frappe source or standard permissions changed.

- A shared header displays the dashboard title, company context and the applied scope. The existing freshness label uses the server's successful generation timestamp; it does not claim machine telemetry or live financial synchronization.
- Company selection uses native readable Companies. Multiple accessible companies require selection; exactly one may be selected automatically. The old blank-company default is not used for the homepage. The selected company is also included when navigating existing detail pages, without claiming those legacy calculations are newly reconciled.
- A shared filter form collects Company, From date, To date, Customer and Project. Apply sends only those five supported keys. Reset clears optional filters and retains the selected company. Dates are custom calendar bounds, avoiding an invented fiscal-year configuration.
- Searchable option controls query permission-aware backend options in pages of 25. “More” controls appear only when another page exists. Project options are company- and optionally customer-scoped; Company/Customer are native-readable shared masters, with the DASH-006 ownership caveats. Option responses use sequence/scope guards to discard stale lookups.
- Desktop filters remain expanded; compact screens collapse them, while the selected scope stays visible. Additional option search controls are in a separate disclosure to keep the main form compact. Inputs persist when navigating, resizing and refreshing.
- The homepage shows at most six Project and six Work Order records with their recorded statuses/start schedules. These are previews, not new health scores, production calculations, counts or financial KPI cards. Shared responsive record lists become cards on phones. Native form actions use `frappe.set_route`; the Control Tower action uses its existing route.
- The same date bounds apply to **Project expected start** and **Work Order planned start**, explicitly labelled on screen. These are schedule cohorts, not accounting posting periods or delivery promises.
- A Customer-only scope does not display company-wide Work Orders as customer-specific. Manufacturing is unavailable until a matching Project provides the verified direct relationship. Project/Customer/company mismatches are denied server-side.
- The homepage explicitly says financial indicators await accounting reconciliation, and other executive analytics are not yet available. Product text does not expose backlog task IDs. No fake amounts, trends, stock estimates, alerts or approval buttons were added.
- Loading, empty, denied, offline, recoverable-error and stale-data states use shared primitives. Read retries are safe. Same-scope background failures can retain the last successful preview; denied or changed-scope failures discard old records so a later offline retry cannot redisplay denied data. Request guards discard superseded responses.
- Refresh performs a read; it no longer invokes the legacy global cache-clearing mutation. Existing detail refresh uses its original read renderer. Existing assistant/navigation assets remain as before.

The previous aggregate homepage renderer and APIs are retained in source, but its unreconciled figures are no longer presented as the default homepage. DASH-004 recorded accounting/filter limitations; this run does not certify those figures by reusing them. Existing finance/detail/report views remain accessible for later child-task improvement.

## Backend contracts and security

`sarathi_owner.api.homepage.options(resource, company=None, customer=None, search="", start=0, **extra)` is GET-only and owner-gated. Only `companies`, `customers` and `projects` are accepted. Project options require Company; shared-master options reject inappropriate Company/Customer scope rather than silently claiming ownership. The method delegates to DASH-006's bounded, permission-aware option helper.

`sarathi_owner.api.homepage.get_homepage(filters=None, **extra)` is GET-only and owner-gated. It accepts only Company, Customer, Project and the two dates; strict types, dates, native link/document/field/User Permissions and company scope come from DASH-006 helpers. Project is translated to the Project list's exact-name condition. Work Orders use their verified Project field. No unrestricted SQL, arbitrary DocType/field access or aggregation is introduced. Unexpected query parameters are rejected except Frappe/browser transport metadata as documented in DASH-006.

The response contains `applied_filters`, `generated_at`, bounded `projects`, `work_orders` with an explicit availability flag/reason, `date_basis` and authored availability messages. Missing Work Order read permission makes that preview unavailable. Native Project read permission is required for the homepage's Project preview; absence yields the shared denied state. Owner capability alone never grants underlying document permissions.

Errors follow DASH-006's authored validation/permission errors and sanitized internal-error handling. Option and preview reads are side-effect-free. No new business records, workflows, migrations or permission grants are part of the implementation.

## Exact file manifest and loading

Created:

- `sarathi_owner/sarathi_owner/api/homepage.py`
- `sarathi_owner/sarathi_owner/public/js/sarathi_owner_homepage.js`
- `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css`
- `sarathi_owner/sarathi_owner/tests/test_homepage.py`
- `sarathi_owner/sarathi_owner/tests/audit_homepage_local.py`
- `docs/dashboard-owner-homepage.md`
- `docs/dashboard-owner-homepage-evidence/browser-results.json`
- `docs/dashboard-owner-homepage-evidence/owner-home-390.png`
- `docs/dashboard-owner-homepage-evidence/owner-home-768.png`
- `docs/dashboard-owner-homepage-evidence/owner-home-1440.png`

Modified: `sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.js` only. The loader awaits the existing controller assets, then awaits the two new `/assets/sarathi_owner/` homepage assets before instantiation. This prevents prototype installation racing the original controller. No frontend framework, dependency, third app or cross-app circular import was added. The pre-task hash comparison confirms that this loader is the only pre-existing file changed; all earlier dirty files remain as they were at task entry.

Local `bench --site frontend clear-cache` exposed the custom page-loader change, and the local backend was restarted to expose the new custom Python module. No VPS deployment, full migration, core modification or GitHub status change was performed.

## Validation and evidence

Executed on the local `frontend` site with Frappe 16.31.0 / ERPNext 16.33.0:

| Check | Actual result |
| --- | --- |
| `sarathi_owner.tests.test_homepage.run` | **27 passed, zero skips**: eight focused homepage tests plus 19 inherited DASH-003 security regressions |
| Owner and native permission scope | Real transactional users/Company/Customer/Project fixtures exercise owner access, manager/operator/supervisor/unrelated denial, forged company/project IDs, mismatched readable links and narrow options |
| Input/preview contracts | Invalid/reversed dates, unsupported fields/resources, ambiguous company, six-row bounds and explicit unavailable manufacturing tested |
| Real browser data | Administrator received existing ERPNext Project/Work Order records; six of each rendered in the tested populated company; initial multi-company selection stayed blank |
| Responsive rendering | 360, 390, 480, 767, 768, 1023, 1024, 1440 CSS px plus 844×390 landscape; no page-level horizontal overflow at any width |
| Filter and navigation behavior | Date Apply, optional-filter Reset retaining Company, existing Project navigation and return preserving applied scope verified |
| Resilience | Offline same-scope data retention and successful recovery verified; injected permission denial clears cached rows and they do not reappear offline |
| Runtime regressions | Zero JavaScript errors and no unexpected HTTP errors; intentionally injected permission-denied response is separately recorded |
| Old aggregate calls | Zero `get_owner_summary` requests from the new homepage |
| Source safety | Python/JavaScript syntax checks, task diff review and pre-task hash preservation checks |

The browser audit uses a temporary Administrator session, revokes it in `finally`, reads existing business records and injects browser-only offline/denied conditions. Backend security tests use native rollback fixtures and leave no test business records. The tests do not certify financial reconciliation or all legacy page formulas.

Reproduce:

```powershell
docker exec -w /home/frappe/frappe-bench frappe_docker_main-backend-1 bench --site frontend execute sarathi_owner.tests.test_homepage.run
python sarathi_owner/sarathi_owner/tests/audit_homepage_local.py
```

The manual audit uses the existing local Python Playwright installation and Chromium. Results and screenshots are saved in ignored `scratch/dash-008/`; selected evidence is retained here: [browser results](dashboard-owner-homepage-evidence/browser-results.json), [phone](dashboard-owner-homepage-evidence/owner-home-390.png), [tablet](dashboard-owner-homepage-evidence/owner-home-768.png), [desktop](dashboard-owner-homepage-evidence/owner-home-1440.png). The audit requires the documented local container/site names and existing Project/Company records. Full Firefox/WebKit ERP sessions, physical factory hardware, formal screen-reader certification, large datasets and VPS latency were not tested in this run. DASH-005's component checks are historical evidence, not rerun claims.

## Integration with completed child tasks

The Owner Dashboard homepage (`sarathi_owner_homepage.js` and `homepage.py`) provides the core executive container and global filter bus. As child tasks have been completed, verified domain modules have been cleanly integrated into the homepage:

- **DASH-008 Foundation & Filters:** Responsive layout, shared header, multi-company selector, calendar date filters, option searches, empty/error/offline resilience, and native Desk routing.
- **DASH-009 Finance KPIs (`data.finance`):** Integrated via `sarathi_owner.api.finance_kpis.get_finance_kpis`. Displays reconciled Revenue, Gross/Net Profit, Margin %, Accounts Receivable, and Accounts Payable, with drill-downs to native P&L and Accounts Receivable/Payable reports.
- **DASH-010 Customer & Sales Analytics (`data.sales`):** Integrated via `sarathi_owner.api.sales_analytics.get_sales_analytics`. Displays customer income attribution, Top Customers, monthly/daily trend chart, and undelivered delivery backlog value.
- **DASH-011 Project & Delivery Health (`data.project_health`):** Integrated via `sarathi_owner.api.project_health.get_project_delivery_health`. Displays project portfolio status & health cards, recorded progress with method details, incomplete task attention list, and undelivered quantity commitments by Item/UOM.

## Remaining epic work and next task

- **DASH-012:** Approved manufacturing summaries, UOM-aware production achievement comparisons, inventory valuation, and reservation-aware material shortages.
- **DASH-013:** Authorized approvals, executive management exceptions, and unified alert drill-downs with explicit triggers.

Recommended next task from backlog: **DASH-012 — Implement manufacturing and inventory summary**.

