# Stock - Setup Domain Skill

## 1. Section Overview & Purpose
Item masters, units of measure, and warehouse hierarchy.

**Module:** `Stock`  
**Section Folder:** `ERPNext_Agent/Stock/Setup`  
**Primary DocTypes:** Item, Item Group, Warehouse

## 2. DocTypes & Field Requirements
### Item
**Mandatory Fields:**
- `item_code` (Item Code - Data)
- `item_group` (Item Group - Link)
- `stock_uom` (Default Unit of Measure - Link)

**Key Contextual Fields:**
- `item_name` (Item Name)
- `image` (Image)
- `disabled` (Disabled)
- `is_stock_item` (Maintain Stock)
- `is_fixed_asset` (Is Fixed Asset)
- `auto_create_assets` (Auto create assets on purchase)
- `is_grouped_asset` (Create Grouped Asset)
- `asset_category` (Asset Category)

### Item Group
- *No strictly required custom fields or uses standard defaults.*

### Warehouse
**Mandatory Fields:**
- `warehouse_name` (Warehouse Name - Data)
- `company` (Company - Link)

**Key Contextual Fields:**
- `disabled` (Disabled)
- `is_rejected_warehouse` (Is Rejected Warehouse)
- `account` (Account)
- `parent_warehouse` (Parent Warehouse)
- `is_group` (Is Group Warehouse)
- `customer` (Customer)
- `address_html` (Address HTML)
- `contact_html` (Contact HTML)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **item_code**: *"What is the Item Code?"*
- **item_group**: *"What is the Item Group?"*
- **stock_uom**: *"What is the Default Unit of Measure?"*
- **warehouse_name**: *"What is the Warehouse Name?"*
- **company**: *"What is the Company?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.