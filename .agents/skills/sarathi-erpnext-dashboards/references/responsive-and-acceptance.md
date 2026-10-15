# Responsive system and release acceptance

## Shared responsive design

Use shared spacing, typography, colors, status semantics, surfaces, focus states, and touch targets. Scope styles to the Sarathi pages so they do not break ERPNext Desk. Choose layout based on available content width, including Desk navigation; viewport breakpoints are starting points.

| Width | Starting behavior |
| --- | --- |
| Under 480 CSS px | Single-column content, compact header, stacked KPI cards, minimal menu |
| 480-767 | One/two KPI columns, collapsible filters, card lists |
| 768-1023 | Two-column dashboard, compact navigation, readable operational tables |
| 1024 and above | Full grids, detailed tables, expanded navigation |

Owner: important business metrics first; compact expandable filters; readable resizing charts; summary cards replacing wide tables on phones.

Production: blockers and overdue jobs first on mobile; searchable/filterable Work Order cards retaining status, progress, due date and blocker. Return from job details without losing filters or list context. Collapse the desktop sidebar into a compact menu.

Shop floor: current job and next action immediately visible; large controls at least approximately 44-48 CSS px (larger where factory use needs it), legible labels at intended distance, minimal typing/dialogs, and text plus color. Confirm consequential actions proportionately and show pending, success, and error feedback. Validate glove use on actual hardware if required; browser emulation cannot prove it.

Prevent page-level horizontal scrolling. Wide tables may scroll inside a labeled container if cards are unsuitable. Charts must resize with readable labels. Dialogs, dropdowns, date pickers and long identifiers must fit. Support keyboard focus, accessible labels, contrast, portrait and landscape. Handle loading, empty, stale/offline, permission-denied and error states; an API failure must not appear as a measured zero.

Refresh periodically or from real record events where useful. Display last successful refresh, avoid stale-response races, stop polling when pages are inactive, clean up listeners/timers, and avoid overwriting edits during a refresh.

## Validation matrix

Maintain requirement, implementation location, test/verification method, result, and evidence. Exercise realistic data and non-administrator sessions. Record unavailable runtime checks as pending.

1. Accuracy: reconcile revenue, profit, receivables and valuation against standard reports using identical company/date/currency filters. Include returns, cancellations, partial payments, historical cutoffs, zero denominators, multi-UOM output, missing schedules, and duplicate-prone joins.
2. Scope: independently test owner, production manager, supervisor, operator, unrelated user and guest. Include forged company/project/workstation/assignment filters, direct API calls, inaccessible linked documents, and cached aggregates after role changes. Match underlying records without revealing restricted totals or names.
3. Workflow: verify start/resume/pause/output/problem against configured transitions, stock/quality rules, and audit records. Retry requests, double-click, submit concurrent updates, and simulate timeout after commit; confirm no duplicate time logs, output or Stock Entries.
4. Materials: test relevant warehouses, partial transfers/consumption, reservations, competing Work Orders, and configured serial/batch constraints. Investigative links must point to permitted records.
5. Responsive: test all three pages at representative 360, 390, 480, 767, 768, 1023, 1024 and 1440 CSS px, plus portrait/landscape phone/tablet and supported browsers. Check overflow, touch targets, chart/table readability, filters, menus, long labels and dialogs. Retain screenshots or browser test evidence where tooling exists.
6. Resilience/performance: verify loading/empty/error/offline/denied states, repeated refresh/navigation cleanup, stale responses, preserved filters, bounded requests, pagination and representative large datasets. Establish an explicit performance target based on the VPS/data workload and report measurements.
7. Lifecycle: version app changes, fixtures and migrations. Verify new-site install and existing-site upgrade, asset build, backup of database/files/configuration, restore rehearsal, and rollback compatible with schema changes. Do not claim a git revert reverses an irreversible migration. Deploy only to the authorized target/site and run role/data smoke checks afterward.

## Required handoff

Provide the audit/retain-improve-build mapping, KPI dictionary, action mapping, role/assignment matrix, requirement-to-test matrix, exact build/test results, and install/upgrade/backup/rollback notes. Distinguish implementation complete, verified locally, verified on site, and pending checks. No release approval claim until the relevant acceptance evidence exists.
