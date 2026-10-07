# Selling - Quotation Domain Skill

## 1. Section Overview & Purpose
Sales proposals and commercial estimates for leads and customers.

**Module:** `Selling`  
**Section Folder:** `ERPNext_Agent/Selling/Quotation`  
**Primary DocTypes:** Quotation

## 2. DocTypes & Field Requirements
### Quotation
**Mandatory Fields:**
- `quotation_to` (Quotation To - Link)
- `transaction_date` (Date - Date)
- `order_type` (Order Type - Select)
- `company` (Company - Link)
- `currency` (Currency - Link)
- `conversion_rate` (Exchange Rate - Float)
- `selling_price_list` (Price List - Link)
- `price_list_currency` (Price List Currency - Link)
- `plc_conversion_rate` (Price List Exchange Rate - Float)
- `items` (Items - Table)
- `status` (Status - Select)

**Key Contextual Fields:**
- `party_name` (Party)
- `customer_name` (Customer Name)
- `valid_till` (Valid Till)
- `has_unit_price_items` (Has Unit Price Items)
- `amended_from` (Amended From)
- `ignore_pricing_rule` (Ignore Pricing Rule)
- `scan_barcode` (Scan Barcode)
- `last_scanned_warehouse` (Last Scanned Warehouse)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **quotation_to**: *"What is the Quotation To?"*
- **transaction_date**: *"What is the Date?"*
- **order_type**: *"What is the Order Type?"*
- **company**: *"What is the Company?"*
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