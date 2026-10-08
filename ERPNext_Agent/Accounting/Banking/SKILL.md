# Accounting - Banking Domain Skill

## 1. Section Overview & Purpose
Bank master setup, company bank accounts, and bank clearing reconciliation.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Banking`  
**Primary DocTypes:** Bank, Bank Account, Payment Entry

## 2. DocTypes & Field Requirements
### Bank
**Mandatory Fields:**
- `bank_name` (Bank Name - Data)

**Key Contextual Fields:**
- `swift_number` (SWIFT number)
- `website` (Website)
- `address_html` (Address HTML)
- `contact_html` (Contact HTML)
- `bank_transaction_mapping` (Bank Transaction Mapping)
- `plaid_access_token` (Plaid Access Token)

### Bank Account
**Mandatory Fields:**
- `account_name` (Account Name - Data)
- `bank` (Bank - Link)

**Key Contextual Fields:**
- `account` (Company Account)
- `account_type` (Account Type)
- `account_subtype` (Account Subtype)
- `disabled` (Disabled)
- `is_default` (Is Default Account)
- `is_company_account` (Is Company Account)
- `company` (Company)
- `is_credit_card` (Is Credit Card)

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

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **bank_name**: *"What is the Bank Name?"*
- **account_name**: *"What is the Account Name?"*
- **bank**: *"What is the Bank?"*
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

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.