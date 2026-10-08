# Subcontracting - Outward Order Domain Skill

## 1. Section Overview & Purpose
Receipt of finished subcontracted items and raw material consumption.

**Module:** `Subcontracting`  
**Section Folder:** `ERPNext_Agent/Subcontracting/Outward Order`  
**Primary DocTypes:** Subcontracting Receipt

## 2. DocTypes & Field Requirements
### Subcontracting Receipt
**Mandatory Fields:**
- `supplier` (Job Worker - Link)
- `company` (Company - Link)
- `posting_date` (Date - Date)
- `posting_time` (Posting Time - Time)
- `items` (Items - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `title` (Title)
- `supplier_name` (Job Worker Name)
- `supplier_delivery_note` (Job Worker Delivery Note)
- `set_posting_time` (Edit Posting Date and Time)
- `is_return` (Is Return)
- `return_against` (Return Against Subcontracting Receipt)
- `cost_center` (Cost Center)
- `project` (Project)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **supplier**: *"What is the Job Worker?"*
- **company**: *"What is the Company?"*
- **posting_date**: *"What is the Date?"*
- **posting_time**: *"What is the Posting Time?"*
- **items**: *"What is the Items?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.