# DASH-003 — Dashboard role and permission matrix

Verified on 13 October 2026 against local site `frontend`, Frappe **16.31.0** and ERPNext **16.33.0**. Related discovery: [foundation](dashboard-foundation.md), [audit](dashboard-audit.md). This task changes custom apps only; ERPNext/Frappe core is read-only.

## Existing permissions discovered

- `Sarathi Owner`, `Manufacturing Manager`, `Manufacturing User`, and `Sarathi Super Admin` existed. Dedicated supervisor/operator roles did not.
- Owner page metadata and its role helper previously admitted `Manufacturing Manager`; the production page admitted `Manufacturing User`. Page visibility alone did not protect all APIs.
- Legacy owner, accounting, subcontracting and production services used `get_all`, raw SQL, or unrestricted value lookups. Native permission filtering was already present in newer production services, but child reads and aggregates required additional protection.
- Legacy production edits required `Sarathi Super Admin` but needed explicit record/write/state checks. The assistant used an unrestricted external client and conversation keys were not separated by user.
- Native Job Card `employee` is a **Job Card Time Log** child table here. It is not an authoritative user assignment list. Native **ToDo** assignments are available.
- Native `Manufacturing User` has Job Card read/write/submit, Work Order read/write/submit and Workstation read/write. `Manufacturing Manager` has Job Card rights but does not alone supply every manufacturing read. Neither manufacturing role supplies Company read in this configuration. Native `Stock User` supplies Company and Work Order read. `Employee` cannot be assumed to remain assigned without an actual Employee relationship; User validation removes it for an unlinked user.

## Role mapping and configuration

Dashboard capabilities are a second prerequisite on top of native rights, never a replacement for them. Role combinations are additive: an explicitly configured executive who also operates production retains both capabilities. Do not use supervisor/operator labels to revoke other intentionally assigned roles.

| Business persona | Dashboard capability role | Native prerequisites and scope |
| --- | --- | --- |
| Owner/executive | Existing `Sarathi Owner` | Assign only needed existing finance, sales, project, stock and manufacturing roles; configure Company/User Permissions. Capability alone grants no accounting or document rights. |
| Production manager | Existing `Manufacturing Manager` | Add `Manufacturing User` when needed for manufacturing masters/Work Orders and appropriate existing Company/project/stock roles. Company and record restrictions remain native. Manufacturing User alone is not factory-manager or executive authorization. |
| Supervisor | New `Sarathi Supervisor` | Native read/write rights for permitted operations plus Company read. Scope is open Job Card ToDo assignments to this user or an explicit Workstation User Permission applicable to Job Card. No implicit area/team inferred from department names. |
| Operator | New `Sarathi Operator` | Native Job Card/related-record rights plus Company read; only this user's open Job Card ToDo assignments. Workstation permission alone does not grant another operator's job. |
| Existing setup administrator | `Sarathi Super Admin` | Keeps existing production/setup capability; native create/read/write permission is still mandatory. This role grants no executive/finance capability by itself. |
| Existing system administrator | `System Manager` or Administrator account | Keeps existing dashboard administrative access. Never assigned to business users as a shortcut. Legacy mutation gate still specifically requires Sarathi Super Admin or Administrator. |

`ensure_dashboard_roles()` creates capability labels only. It assigns no users, adds no DocPerm/Custom DocPerm, and alters no ERPNext role. Test profiles combine existing native roles; they are transactional fixtures, not a production provisioning prescription. The installation administrator must review actual grants and Company/User Permissions before onboarding users.

## Page and data matrix

All “allowed” entries require an authenticated **System User** and underlying native permission. Native User Permissions, permission query conditions, ownership/sharing and field permission levels apply. Missing native rights produce an empty/restricted read or a denied action; the role label does not manufacture access.

| Capability/resource | Owner | Manager | Supervisor | Operator |
| --- | --- | --- | --- | --- |
| `/desk/sarathiownertower` and executive APIs | Allowed | Denied unless also executive | Denied | Denied |
| `/desk/sarathicontroltower` and factory/report/detail APIs | Allowed | Allowed | Denied | Denied |
| Dedicated shop-floor page | Not implemented in DASH-003 | Not implemented | Reserved for later workboard task | Reserved for later workboard task |
| Executive finance / accounting API | Native finance read required | Explicit finance capability plus native read required | Denied at dashboard API | Denied at dashboard API |
| Company, Customer, Project filter options | Native permitted records | Native permitted records | No factory filter endpoint | No factory filter endpoint |
| Work Orders, Job Cards, operations, BOMs, materials | Native permitted records | Native permitted records | Assignment helper only | Assignment helper only |
| Workstations / warehouse / related Work Order | Native permitted records | Native permitted records | Related records must also be readable | Related records must also be readable |
| Stock quantities / operational shortages | Native permitted stock data | Native permitted stock data | No general factory stock endpoint | No general factory stock endpoint |
| Stock valuation, invoice/payment/GL data, currency fields | Native finance rights | Hidden without finance capability; native rights still required with it | Denied via factory API | Denied via factory API |
| Assigned approvals | Native assigned workflow actions only; no custom approval API | Native approved workflow only | Native approved workflow only | Native approved workflow only |
| User/system administration | No implicit grant | Denied by dashboard role | Denied | Denied |
| BOMs and Routings editing | No implicit grant; native authorized forms | No implicit grant; native authorized forms | No custom editing API | No custom editing API |
| Customer organization link | Native create and related Company/Customer read | Same | Denied | Denied |
| Project/Task edit, progress recalculation, integration logging | Only with existing setup gate AND native action rights | Same | Denied | Denied |
| Module catalog / read-only document previews | Native permitted records/fields | Same; finance restriction applies | Denied | Denied |
| Conversational assistant | Native restricted client | Native restricted client; finance restriction applies | Denied | Denied |
| Clear owner caches | Existing administrator capability only | Denied | Denied | Denied |

Finance capability recognizes Sarathi Owner, Accounts User, Accounts Manager, Auditor and System Manager (plus Administrator). A finance role alone does not open a dashboard: the caller must also have that dashboard's capability. Finance source DocTypes and monetary fields remain subject to native read/field permissions.

## Read versus action matrix

| Operation | Backend rule | State/workflow/retry behavior |
| --- | --- | --- |
| Dashboard list/aggregate/detail | Capability gate; native permission-aware lists; authorized parent scope for child rows; permitted fields only | Side-effect-free reads. SQL adapter scopes each legacy source to native permitted IDs and masks forbidden fields; it is used only by custom apps, never patched into Frappe. |
| View assigned Job Card | `check_shop_job(name, "read")`: shop capability, native Job Card and related Company/Workstation/Work Order read, then assignment/team gate | Missing, forbidden and malformed IDs return the same generic denial. No inferred assignment. |
| Prepare authorized Job Card write | `check_shop_job(name, "write")` adds native write; caller must use validated ERPNext controller operation | Helper only: no new Start/Pause/Output/Submit API. Helper rejects submit/cancel/delete permission requests. |
| Reassign/reprioritize jobs | No new dashboard API | Future feature must require explicit native authorization and scoped target-user checks. |
| Edit Project/Task | Existing Sarathi Super Admin/Administrator gate AND native read/write; explicit editable fields and permitted write level | Lock/reload; draft only; reject active workflow. Status/docstatus/workflow transitions cannot be supplied as editable fields. Normal `doc.save()` validates links and business rules. |
| Recalculate Project progress | Same gate and native write | Only draft, editable percent_complete and no active workflow; otherwise use native form/workflow. |
| Log TubePro/CypCut/Tally integration | Existing setup gate; native Log create, Project read; Tally also finance capability | Payload bounded, finite nonnegative quantities, required request_id. Deterministic per-user/source/request ID; identical retry returns same log; changed payload is rejected. This logs records, not machine telemetry or stock transactions. |
| Link Customer organization | Native create plus Company/Customer read | Deterministic company/customer ID prevents duplicate new associations, including simultaneous inserts. Existing association IDs retained. |
| Assistant create/write/submit/cancel/delete | Session-bound custom client uses native action permissions and document methods; source finance guard | Denies arbitrary Python/IPC execution and identity escalation. Rejects direct status/docstatus/workflow and child-table edits; draft-only update/delete; native submit/cancel state and validations; active workflow uses ERPNext form. No direct database transaction writes/commits. |
| Manufacture / stock transfer / production time/output | No new operational API | Native forms/controllers remain authoritative. Future workboard commands must distinguish time recording, output, inspection and stock submission, and provide transactional idempotency. |
| Embedded native report | Executive capability, native report permission and authorized Company | Defaults select a permitted Company. Denies additional non-Company User Permissions or ownership-only source access until individual native report scope handling is verified. Custom scoped aggregates are unaffected. |

No custom document operation sets `ignore_permissions`, bypasses controllers or submits a stock transaction by directly changing status. Native validations may reject an operation that the capability layer permits; that is intentional.

## Scope and enforcement inventory

- `sarathi_visibility.api.access`: centralized capability gates, validated scalar link/date filters, native record checks, read adapters, monetary response filtering, shop-job assignment scope and draft write guard. Context-local allowed-ID caching lasts only for the API call and includes the user. Pagination of allowed-ID discovery does not relax permissions.
- `sarathi_owner.api.permissions`: manager no longer implicitly executive; finance context requires native GL and Sales Invoice read.
- Owner `owner_dashboard`, `pipeline`, `quick_details`: executive gates, validated supplied filters/IDs, permission-aware source reads. Owner financial calculations are unchanged; DASH-003 does not establish accounting reconciliation.
- Shared `module_catalog`: executive/production entry gate, native report/module restrictions and per-user revision cache preserved; native record/field checks plus finance source/field guards on previews.
- Visibility `dashboard` / `dashboard_data`: factory gates, native reads/children, restricted accounting state, permission-aware detail/report data and customer-link retry safety.
- Visibility `accounting`: finance capability on detailed API, safe restricted card for non-finance production users; all reads scoped. Corrected a pre-existing monthly-trend query that mixed named Company placeholders with positional dates; an additional filtered-finance test detects swallowed SQL errors. Formulas were not changed.
- Visibility `subcontracting`: production capability and scoped reads; monetary outputs removed for non-finance users.
- Visibility `control_tower`: factory gates on every whitelisted API; scoped legacy lists/counts/aggregates; native field/document checks and state guards on legacy writes; POST-only mutations.
- Visibility `agent_chat` / `agent_client`: user-namespaced state, message/session bounds and dashboard capability gate; all external client's read/write/execute methods replaced by custom native-authorized methods. The external agent package is unmodified. Native filter fields are validated so restricted currency values cannot be inferred through assistant search filters.
- Page JSON and app-owned setup: align page roles with API policy on install/migrate. Existing routes unchanged.
- Production UI: display a restricted accounting card rather than presenting financial zeroes to a restricted user.

## Remaining boundaries and assumptions

1. Assignment enforcement is implemented and tested as a custom-app helper, not as a completed workboard/action workflow. Later shop-floor endpoints must use it. No team/production-area DocType or digital Employee assignment was assumed.
2. Native ERPNext Desk/API permissions remain independent. For example, assigning Manufacturing User grants its existing Job Card submit and potentially broader native read permissions. The new capability labels do not revoke those native grants. Installation administrators must configure native User Permissions if the same assignment/team restrictions must hold outside Sarathi dashboards. No core override is installed to impose a second global permission system.
3. Native reports with complex record restrictions are deliberately unavailable through the embedded runner until verified. Native report execution, reconciliation and advanced filtering remain later task work; opening a native route delegates to its existing permissions, not this adapter.
4. Generic assistant operations are not a newly certified shop-floor action API. Provider-driven conversations and concurrent generic create confirmations were not end-to-end tested here. Required idempotency for future production transactions remains a workboard implementation acceptance item. Child-table editing and active-workflow operations route through native forms.
5. Legacy aggregates discover all permitted IDs in batches; large-volume performance and more efficient query building remain DASH-006 work. No multi-VPS, telemetry, mobile layout or financial reconciliation claim is made by these security tests.
6. Page roles do not prevent users with overlapping roles from seeing combined authorized capabilities. Role assignments must be reviewed; no existing users were elevated by this task.

## Validation and changed files

Local configuration: selectively ran `ensure_dashboard_roles()`, owner `_ensure_owner_page("sarathiownertower")` and visibility `ensure_module_profile_page()`, then committed their custom-app role/page metadata. No full migrate/backfill, native DocPerm changes or existing-user role assignments were performed. Both pages had no extra custom page-role grants. Native page checks were tested with real owner, manager, supervisor, operator and unrelated users. No DASH-003 test users survived rollback.

Executed all seven unittest modules against the actual Docker site's database: `sarathi_owner.tests.test_module_catalog`, `test_owner_dashboard`, `test_quick_details`; `sarathi_visibility.tests.test_accounting`, `test_dashboard`, `test_subcontracting`, `test_permissions`. The new security suite contains 19 tests with transactional native users/records, including company/customer/warehouse/ID tampering, native SQL aggregate/child scope, currency masking, assignment/team denial, guest/capability denial, draft/workflow guards, duplicate integration/customer-link requests, assistant identity/filter restrictions and conversation isolation. The existing restricted-user catalog and company-scope fixtures now include the manager capability required by the new policy.

Final result: **80 tests executed; 79 passed, 1 skipped**. Skip: `test_live_activity_reads_permission_scoped_time_logs`, because an existing submitted production/time-log fixture is unavailable. Native workflow existence is simulated for the workflow-rejection branch; actual native draft writes, role permissions, User Permissions, records and state rejection run against the installed site. Concurrent transaction races and provider conversations are not claimed as tested.

Validation also passed: AST parsing of all 18 task Python files, Ruff undefined-name/unused-import checks on those files, and `node --check` on the touched production JavaScript. After restarting the local backend, guest HTTP requests to both owner/production summary endpoints returned **403**; Desk responded through its normal login flow. The initial requests during backend startup briefly returned 502; the repeated checks after startup succeeded. No VPS deployment was made.

The baseline hash comparison found no removed files and no task changes in ERPNext/Frappe core, the external agent package, or unrelated existing edits. The prior CSS/page/runtime/Docker changes were preserved. Only the existing production JavaScript received small accounting/subcontracting restricted-state handling changes for this task.

### Exact task file manifest

Created:

- `docs/dashboard-permission-matrix.md`
- `sarathi_visibility/sarathi_visibility/api/access.py`
- `sarathi_visibility/sarathi_visibility/api/agent_client.py`
- `sarathi_visibility/sarathi_visibility/tests/test_permissions.py`

Modified:

- `sarathi_owner/sarathi_owner/api/module_catalog.py`
- `sarathi_owner/sarathi_owner/api/owner_dashboard.py`
- `sarathi_owner/sarathi_owner/api/permissions.py`
- `sarathi_owner/sarathi_owner/api/pipeline.py`
- `sarathi_owner/sarathi_owner/api/quick_details.py`
- `sarathi_owner/sarathi_owner/sarathi_owner/page/sarathiownertower/sarathiownertower.json`
- `sarathi_owner/sarathi_owner/setup/install.py`
- `sarathi_owner/sarathi_owner/tests/test_module_catalog.py`
- `sarathi_visibility/sarathi_visibility/api/accounting.py`
- `sarathi_visibility/sarathi_visibility/api/agent_chat.py`
- `sarathi_visibility/sarathi_visibility/api/control_tower.py`
- `sarathi_visibility/sarathi_visibility/api/dashboard.py`
- `sarathi_visibility/sarathi_visibility/api/dashboard_data.py`
- `sarathi_visibility/sarathi_visibility/api/subcontracting.py`
- `sarathi_visibility/sarathi_visibility/public/js/sarathi_dashboard.js`
- `sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.json`
- `sarathi_visibility/sarathi_visibility/setup/install.py`
- `sarathi_visibility/sarathi_visibility/tests/test_dashboard.py`

Recommended next task: **DASH-004 — Create KPI dictionary and metric formulas**. No subsequent backlog task was started.
