# Manufacturing - Setup Domain Skill

## 1. Section Overview & Purpose
Manufacturing operations, machinery workstations, and routing stages.

**Module:** `Manufacturing`  
**Section Folder:** `ERPNext_Agent/Manufacturing/Setup`  
**Primary DocTypes:** Operation, Workstation, Workstation Type, Routing

## 2. DocTypes & Field Requirements
### Operation
- *No strictly required custom fields or uses standard defaults.*

**Key Contextual Fields:**
- `workstation` (Default Workstation)
- `is_corrective_operation` (Is Corrective Operation)
- `create_job_card_based_on_batch_size` (Create Job Card based on Batch Size)
- `quality_inspection_template` (Quality Inspection Template)
- `batch_size` (Batch Size)
- `sub_operations` (sub_operations)
- `total_operation_time` (Total Operation Time)
- `description` (Description)

### Workstation
**Mandatory Fields:**
- `workstation_name` (Workstation Name - Data)
- `production_capacity` (Job Capacity - Int)

**Key Contextual Fields:**
- `workstation_dashboard` (Workstation Dashboard)
- `workstation_type` (Workstation Type)
- `plant_floor` (Plant Floor)
- `disabled` (Disabled)
- `warehouse` (Warehouse)
- `status` (Status)
- `on_status_image` (Active Status)
- `off_status_image` (Inactive Status)

### Workstation Type
**Mandatory Fields:**
- `workstation_type` (Workstation Type - Data)

**Key Contextual Fields:**
- `workstation_costs` (Operating Components Cost)
- `hour_rate` (Net Hour Rate)
- `description` (Description)

### Routing
- *No strictly required custom fields or uses standard defaults.*

**Key Contextual Fields:**
- `routing_name` (Routing Name)
- `disabled` (Disabled)
- `operations` (BOM Operation)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **workstation_name**: *"What is the Workstation Name?"*
- **production_capacity**: *"What is the Job Capacity?"*
- **workstation_type**: *"What is the Workstation Type?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.