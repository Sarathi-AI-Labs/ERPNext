# Projects - Timesheet Domain Skill

## 1. Section Overview & Purpose
Employee labor hour logging and billable project charges.

**Module:** `Projects`  
**Section Folder:** `ERPNext_Agent/Projects/Timesheet`  
**Primary DocTypes:** Timesheet

## 2. DocTypes & Field Requirements
### Timesheet
**Mandatory Fields:**
- `time_logs` (Time Sheets - Table)

**Key Contextual Fields:**
- `title` (Title)
- `company` (Company)
- `customer` (Customer)
- `currency` (Currency)
- `exchange_rate` (Exchange Rate)
- `sales_invoice` (Sales Invoice)
- `status` (Status)
- `parent_project` (Project)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **time_logs**: *"What is the Time Sheets?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.