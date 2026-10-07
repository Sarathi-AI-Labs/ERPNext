# ERPNext Settings - Other Settings Domain Skill

## 1. Section Overview & Purpose
Miscellaneous ERPNext configuration parameters.

**Module:** `ERPNext Settings`  
**Section Folder:** `ERPNext_Agent/ERPNext Settings/Other Settings`  
**Primary DocTypes:** Global Defaults

## 2. DocTypes & Field Requirements
### Global Defaults
**Mandatory Fields:**
- `default_currency` (Default Currency - Link)

**Key Contextual Fields:**
- `default_company` (Default Company)
- `country` (Country)
- `default_distance_unit` (Default Distance Unit)
- `hide_currency_symbol` (Hide Currency Symbol)
- `disable_rounded_total` (Disable Rounded Total)
- `disable_in_words` (Disable In Words)
- `use_posting_datetime_for_naming_documents` (Use Posting Datetime for Naming Documents)
- `demo_company` (Demo Company)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **default_currency**: *"What is the Default Currency?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.