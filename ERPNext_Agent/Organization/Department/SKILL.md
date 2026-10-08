# Organization - Department Domain Skill

## 1. Section Overview & Purpose
Internal operational divisions and reporting lines.

**Module:** `Organization`  
**Section Folder:** `ERPNext_Agent/Organization/Department`  
**Primary DocTypes:** Department

## 2. DocTypes & Field Requirements
### Department
**Mandatory Fields:**
- `department_name` (Department - Data)
- `company` (Company - Link)

**Key Contextual Fields:**
- `parent_department` (Parent Department)
- `is_group` (Is Group)
- `disabled` (Disabled)
- `lft` (lft)
- `rgt` (rgt)
- `old_parent` (Old Parent)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **department_name**: *"What is the Department?"*
- **company**: *"What is the Company?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.