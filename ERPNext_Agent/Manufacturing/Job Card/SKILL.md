# Manufacturing - Job Card Domain Skill

## 1. Section Overview & Purpose
Shop-floor machine/operator work assignments and actual cycle time tracking.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Job Card`  
**Primary DocTypes:** Job Card

## 2. DocTypes & Field Requirements
### Job Card
**Mandatory Fields:**
- `work_order` (Work Order - Link)
- `company` (Company - Link)
- `operation` (Operation - Link)
- `workstation` (Workstation - Link)

**Key Contextual Fields:**
- `job_card_dashboard` (job_card_dashboard)
- `production_item` (Final Product)
- `bom_no` (Final BOM)
- `for_quantity` (Qty To Manufacture)
- `stock_uom` (Stock UOM)
- `posting_date` (Posting Date)
- `finished_good` (Item to Manufacture)
- `semi_fg_bom` (Manufacturing BOM)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **work_order**: *"What is the Work Order?"*
- **company**: *"What is the Company?"*
- **operation**: *"What is the Operation?"*
- **workstation**: *"What is the Workstation?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.