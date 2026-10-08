# Assets - Asset Movement Domain Skill

## 1. Section Overview & Purpose
Transfer of capital equipment between employees, workstations, or locations.

**Module:** `Assets`  
**Section Folder:** `ERPNext_Agent/Assets/Asset Movement`  
**Primary DocTypes:** Asset Movement, Asset

## 2. DocTypes & Field Requirements
### Asset Movement
**Mandatory Fields:**
- `company` (Company - Link)
- `purpose` (Purpose - Select)
- `transaction_date` (Transaction Date - Datetime)
- `assets` (Assets - Table)

**Key Contextual Fields:**
- `reference_doctype` (Reference Document Type)
- `reference_name` (Reference Document Name)
- `amended_from` (Amended From)

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
- **company**: *"What is the Company?"*
- **purpose**: *"What is the Purpose?"*
- **transaction_date**: *"What is the Transaction Date?"*
- **assets**: *"What is the Assets?"*
- **item_code**: *"What is the Item Code?"*
- **asset_name**: *"What is the Asset Name?"*
- **location**: *"What is the Location?"*
- **purchase_date**: *"What is the Purchase Date?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.