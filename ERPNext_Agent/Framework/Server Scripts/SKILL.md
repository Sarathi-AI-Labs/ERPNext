# Framework - Server Scripts Domain Skill

## 1. Section Overview & Purpose
Sandboxed Python hooks on document save/submit.

**Module:** `Framework`  
**Section Folder:** `ERPNext_Agent/Framework/Server Scripts`  
**Primary DocTypes:** Server Script

## 2. DocTypes & Field Requirements
### Server Script
**Mandatory Fields:**
- `script_type` (Script Type - Select)
- `script` (Script - Code)

**Key Contextual Fields:**
- `reference_doctype` (Reference Document Type)
- `event_frequency` (Event Frequency)
- `cron_format` (Cron Format)
- `doctype_event` (DocType Event)
- `api_method` (API Method)
- `allow_guest` (Allow Guest)
- `module` (Module (for export))
- `disabled` (Disabled)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **script_type**: *"What is the Script Type?"*
- **script**: *"What is the Script?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.