# Organization - Letter Head Domain Skill

## 1. Section Overview & Purpose
Official document letterheads and headers.

**Module:** `Organization`  
**Section Folder:** `ERPNext_Agent/Organization/Letter Head`  
**Primary DocTypes:** Letter Head

## 2. DocTypes & Field Requirements
### Letter Head
**Mandatory Fields:**
- `letter_head_name` (Letter Head Name - Data)

**Key Contextual Fields:**
- `source` (Letter Head Based On)
- `footer_source` (Footer Based On)
- `disabled` (Disabled)
- `is_default` (Default Letter Head)
- `image` (Image)
- `image_height` (Image Height (px))
- `image_width` (Image Width (px))
- `align` (Align)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **letter_head_name**: *"What is the Letter Head Name?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.