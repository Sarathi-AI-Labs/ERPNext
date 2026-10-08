# Accounting - Taxes Domain Skill

## 1. Section Overview & Purpose
Tax categories, GST rate templates, withholding tax, and tax calculation rules.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Taxes`  
**Primary DocTypes:** Tax Category, Sales Taxes and Charges Template, Purchase Taxes and Charges Template

## 2. DocTypes & Field Requirements
### Tax Category
- *No strictly required custom fields or uses standard defaults.*

### Sales Taxes and Charges Template
**Mandatory Fields:**
- `title` (Title - Data)
- `company` (Company - Link)

**Key Contextual Fields:**
- `is_default` (Default)
- `disabled` (Disabled)
- `tax_category` (Tax Category)
- `taxes` (Sales Taxes and Charges)

### Purchase Taxes and Charges Template
**Mandatory Fields:**
- `title` (Title - Data)
- `company` (Company - Link)

**Key Contextual Fields:**
- `is_default` (Default)
- `disabled` (Disabled)
- `tax_category` (Tax Category)
- `taxes` (Purchase Taxes and Charges)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **title**: *"What is the Title?"*
- **company**: *"What is the Company?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.