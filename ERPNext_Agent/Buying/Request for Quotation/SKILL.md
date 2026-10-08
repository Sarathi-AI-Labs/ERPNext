# Buying - Request for Quotation Domain Skill

## 1. Section Overview & Purpose
Tendering documents sent to multiple vendors to solicit competitive bids.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Request for Quotation`  
**Primary DocTypes:** Request for Quotation, Supplier

## 2. DocTypes & Field Requirements
### Request for Quotation
**Mandatory Fields:**
- `company` (Company - Link)
- `transaction_date` (Date - Date)
- `status` (Status - Select)
- `suppliers` (Suppliers - Table)
- `items` (Items - Table)
- `subject` (Subject - Data)

**Key Contextual Fields:**
- `vendor` (Supplier)
- `schedule_date` (Required Date)
- `has_unit_price_items` (Has Unit Price Items)
- `amended_from` (Amended From)
- `email_template` (Email Template)
- `preview` (Preview Email)
- `html_llwp` (html_llwp)
- `send_attached_files` (Send Attached Files)

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
- **company**: *"What is the Company?"*
- **transaction_date**: *"What is the Date?"*
- **status**: *"What is the Status?"*
- **suppliers**: *"What is the Suppliers?"*
- **items**: *"What is the Items?"*
- **subject**: *"What is the Subject?"*
- **supplier_name**: *"What is the Supplier Name?"*
- **supplier_type**: *"What is the Supplier Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.