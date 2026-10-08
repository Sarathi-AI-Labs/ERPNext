# Projects - Setup Domain Skill

## 1. Section Overview & Purpose
Project types and labor activity categorizations.

**Module:** `Projects`  
**Section Folder:** `ERPNext_Agent/Projects/Setup`  
**Primary DocTypes:** Project Type, Activity Type

## 2. DocTypes & Field Requirements
### Project Type
**Mandatory Fields:**
- `project_type` (Project Type - Data)

**Key Contextual Fields:**
- `description` (Description)

### Activity Type
**Mandatory Fields:**
- `activity_type` (Activity Type - Data)

**Key Contextual Fields:**
- `costing_rate` (Default Costing Rate)
- `billing_rate` (Default Billing Rate)
- `disabled` (Disabled)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **project_type**: *"What is the Project Type?"*
- **activity_type**: *"What is the Activity Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.