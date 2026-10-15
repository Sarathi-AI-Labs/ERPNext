# Data contracts, permissions, and valid actions

## KPI dictionary

Create an implementation-specific dictionary before coding metrics. Each entry needs: display label; exact source DocType/fields; formula and grouping grain; posting/planned/actual date semantics and timezone; included docstatus/statuses; company/currency/UOM; supported filters and joins; access scope; drill-down target; reference report; and expected reconciliation tolerance. The definitions below are requirements to resolve against the installed version, not executable formulas or assumed field names.

| Metric | Required definition and validation |
| --- | --- |
| Revenue | Define the submitted Sales Invoice accounting basis, net/tax treatment, returns/credit notes, posting dates, base currency, and any GL adjustments. Reconcile to the selected standard sales/accounting report. Sales Orders are commitments. |
| Profit and margin | Reuse installed Profit and Loss/accounting logic with fiscal year, income/expense classification, returns, accruals, closing entries, and period semantics. Define net/gross scope and zero-revenue margin behavior. Do not claim unallocated accounts are customer-specific profit. |
| Receivables | Use standard Accounts Receivable/payment-ledger semantics at an as-of date, including advances, allocations, credit notes, and historical payment cutoff. Current outstanding fields alone do not establish historical balances. |
| Inventory value | Follow standard stock valuation/ledger logic at the selected date, respecting warehouse/company, valuation method, cancellations, and reposting. Do not use selling prices or purchase totals. |
| Overdue/active work | Define open submitted statuses, the relevant planned completion date, missing dates, stopped/closed/cancelled exclusions, and company/Project scope. |
| Output versus target | Compare compatible period, item, and UOM grains; identify completed production versus in-process operation output. Do not sum unlike UOMs or multiply counts through child joins. |
| Material readiness | Use Work Order remaining demand, source warehouse, transferred/consumed quantities, applicable reservations and stock constraints. Define whether measuring on-hand or projected readiness. Prevent the same stock being promised to multiple jobs. Do not implement all shortages as global required minus Bin actual quantity. |
| Delayed operations | Compare actual Job Card/operation state and schedule, respecting finished/cancelled work, timezone, and missing schedules. |
| Project/customer health | Use verified links between Sales Orders, Projects, Work Orders, and invoices. Deduplicate joins and document risk thresholds. |
| Quality/rework/downtime | Use configured inspections, rejection/rework and downtime sources; distinguish unmeasured data from measured zero. |

## Read service contract

- ERPNext/Frappe core source is read-only. Implement adapters and aggregation endpoints inside the Sarathi custom apps, consuming existing records/APIs/report logic without core patches, monkey-patching, controller overrides, or direct core schema changes. See the mandatory boundary in `../SKILL.md`.
- Verify actual field and method availability in installed source/schema. Do not assume that every version has the same reservation, routing, assignment, or production APIs.
- Whitelist intended endpoints; reject guests. Validate dates, company, link filters, status enums, bounded page sizes, sort columns, and supported combinations server-side.
- Check dashboard roles and underlying DocType/document permissions, User Permissions, company, and assignment scope. A page role check alone is insufficient. Resolve roles and assignment mappings from the installation; role names are not a security model by themselves.
- Prefer permission-aware queries. `get_all`, SQL, query-builder aggregates, and report execution must not silently bypass access. Apply equivalent row restrictions to joins, totals, chart series, counts, and drill-downs. Never use `ignore_permissions` to simplify dashboard endpoints.
- Keep aggregation and detail reads separate from writes. Avoid N+1 queries; aggregate at the correct grain, paginate detail, allowlist sorting, and inspect relevant query plans/indexes for large datasets.
- Cache only with site, user/permission scope, and normalized filters in the key. Invalidate on relevant changes; do not leak a privileged cached aggregate to another role.
- Use consistent filter meaning across cards, charts, and lists. Explicitly mark unavailable dimensions. Include applied filters, generation time, currency/UOM, and availability indicators in responses.
- Escape record/user text in HTML and use safe route construction. Reject malformed inputs and do not return secrets or raw tracebacks.

## Shop-floor action mapping

For each proposed action document: installed method/controller; document type; permitted roles and assignment scope; required state and fields; transition; side effects; audit evidence; concurrency/idempotency behavior; and success/error UI.

- Starting/resuming a Job Card, opening a time log, pausing/closing that log, recording completed operation quantity, quality rejection, and submitting a manufacture Stock Entry are distinct actions. Do not collapse them into direct field updates.
- Use normal ERPNext document/controller/workflow methods and permissions for create/save/submit. Preserve stock validation, negative stock rules, serial/batch rules, quality requirements, and transaction boundaries.
- Check authorization and current state again at mutation time. Do not trust client-submitted employee, workstation, company, assignment, output totals, or available actions.
- Handle concurrent operators and stale forms. Use server-side idempotency or an equivalent persistent uniqueness/state guarantee appropriate to the action. Disabling a button alone cannot prevent duplicates; retries after timeouts must return or reconcile the original result.
- Audit actor, document, timestamp, action, quantity/time, result, and transaction identity through ERPNext or a scoped auditable record. Keep secrets out of logs.
- Blocker reporting needs a real issue/problem record and authorized scope; if no suitable source exists, design an app-owned DocType with permissions and migrations before enabling the action.
- Refresh from authoritative state after success. Surface actionable validation failures. Never silently queue or auto-replay production writes while offline.
