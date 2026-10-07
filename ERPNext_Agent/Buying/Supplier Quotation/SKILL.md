# Buying - Supplier Quotation Domain Skill

## 1. Section Overview & Purpose
Commercial quotations received from vendors with price validity periods.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Supplier Quotation`  
**Primary DocTypes:** Supplier Quotation, Supplier

## 2. DocTypes & Field Requirements
### Supplier Quotation
**Mandatory Fields:**
- `supplier` (Supplier - Link)
- `company` (Company - Link)
- `status` (Status - Select)
- `transaction_date` (Date - Date)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `items` (Items - Table)

**Key Contextual Fields:**
- `supplier_name` (Supplier Name)
- `valid_till` (Valid Till)
- `quotation_number` (Quotation Number)
- `has_unit_price_items` (Has Unit Price Items)
- `amended_from` (Amended From)
- `cost_center` (Cost Center)
- `project` (Project)
- `buying_price_list` (Price List)

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
- **company**: *"What is the Company?"*
- **status**: *"What is the Status?"*
- **transaction_date**: *"What is the Date?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Exchange Rate?"*
- **items**: *"What is the Items?"*
- **supplier_name**: *"What is the Supplier Name?"*
- **supplier_type**: *"What is the Supplier Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.