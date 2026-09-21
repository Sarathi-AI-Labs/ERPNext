# Sarathi Industrial Dashboard

Open `/desk/sarathicontroltower`. The route is retained for existing bookmarks.

## Navigation

1. Select your organization (ERPNext Company).
2. Select a Customer card. Other customers and their projects disappear.
3. Select a Project. Its main BOM, production and sales records become the scope.
4. Use the breadcrumb to return to customer projects or the organization.

The selection is stored in the URL. Browser Back and reload preserve the view.
The page refreshes every 30 seconds while visible, and after your ERPNext saves
through the realtime connection. A failed refresh displays an error instead of
leaving the page indefinitely at “Loading”.

## Create a manufacturing project

1. Select an organization and use **Create → Customer**, or **Link existing customer**.
   Linking records supports the same customer buying from multiple organizations.
2. Select that customer and use **Create → Project**. Organization, customer and
   the Sarathi Manufacturing Project flag are filled automatically.
3. Select the project and use **Create → BOM**. Choose the product, quantities,
   materials and operations in ERPNext, then save and submit.
4. The first submitted project BOM becomes its main BOM. Drafts and revisions
   remain visible. To change the main BOM, select an active submitted revision
   on the Project. Existing Work Orders retain their historical BOM.
5. Use **Create → Sales Order** and **Create → Work Order**. Complete ERPNext's
   required quantities, warehouses and commercial fields before submitting.
6. Create Job Cards, manufacturing Stock Entries and Pick Lists from the linked
   Work Order using ERPNext's native actions.

Global masters (Item, Warehouse, Operation, Workstation, Plant Floor and Routing)
are available under **Setup**. Buttons respect create permissions.

## Existing records

The migration adds `Project.custom_sarathi_bom`,
`Project.custom_sarathi_manufacturing` and `BOM.custom_sarathi_project`.
It backfills only unambiguous same-company Sales Order customer links and
unshared Work Order BOM assignments. It never assigns a BOM by matching an item.

Missing customer links appear under **Unassigned customer**. Use the data-quality
report's Project link to assign the correct customer and main BOM. Existing
unflagged projects can be edited without enforcing new manufacturing requirements;
enable the flag once their links are complete. No customer identities are guessed.

## Reports and calculations

Overview covers project status, progress, customers and deadlines. Sales contains
order status and sales trends. Production contains planned/produced quantities,
operation hours, Work Orders, Job Cards, tasks and workstation workload.
Engineering contains explicitly linked BOMs, revisions, components and operations.
Materials & Stock contains requirements, stock movements and finished receipts.
Integrations contains linked machine logs. Reports exposes all these datasets.

- Status filters select projects. Date filters select Sales Orders by transaction
  date, Work Orders by planned start, Job Cards and Stock Entries by posting date.
  Project progress, tasks, deadlines and BOM assignments are current snapshots.
- Cancelled records remain inspectable in reports but do not contribute to active
  counts, submitted-order value or produced-quantity charts.
- Sales trends keep currencies separate. For a mixed-project Sales Order, a
  project-filtered value uses its selected item net amounts, excluding taxes; the
  report states this basis. Full orders include taxes.
- Produced quantities come from submitted Work Orders, grouped by item and unit.
  Finished receipts are submitted Stock Entry finished-item movements, not a
  claim that those goods remain allocated to the project.
- Material demand comes from open submitted Work Order Items. Still-to-transfer
  demand subtracts the greater of consumed and transferred quantities. Shared
  source-warehouse stock is shown once per material/warehouse/company. Potential
  shortages are advisory availability checks, not stock reservations. Blank stock
  means inaccessible stock data or an unspecified warehouse.
- Workstation hours describe selected Job Cards, not total factory capacity.
- Each KPI opens its exact report subset. Tables page through all matching rows;
  CSV exports include all matching rows and neutralize spreadsheet formulas.
- Read/user permissions apply before aggregation. Export permission is required
  for CSV downloads. Child records are restricted to authorized parents and fields.

The native **Sarathi Industrial Analysis** Script Report uses the same query and
calculation code as the dashboard. The report selector changes its dataset.

## Project totals and operation analysis

### Project health overview

The Overview now shows each ongoing project's current recorded operation,
workstation, next outstanding Work Order operation, finished/total operation
counts, purchasing, quality, delivery and invoicing. Selecting a project shows
the same health panel for that project even after completion. The metric buttons
open the scoped full reports; Organization → Customer → Project navigation is
unchanged. Material shortage count is only shown in a selected project when
source warehouse availability is readable and known. Blank means unknown,
not zero. Quality passed/rejected are submitted inspection document counts,
not part counts. Last activity is the last recorded Job Card update or time log;
the page refreshes every 30 seconds and on ERPNext save events.

To turn this into physical cutting, welding and grinding counts, finish one real
project's customer/main BOM links, create stock Items and units for each actual
intermediate part, configure operation output BOMs and warehouses, and post the
native Job Card/Stock Entry output movements. Reconcile the submitted outputs
with ERPNext reports before repeating the setup for other projects. Keep
Completed Projects separate from the In progress view.

### Complete project document pipeline

Procurement includes Material Request, Purchase Order, Purchase Receipt and
Purchase Invoice item reports. Delivery & Billing includes Delivery Note and
Sales Invoice items. Explicit item Project fields override document defaults;
native item links propagate ownership only when unambiguous. Conflicts are
excluded and listed as exceptions. Orphan procurement is visible at organization
level and is never attributed to a project based on matching Item codes.

All pipeline reports use lifetime records. Material consumption includes completed
submitted Work Orders. Stock movement items and the voucher stock ledger follow
selected, readable document item rows; draft/cancelled entries do not count as
posted production. Current shared stock and native project reservations are
separate reports. Returns retain native signed quantities. Buying receipts and
stock-updating invoices are separate auditable documents, not added together as
independent receipts. Invoice item values exclude document taxes; outstanding is
whole-document information and is blank for partially selected documents. It must
not be summed across repeated item rows.

Quality & Rework includes project-linked inspection results, corrective Job Cards,
employee/time-log history and sub-operations. Sample size is not rejected quantity.
The physical operation output report uses submitted Manufacture Stock Entry item
quantities linked to Job Cards. Without explicit operation outputs, it is empty;
Work Order completion is never converted to guessed physical part quantities.
Setup links identify missing customer/main BOM/validation and output configuration.
Linked readable subassembly BOMs appear in engineering; manufacturing validation
allows active main or structurally linked subassembly BOMs, excluding another
project's BOM. New procurement and fulfilment saves validate item project company
and, for selling documents, customer consistency.

### Live project production

The main page separates In progress, Not started, Completed, On hold / Stopped,
Production finished / Closure pending, and Cancelled projects. In progress means
recorded manufacturing has started; merely creating a Job Card is not a start.
Completed Project records never enter the In progress cards. An Open project with
finished submitted manufacturing instead awaits project closure.

Running now requires an open Job Card Time Log (from_time set, to_time empty), a
submitted active Work Order, and a non-completed/non-held Job Card. Cards list all
simultaneously running Job Cards with their actual recorded workstation, start
time, quantities, and last record activity. Started production without an open
time log remains In progress with no operation recorded as running. Closed and
stopped Work Orders do not contribute running activities; contradictory open time
logs appear as alerts. Operators must record starts/stops correctly; this does not
independently measure physical machine activity.

Live project activity is available in the dashboard/native report and CSV export.
Live production states use lifetime records independently of activity date filters.
Save/update-after-submit events request refresh; the 30-second timer is a fallback.

Organization/customer summaries include Total, Completed, Ongoing (Project status
Open), On hold, and Delayed projects. The selected-project summary cards and
Organization → Customer → Project navigation are preserved.

Overview has expandable ongoing-project rows; a selected project shows its own
operations regardless of whether it is Open or Completed. Production contains
Project production summary and Lifetime operation balances reports. Each row
identifies its Work Order, operation sequence, workstation, output item/unit,
planned quantity, completed quantity, process loss, remaining quantity and hours.
ERPNext Work Order Operation balances are authoritative, so split Job Cards do
not multiply the planned quantity. Corrective cards are reported separately.
Cancelled/draft Work Orders are excluded from submitted production balances.
Stopped/closed Work Orders remain visible with their status and outstanding work.

Remaining = max(planned − completed − process loss, 0). Quantities describe Work
Order output units, not counts of every physical BOM component. Different operation
quantities must not be summed as unique finished parts. Charts separate units;
full paginated reports and CSVs include every matching row. Production status is
separate from Project status; completed-project/unfinished-production conflicts
produce alerts. Lifetime operation balances and current warehouse balances are
not restricted by activity date filters.

Materials & Stock contains Semi-finished shared warehouse stock. This lists each
configured operation output Item/target Warehouse once with its current Bin
balance and related projects. It is shared stock, not project-reserved stock.
Hidden stock values are blank. Stock tracking status identifies missing setup.

### Physical part inventory setup

Existing business Items/BOMs are not automatically converted. To record physical
cut, welded or ground parts, define their actual stock Items and units, configure
ERPNext semi-finished tracking and operation output BOMs/target warehouses, and
use the native Job Card/Stock Entry workflow. Submitted stock movements then feed
the warehouse report automatically. Validate component quantities and yields on
one real manufacturing workflow before adopting it across projects. Without these
records the dashboard shows operation progress, not invented part inventory.

## Deployment commands

Build the custom image using `INSTALL.md`, recreate the app services, and run
`bench --site frontend migrate`. Clear cache and reload the browser afterwards.
The custom image preserves the browser Origin header for WebSocket authentication
when a site directory (`frontend`) differs from the public host (`localhost`).
The WebSocket service authenticates through `SARATHI_SOCKET_BACKEND_URL`
(`http://backend:8000`) with the selected site header. Browser origin checks,
session cookies and Frappe's socket secret remain enforced. The build checks the
Frappe source before applying this Docker routing patch and fails if it changes.

Run the transactional integration suite in the backend:

```sh
bench --site frontend execute sarathi_visibility.tests.test_dashboard.run
```

The suite creates temporary customers, projects, BOMs and a restricted user, then
rolls everything back. It covers scope isolation, same-item BOM isolation, main BOM
assignment, document validation, permissions, pagination, CSV and report parity.
