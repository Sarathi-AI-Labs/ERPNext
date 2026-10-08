---
name: ERPNext Settings Skill
description: Global configuration, business rules, single DocType controls, negative stock toggles, manufacturing tolerances, and automated numbering.
version: 1.0.0
module: ERPNext Settings
---

# ERPNext Global Configuration & Business Settings Domain Skill

## 1. Domain Overview
The **ERPNext Settings** module encompasses singleton ("Single") DocTypes that define the operational rules and behavioral boundaries across all other modules.

### Key Entities:
1. **Stock Settings**: Controls `allow_negative_stock` (strictly 0 in this environment), automated valuation recalculation, serial/batch naming series, and default sample retention warehouses.
2. **Manufacturing Settings**: Controls overproduction allowance percentages, backflush raw materials based on material transfer vs BOM, and capacity planning limits.
3. **Accounts Settings**: Controls credit limit enforcement, round off accounts, default fiscal years, and payment reconciliation thresholds.
4. **Buying Settings**: Controls supplier quotation requirements, purchase order approvals, and over-receipt allowances.
5. **Selling Settings**: Controls customer credit validation, sales commission calculations, and quotation validity defaults.
6. **Global Defaults**: Defines system-wide default company, default currency, and active fiscal year.

---

## 2. Field Requirements & Rules
All entities in this module are Single DocTypes (meaning only one row exists in the database per site):
- **Stock Settings**:
  - `allow_negative_stock` (Check, must remain 0 for strict inventory integrity).
  - `auto_indent` (Check): Enables auto material requests when items hit reorder levels.
- **Manufacturing Settings**:
  - `backflush_raw_materials_based_on` (Select: "BOM" or "Material Transferred for Manufacture").
  - `overproduction_percentage_for_work_order` (Percent).

---

## 3. Workflow & Lifecycle Transitions
- Single DocTypes are non-submittable (`is_submittable = 0`).
- Changes must be saved via `frappe.get_single(doctype).update(values).save()`.
