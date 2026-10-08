# Buying - Setup Domain Skill

## 1. Section Overview & Purpose
Vendor registry, payment terms, and vendor categorization.

**Module:** `Buying`  
**Section Folder:** `ERPNext_Agent/Buying/Setup`  
**Primary DocTypes:** Supplier, Supplier Group

## 2. DocTypes & Field Requirements
### Supplier
**Mandatory Fields:**
- `supplier_name` (Supplier Name - Data)
- `supplier_type` (Supplier Type - Select)

**Key Contextual Fields:**
- `alias` (Alias)
- `gender` (Gender)
- `supplier_group` (Supplier Group)
- `country` (Country)
- `image` (Image)
- `default_currency` (Billing Currency)
- `default_bank_account` (Company Bank Account)
- `default_price_list` (Price List)

### Supplier Group
**Mandatory Fields:**
- `supplier_group_name` (Supplier Group Name - Data)

**Key Contextual Fields:**
- `parent_supplier_group` (Parent Supplier Group)
- `is_group` (Is Group)
- `payment_terms` (Default Payment Terms Template)
- `accounts` (Accounts)
- `lft` (lft)
- `rgt` (rgt)
- `old_parent` (Old Parent)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **supplier_name**: *"What is the Supplier Name?"*
- **supplier_type**: *"What is the Supplier Type?"*
- **supplier_group_name**: *"What is the Supplier Group Name?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.