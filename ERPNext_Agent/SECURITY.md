# SECURITY & COMPLIANCE SPECIFICATION

## 1. Authentication & User Identity Context

1. **Session Context Integrity**:
   - The Agent operates strictly within the authenticated Frappe session context (`frappe.session.user`).
   - The agent NEVER creates or uses a hardcoded bypass superuser.
   - Operations triggered from the chat API inherit the exact role and permission limits of the currently logged-in user.

---

## 2. Permission Checking (`CheckPermissionTool`)

Before any mutation plan is presented to the user or executed:
- The agent invokes `frappe.has_permission(doctype, ptype)`:
  - `create`: For insertions.
  - `write`: For updates.
  - `submit`: For submittable workflow transitions.
  - `cancel`: For cancellations.
  - `delete`: For deletions.
- If permission is denied:
  - The transaction is blocked immediately.
  - A friendly error is returned explaining that the user's role does not possess the required permissions.

---

## 3. Pre-Mutation Duplicate & Integrity Validation

To protect against raw database crashes and unhandled SQL Integrity Errors (such as MariaDB error 1062 for duplicate keys):
- The agent performs pre-insertion existence checks using `frappe.db.exists`:
  - `Company`: Verifies `company_name` and `abbr` uniqueness.
  - `Project`: Verifies `project_name` uniqueness.
  - `Item`: Verifies `item_code` uniqueness.
  - `Customer` / `Supplier`: Verifies party name uniqueness.
- When duplicates are detected, the agent explains the conflict and prompts the user to provide an alternative name or identifier.

---

## 4. Human-in-the-Loop Confirmation Gate

For all operations that create, modify, submit, cancel, or delete records:
- The agent NEVER commits changes directly on the first user message without explicit verification.
- A confirmation card is rendered summarizing the target DocType, extracted parameters, and validation checklist.
- The user must explicitly confirm (via "Confirm", "Yes", or clicking the `[Confirm & Create]` button).
- The user can cancel at any time, returning the agent to `IDLE` state.

---

## 5. Defense Against Arbitrary Code Execution

- **Zero Raw SQL Injection**: The agent does not generate SQL queries directly from user prompts. All reads and writes use Frappe ORM parameterized methods (`frappe.get_doc`, `frappe.get_all`, `doc.insert`).
- **Zero Python `eval()` / `exec()` of User Prompts**: User instructions are parsed as semantic parameters, not executed as Python scripts.
- **Zero Shell Command Access**: The agent has no tool to execute arbitrary bash/cmd commands.

---

## 6. Immutable Audit Logging

Every agent transaction that changes ERPNext state is logged into `ERPNext_Agent/logs/agent_audit.jsonl`:
- **Logged Attributes**:
  - `timestamp`: UTC ISO-8601 timestamp.
  - `event_type`: CREATE, UPDATE, SUBMIT, CANCEL, DELETE.
  - `module`: Target ERPNext module.
  - `tool_name`: Executed tool.
  - `inputs`: Sanitized parameter values (passwords, tokens, and secrets masked with `********`).
  - `output`: Document name and structured result.
  - `validation`: Read-back verification result.
  - `status`: SUCCESS or FAILED.
  - `error`: Error message if applicable.
- The audit log is append-only and provides full non-repudiation for industrial AI operations.
