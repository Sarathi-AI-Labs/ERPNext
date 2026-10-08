# Stock - Tools Domain Skill

## 1. Section Overview & Purpose
Physical stock count reconciliations and landed cost vouchers.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Tools`  
**Primary DocTypes:** Stock Reconciliation

## 2. DocTypes & Field Requirements
### Stock Reconciliation
**Mandatory Fields:**
- `company` (Company - Link)
- `purpose` (Purpose - Select)
- `posting_date` (Posting Date - Date)
- `posting_time` (Posting Time - Time)
- `items` (Items - Table)

**Key Contextual Fields:**
- `set_posting_time` (Edit Posting Date and Time)
- `set_warehouse` (Default Warehouse)
- `scan_barcode` (Scan Barcode)
- `last_scanned_warehouse` (Last Scanned Warehouse)
- `scan_mode` (Scan Mode)
- `expense_account` (Difference Account)
- `difference_amount` (Difference Amount)
- `amended_from` (Amended From)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **purpose**: *"What is the Purpose?"*
- **posting_date**: *"What is the Posting Date?"*
- **posting_time**: *"What is the Posting Time?"*
- **items**: *"What is the Items?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.