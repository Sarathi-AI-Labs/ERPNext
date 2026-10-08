# ERPNext Settings - Accounts Settings Domain Skill

## 1. Section Overview & Purpose
Credit limit enforcement and fiscal defaults.

**Module:** `ERPNext Settings`  
**Section Folder:** `ERPNext_Agent/ERPNext Settings/Accounts Settings`  
**Primary DocTypes:** Accounts Settings

## 2. DocTypes & Field Requirements
### Accounts Settings
- *No strictly required custom fields or uses standard defaults.*

**Key Contextual Fields:**
- `unlink_payment_on_cancellation_of_invoice` (Unlink Payment on cancellation of invoice)
- `unlink_advance_payment_on_cancelation_of_order` (Unlink Advance Payment on cancellation of order)
- `delete_linked_ledger_entries` (Delete Accounting and Stock Ledger entries on deletion of transaction)
- `enable_immutable_ledger` (Enable Immutable Ledger)
- `check_supplier_invoice_uniqueness` (Check Supplier invoice number uniqueness)
- `automatically_fetch_payment_terms` (Automatically fetch Payment Terms from Order/Quotation)
- `enable_subscription` (Enable Subscription)
- `enable_common_party_accounting` (Enable Common Party Accounting)

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