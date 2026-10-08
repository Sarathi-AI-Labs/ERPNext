# Framework - DocType Domain Skill

## 1. Section Overview & Purpose
Frappe core meta-schema builder and controller definitions.

**Module:** `Framework`  
**Section Folder:** `ERPNext_Agent/Framework/DocType`  
**Primary DocTypes:** DocType

## 2. DocTypes & Field Requirements
### DocType
**Mandatory Fields:**
- `module` (Module - Link)

**Key Contextual Fields:**
- `form_builder` (Form Builder)
- `permissions` (Permissions)
- `restrict_to_domain` (Restrict To Domain)
- `read_only` (User Cannot Search)
- `in_create` (User Cannot Create)
- `protect_attached_files` (Protect Attached Files)
- `naming_rule` (Naming Rule)
- `autoname` (Auto Name)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **module**: *"What is the Module?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.