# Framework - Customization Domain Skill

## 1. Section Overview & Purpose
DocType schema extensions and field overrides.

**Module:** `Framework`  
**Section Folder:** `ERPNext_Agent/Framework/Customization`  
**Primary DocTypes:** Custom Field, Property Setter

## 2. DocTypes & Field Requirements
### Custom Field
**Mandatory Fields:**
- `dt` (DocType - Link)
- `fieldtype` (Field Type - Select)

**Key Contextual Fields:**
- `is_system_generated` (Is System Generated)
- `module` (Module (for export))
- `label` (Label)
- `placeholder` (Placeholder)
- `label_help` (Label Help)
- `fieldname` (Fieldname)
- `insert_after` (Insert After)
- `length` (Length)

### Property Setter
**Mandatory Fields:**
- `doctype_or_field` (Applied On - Select)
- `doc_type` (DocType - Link)
- `property` (Property - Data)

**Key Contextual Fields:**
- `is_system_generated` (Is System Generated)
- `help` (Help)
- `field_name` (Field Name)
- `row_name` (Row Name)
- `module` (Module (for export))
- `property_type` (Property Type)
- `value` (Set Value)
- `default_value` (Default Value)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **dt**: *"What is the DocType?"*
- **fieldtype**: *"What is the Field Type?"*
- **doctype_or_field**: *"What is the Applied On?"*
- **doc_type**: *"What is the DocType?"*
- **property**: *"What is the Property?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.