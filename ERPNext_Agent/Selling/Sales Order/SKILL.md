# Selling - Sales Order Domain Skill

## 1. Section Overview & Purpose
Confirmed customer orders and demand commitments.

**Module:** `Selling`  
**Section Folder:** `ERPNext_Agent/Selling/Sales Order`  
**Primary DocTypes:** Sales Order

## 2. DocTypes & Field Requirements
### Sales Order
**Mandatory Fields:**
- `company` (Company - Link)
- `customer` (Customer - Link)
- `order_type` (Order Type - Select)
- `transaction_date` (Date - Date)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `selling_price_list` (Price List - Link)
- `price_list_currency` (Price List Currency - Link)
- `plc_conversion_rate` (Price List Exchange Rate - Float)
- `items` (Items - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `customer_name` (Customer Name)
- `transaction_time` (Time)
- `delivery_date` (Delivery Date)
- `tax_id` (Tax Id)
- `skip_delivery_note` (Skip Delivery Note)
- `has_unit_price_items` (Has Unit Price Items)
- `is_subcontracted` (Is Subcontracted)
- `amended_from` (Amended From)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **customer**: *"What is the Customer?"*
- **order_type**: *"What is the Order Type?"*
- **transaction_date**: *"What is the Date?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Exchange Rate?"*
- **selling_price_list**: *"What is the Price List?"*
- **price_list_currency**: *"What is the Price List Currency?"*
- **plc_conversion_rate**: *"What is the Price List Exchange Rate?"*
- **items**: *"What is the Items?"*
- **status**: *"What is the Status?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.