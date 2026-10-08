# Organization - User Domain Skill

## 1. Section Overview & Purpose
System user profiles, credentials, and roles.

**Module:** `Organization`  
**Section Folder:** `ERPNext_Agent/Organization/User`  
**Primary DocTypes:** User

## 2. DocTypes & Field Requirements
### User
**Mandatory Fields:**
- `email` (Email - Data)
- `first_name` (First Name - Data)

**Key Contextual Fields:**
- `enabled` (Enabled)
- `middle_name` (Middle Name)
- `last_name` (Last Name)
- `full_name` (Full Name)
- `username` (Username)
- `language` (Language)
- `time_zone` (Time Zone)
- `send_welcome_email` (Send Welcome Email)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **email**: *"What is the Email?"*
- **first_name**: *"What is the First Name?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.