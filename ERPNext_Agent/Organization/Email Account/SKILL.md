# Organization - Email Account Domain Skill

## 1. Section Overview & Purpose
SMTP/IMAP company mailboxes.

**Module:** `Organization`  
**Section Folder:** `ERPNext_Agent/Organization/Email Account`  
**Primary DocTypes:** Email Account

## 2. DocTypes & Field Requirements
### Email Account
**Mandatory Fields:**
- `email_id` (Email Address - Data)

**Key Contextual Fields:**
- `company` (Company)
- `email_account_name` (Email Account Name)
- `enable_incoming` (Enable Incoming)
- `enable_outgoing` (Enable Outgoing)
- `service` (Service)
- `domain` (Domain)
- `frappe_mail_site` (Frappe Mail Site)
- `auth_method` (Method)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **email_id**: *"What is the Email Address?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.