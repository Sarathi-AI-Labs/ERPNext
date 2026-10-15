# DASH-006 — Permission-aware filter and data helpers

## Audit and retain/improve/build decision

Inspected DASH-001 through DASH-005, current API modules, access helpers, permission tests and installed metadata. Working on `feature/Gaurav_2`; existing dirty work is preserved using the local `scratch/dash-006/baseline.json` hash manifest. ERPNext 16.33.0 / Frappe 16.31.0 source remains read-only.

| Existing utility | Decision |
| --- | --- |
| `api.access.require_session`, capabilities, `check_record`, `allowed_fields`, `check_shop_job` | Reuse native permissions, field permissions, finance separation and explicit assignment policy |
| `access.validate_filters` and `authorized` | Retain legacy contracts; add strict resource-specific validation separately instead of breaking every existing caller |
| `scoped_rows`, `scoped_value`, `scoped_sql`, `scoped_count` | Retain legacy adapters; they can enumerate whole allowed datasets, so do not use them for the new bounded read endpoints |
| Production `get_report` | Reuse bounded pagination validation before loading; keep successful response shape |
| Owner/production aggregate loaders | Retain; no metric or SQL rewrite in this task |
| Safe record/filter-option foundation | Build a small allowlisted API in `sarathi_visibility.api.data_helpers`, reusable from owner without circular imports |

Customer and Workstation are shared masters without a native Company field. A Company filter cannot honestly scope them by direct ownership; their contracts must reject that filter. Shift/team relationships are not assumed. Financial formulas and custom aggregation remain outside this task.

## Module, supported resources and filters

Implementation: `sarathi_visibility/sarathi_visibility/api/data_helpers.py`. Both apps can import it; it depends on the existing visibility access module, not the owner app. No framework or external dependency was added. Metadata was read from the running site's installed DocTypes before defining these contracts.

Every resource supports an exact `name` filter. Additional supported filters:

| Resource key | DocType | Additional filters | Date basis | Returned fields / sortable allowlist |
| --- | --- | --- | --- | --- |
| `projects` | Project | company, customer, status, docstatus, from_date, to_date | expected_start_date, Date | name, project_name, company, customer, status, expected_start_date |
| `work_orders` | Work Order | company, project, status, docstatus, from_date, to_date | planned_start_date, Datetime | name, company, project, status, production_item, qty, produced_qty, planned_start_date |
| `job_cards` | Job Card | company, project, work_order, workstation, status, docstatus, from_date, to_date | posting_date, Date | name, company, project, work_order, workstation, operation, status, posting_date, total_completed_qty |
| `warehouses` | Warehouse | company, is_group | None | name, warehouse_name, company, is_group |
| `customers` | Customer | None | None | name, customer_name |
| `companies` | Company | None | None | name |
| `workstations` | Workstation | status | None | name, status |

These are explicit contracts, not a generic arbitrary-DocType API. Unsupported dimensions (including warehouse on Work Order, customer on Job Card, shift, team and assigned_user) are rejected. Relationships needing joins are deliberately not guessed. An installed field missing from a display selection is omitted; an unsupported/missing requested filter fails rather than claiming it was applied. Status values come from each installed Select field's options, preserving exact spelling/case. For example, Project uses `On hold`, while Job Card uses `On Hold`.

### Input rules

- Filters: Python dict, JSON object string (maximum 4096 characters), or `None`. Arrays, scalar JSON, malformed JSON and unknown names are invalid. Optional supported values of `None` or empty string are omitted; unknown names remain invalid even when empty.
- Record IDs: nonempty strings, at most 140 characters, no control characters. Linked IDs must pass existing native document-read checks. Missing and inaccessible records receive the same generic permission denial; malformed IDs are validation errors.
- Dates: exact valid `YYYY-MM-DD`; start must be on/before end. Date endpoints use inclusive bounds. Datetime endpoints use local midnight at the start and exclusive midnight after the end date, matching the site's calendar/timezone semantics. Missing schedules do not fall back to creation dates. Dates beyond an inclusive Datetime calendar boundary are rejected.
- `docstatus`: integer or integer string 0, 1 or 2. `is_group`: 0 or 1. Booleans and expressions/operators are not accepted as substitutes.
- Sorting: `sort_by` must be an available, permitted field in the table above; `sort_direction` is exactly `asc` or `desc`. A secondary `name asc` makes non-name ordering deterministic for a stable dataset.
- Pagination: `start` defaults to 0, range 0–100000; `page_length` defaults to 25, range 1–100. Integer HTTP strings are accepted; booleans, floats, negatives, zero lengths, oversized lengths and SQL fragments are rejected. One extra record is fetched to compute `has_next`.
- Option search: string up to 140 characters without controls; searches the permitted display-label field with literal LIKE wildcard escaping. It is not an arbitrary SQL or field expression.
- No client-selected `fields`, `doctype`, ordering clauses, grouping, write changes or permission flags. `cmd` and `_` are ignored transport metadata used by Frappe/browser dispatch, never data-selection inputs. Frappe itself strips top-level `ignore_permissions` and `flags` during dispatch; the helpers never use either and internal direct calls reject them as unexpected parameters.

## Authorization and company scope

Every public endpoint rejects Guest/Website User sessions, requires an existing owner or production capability, then requires underlying DocType read permission. Capabilities reuse DASH-003 role mappings; this task grants no roles to existing users and changes no standard permissions. All record, option and count queries use installed permission-aware `frappe.get_list`; no `get_all`, raw SQL, arbitrary query-builder input, global allowed-ID enumeration or permission bypass is introduced.

Company-owned resources require an authorized Company. An explicit Company is checked with native list and document permissions. With no Company input, exactly one readable Company may be resolved automatically; zero is denied and more than one requires selection. No first-company or demonstration-company default exists. The enforced Company is included in `applied_filters`. Linked records carrying a company must match it. Work Order + Project combinations are checked for consistency before querying.

Individual resource reads additionally check the named document and require it to appear in the permission-aware, company-filtered result. Only fixed display fields intersected with `access.allowed_fields` are returned; forbidden fields cannot be used for sorting/filtering. `allowed_fields` retains native permlevel checks and DASH-003 financial-field separation. Read access never serializes an entire document or its children.

Customer and Workstation dropdowns return native-readable shared master records across the current site; they do **not** claim company ownership or organization-association filtering. Company User Permissions alone are not a substitute for Customer/Workstation User Permissions. If a future page needs company-associated masters, define a verified relationship-specific contract rather than passing an ignored Company filter.

`get_shop_job(name)` is an **internal, non-whitelisted** read helper. It reuses `check_shop_job(name, "read")`: native Job Card and related Company/Workstation/Work Order checks plus current-user open ToDo assignment, or the already documented supervisor Workstation scope. It returns only permitted job-card display fields. Operators/supervisors cannot call the broad list/options/count APIs merely because they can open a workboard. No assignment list, team inference or shop-floor transaction API is implemented here.

## Helpers, endpoints and responses

Public read endpoints are explicitly **GET-only**, under `/api/method/sarathi_visibility.api.data_helpers.`:

| Function | Input | Successful Frappe `message` payload |
| --- | --- | --- |
| `get_records(resource, filters=None, start=0, page_length=25, sort_by="name", sort_direction="asc", **extra)` | Resource allowlist, supported filters and bounded sort/page arguments | `{rows, start, page_length, has_next, applied_filters}` |
| `get_record(resource, name, filters=None, **extra)` | One readable ID within supported scope | A single projected record dict |
| `get_options(resource, filters=None, search="", start=0, page_length=25, **extra)` | Allowlisted option resource, scope and search/page arguments | `{options: [{value, label}], start, page_length, has_next, applied_filters}` |
| `get_count(resource, filters=None, **extra)` | Same supported scope, no arbitrary group/aggregate arguments | `{count, applied_filters}` |

Internal utilities: `pagination(start=0, page_length=25)` returns validated `(start, length)`; `validated_filters(spec, filters=None)` takes a **trusted server-owned Resource declaration** and returns `(native_conditions, applied_filters)`; `get_shop_job(name)` returns a permission-projected job. Endpoint callers should use `get_records`/`get_record`, not just validation followed by an unrestricted query.

Examples using actual signatures:

```python
from sarathi_visibility.api.data_helpers import get_records, get_options, get_shop_job

page = get_records("work_orders", {"company": selected_company, "status": "In Process"},
                   start=0, page_length=25, sort_by="planned_start_date")
customers = get_options("customers", search=search_text, page_length=20)
# Only inside an independently authorized future shop-floor endpoint:
assigned_job = get_shop_job(job_card_name)
```

```javascript
frappe.call({
  method: "sarathi_visibility.api.data_helpers.get_records",
  type: "GET",
  args: {resource: "projects", filters: {company: selectedCompany}, page_length: 25},
  callback: ({message}) => renderAuthorizedRows(message.rows),
});
```

Empty lists/pages are successful empty arrays with `has_next: false`; an empty readable count is zero. Unsupported filters/sorts/arguments raise authored `frappe.ValidationError` (HTTP 417 in this installation). Missing/forbidden records and capability/company denial raise generic `frappe.PermissionError` (403). Internal failures are logged server-side and raise a generic `DashboardReadError` (500), never a misleading empty array. The shared read decorator enables Frappe's supported per-request traceback-suppression flag; actual HTTP denial/validation responses were verified without `exc`, `exception` or traceback content. No global Frappe configuration or source is changed. Standard framework dispatch/authentication errors remain framework-owned.

Counts use the verified Frappe 16 dictionary expression `{"COUNT": "name", "as": "total"}` through the same permission-aware list engine and filters. The first integration run caught that this installed version rejects legacy string SQL aggregate expressions; it was corrected and the negative count tests now pass. Custom grouped, financial and manufacturing aggregations are **not supported** by this layer. A future KPI implementation must separately prove its row/field scope; do not treat this count proof as approval for arbitrary SQL or joins.

## Existing API integration

Only `sarathi_visibility.api.dashboard.get_report` changed: it calls shared `pagination` before invoking the existing loader, preserving valid requests and the existing `{title, columns, rows, total, start, page_length}` response. Invalid limits/offsets that previously silently clamped are now validation errors. No existing KPI formulas, data joins, filters, export contracts, owner endpoints, workflow actions or UI files were rewritten. The legacy report still materializes its existing aggregate dataset before slicing; this task does not claim that converting its pagination validation converts that loader into a bounded query.

New endpoints remain opt-in for subsequent dashboard features. Owner can import this visibility-owned module through the existing app dependency direction. DASH-005 remains presentation-only; it cannot authorize these reads.

## Efficiency and validation

List/options operations fetch at most 101 projected rows; detail reads fetch at most two after one named document check. Company selection fetches at most two names. Linked-filter checks are proportional to the fixed number of supported filters, not the result rows; no per-row document loading or full-site allowed-ID enumeration is used. Count is one permission-filtered database aggregate rather than loading rows into Python. Metadata uses existing Frappe caches; business results are not stored in a cross-user cache. No new indexes, migrations or external pagination framework were added.

Executed against the local Docker site:

- **39 tests passed, zero skips**, in `test_data_helpers.run`, including the existing 19 DASH-003 regressions and 20 helper tests. Positive and negative checks cover real native users/Company/Customer/Project/Warehouse/User Permission records, forged Work Order/Job Card IDs, scope-limited options/counts, guests and unrelated/shop roles, explicit ToDo assignments, invalid filters/dates/statuses/sorts/pages, missing records, stable pages and empty pages, literal search wildcards, GET-only registration, no document saves in read helpers, fixed projections, sanitized internal failures and bounded per-query behavior.
- The restricted-field selection/sort test deliberately patches the output of the reused native field-permission helper to exercise redaction; it is not a claim that every site's custom permlevel configuration was tested. Native field/finance behavior is also exercised by inherited permission regressions.
- **10 direct HTTP checks passed**: authorized list/detail/options/count, forged ID denial, invalid SQL-style ordering, arbitrary fields, unsupported filters, Guest denial and POST denial. Temporary native HTTP test User/User Permissions/session were removed and removal asserted. Existing business records were only read.
- **15 existing production regression tests completed: 14 passed, one skipped** because submitted production time-log data was unavailable. Valid legacy report pagination/export/summary contracts passed. No skipped test is counted as a successful check.
- Existing owner/production browser routes were rechecked after the local backend reload; results are recorded in the validation artifact. This task does not claim exhaustive new UI testing.
- Python syntax, task diff whitespace and pre-task baseline preservation checks are recorded at handoff.

Transactional integration tests reuse native rollback fixtures; they do not persist sample business records as dashboard data. Run sequentially against the local site to avoid test-fixture transaction contention:

```powershell
docker exec -w /home/frappe/frappe-bench frappe_docker_main-backend-1 bench --site frontend execute sarathi_visibility.tests.test_data_helpers.run
docker exec -w /home/frappe/frappe-bench frappe_docker_main-backend-1 bench --site frontend execute sarathi_visibility.tests.test_dashboard.run
python sarathi_visibility/sarathi_visibility/tests/audit_data_helpers_local.py
```

The manual HTTP audit requires existing Project/Customer/Company data and the named local Docker stack. It creates a temporary native user with existing roles and narrow User Permissions, commits only those test security fixtures so HTTP can see them, and deletes them in `finally`. It is local testing, not a live VPS deployment. Test cookies are kept in memory and not included in the report. If interrupted during fixture setup/cleanup, inspect and remove `dash006-http-*` audit users before another run.

Performance evidence is bounded ORM calls and absence of row-dependent checks, exercised against the existing small local dataset. Large factory datasets, query-plan profiling, concurrent page changes and VPS latency remain unmeasured. Offset pagination is deterministic for a stable dataset, not a snapshot guarantee while records change. No claim of large-dataset performance certification is made.

## Exact task files, limits and next task

Created:

- `sarathi_visibility/sarathi_visibility/api/data_helpers.py`
- `sarathi_visibility/sarathi_visibility/tests/test_data_helpers.py`
- `sarathi_visibility/sarathi_visibility/tests/audit_data_helpers_local.py`
- `docs/dashboard-data-helpers.md`
- `docs/dashboard-data-helper-validation.json`

Modified: `sarathi_visibility/sarathi_visibility/api/dashboard.py` (only the existing report pagination validation). Pre-existing dirty changes are preserved. No ERPNext/Frappe core, standard DocPerm, source controller, database schema, frontend or other unrelated file changed in this task. Local ignored `scratch/dash-006/` holds baseline hashes, intermediate evidence and route screenshots.

No full dashboard, shop-floor assignments list/actions, financial formulas, arbitrary grouped aggregation, company-associated shared-master join, shift/team model, deployment or upgrade rehearsal was implemented. Those require their own approved contracts/data and later tasks. Existing broad legacy loaders and their DASH-003/DASH-004 limitations remain; this foundation is not a security certification of every existing API.

Recommended next backlog task: **DASH-007 — Owner & Executive Dashboard**, using DASH-004 metric definitions, DASH-005 components and these validated read contracts. DASH-007 has not been started. DASH-006 is ready for foundation review subject to the recorded limits.
