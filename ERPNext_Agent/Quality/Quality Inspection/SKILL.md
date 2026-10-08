# Quality - Quality Inspection Domain Skill

## 1. Section Overview & Purpose
Measurement testing and acceptance/rejection verdicts.

**Module:** `Quality`  
**Section Folder:** `ERPNext_Agent/Quality/Quality Inspection`  
**Primary DocTypes:** Quality Inspection

## 2. DocTypes & Field Requirements
### Quality Inspection
**Mandatory Fields:**
- `report_date` (Report Date - Date)
- `status` (Status - Select)
- `inspection_type` (Inspection Type - Select)
- `reference_type` (Reference Type - Select)
- `reference_name` (Reference Name - Dynamic Link)
- `item_code` (Item Code - Link)
- `sample_size` (Sample Size - Float)
- `inspected_by` (Inspected By - Link)

**Key Contextual Fields:**
- `company` (Company)
- `child_row_reference` (Child Row Reference)
- `item_serial_no` (Item Serial No)
- `batch_no` (Batch No)
- `item_name` (Item Name)
- `description` (Description)
- `bom_no` (BOM No)
- `quality_inspection_template` (Quality Inspection Template)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **report_date**: *"What is the Report Date?"*
- **status**: *"What is the Status?"*
- **inspection_type**: *"What is the Inspection Type?"*
- **reference_type**: *"What is the Reference Type?"*
- **reference_name**: *"What is the Reference Name?"*
- **item_code**: *"What is the Item Code?"*
- **sample_size**: *"What is the Sample Size?"*
- **inspected_by**: *"What is the Inspected By?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.