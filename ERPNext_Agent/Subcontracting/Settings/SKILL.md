# Subcontracting - Settings Domain Skill

## 1. Section Overview & Purpose
Subcontracting parameters and scrap tolerances.

**Module:** `Subcontracting`  
**Section Folder:** `ERPNext_Agent/Subcontracting/Settings`  
**Primary DocTypes:** Subcontracting Settings

## 2. DocTypes & Field Requirements
### Subcontracting Settings
- *No strictly required custom fields or uses standard defaults.*

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- Identify the target DocType and ask the user for its primary identifier and owning Company.

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.