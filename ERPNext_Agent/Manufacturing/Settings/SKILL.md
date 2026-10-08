# Manufacturing - Settings Domain Skill

## 1. Section Overview & Purpose
Overproduction allowances and shop floor backflush rules.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Settings`  
**Primary DocTypes:** Manufacturing Settings

## 2. DocTypes & Field Requirements
### Manufacturing Settings
- *No strictly required custom fields or uses standard defaults.*

**Key Contextual Fields:**
- `material_consumption` (Allow Continuous Material Consumption)
- `get_rm_cost_from_consumption_entry` (Get Raw Materials Cost from Consumption Entry)
- `backflush_raw_materials_based_on` (Backflush Raw Materials Based On)
- `validate_components_quantities_per_bom` (Validate Components and Quantities Per BOM)
- `update_bom_costs_automatically` (Update BOM Cost Automatically)
- `allow_editing_of_items_and_quantities_in_work_order` (Allow Editing of Items and Quantities in Work Order)
- `overproduction_percentage_for_sales_order` (Overproduction Percentage For Sales Order)
- `overproduction_percentage_for_work_order` (Overproduction Percentage For Work Order)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- Identify the target DocType and ask the user for its primary identifier and owning Company.

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.