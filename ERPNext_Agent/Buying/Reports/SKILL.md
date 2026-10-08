# Buying - Reports Domain Skill

## 1. Section Overview & Purpose
Procurement analytics, supplier delivery performance, and purchase order tracking.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Reports`  
**Primary DocTypes:** Purchase Order, Purchase Invoice

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
- **posting_date**: *"What is the Posting Date?"*
- **credit_to**: *"What is the Credit To?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.