# Manufacturing - Tools Domain Skill

## 1. Section Overview & Purpose
BOM rate replacement tools and bulk revision replanning.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Tools`  
**Primary DocTypes:** BOM

## 2. DocTypes & Field Requirements
### BOM
**Mandatory Fields:**
- `company` (Company - Link)
- `item` (Item to Manufacture - Link)
- `quantity` (Quantity (Output Qty) - Float)
- `items` (Components - Table)
- `currency` (Currency - Link)
- `conversion_rate` (Conversion Rate - Float)

**Key Contextual Fields:**
- `custom_sarathi_project` (Sarathi Project)
- `uom` (Unit Of Measure)
- `cost_allocation_per` (% Cost Allocation)
- `cost_allocation` (Cost Allocation)
- `process_loss_percentage` (% Process Loss)
- `process_loss_qty` (Process Loss Qty)
- `with_operations` (With Operations)
- `track_semi_finished_goods` (Track Semi Finished Goods)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **company**: *"What is the Company?"*
- **item**: *"What is the Item to Manufacture?"*
- **quantity**: *"What is the Quantity (Output Qty)?"*
- **items**: *"What is the Components?"*
- **currency**: *"What is the Currency?"*
- **conversion_rate**: *"What is the Conversion Rate?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.