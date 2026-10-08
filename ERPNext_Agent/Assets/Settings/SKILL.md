# Assets - Settings Domain Skill

## 1. Section Overview & Purpose
Asset numbering series, automated depreciation posting toggles, and default ledgers.

**Module:** `Assets`  
**Section Folder:** `ERPNext_Agent/Assets/Settings`  
**Primary DocTypes:** Asset Category

## 2. DocTypes & Field Requirements
### Asset Category
**Mandatory Fields:**
- `asset_category_name` (Asset Category Name - Data)
- `accounts` (Accounts - Table)

**Key Contextual Fields:**
- `enable_cwip_accounting` (Enable Capital Work in Progress Accounting)
- `non_depreciable_category` (Non Depreciable Category)
- `finance_books` (Finance Books)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **asset_category_name**: *"What is the Asset Category Name?"*
- **accounts**: *"What is the Accounts?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.