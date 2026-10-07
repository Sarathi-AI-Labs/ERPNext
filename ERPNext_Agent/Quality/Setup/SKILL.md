# Quality - Setup Domain Skill

## 1. Section Overview & Purpose
Inspection parameters, tolerances, and checklists.

**Module:** `Quality`  
**Section Folder:** `ERPNext_Agent/Quality/Setup`  
**Primary DocTypes:** Quality Inspection Parameter, Quality Inspection Template

## 2. DocTypes & Field Requirements
### Quality Inspection Parameter
- *No strictly required custom fields or uses standard defaults.*

### Quality Inspection Template
**Mandatory Fields:**
- `quality_inspection_template_name` (Quality Inspection Template Name - Data)
- `item_quality_inspection_parameter` (Item Quality Inspection Parameter - Table)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **quality_inspection_template_name**: *"What is the Quality Inspection Template Name?"*
- **item_quality_inspection_parameter**: *"What is the Item Quality Inspection Parameter?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.