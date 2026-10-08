# Users and System - Roles Domain Skill

## 1. Section Overview & Purpose
System roles and module permission matrices.

**Module:** `Users and System`  
**Section Folder:** `ERPNext_Agent/Users and System/Roles`  
**Primary DocTypes:** Role

## 2. DocTypes & Field Requirements
### Role
**Mandatory Fields:**
- `role_name` (Role Name - Data)

**Key Contextual Fields:**
- `home_page` (Home Page)
- `restrict_to_domain` (Restrict To Domain)
- `disabled` (Disabled)
- `is_custom` (Is Custom)
- `desk_access` (Desk Access)
- `two_factor_auth` (Two Factor Authentication)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **role_name**: *"What is the Role Name?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.