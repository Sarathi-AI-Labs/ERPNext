# Accounting - Share Management Domain Skill

## 1. Section Overview & Purpose
Equity allocation, shareholder register, and share transfers.

**Module:** `Accounting`  
**Section Folder:** `ERPNext_Agent/Accounting/Share Management`  
**Primary DocTypes:** Company

## 2. DocTypes & Field Requirements
### Company
**Mandatory Fields:**
- `company_name` (Company - Data)
- `abbr` (Abbr - Data)
- `default_currency` (Default Currency - Link)
- `country` (Country - Link)
- `valuation_method` (Default Stock Valuation Method - Select)

**Key Contextual Fields:**
- `is_group` (Is Group)
- `default_holiday_list` (Default Holiday List)
- `default_letter_head` (Default Letter Head)
- `tax_id` (Tax ID)
- `domain` (Domain)
- `date_of_establishment` (Date of Establishment)
- `parent_company` (Parent Company)
- `reporting_currency` (Reporting Currency)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company_name**: *"What is the Company?"*
- **abbr**: *"What is the Abbr?"*
- **default_currency**: *"What is the Default Currency?"*
- **country**: *"What is the Country?"*
- **valuation_method**: *"What is the Default Stock Valuation Method?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.