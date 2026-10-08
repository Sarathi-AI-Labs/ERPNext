# Accounting - Budget Domain Skill

## 1. Section Overview & Purpose
Cost center and project budget variance tracking and monthly expense limits.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Budget`  
**Primary DocTypes:** Cost Center, Account

## 2. DocTypes & Field Requirements
### Cost Center
**Mandatory Fields:**
- `cost_center_name` (Cost Center Name - Data)
- `parent_cost_center` (Parent Cost Center - Link)
- `company` (Company - Link)

**Key Contextual Fields:**
- `cost_center_number` (Cost Center Number)
- `is_group` (Is Group)
- `disabled` (Disabled)
- `lft` (lft)
- `rgt` (rgt)
- `old_parent` (old_parent)

### Account
**Mandatory Fields:**
- `account_name` (Account Name - Data)
- `company` (Company - Link)
- `parent_account` (Parent Account - Link)

**Key Contextual Fields:**
- `disabled` (Disable)
- `account_number` (Account Number)
- `is_group` (Is Group)
- `root_type` (Root Type)
- `report_type` (Report Type)
- `account_currency` (Currency)
- `account_category` (Account Category)
- `account_type` (Account Type)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **cost_center_name**: *"What is the Cost Center Name?"*
- **parent_cost_center**: *"What is the Parent Cost Center?"*
- **company**: *"What is the Company?"*
- **account_name**: *"What is the Account Name?"*
- **parent_account**: *"What is the Parent Account?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.