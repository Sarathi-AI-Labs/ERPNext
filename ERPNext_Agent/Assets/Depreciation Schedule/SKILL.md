# Assets - Depreciation Schedule Domain Skill

## 1. Section Overview & Purpose
Straight line and written down value depreciation schedules and automated monthly posting.

**Module:** `Assets`  
**Section Folder:** `ERPNext_Agent/Assets/Depreciation Schedule`  
**Primary DocTypes:** Asset Depreciation Schedule, Asset

## 2. DocTypes & Field Requirements
### Asset Depreciation Schedule
**Mandatory Fields:**
- `asset` (Asset - Link)

**Key Contextual Fields:**
- `company` (Company)
- `net_purchase_amount` (Net Purchase Amount)
- `opening_accumulated_depreciation` (Opening Accumulated Depreciation)
- `opening_number_of_booked_depreciations` (Opening Number of Booked Depreciations)
- `finance_book` (Finance Book)
- `finance_book_id` (Finance Book Id)
- `depreciation_method` (Depreciation Method)
- `total_number_of_depreciations` (Total Number of Depreciations)

### Asset
**Mandatory Fields:**
- `item_code` (Item Code - Link)
- `asset_name` (Asset Name - Data)
- `location` (Location - Link)
- `company` (Company - Link)
- `purchase_date` (Purchase Date - Date)

**Key Contextual Fields:**
- `item_name` (Item Name)
- `image` (Image)
- `asset_category` (Asset Category)
- `asset_type` (Asset Type)
- `maintenance_required` (Maintenance Required)
- `calculate_depreciation` (Calculate Depreciation)
- `purchase_receipt` (Purchase Receipt)
- `purchase_receipt_item` (Purchase Receipt Item)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **asset**: *"What is the Asset?"*
- **item_code**: *"What is the Item Code?"*
- **asset_name**: *"What is the Asset Name?"*
- **location**: *"What is the Location?"*
- **company**: *"What is the Company?"*
- **purchase_date**: *"What is the Purchase Date?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.