# Manufacturing - Material Planning Domain Skill

## 1. Section Overview & Purpose
Master production scheduling, material demand aggregation, and automated work order generation.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Material Planning`  
**Primary DocTypes:** Production Plan

## 2. DocTypes & Field Requirements
### Production Plan
**Mandatory Fields:**
- `company` (Company - Link)
- `posting_date` (Posting Date - Date)
- `po_items` (Assembly Items - Table)

**Key Contextual Fields:**
- `get_items_from` (Get Items From)
- `reserve_stock` (Reserve Stock)
- `item_code` (Item Code)
- `customer` (Customer)
- `warehouse` (Warehouse)
- `project` (Project)
- `sales_order_status` (Sales Order Status)
- `from_date` (From Date)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **posting_date**: *"What is the Posting Date?"*
- **po_items**: *"What is the Assembly Items?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.