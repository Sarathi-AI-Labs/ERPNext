# Users and System - Audits Domain Skill

## 1. Section Overview & Purpose
System access logs, document modification trails, and security audits.

**Module:** `Users and System`  
**Section Folder:** `ERPNext_Agent/Users and System/Audits`  
**Primary DocTypes:** Activity Log

## 2. DocTypes & Field Requirements
### Activity Log
**Mandatory Fields:**
- `subject` (Subject - Small Text)

**Key Contextual Fields:**
- `content` (Message)
- `communication_date` (Date)
- `ip_address` (IP Address)
- `operation` (Operation)
- `status` (Status)
- `reference_doctype` (Reference Document Type)
- `reference_name` (Reference Name)
- `reference_owner` (Reference Owner)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **subject**: *"What is the Subject?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.