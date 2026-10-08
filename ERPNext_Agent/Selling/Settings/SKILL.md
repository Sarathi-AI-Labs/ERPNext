# Selling - Settings Domain Skill

## 1. Section Overview & Purpose
Credit limit verification and price list policies.

**Module:** `Selling`  
**Section Folder:** `ERPNext_Agent/Selling/Settings`  
**Primary DocTypes:** Selling Settings

## 2. DocTypes & Field Requirements
### Selling Settings
**Mandatory Fields:**
- `sales_update_frequency` (How often should sales data be updated in Company/Project? - Select)

**Key Contextual Fields:**
- `cust_master_name` (Customer Naming By)
- `naming_series_details` (Naming Series options)
- `configure` (Configure Series)
- `customer_group` (Default Customer Group)
- `territory` (Default Territory)
- `selling_price_list` (Default Price List)
- `fallback_to_default_price_list` (Use prices from Default Price List as fallback)
- `editable_price_list_rate` (Allow editing Price List rate in transactions)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **sales_update_frequency**: *"What is the How often should sales data be updated in Company/Project??"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.