# Stock - Purchase Receipt Domain Skill

## 1. Section Overview & Purpose
Inbound vendor delivery receipts and inventory intake.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Purchase Receipt`  
**Primary DocTypes:** Purchase Receipt

## 2. DocTypes & Field Requirements
### Purchase Receipt
**Mandatory Fields:**
- `supplier` (Supplier - Link)
- `posting_date` (Date - Date)
- `posting_time` (Posting Time - Time)
- `company` (Company - Link)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `items` (Items - Table)
- `base_net_total` (Net Total (Company Currency) - Currency)
- `status` (Status - Select)

**Key Contextual Fields:**
- `supplier_name` (Supplier Name)
- `supplier_delivery_note` (Supplier Delivery Note)
- `subcontracting_receipt` (Subcontracting Receipt)
- `set_posting_time` (Edit Posting Date and Time)
- `apply_putaway_rule` (Apply Putaway Rule)
- `is_return` (Is Return)
- `return_against` (Return Against Purchase Receipt)
- `cost_center` (Cost Center)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **supplier**: *"What is the Supplier?"*
- **posting_date**: *"What is the Date?"*
- **posting_time**: *"What is the Posting Time?"*
- **company**: *"What is the Company?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Exchange Rate?"*
- **items**: *"What is the Items?"*
- **base_net_total**: *"What is the Net Total (Company Currency)?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.