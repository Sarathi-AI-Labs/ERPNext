---
name: Framework Skill
description: Low-code metadata layer of Frappe Framework, DocType schema customization, Custom Fields, Property Setters, Server Scripts, Client Scripts, and Print Formats.
version: 1.0.0
module: Framework
---

# Frappe Framework Low-Code Domain Skill

## 1. Domain Overview
The **Framework** module enables dynamic schema manipulation, low-code scripting, and UI customization inside Frappe v16 without requiring direct database modifications or Python file alterations.

### Key Entities:
1. **DocType**: Core meta-object defining database table schemas, controllers, child tables, permissions, and behavior.
2. **Custom Field**: Safely adds user/developer defined attributes to standard ERPNext DocTypes (e.g. `custom_sarathi_bom` on `Project`).
3. **Property Setter**: Overrides standard DocType or DocField attributes (such as `read_only`, `hidden`, `default`, `mandatory`) non-destructively.
4. **Server Script**: Sandboxed Python script executed on DocType triggers (`before_insert`, `after_save`, `on_submit`, `before_cancel`) or API methods.
5. **Client Script**: Browser-side JavaScript executed during desk view interactions (`refresh`, `validate`, field changes).
6. **Workflow**: State machine definition overriding standard `docstatus` with custom multistage approval steps.

---

## 2. Field Requirements & Rules

### Custom Field
- **dt** (Link DocType, Required): Target DocType receiving the custom field (e.g. `Project`).
- **fieldname** (Data, Required): Snake_case identifier prefixed with `custom_` (e.g. `custom_sarathi_manufacturing`).
- **label** (Data, Required): Human display label.
- **fieldtype** (Select, Required): Data, Select, Check, Int, Float, Currency, Link, Table, etc.
- **options** (Small Text): If `fieldtype` is Link, options specifies target DocType (e.g. `BOM`). If Select, newline-separated options.
- **insert_after** (Data, Optional): Target field after which to place this UI element.

### Property Setter
- **doc_type** (Link DocType, Required).
- **property** (Data, Required): e.g. `read_only`, `reqd`, `hidden`.
- **property_type** (Data, Required): "Check", "Data", "Select", "Small Text".
- **value** (Data, Required).

---

## 3. Workflow & Lifecycle Transitions
- Framework metadata documents are non-submittable (`is_submittable = 0`).
- Modifications immediately take effect after cache clearing (`frappe.clear_cache()`).
