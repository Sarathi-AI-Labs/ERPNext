# Subcontracting - Setup Domain Skill

## 1. Section Overview & Purpose
Service items and outsourced process specifications.

**Module:** `Subcontracting`  
**Section Folder:** `ERPNext_Agent/Subcontracting/Setup`  
**Primary DocTypes:** Subcontracting BOM

## 2. DocTypes & Field Requirements
### Subcontracting BOM
**Mandatory Fields:**
- `finished_good` (Finished Good - Link)
- `finished_good_qty` (Finished Good Qty - Float)
- `finished_good_bom` (Finished Good BOM - Link)
- `service_item` (Service Item - Link)
- `service_item_qty` (Service Item Qty - Float)
- `service_item_uom` (Service Item UOM - Link)

**Key Contextual Fields:**
- `is_active` (Is Active)
- `finished_good_uom` (Finished Good UOM)
- `conversion_factor` (Conversion Factor)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **finished_good**: *"What is the Finished Good?"*
- **finished_good_qty**: *"What is the Finished Good Qty?"*
- **finished_good_bom**: *"What is the Finished Good BOM?"*
- **service_item**: *"What is the Service Item?"*
- **service_item_qty**: *"What is the Service Item Qty?"*
- **service_item_uom**: *"What is the Service Item UOM?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.