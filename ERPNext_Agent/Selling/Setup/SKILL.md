# Selling - Setup Domain Skill

## 1. Section Overview & Purpose
Customer master records, territories, and sales partners.

**Module:** `Selling`  
**Section Folder:** `ERPNext_Agent/Selling/Setup`  
**Primary DocTypes:** Customer, Customer Group

## 2. DocTypes & Field Requirements
### Customer
**Mandatory Fields:**
- `customer_name` (Customer Name - Data)
- `customer_type` (Customer Type - Select)

**Key Contextual Fields:**
- `alias` (Alias)
- `gender` (Gender)
- `customer_group` (Customer Group)
- `territory` (Territory)
- `image` (Image)
- `default_currency` (Billing Currency)
- `default_bank_account` (Company Bank Account)
- `default_price_list` (Price List)

### Customer Group
**Mandatory Fields:**
- `customer_group_name` (Customer Group Name - Data)

**Key Contextual Fields:**
- `parent_customer_group` (Parent Customer Group)
- `is_group` (Is Group)
- `default_price_list` (Default Price List)
- `payment_terms` (Default Payment Terms Template)
- `lft` (lft)
- `rgt` (rgt)
- `old_parent` (old_parent)
- `accounts` (Accounts)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **customer_name**: *"What is the Customer Name?"*
- **customer_type**: *"What is the Customer Type?"*
- **customer_group_name**: *"What is the Customer Group Name?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.