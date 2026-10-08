# AGENT CONVERSATIONAL FLOW SPECIFICATION

## 1. Multi-Turn Finite State Machine (FSM)

The Sarathi AI Agent implements a deterministic Finite State Machine to manage multi-turn dialogues safely:

```
  ┌─────────┐
  │  IDLE   │ ◄──────────────────────────────┐
  └────┬────┘                                │
       │ User sends request                  │ (User cancels / reset)
       ▼                                     │
  ┌─────────────────────────┐                │
  │ INTENT & DOCTYPE MATCH  │                │
  └────┬────────────────────┘                │
       │                                     │
       ├───────── Missing mandatory fields?  │
       │                                     │
       ▼                                     │
  ┌─────────────────────────┐                │
  │    COLLECTING_SLOTS     │                │
  │ (Interactive Intake)    │ ───────────────┤
  └────┬────────────────────┘                │
       │ User provides answers               │
       ▼                                     │
  ┌─────────────────────────┐                │
  │ PERMISSION & DUP CHECK  │                │
  └────┬────────────────────┘                │
       │ Pre-checks pass                     │
       ▼                                     │
  ┌─────────────────────────┐                │
  │  AWAITING_CONFIRMATION  │                │
  │ (Checklist & Card)      │ ───────────────┘
  └────┬────────────────────┘
       │ User confirms ("Confirm" / Button)
       ▼
  ┌─────────────────────────┐
  │   TOOL MUTATION EXEC    │
  └────┬────────────────────┘
       │ Record created
       ▼
  ┌─────────────────────────┐
  │  READ-BACK VERIFICATION │
  └────┬────────────────────┘
       │ Verified in Database
       ▼
  ┌─────────────────────────┐
  │ AUDIT LOGGING & RESPONSE│ ──► [Back to IDLE]
  └─────────────────────────┘
```

---

## 2. End-to-End Walkthrough: Company Creation Slice

### Turn 1: Initial Intent Detection & Missing Slot Discovery
- **User Input**:
  ```
  "I want to create a new company."
  ```
- **Agent Analysis**:
  1. `SkillRouter.route()` matches action `CREATE`, primary module `Organization`, DocType `Company`.
  2. `SkillLoader.load_skill("Organization")` loads domain rules.
  3. `SkillLoader.get_section_for_doctype("Organization", "Company")` loads `section_info.json`.
  4. Checks mandatory fields for `Company`: `company_name` and `abbr`. Neither was supplied.
  5. Transitions session state to `COLLECTING_SLOTS`.
- **Agent Response**:
  ```markdown
  Sure. I can create a Company in ERPNext.

  **Module:**
  Organization

  **DocType:**
  Company

  I need:
  - Company Name
  - Company Abbreviation

  Please provide the company name, company abbreviation.
  ```

---

### Turn 2: Providing Company Name
- **User Input**:
  ```
  "Gaurav Manufacturing."
  ```
- **Agent Analysis**:
  1. Detects active state `COLLECTING_SLOTS`.
  2. Extracts first missing field: `company_name = "Gaurav Manufacturing"`.
  3. Re-evaluates remaining missing slots: `abbr` (Company Abbreviation) is still missing.
- **Agent Response**:
  ```markdown
  I still need the following information to create the **Company**:

  - **Company Abbreviation** (Unique 2-5 letter code (e.g. 'GM'))

  Please provide the missing detail(s).
  ```

---

### Turn 3: Providing Abbreviation & Safety Gate
- **User Input**:
  ```
  "GM."
  ```
- **Agent Analysis**:
  1. Sanitizes input: `abbr = "GM"`.
  2. Applies standard defaults: `country = "India"`, `default_currency = "INR"`.
  3. All mandatory fields present: `{"company_name": "Gaurav Manufacturing", "abbr": "GM", "country": "India", "default_currency": "INR"}`.
  4. **Pre-mutation duplicate check**: Queries `frappe.db.exists("Company", "Gaurav Manufacturing")` and `frappe.db.exists("Company", {"abbr": "GM"})`. Both return `False` (unique).
  5. **Permission check**: Invokes `CheckPermissionTool.execute("Company", "create")`. Returns `has_permission = True`.
  6. Transitions session state to `AWAITING_CONFIRMATION`.
- **Agent Response (with interactive Confirmation Card)**:
  ```markdown
  I understood:

  Company:
  **Gaurav Manufacturing**

  Abbreviation:
  **GM**

  **Action:**
  Create Company

  I am validating the request before execution.

  ✓ Organization Skill loaded
  ✓ Company DocType identified
  ✓ Required fields available
  ✓ Permission checked
  ✓ Duplicate check completed

  Ready to create the Company.
  ```
  *(Chatbox displays [✓ Confirm & Create] and [✕ Cancel] action buttons).*

---

### Turn 4: Confirmation, Execution, Read-Back & Audit
- **User Input**:
  ```
  "Yes, create it." (or user clicks [✓ Confirm & Create])
  ```
- **Agent Execution**:
  1. Recognizes confirmation intent.
  2. Executes `CreateDocumentTool.execute("Company", pending_values)`. Frappe creates company, generates standard Chart of Accounts, Cost Centers, and Warehouses.
  3. Executes `ReadBackValidator.verify_document_created("Company", "Gaurav Manufacturing", pending_values)`. Verifies record exists and field values match.
  4. Appends audit record to `ERPNext_Agent/logs/agent_audit.jsonl`.
  5. Resets session to `IDLE`.
- **Agent Final Response**:
  ```markdown
  Creating Company...

  ✓ ERPNext operation executed
  ✓ Company created
  ✓ Record read back successfully
  ✓ Result verified

  Company **"Gaurav Manufacturing"** was created successfully and verified in ERPNext.

  [🚀 Open Company in Desk](/app/company/Gaurav Manufacturing)
  ```
  *(Dashboard UI catches `status === "COMPLETED"`, triggers top glowing banner, highlights section, and auto-refreshes data).*
