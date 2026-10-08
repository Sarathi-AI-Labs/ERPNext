# Buying - Purchase Order Domain Skill

## 1. Section Overview & Purpose
Legally binding vendor procurement contracts with delivery lead times and pricing terms.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Purchase Order`  
**Primary DocTypes:** Purchase Order, Supplier

## 2. DocTypes & Field Requirements
### Purchase Order
**Mandatory Fields:**
- `supplier` (Supplier - Link)
- `transaction_date` (Date - Date)
- `company` (Company - Link)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `items` (Items - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `supplier_name` (Supplier Name)
- `order_confirmation_no` (Order Confirmation No)
- `order_confirmation_date` (Order Confirmation Date)
- `transaction_time` (Time)
- `schedule_date` (Required By)
- `is_subcontracted` (Is Subcontracted)
- `has_unit_price_items` (Has Unit Price Items)
- `supplier_warehouse` (Supplier Warehouse)

### Supplier
**Mandatory Fields:**
- `supplier_name` (Supplier Name - Data)
- `supplier_type` (Supplier Type - Select)

**Key Contextual Fields:**
- `alias` (Alias)
- `gender` (Gender)
- `supplier_group` (Supplier Group)
- `country` (Country)
- `image` (Image)
- `default_currency` (Billing Currency)
- `default_bank_account` (Company Bank Account)
- `default_price_list` (Price List)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **supplier**: *"What is the Supplier?"*
- **transaction_date**: *"What is the Date?"*
- **company**: *"What is the Company?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Exchange Rate?"*
- **items**: *"What is the Items?"*
- **status**: *"What is the Status?"*
- **supplier_name**: *"What is the Supplier Name?"*
- **supplier_type**: *"What is the Supplier Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.