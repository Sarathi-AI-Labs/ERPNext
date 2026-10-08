# SKILL ARCHITECTURE SPECIFICATION

## 1. The 13 Module Skill Domains

The Sarathi Industrial AI Agent organizes all ERPNext capabilities into 13 discrete module domains. Each module folder contains its specialized domain rules, field requirements, workflows, and submodule section skills:

```
ERPNext_Agent/
├── 01. Organization/          # Legal entities, Company, Department, Branch, Currencies
├── 02. Assets/                # Fixed Assets, Depreciation Schedules, Asset Maintenance
├── 03. Buying/                # Suppliers, Purchase Orders, RFQs, Purchase Invoices
├── 04. Manufacturing/         # BOMs, Work Orders, Operations, Job Cards, Workstations
├── 05. Projects/              # Projects, Tasks, Timesheets, Sarathi BOM Linking
├── 06. Quality/               # Quality Inspections, Parameters, Non-Conformance
├── 07. Selling/               # Customers, Quotations, Sales Orders, Sales Invoices
├── 08. Subcontracting/        # Subcontracting Orders, Subcontracting BOMs, Receipts
├── 09. Accounting/            # Chart of Accounts, Journal Entries, Payments, Cost Centers
├── 10. Stock/                 # Items, Warehouses, Stock Entries, Delivery Notes, Receipts
├── 11. ERPNext Settings/      # Global Defaults, System Configuration, Stock Settings
├── 12. Framework/             # DocTypes, Custom Fields, Client/Server Scripts, Print Formats
└── 13. Users and System/      # Users, Roles, Role Permissions, System Settings, Audits
```

---

## 2. Skill Folder Anatomy

Every module directory adheres to a standardized four-file contract:

1. **`SKILL.md`**:
   - High-level domain overview, business purpose, primary DocTypes, and validation rules.
2. **`rules.json`**:
   - Machine-readable business rules, auto-set field calculations, and invariant integrity constraints.
3. **`workflows.json`**:
   - State transition rules (Draft -> Submitted -> Cancelled) and submittability definitions.
4. **`examples.json`**:
   - Few-shot natural language input/output conversational examples for LLM/Agent alignment.
5. **Submodule Section Folders** (e.g. `Organization/Company/`):
   - `section_info.json`: Lists the section's primary DocTypes, description, and slot-filling questions for missing fields.
   - `SKILL.md`: Detailed field-by-field guidelines for that specific submodule.

---

## 3. Dynamic On-Demand Loading (`SkillLoader`)

To prevent LLM context window bloat and eliminate prompt hallucinations:
- **Zero Full-Context Loading**: The agent NEVER injects all 13 module skills into a single prompt.
- **Targeted Loading**: When `SkillRouter` detects `Organization` and `Company`, `SkillLoader` loads ONLY `Organization/SKILL.md` and `Organization/Company/section_info.json`.
- **Runtime Frappe Metadata Integration**: For live field definitions, `GetDocMetaTool` queries Frappe's live database schema (`frappe.get_meta(doctype)`), ensuring that custom fields (e.g. `custom_sarathi_manufacturing`, `custom_sarathi_bom`) are discovered dynamically without hardcoding.

---

## 4. Cross-Module Dependencies

Certain workflows span multiple modules. The `DependencyResolver` models these relationships as a Directed Acyclic Graph (DAG):

```
Company (Organization)
   │
   ├─► Customer (Selling)
   │     │
   │     └─► Sales Order (Selling)
   │           │
   │           └─► Project (Projects)
   │                 │
   │                 ├─► Engineering BOM (Manufacturing)
   │                 │     │
   │                 │     └─► Work Order (Manufacturing)
   │                 │           │
   │                 │           └─► Stock Entry: Manufacture (Stock)
   │                 │
   │                 └─► Sales Invoice (Selling/Accounting)
```

The `DependencyResolver` inspects foreign key link fields and ensures prerequisite records exist before child record creation.
