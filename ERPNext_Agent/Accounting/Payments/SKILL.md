# Accounting - Payments Domain Skill

## 1. Section Overview & Purpose
Customer receipts, vendor remittances, advance payments, and internal bank transfers.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Payments`  
**Primary DocTypes:** Payment Entry, Payment Request, Mode of Payment

## 2. DocTypes & Field Requirements
### Payment Entry
**Mandatory Fields:**
- `payment_type` (Payment Type - Select)
- `posting_date` (Posting Date - Date)
- `company` (Company - Link)
- `paid_from` (Account Paid From - Link)
- `paid_from_account_currency` (Account Currency (From) - Link)
- `paid_to` (Account Paid To - Link)
- `paid_to_account_currency` (Account Currency (To) - Link)
- `paid_amount` (Paid Amount - Currency)
- `source_exchange_rate` (Source Exchange Rate - Float)
- `base_paid_amount` (Paid Amount (Company Currency) - Currency)
- `received_amount` (Received Amount - Currency)
- `target_exchange_rate` (Target Exchange Rate - Float)
- `base_received_amount` (Received Amount (Company Currency) - Currency)

**Key Contextual Fields:**
- `payment_order_status` (Payment Order Status)
- `mode_of_payment` (Mode of Payment)
- `party_type` (Party Type)
- `party` (Party)
- `party_name` (Party Name)
- `book_advance_payments_in_separate_party_account` (Book Advance Payments in Separate Party Account)
- `reconcile_on_advance_payment_date` (Reconcile on Advance Payment Date)
- `apply_tds` (Consider for Tax Withholding)

### Payment Request
**Mandatory Fields:**
- `payment_request_type` (Payment Request Type - Select)
- `grand_total` (Amount - Currency)

**Key Contextual Fields:**
- `transaction_date` (Transaction Date)
- `failed_reason` (Reason for Failure)
- `company` (Company)
- `mode_of_payment` (Mode of Payment)
- `party_type` (Party Type)
- `party` (Party)
- `party_name` (Party Name)
- `reference_doctype` (Reference Doctype)

### Mode of Payment
- *No strictly required custom fields or uses standard defaults.*

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **payment_type**: *"What is the Payment Type?"*
- **posting_date**: *"What is the Posting Date?"*
- **company**: *"What is the Company?"*
- **paid_from**: *"What is the Account Paid From?"*
- **paid_from_account_currency**: *"What is the Account Currency (From)?"*
- **paid_to**: *"What is the Account Paid To?"*
- **paid_to_account_currency**: *"What is the Account Currency (To)?"*
- **paid_amount**: *"What is the Paid Amount?"*
- **source_exchange_rate**: *"What is the Source Exchange Rate?"*
- **base_paid_amount**: *"What is the Paid Amount (Company Currency)?"*
- **received_amount**: *"What is the Received Amount?"*
- **target_exchange_rate**: *"What is the Target Exchange Rate?"*
- **base_received_amount**: *"What is the Received Amount (Company Currency)?"*
- **payment_request_type**: *"What is the Payment Request Type?"*
- **grand_total**: *"What is the Amount?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.