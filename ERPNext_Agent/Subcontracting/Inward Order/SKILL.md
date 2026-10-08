# Subcontracting - Inward Order Domain Skill

## 1. Section Overview & Purpose
Outsourced job work commitments with vendor component supply.

**Module:** `Subcontracting`  
**Section Folder:** `ERPNext_Agent/Subcontracting/Inward Order`  
**Primary DocTypes:** Subcontracting Order

## 2. DocTypes & Field Requirements
### Subcontracting Order
**Mandatory Fields:**
- `purchase_order` (Subcontracting Purchase Order - Link)
- `supplier` (Job Worker - Link)
- `supplier_name` (Job Worker Name - Data)
- `supplier_warehouse` (Job Worker Warehouse - Link)
- `company` (Company - Link)
- `transaction_date` (Date - Date)
- `items` (Items - Table)
- `service_items` (Service Items - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `supplier_currency` (Job Worker Currency)
- `schedule_date` (Required By)
- `amended_from` (Amended From)
- `cost_center` (Cost Center)
- `project` (Project)
- `set_warehouse` (Set Target Warehouse)
- `total_qty` (Total Quantity)
- `total` (Total)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **purchase_order**: *"What is the Subcontracting Purchase Order?"*
- **supplier**: *"What is the Job Worker?"*
- **supplier_name**: *"What is the Job Worker Name?"*
- **supplier_warehouse**: *"What is the Job Worker Warehouse?"*
- **company**: *"What is the Company?"*
- **transaction_date**: *"What is the Date?"*
- **items**: *"What is the Items?"*
- **service_items**: *"What is the Service Items?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.