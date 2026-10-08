---
name: Organization Skill
description: Core organizational hierarchy, legal entities, chart of accounts roots, departments, and custom organizational mappings in ERPNext and Frappe.
version: 1.0.0
module: Organization
---

# Organization Domain Skill

## 1. Domain Overview
The **Organization** module represents the structural and institutional backbone of ERPNext. All financial, manufacturing, inventory, and procurement transactions are partitioned by legal entity (`Company`).

### Key Entities:
1. **Company**: Root legal entity. Defines default currency, chart of accounts, standard warehouses, and fiscal year associations.
2. **Fiscal Year**: The statutory accounting year (e.g. 2026-2027) with defined start and end dates.
3. **Cost Center**: Budgeting and expense allocation nodes arranged in a nested tree structure.
4. **Department**: Operational units (e.g., "R&D", "Assembly", "Sales") organized hierarchically.
5. **Branch**: Physical office or regional unit without independent balance sheets.
6. **Sarathi Customer Organization**: Custom DocType linking external client organizations to internal operations.

---

## 2. Field Requirements & Rules

### Company
- **company_name** (Data, Required): Unique official legal name.
- **abbr** (Data, Required): 1 to 5 uppercase character abbreviation used as a suffix across accounts, warehouses, and cost centers (e.g., `S` or `SAI`). Once set, changing abbreviation triggers bulk ledger renames.
- **default_currency** (Link Currency, Required): Base reporting currency (e.g. `INR`, `USD`).
- **country** (Link Country, Required): Legal jurisdiction.
- **is_group** (Check): 1 if parent holding company, 0 if operational entity.

### Cost Center
- **cost_center_name** (Data, Required): Label of the node.
- **company** (Link Company, Required): Owning company.
- **is_group** (Check): 1 for grouping branch nodes, 0 for posting leaf nodes.
- **parent_cost_center** (Link Cost Center, Required if not root).

### Department
- **department_name** (Data, Required).
- **company** (Link Company, Optional).
- **parent_department** (Link Department, Optional).

---

## 3. Workflow & Lifecycle Transitions
- Organizational entities are non-submittable master records (`is_submittable = 0`, `docstatus = 0`).
- Deletion is blocked if child transactions (GL Entries, Stock Ledgers, Invoices) reference the entity.
- Renaming companies or abbreviations must be done through Frappe rename tools to preserve relational integrity.

---

## 4. Edge Cases & Constraints
1. **Abbreviation Collision**: Abbreviation must be unique across all companies in the site.
2. **Tree Structure Integrity**: An operational transaction can only post to leaf cost centers (`is_group = 0`).
3. **Fiscal Year Overlaps**: Two fiscal years for the same company cannot have overlapping date ranges.
