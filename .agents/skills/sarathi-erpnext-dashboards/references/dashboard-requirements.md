# Dashboard requirements

## Owner and executive

Answer: how is the business performing, and what needs management attention?

Header: authorized company, date range, Customer, Project, refresh timestamp. Prioritize revenue, accounting profit/margin, open overdue production jobs, and receivables as of the selected date. Include revenue/profit trends and comparable prior periods, top customers and sales trends, project delivery health, inventory shortages/excess, and an exception/decision list. Provide links to underlying records, standard reports, and the production tower with applicable filters retained.

Navigation: Overview; Finance & Profitability; Sales & Customers; Projects & Delivery; Manufacturing Summary; Inventory & Procurement; Approvals & Business Risks; Reports.

Profit must be supported by accounting logic, not sales less purchase invoices. Make unsupported Customer/Project dimensions explicit instead of showing company-wide amounts under a misleading filtered label.

## Production management control tower

Answer: what is happening across the factory, and where is work blocked?

Filters: date/shift, Project, Customer, Workstation, Work Order status, and configured production area. Shift and production area require actual configuration and record mappings.

Prioritize active Work Orders, output versus target, delayed operations, and material blockers. Show the sequence Work Order -> material readiness -> Job Cards/operations -> manufacture -> finished goods. Present BOM/routing/workstation context through record links where configured.

Work Order list: identifier, item, Project, planned quantity, produced quantity, status, expected completion, and blocker. Include server-side search, filters, stable pagination, and drill-downs that preserve filter context. Show workstation recorded activity and downtime, material shortages with affected jobs, quality/rework, subcontracting due dates, and finished goods/transfers where sources exist.

Navigation: Factory Overview; Work Orders; Job Cards & Operations; Production Planning; Materials & Shortages; Workstations & Downtime; Quality & Rework; Subcontracting; Finished Goods & Transfers; Production Reports.

Do not invent live machine status from scheduled operations. Label recorded states and refresh times accurately.

## Shop-floor workboard

Answer: what should I work on, what is its status, and what action comes next?

Show operator/supervisor identity, configured shift, Running/Waiting/Blocked counts, current Work Order, item, operation, workstation, target, produced/rejected/remaining quantities, and a short list of assigned next jobs. Use text plus color for statuses.

Proposed controls: Start/Resume, Record Pause, Report Output, Report Problem. Each control requires a documented backend operation and workflow preconditions. If no mapping exists, explain unavailability and link to the authorized ERPNext form; do not build a pretend working button.

Operators see only authorized assigned operations/workstations. Supervisors see their authorized area/team; multiple jobs, reassignment, prioritization, output, and quality actions depend on explicit permissions. Work Order administration stays read-only or restricted for operators. Never infer supervisor access from a label alone.

## First release and later scope

First release: owner business/financial overview, consistent Customer/Project filters, Work Order/Job Card tracking, material and delay alerts, scoped supervisor/operator workboard, auditable actions, record links, and responsive layouts.

Later: predictive alerts, customer profitability beyond supported accounting dimensions, capacity optimization, predictive bottlenecks, machine telemetry/OEE, root-cause analytics, and AI recommendations. Do not display these as operational without source data and validation.
