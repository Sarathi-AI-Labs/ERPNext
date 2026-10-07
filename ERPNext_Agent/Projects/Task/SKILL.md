# Projects - Task Domain Skill

## 1. Section Overview & Purpose
Discrete project work breakdown items, milestones, and dependencies.

**Module:** `Projects`  
**Section Folder:** `ERPNext_Agent/Projects/Task`  
**Primary DocTypes:** Task

## 2. DocTypes & Field Requirements
### Task
**Mandatory Fields:**
- `subject` (Subject - Data)

**Key Contextual Fields:**
- `project` (Project)
- `issue` (Issue)
- `type` (Type)
- `color` (Color)
- `is_group` (Is Group)
- `status` (Status)
- `priority` (Priority)
- `task_weight` (Weight)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **subject**: *"What is the Subject?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.