# Accounting - Accounts Setup Domain Skill

## 1. Section Overview & Purpose
Chart of Accounts management, cost center budget trees, and fiscal year configurations.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Accounts Setup`  
**Primary DocTypes:** Account, Cost Center, Fiscal Year

## 2. DocTypes & Field Requirements
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

### Fiscal Year
**Mandatory Fields:**
- `year` (Year Name - Data)
- `year_start_date` (Year Start Date - Date)
- `year_end_date` (Year End Date - Date)

**Key Contextual Fields:**
- `disabled` (Disabled)
- `is_short_year` (Is Short/Long Year)
- `companies` (Companies)
- `auto_created` (Auto Created)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **account_name**: *"What is the Account Name?"*
- **company**: *"What is the Company?"*
- **parent_account**: *"What is the Parent Account?"*
- **cost_center_name**: *"What is the Cost Center Name?"*
- **parent_cost_center**: *"What is the Parent Cost Center?"*
- **year**: *"What is the Year Name?"*
- **year_start_date**: *"What is the Year Start Date?"*
- **year_end_date**: *"What is the Year End Date?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.