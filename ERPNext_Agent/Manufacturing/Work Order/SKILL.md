# Manufacturing - Work Order Domain Skill

## 1. Section Overview & Purpose
Production batch authorization, WIP warehouse staging, and finished goods assembly.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Work Order`  
**Primary DocTypes:** Work Order

## 2. DocTypes & Field Requirements
### Work Order
**Mandatory Fields:**
- `company` (Company - Link)
- `production_item` (Item To Manufacture - Link)
- `bom_no` (BOM No - Link)
- `qty` (Qty To Manufacture - Float)
- `planned_start_date` (Planned Start Date - Datetime)
- `status` (Status - Select)

**Key Contextual Fields:**
- `sales_order` (Sales Order)
- `reserve_stock` (Reserve Stock)
- `max_producible_qty` (Max Producible Qty)
- `material_transferred_for_manufacturing` (Material Transferred for Manufacturing)
- `additional_transferred_qty` (Additional Transferred Qty)
- `produced_qty` (Manufactured Qty)
- `process_loss_qty` (Process Loss Qty)
- `disassembled_qty` (Disassembled Qty)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **production_item**: *"What is the Item To Manufacture?"*
- **bom_no**: *"What is the BOM No?"*
- **qty**: *"What is the Qty To Manufacture?"*
- **planned_start_date**: *"What is the Planned Start Date?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.