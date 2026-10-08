# Stock - Delivery Note Domain Skill

## 1. Section Overview & Purpose
Outbound shipment and customer delivery fulfillment.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Delivery Note`  
**Primary DocTypes:** Delivery Note

## 2. DocTypes & Field Requirements
### Delivery Note
**Mandatory Fields:**
- `customer` (Customer - Link)
- `posting_date` (Date - Date)
- `posting_time` (Posting Time - Time)
- `company` (Company - Link)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `selling_price_list` (Price List - Link)
- `price_list_currency` (Price List Currency - Link)
- `plc_conversion_rate` (Price List Exchange Rate - Float)
- `items` (Delivery Note Item - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `tax_id` (Tax Id)
- `customer_name` (Customer Name)
- `set_posting_time` (Edit Posting Date and Time)
- `amended_from` (Amended From)
- `is_return` (Is Return)
- `issue_credit_note` (Issue Credit Note)
- `return_against` (Return Against Delivery Note)
- `cost_center` (Cost Center)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **customer**: *"What is the Customer?"*
- **posting_date**: *"What is the Date?"*
- **posting_time**: *"What is the Posting Time?"*
- **company**: *"What is the Company?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Exchange Rate?"*
- **selling_price_list**: *"What is the Price List?"*
- **price_list_currency**: *"What is the Price List Currency?"*
- **plc_conversion_rate**: *"What is the Price List Exchange Rate?"*
- **items**: *"What is the Delivery Note Item?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.