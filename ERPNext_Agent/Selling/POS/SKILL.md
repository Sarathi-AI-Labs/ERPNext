# Selling - POS Domain Skill

## 1. Section Overview & Purpose
Retail checkout profiles and cashier registers.

**Module:** `Selling`  
**Section Folder:** `ERPNext_Agent/Selling/POS`  
**Primary DocTypes:** POS Profile

## 2. DocTypes & Field Requirements
### POS Profile
**Mandatory Fields:**
- `company` (Company - Link)
- `warehouse` (Warehouse - Link)
- `payments` (Payment Methods - Table)
- `currency` (Currency - Link)
- `write_off_account` (Write Off Account - Link)
- `write_off_cost_center` (Write Off Cost Center - Link)
- `write_off_limit` (Write Off Limit - Currency)

**Key Contextual Fields:**
- `customer` (Customer)
- `country` (Country)
- `disabled` (Disabled)
- `company_address` (Company Address)
- `set_grand_total_to_default_mop` (Set Grand Total to Default Payment Method)
- `selling_price_list` (Price List)
- `income_account` (Income Account)
- `expense_account` (Expense Account)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **warehouse**: *"What is the Warehouse?"*
- **payments**: *"What is the Payment Methods?"*
- **currency**: *"What is the Currency?"*
- **write_off_account**: *"What is the Write Off Account?"*
- **write_off_cost_center**: *"What is the Write Off Cost Center?"*
- **write_off_limit**: *"What is the Write Off Limit?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.