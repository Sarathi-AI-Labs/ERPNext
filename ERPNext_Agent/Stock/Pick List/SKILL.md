# Stock - Pick List Domain Skill

## 1. Section Overview & Purpose
Warehouse picking slips for batch and serial item fulfillment.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Pick List`  
**Primary DocTypes:** Pick List

## 2. DocTypes & Field Requirements
### Pick List
**Mandatory Fields:**
- `company` (Company - Link)
- `status` (Status - Select)

**Key Contextual Fields:**
- `purpose` (Purpose)
- `customer` (Customer)
- `for_qty` (Qty of Finished Goods Item)
- `parent_warehouse` (Warehouse)
- `consider_rejected_warehouses` (Consider Rejected Warehouses)
- `get_item_locations` (Get Item Locations)
- `pick_manually` (Pick Manually)
- `ignore_pricing_rule` (Ignore Pricing Rule)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.