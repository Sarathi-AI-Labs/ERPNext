# Users and System - System Settings Domain Skill

## 1. Section Overview & Purpose
Platform session controls, timezone, and security configurations.

**Module:** `Users and System`  
**Section Folder:** `ERPNext_Agent/Users and System/System Settings`  
**Primary DocTypes:** System Settings

## 2. DocTypes & Field Requirements
### System Settings
**Mandatory Fields:**
- `language` (Language - Link)
- `time_zone` (Time Zone - Select)
- `date_format` (Date Format - Select)
- `time_format` (Time Format - Select)
- `number_format` (Number Format - Select)

**Key Contextual Fields:**
- `app_name` (Application Name)
- `country` (Country)
- `currency` (Currency)
- `enable_onboarding` (Enable Onboarding)
- `setup_complete` (Setup Complete)
- `disable_document_sharing` (Disable Document Sharing)
- `use_number_format_from_currency` (Use Number Format from Currency)
- `first_day_of_the_week` (First Day of the Week)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **language**: *"What is the Language?"*
- **time_zone**: *"What is the Time Zone?"*
- **date_format**: *"What is the Date Format?"*
- **time_format**: *"What is the Time Format?"*
- **number_format**: *"What is the Number Format?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.