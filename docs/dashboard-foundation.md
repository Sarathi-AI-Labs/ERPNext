# DASH-001 — Dashboard Foundation & Architecture

Status: ready for architecture review; approval not yet recorded. Inspected 13 October 2026 on branch `feature/Gaurav_2`. Scope is foundation documentation only: no dashboard implementation, child-task execution, database migration, image build, deployment, or GitHub status change.

## Evidence and limits

This document distinguishes **source-verified**, **runtime version observed**, **historical evidence**, and **proposed** behavior. Source presence does not prove a screen or business calculation works in the current installation.

- Repository instructions: no `AGENTS.md` was found by the repository search. Applied the [dashboard skill](../.agents/skills/sarathi-erpnext-dashboards/SKILL.md) and the supplied DASH-001 instructions.
- Source inspected: both apps' hooks, setup code, page JSON/JS/Python, frontend controllers/styles, API modules, custom DocType metadata, test definitions, packaging, Containerfile, Compose references, and CI configuration.
- Runtime version observed with `docker exec frappe_docker_main-backend-1 bench version`: ERPNext **16.33.0**, Frappe **16.31.0**, both Sarathi apps **0.0.1**. This identifies bench packages, not proof of site installation metadata or source equality with the working tree.
- Local tools observed: Python 3.13.2, Node 22.14.0; Docker services are running. No authenticated browser, live business-data reconciliation, role probe, or transaction test was executed for this documentation task.
- [7 October audit](sarathi-dashboard-audit-2026-10-07.md) reports earlier rendering, API and regression checks plus unresolved finance/access defects. Those results are historical, not rerun here.
- Existing untracked [navigation/cache notes](dashboard-navigation-cache.md) and [owner loader repair notes](owner-blank-page-fix.md) describe more recent local changes. Read and preserved; their claims were not independently retested here.

### Pre-existing work preserved

At entry, tracked modifications existed in `pwd.yml`; owner dashboard CSS, controller JS, page HTML and page JS; production dashboard CSS, controller JS and page JS. Untracked files included `.agents/`, the two notes above, and production runtime/assistant JS/CSS. None were reset, overwritten, staged, or committed. This task adds only this document.

## Current application structure and routes

Paths below are relative to the repository. Under each app, the Python package has the same name as its outer directory.

| Component | Source-verified implementation | Responsibility today |
| --- | --- | --- |
| Owner Desk page | `sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/` with `.json`, `.js`, `.html`, `.py` | Page name `sarathiownertower`; app-screen hook points to `/desk/sarathiownertower` |
| Production Desk page | `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/` with the same file types | Page name `sarathicontroltower`; app-screen hook points to `/desk/sarathicontroltower` |
| Owner frontend | `sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js`, `public/css/sarathi_owner_dashboard.css` | `frappe.SarathiOwnerDashboard`, summary/detail/report rendering, filters and refresh |
| Production frontend | `sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`, `public/css/sarathi_dashboard.css` | `frappe.SarathiIndustrialDashboard`, organization/customer/project navigation, operational reports, accounting/subcontracting views |
| Shared runtime and assistant | Production `public/js/sarathi_dashboard_runtime.js`, `sarathi_dashboard_assistant.js`, and `public/css/sarathi_dashboard_assistant.css` | Both page loaders use these currently untracked assets; active-host lifecycle, loading, scoped browser eviction and assistant attachment |
| Alternate/legacy surface | Production `public/js/sarathi_website_tower.js`, `public/css/sarathi_control_tower.css`, `api/control_tower.py`, `api/data.py` | Separate API/UI paths coexist; do not assume they are the active Desk implementation or delete them without caller analysis |
| Module/detail browsing | Owner `public/js/sarathi_module_browser.js`, `public/css/sarathi_module_browser.css`, `api/module_catalog.py`, `api/detail_analytics.py`, `api/quick_details.py` | Native module/record/report discovery and quick detail support; preserve callers, even where launcher UI is disabled |
| Setup and navigation metadata | Both `hooks.py`, `setup/install.py`, `desktop_icon/*.json`; production workspace/report metadata | Install/migrate page roles, desktop icons, links, custom relationships and notifications |
| Shop floor | No dedicated page found in either app's page inventory | Proposed future page in `sarathi_visibility`; native Job Card access is not equivalent to an assignment-scoped workboard |

The two page Python files only set `context.no_cache = 1`; Desk behavior resides in page JS and the public controllers, not a substantial page Python backend. Owner hooks globally include owner CSS/JS. Production hooks globally include prefill JS and `sarathi_control_tower.css`, while the active page also loads `sarathi_dashboard.css`: preserve this distinction when auditing CSS effects.

Both page loaders share an initialization promise, load runtime first, request controller/style assets, instantiate only on the matching route, call `show`, and activate the shared host. They declare hide callbacks; runtime also observes router changes. Retain that lifecycle intent and the loader repair's plain asset paths. Runtime currently fetches/injects assets and caches asset promises; dependency order and compatibility with Desk loading/CSP need testing before generalizing it.

## Current frontend-to-backend flow

1. Frappe resolves the registered Desk Page and its role metadata.
2. Page JS loads custom assets and initializes the dashboard controller.
3. Owner uses `frappe.call` for context, summary, page data, reports and quick details. Production dispatches to `sarathi_visibility.api.dashboard.*`, with separate accounting/subcontracting calls.
4. Custom Python services read ERPNext documents/ledgers or execute existing report logic, assemble response structures, and return them for rendering. Some branches use permission-aware ORM queries; others use unrestricted queries or SQL and need review.
5. Custom-app document-event hooks publish payload-free invalidation events after commit. Frontends also poll while active. These are record-refresh signals, not physical machine telemetry.
6. Native links/forms remain the transaction surface; additional legacy custom mutation and assistant paths exist and must be assessed separately from dashboard reads.

### API inventory at the architectural boundary

Module paths use their Python import names; all listed names were found in source. A whitelist declaration does not certify authorization correctness.

| Module | Existing public methods / key helpers |
| --- | --- |
| `sarathi_owner.api.owner_dashboard` | Whitelisted `get_owner_context`, `get_owner_summary`, `get_page_data`, `get_live_report_data`, `clear_owner_cache`; internal page/chart loaders and `broadcast_live_event` |
| `sarathi_owner.api.quick_details` | Whitelisted `get_details` |
| `sarathi_owner.api.module_catalog` | Whitelisted `get_catalog`, `get_entry`; metadata revision and invalidation helpers |
| `sarathi_owner.api.pipeline` | Internal `get_project_pipeline` and relationship resolution, called by owner service |
| `sarathi_visibility.api.dashboard` | Whitelisted `get_summary`, `get_report`, `get_record`, `export_report`; POST `associate_customer` creates a customer/company association |
| `sarathi_visibility.api.dashboard_data` | Internal `load`, `parse_filters`, `rows`, `children`, `check_link`, shared by active dashboard/report services |
| `sarathi_visibility.api.production`, `.pipeline` | Internal production analysis/activity and explicit line-level pipeline attribution |
| `sarathi_visibility.api.accounting` | Whitelisted `get_accounting_dashboard`; internal `get_accounting_card_summary` |
| `sarathi_visibility.api.subcontracting` | Whitelisted `get_subcontracting_dashboard`; internal `get_subcontracting_card_summary` |
| `sarathi_visibility.api.control_tower` | Whitelisted `get_dashboard`, `get_organization_summary`, `get_project_summary`, `get_project_boms`, `get_project_materials`, `get_project_production`, `get_workstations`, `get_stock_entries`, `get_finished_goods`, `get_form_schema`; mutation endpoints `update_project`, `update_task`, `recalculate_progress`, `sync_tubepro`, `sync_cypcut`, `sync_tally` |
| `sarathi_visibility.api.agent_chat` | Whitelisted POST `send_message`, GET `get_suggestions`; imports `ERPNext_Agent.core.state`, `.workflow` and `.tools.client` |

Owner already imports production accounting and dashboard summary services. Both page loaders use production shared assets. Therefore the recommended dependency direction is **owner -> visibility -> ERPNext/Frappe**, not a new circular shared-app relationship. Current package metadata does not establish this whole application dependency/install contract: owner has no declared project dependency list, visibility declares `frappe`, and assistant imports require separate environment provisioning.

### Data and custom metadata

Source references include Company, Customer, Project, Task, Sales Order/Item, Sales Invoice/Item, Delivery Note, Purchase Order/Receipt/Invoice, Material Request, Supplier, Payment Entry, GL Entry, Account, Cost Center, Budget, Warehouse, Item, Bin, Stock Ledger Entry, Stock Reservation Entry, Work Order/Item/Operation, Job Card/Time Log/Operation, BOM/Item/Operation, Routing, Operation, Workstation/Type, Plant Floor, Production Plan, Stock Entry/Detail, Pick List, Quality Inspection, and Subcontracting Order/Receipt. Availability and fields still require site-level verification in DASH-002; a string in code is not installed-schema proof.

Five app-owned DocTypes are present under production `sarathi_visibility/doctype/`: Sarathi Customer Organization, Sarathi Project Controller, Sarathi Material Requirement, Sarathi Production Tracker, Sarathi Machine Integration Log. The first declares System Manager, Manufacturing Manager/User, Sales User and Sarathi Super Admin permissions; the other four declare System Manager permissions. They are not evidence of complete supervisor/operator access or active machine integration.

`setup/dashboard.py` uses Frappe's Custom Field mechanism for `Project.custom_sarathi_manufacturing`, `Project.custom_sarathi_bom`, `BOM.custom_sarathi_project`, and contains relationship backfill and lifecycle validation. Install/migrate setup also changes page/icon/sidebar records. These are existing custom-app behaviors, not core-source edits, but migrations have business/metadata side effects: do not run them as read-only inspection or introduce new standard-DocType customizations in DASH-001.

## Current permissions and risks

Owner Page JSON permits Sarathi Owner, System Manager and Manufacturing Manager. `api/permissions.py` mirrors owner access and special-cases Administrator. Finance access has a broader role set (Accounts Manager/User, Auditor, Sarathi Owner, System Manager, Administrator) and a fallback based on GL Entry/Sales Invoice read permission. This does not itself apply row/company restrictions.

Production Page JSON permits Manufacturing User, Manufacturing Manager, System Manager and Sarathi Super Admin. Its permission helper distinguishes super-admin mutation rights from setup editing; legacy mutation endpoints call `require_super_admin`. `dashboard_data.parse_filters` validates dates/status, checks selected Company/Customer/Project read access and rejects inconsistent relationships. `rows` uses `frappe.get_list`; child reads constrain parent names and permitted fields. These are useful patterns to retain, not proof that every related endpoint is secure.

| Finding | Evidence and consequence | Follow-up boundary |
| --- | --- | --- |
| Inconsistent row/company authorization | Owner context uses `get_all`; financial services use raw SQL and `get_all`. Earlier audit demonstrated company-restriction bypass | DASH-003 defines intended scope; DASH-006 implements uniform permission-aware helpers; direct API tests later |
| Unsupported financial assumptions | Accounting source still contains zero-GL invoice fallback, 70/30 expense split, expense × 1.35 budget, and expense × 0.1 commitment | DASH-004 documents true definitions; finance implementation/reconciliation belongs to DASH-009, not this task |
| Pagination after full load | `dashboard_data.rows` has `limit_page_length=0`; `get_report` loads all data then slices a bounded page | DASH-006 designs efficient server-side pagination/aggregation without changing totals or attribution |
| Broad cache mutation in a UI flow | Whitelisted `clear_owner_cache` calls `frappe.clear_cache()` and frontend invokes it | Separate read contracts from maintenance; targeted invalidation, authorization and caller assessment in follow-up |
| Missing dedicated shop-floor scope | No separate Page or complete supervisor/operator assignment policy discovered | DASH-003 captures role/scoping requirements; DASH-022–026 implement later |
| Existing core patch in build | `sarathi_visibility/Containerfile` executes `patch_socket_backend.py`, which rewrites `apps/frappe/realtime/utils.js` and middleware authentication JS | Conflicts with mandatory read-only-core architecture. Do not run this build recipe as approved deployment. Release remediation must use supported infrastructure configuration without core modifications; removal/replacement is outside this documentation run |
| Setup side effects and older endpoint overlap | Existing custom fields, backfills, validation hooks, legacy mutation services and alternate frontend | Preserve working behavior; trace callers and migration impact before any refactor |
| Assistant external dependency | `ERPNext_Agent` imports plus cache-persisted conversation state and transactional capabilities | Preserve existing integration; separately verify provisioning, session ownership, permissions and confirmation flow before release; not the shop-floor write service |
| CSS/lifecycle complexity | Global hooks plus page styles, many overlapping breakpoints, shared injected assets and event/poll refresh | DASH-005 defines shared primitives; mobile, inactive timers and stale responses need fresh tests |
| Demo context in documentation | Visibility README names a particular company/project/order | Treat as examples, not tenant configuration; never propagate into production defaults |

No correction of these risks is claimed by DASH-001. Existing unsafe behavior is recorded, not approved for reuse unchanged.

## Recommended architecture and dashboard boundaries

**Decision:** retain two custom apps and three connected Frappe Desk pages. One client company gets one dedicated VPS/site/database environment; its many Customer records live inside that installation. No installation per Customer, no shared cross-client database.

| Experience | Owns | Shares / links out |
| --- | --- | --- |
| Owner (`sarathi_owner`) | Business performance, financial and customer trends, project/delivery health, high-level manufacturing/inventory risks, management decisions | Production summary services and authorized control-tower drill-down; native accounting reports and approvals |
| Production (`sarathi_visibility`) | Factory-wide Work Orders/Job Cards, readiness, delays, bottlenecks, workstation recorded activity, quality/subcontracting exceptions | Native production/stock records; shop-floor job detail; owner sees summarized impact |
| Shop floor (future Page in `sarathi_visibility`) | Authenticated user's assigned operations; supervisor's authorized team/area; current/next work and permitted actions | Same production services with narrower scope; valid native Job Card/stock workflows, never owner financial datasets |

Keep established owner/production URLs. Proposed shop-floor slug: `sarathishopfloor`; reserve only after route-conflict/site metadata checks in its implementation task. No route is created here.

UI -> custom permission-aware read service -> existing ERPNext records/report logic is the read path. Shop-floor command -> custom authorization/idempotency adapter -> existing ERPNext document/controller/workflow method is the future write path. Starting time, pausing time, reporting output and submitting manufacture are distinct operations. No direct field hacks, bypasses, speculative telemetry, or duplicated accounting/stock engines.

**Core boundary:** ERPNext/Frappe source, including `ERPNEXT_MAIN/` and installed bench `apps/erpnext`/`apps/frappe`, stays read-only. All new executable dashboard code, assets, tests and app-owned migrations belong in the Sarathi apps. No patches, monkey-patching, core-controller overrides or direct core schema modifications. Existing metadata customizations must be documented and reviewed; they do not grant permission for arbitrary new schema changes. The conflicting build helper above must be addressed before a compliant release.

### Foundation conventions (proposed, not implemented)

- Keep Page registration/lifecycle in each existing module's `page/<slug>/`; keep controllers/styles in app `public/`; thin whitelisted APIs in `api/`, with reusable pure calculations and permission/query helpers behind them. Shared operational primitives live in visibility because owner already depends on it. Extract incrementally, retain endpoint compatibility and avoid a third app.
- Shared UI covers spacing/type/color/status tokens, header/navigation, filter panel, KPI shell, table/card adapters and state panels. Scope CSS to Sarathi roots; avoid overriding Desk globally. Role-specific screen density remains intentional.
- Server authorization includes authenticated Desk access, dashboard capability, underlying DocType/document read/write, allowed companies, User Permissions and assignment/area scope. Client roles and hidden controls are hints, never enforcement. Totals, options, exports, charts and drill-downs use the same permitted population. SQL/child-table queries require explicit equivalent scope.
- Normalize and validate filter inputs server-side: company/customer/project relationships, date order/timezone, warehouse, status allowlist, bounded pagination and sort allowlist. Define each dimension's applicability; unsupported financial filters must be labeled unavailable, never silently ignored. Preserve URL/filter context on drill-down/return.
- Read responses should include applied filters, generation/last-success time, currency/UOM and availability; distinguish missing, denied, failed and measured zero. Separate bounded detail endpoints from aggregates. Cache only by site, permission/user scope and normalized filters; define invalidation and avoid N+1 joins.
- Show loading on initial fetch, explicit empty data, actionable errors, denied access and stale/offline status retaining last-success time. Prevent old responses overwriting new filters; suspend polling and clean listeners on navigation. Never silently queue or replay production commands offline.
- Every KPI definition records source fields/report, formula/grain, status/docstatus exclusions, date basis, currency/UOM, supported filters, scope, refresh, drill-down, reference report and reconciliation tolerance. Revenue uses the agreed Sales Invoice accounting basis; profit uses P&L logic; valuation uses stock valuation logic; historical receivables require as-of payment semantics. No full KPI dictionary is implemented here.
- New write methods must recheck state/permission, use existing ERPNext methods, enforce server-side duplicate prevention/concurrency handling and record an audit trail. Do not reuse assistant or legacy mutation endpoints without specific action mapping and validation.

### Responsive requirements

Use actual available Desk content width, with starting ranges under 480, 480–767, 768–1023 and 1024+ CSS px. Phones use a compact header/menu, stacked cards and expandable filters; tablets use two-column grids; desktop can show full navigation and tables. Owner emphasizes key business figures; production puts blockers/overdue work first with searchable cards; shop floor puts current operation and large controls first.

No page-level horizontal scrolling. Wide tables become cards or intentionally scroll in their own container; charts resize and retain readable labels. Controls need accessible labels/focus/contrast; status combines text/icons and color. Shop-floor touch targets aim for 44–48 CSS px or larger. Verify both orientations, long record names, dropdowns/date pickers/dialogs, error states and physical touch hardware where relevant. Existing media queries are evidence of responsive intent, not acceptance certification.

## Retain / improve / build mapping

| Retain and preserve | Improve in scoped follow-ups | Build only in later tasks |
| --- | --- | --- |
| Both URLs, app boundaries, record/report links, customer/project hierarchy | Permission/query consistency and filter contracts | Dedicated assignment-scoped shop-floor Page |
| Explicit Project/BOM/Work Order relationships and historical BOM attribution | Source-backed financial definitions and reconciliation | Validated operational action adapters and duplicate prevention |
| Report/export and quick-detail behavior, schema-aware loading | Query bounds, shared primitives, accessibility and lifecycle tests | Missing owner/manager requirements after detailed gap audit |
| Shared active-host/assistant intent and plain-path loader repair | Dependency/install declaration and core-patch-free release recipe | Advanced analytics only after reliable sources exist |

## Child-task handoff without implementation

| Next task | Input from DASH-001 | Deliverable owned by that task |
| --- | --- | --- |
| DASH-002 — detailed app/route audit | Source paths, API families, legacy overlap, prior audit and risk register | Full file/function/caller inventory, installed metadata/assets verification, behavior/gap map; distinguish workspace from running site |
| DASH-003 — role/permission matrix | Current page/helper roles, known scope gaps, proposed dashboard boundaries | Explicit owner/manager/supervisor/operator capabilities, company/area/assignment policy and authorization requirements |
| DASH-004 — KPI dictionary | Definition schema and identified finance/readiness risks | Exact formulas, source fields, supported filters, report reconciliation and edge-case expectations |
| DASH-005 — shared responsive components | Visibility ownership of shared primitives, existing lifecycle/assets to preserve | Reusable scoped components and responsive states, incremental adoption with no route regressions |
| DASH-006 — permission-aware data helpers | Existing `parse_filters`/parent-scoped child patterns and permission/pagination gaps | Consistent validation, access-scoped aggregates/detail reads, pagination/query plan and safe cache behavior |

Practical order: detailed audit establishes actual sources/callers; role and KPI definitions then inform shared data/UI work. The GitHub parent-epic dependency labels are organizational grouping, not a requirement to finish every epic child before inspecting the first child. DASH-001 does not declare any child complete.

## Testing, configuration, release and maintenance foundation

Six test modules exist: owner `test_owner_dashboard.py` (15 test methods), `test_quick_details.py` (14), `test_module_catalog.py` (9); visibility `test_dashboard.py` (15), `test_accounting.py` (4), `test_subcontracting.py` (4). These counts describe definitions, not results. Tests import Frappe; some connect to site `frontend`, and production transactional tests create fixtures/roll back. Do not run the entire suite against a business site merely to validate a document. Existing CI includes pre-commit, ERPNext JS tests, and custom-app Semgrep; that does not establish complete dashboard-specific integration/browser coverage.

Future validation must cover pure calculations, permission-scoped API integration, native workflow transactions, source/report reconciliation, representative volumes, refresh/navigation and desktop/tablet/phone rendering using actual non-admin roles. Keep a requirement -> implementation -> test -> result/evidence matrix. Tests that confirm response keys do not establish accounting correctness.

Keep per-site companies, warehouses, timezone, currency, shifts, assignments and production areas configurable, separate from Customer identity. Installed apps and dependent runtime packages/assets must be included in release manifests. Track app versions, changes, metadata/migrations and native ERPNext compatibility. Document database/files/config backup, restore rehearsal, upgrade and schema-compatible rollback on a test site before a VPS release. Audit current setup side effects and legacy rename migrations first. The existing `INSTALL.md` cannot be treated as a compliant recipe while its Containerfile patches core. No install/migrate/build/restart command was run here.

### Unresolved decisions

- Intended owner finance capabilities versus Manufacturing Manager access need DASH-003 review.
- Assignment source (Employee/user/Job Card/workstation), supervisor area/team and shift configuration are not established.
- Financial accounting basis, customer/project allocation limits and material reservation semantics need explicit dictionary/site verification.
- Core-patch-free websocket deployment approach and complete assistant/app dependency provisioning require later release work.
- Current live site metadata, financial reconciliation and physical-device/browser behavior remain unverified in this run. These do not prevent architecture review, but block claims of release readiness.

## DASH-001 acceptance and validation

| Criterion | Result |
| --- | --- |
| Current structure/routes/data flow recorded | Documented from source; runtime versions observed |
| Three dashboard boundaries/recommended architecture | Documented; shop floor clearly proposed |
| Existing functionality preserved | Documentation-only change; app/local-change hashes checked for preservation |
| Gaps/risks/assumptions/dependencies | Recorded with source versus historical distinction |
| DASH-002–006 can proceed | Handoff and sequencing documented; no child implementation |
| Changes relevant to this task | Only `docs/dashboard-foundation.md` added |
| Applicable checks | Source route/metadata assertions, document link checks, preservation hashes and whitespace checks; results recorded below |

Executed validation:

- `git branch --show-current` / `git status --short`: confirmed branch and pre-existing tracked/untracked work; final status adds only this document to the entry list.
- `rg --files` and targeted `rg -n` / `Get-Content`: inspected the source/documentation inventory described above. An initial no-match `AGENTS.md` search returned exit 1; a PowerShell wildcard passed to one `rg` invocation was rejected and the search was rerun using directory plus `-g '*.py'`. Neither failure changed files.
- `docker ps --format '{{.Names}}'` and `docker exec frappe_docker_main-backend-1 bench version`: succeeded; services and package versions observed without invoking app setup/migrations.
- Python AST/JSON inventory: read whitelisted method definitions, five custom DocTypes' permission roles and six test modules' test-method counts successfully, without importing/executing application code.
- Python source/document assertions: **passed** for both page JSON route names/roles, lifecycle callback presence, accompanying HTML/Python files, all relative Markdown links and no trailing whitespace in this document.
- SHA-256 snapshots of custom-app files and all pre-existing dirty/untracked files (excluding generated bytecode): **matched** before and after document creation. No application or existing local-work file changed.
- `git diff --check`: **passed**, with Git line-ending conversion warnings on pre-existing modified app files. `git diff --name-only -- ERPNEXT_MAIN`: empty. The new untracked document was checked separately by Python because ordinary `git diff --check` does not inspect untracked files.
- Business integration suites, browser/device checks, restricted-role probes and financial reconciliation: **not run**; not necessary to validate this documentation-only change and no current runtime success claim is made.

Architecture approval and live-system acceptance are separate from this documentation handoff. Recommended next task: **DASH-002**, to complete the detailed caller/installed-schema/behavior gap audit before implementing role, metric or shared-component changes.
