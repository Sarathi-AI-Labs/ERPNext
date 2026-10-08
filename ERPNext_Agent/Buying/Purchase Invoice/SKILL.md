# Buying - Purchase Invoice Domain Skill

## 1. Section Overview & Purpose
Accounts payable billing against purchase orders and incoming goods receipts.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Purchase Invoice`  
**Primary DocTypes:** Purchase Invoice, Supplier

## 2. DocTypes & Field Requirements
### Purchase Invoice
**Mandatory Fields:**
- `supplier` (Supplier - Link)
- `posting_date` (Posting Date - Date)
- `items` (Items - Table)
- `credit_to` (Credit To - Link)

**Key Contextual Fields:**
- `supplier_name` (Supplier Name)
- `tax_id` (Tax Id)
- `company` (Company)
- `posting_time` (Posting Time)
- `set_posting_time` (Edit Posting Date and Time)
- `due_date` (Due Date)
- `is_paid` (Is Paid)
- `is_return` (Is Return (Debit Note))

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
- **posting_date**: *"What is the Posting Date?"*
- **items**: *"What is the Items?"*
- **credit_to**: *"What is the Credit To?"*
- **supplier_name**: *"What is the Supplier Name?"*
- **supplier_type**: *"What is the Supplier Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.