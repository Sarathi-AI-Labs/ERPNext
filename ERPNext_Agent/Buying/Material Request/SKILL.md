# Buying - Material Request Domain Skill

## 1. Section Overview & Purpose
Internal purchase requisitions, indent approvals, and manufacturing component demand.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Material Request`  
**Primary DocTypes:** Material Request

## 2. DocTypes & Field Requirements
### Material Request
**Mandatory Fields:**
- `material_request_type` (Purpose - Select)
- `company` (Company - Link)
- `transaction_date` (Transaction Date - Date)
- `items` (Items - Table)

**Key Contextual Fields:**
- `title` (Title)
- `customer` (Customer)
- `auto_created_via_reorder` (Auto Created (Reorder))
- `schedule_date` (Required By)
- `buying_price_list` (Price List)
- `amended_from` (Amended From)
- `scan_barcode` (Scan Barcode)
- `last_scanned_warehouse` (Last Scanned Warehouse)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **material_request_type**: *"What is the Purpose?"*
- **company**: *"What is the Company?"*
- **transaction_date**: *"What is the Transaction Date?"*
- **items**: *"What is the Items?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.