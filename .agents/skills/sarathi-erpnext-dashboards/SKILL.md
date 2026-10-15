---
name: sarathi-erpnext-dashboards
description: Builds and audits Sarathi AI Labs role-based ERPNext dashboards in sarathi_owner and sarathi_visibility, including executive finance, production control, shop-floor workflows, permissions, and mobile layouts. Use for implementation, redesign, validation, or release work on these dashboards.
---

# Sarathi ERPNext dashboards

Build three connected Frappe Desk experiences inside each company's dedicated ERPNext installation. ERPNext owns accounting, stock, manufacturing transactions, and workflow validation. This skill works through ordinary file, terminal, and browser capabilities; it requires no agent-specific API or plugin.

## Scope and architecture

- Owner and executive: `sarathi_owner`, `/desk/sarathiownertower`.
- Production management: `sarathi_visibility`, `/desk/sarathicontroltower`.
- Shop floor: a dedicated page in `sarathi_visibility`; discover any existing route before choosing a new one.
- One customer company gets one VPS and ERPNext site/database environment, containing its own business customers, users, configuration, and data. Do not introduce a shared cross-client database or confuse Customer with Company.
- Retain the app boundaries and ERPNext backend. A fresh dashboard build may replace presentation and dashboard services where necessary; inspect existing code first and preserve working business behavior and unrelated local edits.
- Share responsive styles, filter semantics, permissions helpers, and data services without creating circular app dependencies or an unnecessary third app.

## Mandatory boundary: ERPNext/Frappe source is read-only

- Never edit, delete, patch, fork, or replace ERPNext/Frappe core source, including `ERPNEXT_MAIN/` and installed bench `apps/erpnext/` or `apps/frappe/`. Reading source to understand data, reports, permissions, and APIs is allowed.
- Put all dashboard implementation, assets, endpoints, tests, fixtures, and app-owned migrations in `sarathi_owner` or `sarathi_visibility`; supporting documentation may live in project documentation directories.
- Consume existing ERPNext records, supported APIs, reports, and document/controller methods. Do not monkey-patch core behavior, override core controllers/methods, or directly alter core database schema to make a dashboard work.
- Authorized shop-floor actions may change business records through existing validated ERPNext operations; this does not authorize source-code changes. Dashboard reads must remain side-effect-free.
- If a requirement cannot be met within this boundary, document the limitation and offer a custom-app solution or an existing ERPNext form/action. Do not modify core as a workaround.
- Before handoff, inspect the diff and confirm that this task introduced no ERPNext/Frappe core changes. Preserve any pre-existing unrelated edits.

## Begin with evidence

Read repository instructions and inspect git status before edits. Discover actual Frappe/ERPNext versions, app hooks, page assets, API methods, fixtures, migrations, DocTypes, role permissions, assignment mechanisms, and available test/runtime tooling. README claims are leads, not proof of live configuration. Never expose site secrets in output.

Produce an audit and a retain/improve/build mapping in project documentation before changing dashboard code. For every KPI, record source fields, formula, date basis, status exclusions, currency/UOM, filter support, permission scope, refresh expectations, and reconciliation report. Mark assumptions and unavailable sources explicitly. Existing demo company/project defaults must not become production restrictions.

Use [dashboard-requirements.md](references/dashboard-requirements.md) to scope screens, [data-and-actions.md](references/data-and-actions.md) before backend work, and [responsive-and-acceptance.md](references/responsive-and-acceptance.md) before layout or validation work. These references contain the product requirements; do not substitute an unrelated website builder or standalone ERP.

## Implement in reviewable stages

1. Audit and foundation: document contracts, role scopes, metric definitions, and shared design tokens.
2. Owner: implement real business metrics and drill-downs, with accounting reconciliation.
3. Production: implement Work Order/Job Card progress, shortages, delays, and factory coordination.
4. Shop floor: implement assignment-scoped work and only actions mapped to valid ERPNext methods.
5. Advanced intelligence: add quality, subcontracting, downtime, timelines, capacity, or telemetry only when reliable configured sources exist. Forecasting, predictive alerts, OEE, and AI recommendations are later enhancements.
6. Release: validate accuracy, access, responsive behavior, concurrency, performance, installation, upgrade, backup, and rollback.

Apply mobile requirements during each stage. Keep a requirements-to-code-and-test matrix and a short implementation status document so either agent can resume the work. Proceed within the user's authorized scope; a skill-only request ends after creating and validating the skill. Do not deploy to a live VPS merely because implementation was requested.

## Completion evidence

Report what changed, files/routes, validation actually executed, unresolved configuration decisions, and remaining acceptance failures. Never label demo values, unavailable data, or unexecuted tests as verified. A successful local build alone does not establish financial reconciliation, role isolation, or production readiness.

## Portable use

Keep this folder at `<repository>/.agents/skills/sarathi-erpnext-dashboards/`. Invoke in Codex with `$sarathi-erpnext-dashboards`; in Antigravity, request the skill by name (or use the available skill slash command). If discovery is unavailable in an older client, explicitly ask it to read this `SKILL.md`; legacy Antigravity also supports `.agent/skills/`. Keep one maintained copy and relative reference links.

Discovery references: [Codex skills](https://developers.openai.com/codex/skills) and [Antigravity skills](https://antigravity.google/docs/skills). Format compatibility does not prove execution in both clients; report runtime checks separately.
