# DASH-005 — Shared responsive UI foundation

## Inspection and implementation boundary

Reviewed DASH-001 architecture, DASH-002 audit, DASH-003 permission matrix, DASH-004 KPI definitions, the dashboard skill and responsive acceptance requirements. Baseline hashes of tracked and untracked files are retained locally in `scratch/dash-005/baseline.json`. Existing uncommitted changes are preserved. ERPNext/Frappe source, backend behavior and metric formulas remain outside this task.

| Existing surface | Decision |
| --- | --- |
| Frappe Desk pages, page lifecycle and shared runtime loader | Retain; load the shared UI before dashboard controllers |
| Owner inline template and production page template | Retain actual active templates; enhance their existing controls in place |
| Existing filters and their event handlers | Retain values and backend contracts; add responsive disclosure without recreating inputs |
| Existing icons and Frappe Charts | Retain; no additional icon/chart dependency |
| Existing dashboard CSS and delegated drill-down handlers | Retain; shared styles are scoped to marked Sarathi roots |
| Duplicated KPI presentation, production badges and percentage bars | Reuse shared presentation helpers; supplied values remain authoritative |
| Table matrices | Keep horizontal scrolling inside labelled containers; ordinary shared record lists can become cards |
| Missing reusable layout, header, actions and state primitives | Implement in the production app for one-way consumption by owner and future shop-floor pages |

Implementation and browser evidence are recorded below after validation. This is a UI task, not certification of financial reconciliation, workflow permissions or complete dashboards.

## Shared API and consumption

`frappe.sarathiUI` is a plain JavaScript namespace. Both page loaders first await the existing runtime loading `/assets/sarathi_visibility/css/sarathi_ui.css` and `/assets/sarathi_visibility/js/sarathi_ui.js`, then load their existing page assets. Separate awaited stages prevent controller execution before the shared namespace exists. The owner app already consumes production-owned runtime/assistant assets; this extends that one-way dependency without another app or circular imports. HTTP asset delivery was verified against the local installation; no bundled framework or new dependency was introduced.

| API | Contract |
| --- | --- |
| `layout(options)` | Marked root, role-specific density, optional header and `.content` insertion point |
| `header(options)` | Title, description, company, optional valid timestamp and supplied action nodes; no invented live claim |
| `kpi(options)` | Supplied formatted value/unit/description/comparison; missing is an em dash, zero remains zero; interactive only with callback or valid destination |
| `filterBar(options)` | Labelled native inputs, loading/empty/error option states, `values()` and `setOptions()`, apply/reset callbacks and caller validation |
| `recordList(options)` | Column definitions, supplied rows, safe text or explicitly supplied DOM renderers, optional search/sort/page/action callbacks; phone cards or explicit scroll mode |
| `status(value)` | Actual supplied label with restrained presentation tone; never changes stored workflow status |
| `progress(options)` | Supplied percentage and optional textual quantity/status; invalid/blank/NaN is unavailable; visual width bounded to 0–100, original percentage remains in accessible text |
| `chart(options)` | Existing chart renderer plus title/description/state; call `.mount()` after attaching and `.dispose()` before removal |
| `observeChart(element, instance)` | Retains installed Frappe Charts' native ResizeObserver rather than adding competing redraws; returns cleanup |
| `action(options)` | Callback or same-origin HTTP destination required; pending deduplication, disabled/confirmation/success/error feedback, generic errors |
| `state(kind, options)` | Loading, empty, unavailable, denied, error, stale and offline patterns; retry offered only with explicit `retryKind: "read"` |
| `enhance(root)` | Idempotent legacy adapter: compact filters/menu, labelled table scroll regions, delegated keyboard activation; `.dispose()` releases adapter observers/listeners |

Callbacks perform the actual operations. Shared UI never calls an API, computes a KPI, infers assignments, or grants permissions. Filter validation is presentation feedback only; DASH-006 must independently validate all server parameters. Pass authored business messages to `state`, never exception strings. Consequential actions must supply a confirmation callback using the existing Frappe confirmation pattern, and still use validated backend operations. A button's pending guard is not server idempotency and cannot resolve uncertain transaction outcomes.

Future shop-floor consumption, after the same two shared assets have loaded:

```javascript
const ui = frappe.sarathiUI;
const screen = ui.layout({
  title: "Assigned work",
  density: "shop-floor",
  company: authorizedContext.company,
});
page.main[0].append(screen);
screen.content.append(ui.state("loading"));
// Replace with assignment-scoped records from a separately authorized data layer.
// Add production actions only after their workflows and permissions are implemented.
```

`recordList` sorting/search/pagination delegate to supplied callbacks. No control is added unless its callback exists. Sort actions remain outside the table header so they remain usable when phone cards visually hide column headers. Use `mode: "scroll"` for a genuine matrix. Progress does not derive a ratio from quantities: the backend must return unavailable for an invalid/zero denominator. Use `text` for an approved quantity equivalent alongside a supplied percentage.

## Existing-page integration

Owner uses shared KPI markup while retaining `.sod-card`, `.sod-label`, `.sod-kpi-val` and `data-action` for existing modal drill-down and smooth refresh. The legacy delegated handler remains the sole click owner; the shared adapter adds Enter/Space activation to its non-native buttons. Charts retain Frappe Charts, disable decorative animation and release listeners before replacement/navigation. The initial owner freshness label now waits for records rather than claiming live synchronization.

Production uses shared KPI DOM nodes with its existing read-only detail-modal callback, shared status badges, empty states and percentage presentation. Existing filters, queries, project/customer navigation and reports remain. Both pages retain their original layout/header templates while using the shared adapter and scoped responsive rules. Complex legacy manufacturing tables retain intentional horizontal scrolling inside labelled keyboard-focusable regions rather than being flattened into misleading cards.

Styles apply only under `[data-sarathi-ui]`. Design tokens inherit Frappe surface/text/border colors; focus outlines, wrapped text, readable status text and reduced-motion support are shared. Small phones use one KPI column, intermediate sizes allow two, desktop keeps the existing grid. Filter/menu disclosures preserve the original input elements and values. Standard controls target at least 44 CSS pixels; new shop-floor density uses 56-pixel controls and larger text. No complete shop-floor route was created.

## Exact task-owned files

Created:

- `sarathi_visibility/sarathi_visibility/public/js/sarathi_ui.js`
- `sarathi_visibility/sarathi_visibility/public/css/sarathi_ui.css`
- `sarathi_visibility/sarathi_visibility/tests/test_shared_ui_browser.py`
- `sarathi_visibility/sarathi_visibility/tests/audit_shared_ui_local.py`
- `docs/dashboard-ui-foundation.md`
- `docs/dashboard-ui-evidence/browser-results.json`
- `docs/dashboard-ui-evidence/sarathiownertower-390.png`
- `docs/dashboard-ui-evidence/sarathiownertower-1440.png`
- `docs/dashboard-ui-evidence/sarathicontroltower-390.png`
- `docs/dashboard-ui-evidence/sarathicontroltower-768.png`
- `docs/dashboard-ui-evidence/sarathiownertower-drilldown-390.png`
- `docs/dashboard-ui-evidence/sarathicontroltower-drilldown-390.png`
- `docs/dashboard-ui-evidence/shop-floor-component-fixture-390.png`

Modified, preserving previous working-tree changes:

- `sarathi_owner/sarathi_owner/public/js/sarathi_owner_dashboard.js`
- `sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.js`
- `sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`
- `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.js`

Local ignored scratch outputs contain the pre-task hash manifest, source snapshots, additional screenshots and audit output. No core source, backend file, existing CSS file, DocType or database schema was changed by this task.

## Validation and evidence

Executed locally on 13 October 2026:

| Requirement/check | Actual result |
| --- | --- |
| Shared presentation contract suite | 12 tests pass in Chromium, Firefox and WebKit; synthetic inputs are component fixtures, not dashboard business data |
| Both actual Desk routes | HTTP 200; authenticated Administrator received existing real API data; shared assets/root markers present |
| Responsive rendered pages | Both tested at widths 360, 390, 480, 767, 768, 1023, 1024, 1440 and landscape 844×390; page scroll width never exceeded viewport |
| Phone layout | Both actual KPI grids verified as a single column at 390 px |
| Existing controls | All measured visible button/input/select/role-button bounds at least 44×44 across the nine viewports on both pages |
| Filters/navigation | Expand/collapse retained status selection; existing production operational tab rendered; keyboard KPI activation opened each existing detail dialog |
| Standard ERP page | Native Company list navigation left no visible shared UI root |
| Runtime failures | Final actual-page audit: zero JavaScript errors, zero HTTP failures, zero blocked mutation calls; temporary audit session revoked |
| Component states/actions | Missing versus zero, escaped text, invalid progress, original statuses, disabled/pending/error/confirmation actions, read-only retry, filters, mobile sorting/search/page callbacks, focus and chart cleanup checked |
| Source checks | JavaScript syntax checks and task diff whitespace checks; baseline hashes establish only the four listed pre-existing files changed |

The initial browser run exposed competing chart redraws; the adapter now retains native resizing and owner chart lifecycle cleanup, with animations disabled. Expanded component tests also exposed an inaccessible mobile sort button in a visually hidden table header; sorting controls now remain outside that header. Final passing results above follow these fixes.

Reproduce component checks from the repository root:

```powershell
python sarathi_visibility/sarathi_visibility/tests/test_shared_ui_browser.py
$env:SARATHI_UI_BROWSER='firefox' # or webkit; default is chromium
python sarathi_visibility/sarathi_visibility/tests/test_shared_ui_browser.py
Remove-Item Env:SARATHI_UI_BROWSER
```

The existing local Python Playwright package and browser binaries were used without installing a framework. The manual `audit_shared_ui_local.py` requires the running local Docker stack, `frontend` site and the existing backend container name; it creates and revokes a temporary Administrator session without printing cookies. It guards known transaction-writing endpoints and stores results under `scratch/dash-005`. It is not a production-site test or a permissions certification. Local `bench --site frontend clear-cache` was used to expose changed custom page loaders; no migrations or core changes were required.

Evidence: [browser results](dashboard-ui-evidence/browser-results.json), [owner phone](dashboard-ui-evidence/sarathiownertower-390.png), [owner desktop](dashboard-ui-evidence/sarathiownertower-1440.png), [production phone](dashboard-ui-evidence/sarathicontroltower-390.png), [production tablet](dashboard-ui-evidence/sarathicontroltower-768.png), [owner drill-down](dashboard-ui-evidence/sarathiownertower-drilldown-390.png), [production drill-down](dashboard-ui-evidence/sarathicontroltower-drilldown-390.png). The [shop-floor fixture](dashboard-ui-evidence/shop-floor-component-fixture-390.png) demonstrates density and states only, not a functioning shop-floor dashboard.

## Limits and next task

Actual ERP page rendering was tested in Chromium; the reusable components were additionally tested in Firefox and WebKit. Full ERP sessions in those browsers, all custom subviews/dialogs, dark theme, physical gloves, industrial viewing distances and factory hardware remain unverified. Browser viewport testing does not establish those conditions. Readable text and visible keyboard focus are checked; no formal screen-reader or WCAG certification is claimed. Offline/stale/denied patterns are available to consumers; existing pages' complete network-state orchestration remains future page work.

No backend transaction tests, financial reconciliation, role isolation probes, installation/upgrade rehearsal, or VPS deployment are claimed for this UI task. Preserve the DASH-003/DASH-004 caveats. Shop-floor assignments/actions and complete role dashboards remain later tasks. Changes are ready for UI review, not production-release approval.

Recommended next: **DASH-006 — Build permission-aware filter and data helpers**, so these components receive validated, scoped data consistently. Stop after DASH-005; DASH-006 has not been started.
