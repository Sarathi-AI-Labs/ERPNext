# Quality - Non Conformance Domain Skill

## 1. Section Overview & Purpose
Corrective and preventive action (CAPA) logs.

**Module:** `Quality`  
**Section Folder:** `ERPNext_Agent/Quality/Non Conformance`  
**Primary DocTypes:** Quality Action

## 2. DocTypes & Field Requirements
### Quality Action
**Mandatory Fields:**
- `corrective_preventive` (Corrective/Preventive - Select)

**Key Contextual Fields:**
- `review` (Review)
- `feedback` (Feedback)
- `status` (Status)
- `date` (Date)
- `goal` (Goal)
- `procedure` (Procedure)
- `resolutions` (Resolutions)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **corrective_preventive**: *"What is the Corrective/Preventive?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.