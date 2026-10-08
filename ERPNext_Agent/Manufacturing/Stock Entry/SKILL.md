# Manufacturing - Stock Entry Domain Skill

## 1. Section Overview & Purpose
Manufacture stock entries, WIP staging, and scrap recording.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Stock Entry`  
**Primary DocTypes:** Stock Entry

## 2. DocTypes & Field Requirements
### Stock Entry
**Mandatory Fields:**
- `company` (Company - Link)
- `stock_entry_type` (Stock Entry Type - Link)
- `items` (Items - Table)

**Key Contextual Fields:**
- `purpose` (Purpose)
- `set_posting_time` (Edit Posting Date and Time)
- `posting_date` (Posting Date)
- `posting_time` (Posting Time)
- `add_to_transit` (Add to Transit)
- `apply_putaway_rule` (Apply Putaway Rule)
- `inspection_required` (Inspection Required)
- `work_order` (Work Order)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **stock_entry_type**: *"What is the Stock Entry Type?"*
- **items**: *"What is the Items?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.