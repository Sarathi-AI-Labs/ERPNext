# Projects - Reports Domain Skill

## 1. Section Overview & Purpose
Project costing, budget variance, and Gantt tracking.

**Module:** `Projects`  
**Section Folder:** `ERPNext_Agent/Projects/Reports`  
**Primary DocTypes:** Project

## 2. DocTypes & Field Requirements
### Project
**Mandatory Fields:**
- `project_name` (Project Name - Data)
- `company` (Company - Link)

**Key Contextual Fields:**
- `status` (Status)
- `project_type` (Project Type)
- `custom_sarathi_manufacturing` (Sarathi Manufacturing Project)
- `percent_complete_method` (% Complete Method)
- `project_template` (From Template)
- `priority` (Priority)
- `department` (Department)
- `is_active` (Is Active)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **project_name**: *"What is the Project Name?"*
- **company**: *"What is the Company?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.