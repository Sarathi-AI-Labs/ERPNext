# Quality - Quality Goals and Reviews Domain Skill

## 1. Section Overview & Purpose
ISO quality objectives and management reviews.

**Module:** `Quality`  
**Section Folder:** `ERPNext_Agent/Quality/Quality Goals and Reviews`  
**Primary DocTypes:** Quality Goal

## 2. DocTypes & Field Requirements
### Quality Goal
**Mandatory Fields:**
- `goal` (Goal - Data)

**Key Contextual Fields:**
- `frequency` (Monitoring Frequency)
- `procedure` (Procedure)
- `weekday` (Weekday)
- `date` (Date)
- `objectives` (Objectives)

## 3. Conversational Requirement Discovery (Interactive Chatbot Slot-Filling)
When a user requests to create or configure records in this section (e.g. *'I want to create a new record'*):
1. **Analyze input:** Check if mandatory fields were provided.
2. **If missing details:** The AI Agent MUST ask the user for the required information in a clear, formatted checklist before attempting creation.
3. **Required Questions:**
- **goal**: *"What is the Goal?"*

## 4. Execution & Validation Workflow
1. Pre-validate foreign references (Company, Customer, Supplier, Warehouse).
2. Invoke `create_document` with sanitized parameters.
3. Read-back verify via `ReadBackValidator` to confirm database existence and correct `docstatus`.
4. Record the transaction in `AuditLogger` (`logs/agent_audit.jsonl`).
5. Return a user-friendly confirmation with direct ERPNext document links.