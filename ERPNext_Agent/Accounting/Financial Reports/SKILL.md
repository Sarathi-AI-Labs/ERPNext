# Accounting - Financial Reports Domain Skill

## 1. Section Overview & Purpose
General Ledger, Trial Balance, Profit and Loss, and Balance Sheet analysis.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Financial Reports`  
**Primary DocTypes:** Journal Entry, GL Entry

## 2. DocTypes & Field Requirements
### Journal Entry
**Mandatory Fields:**
- `company` (Company - Link)
- `voucher_type` (Entry Type - Select)
- `posting_date` (Posting Date - Date)
- `accounts` (Accounting Entries - Table)

**Key Contextual Fields:**
- `multi_currency` (Multi Currency)
- `apply_tds` (Consider for Tax Withholding )
- `tax_withholding_category` (Tax Withholding Category)
- `is_system_generated` (Is System Generated)
- `amended_from` (Amended From)
- `for_all_stock_asset_accounts` (For All Stock Asset Accounts)
- `stock_asset_account` (Stock Asset Account)
- `periodic_entry_difference_account` (Periodic Entry Difference Account)

### GL Entry
- *No strictly required custom fields or uses standard defaults.*

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **voucher_type**: *"What is the Entry Type?"*
- **posting_date**: *"What is the Posting Date?"*
- **accounts**: *"What is the Accounting Entries?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.