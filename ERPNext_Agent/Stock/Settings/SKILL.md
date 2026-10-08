# Stock - Settings Domain Skill

## 1. Section Overview & Purpose
Zero negative stock rule and serial/batch defaults.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Settings`  
**Primary DocTypes:** Stock Settings

## 2. DocTypes & Field Requirements
### Stock Settings
- *No strictly required custom fields or uses standard defaults.*

**Key Contextual Fields:**
- `item_naming_by` (Item Naming By)
- `naming_series_details` (Naming Series options)
- `configure` (Configure Series)
- `item_group` (Default Item Group)
- `valuation_method` (Default Valuation Method)
- `auto_insert_price_list_rate_if_missing` (Auto insert Item Price if missing)
- `update_existing_price_list_rate` (Update existing Price List Rate)
- `update_price_list_based_on` (Update Price List based on)

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