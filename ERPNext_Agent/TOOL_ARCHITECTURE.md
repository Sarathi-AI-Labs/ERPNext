# TOOL ARCHITECTURE SPECIFICATION

## 1. Controlled Tool Philosophy

The Sarathi AI Agent interacts with ERPNext strictly through controlled, typed, and permission-checked tools.
- **NO Arbitrary SQL**: The agent cannot execute raw `frappe.db.sql("DROP...")` or uncontrolled SQL statements.
- **NO Arbitrary Python Code Execution**: The agent does not generate and execute arbitrary Python strings on the fly.
- **NO Direct Shell Commands**: The agent cannot spawn bash shells or command-line processes directly from user input.
- **Controlled Frappe ORM**: All mutations pass through `frappe.new_doc()`, `doc.insert()`, `doc.save()`, `doc.submit()`, and `doc.cancel()`, ensuring all standard ERPNext hooks, validation methods, and ledger postings execute properly.

---

## 2. Base Tool Contract (`BaseTool`)

Located in `ERPNext_Agent/tools/base_tool.py`:
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    def __init__(self, client: FrappeClient):
        self.client = client

    def validate_inputs(self, params: Dict[str, Any]) -> None:
        """Validates input dictionary against JSON schema."""
        ...

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Executes the tool and returns a structured dictionary."""
        ...
```

---

## 3. Tool Inventory

| Tool Name | Class | Source File | Purpose |
|---|---|---|---|
| `create_document` | `CreateDocumentTool` | `tools/document_tools.py` | Inserts a new document with validation. |
| `get_document` | `GetDocumentTool` | `tools/document_tools.py` | Fetches a full document including child tables. |
| `update_document` | `UpdateDocumentTool` | `tools/document_tools.py` | Updates specific fields and saves. |
| `delete_document` | `DeleteDocumentTool` | `tools/document_tools.py` | Deletes a draft or cancelled document. |
| `submit_document` | `SubmitDocumentTool` | `tools/workflow_tools.py` | Submits a submittable document (`docstatus=1`). |
| `cancel_document` | `CancelDocumentTool` | `tools/workflow_tools.py` | Cancels a submitted document (`docstatus=2`). |
| `amend_document` | `AmendDocumentTool` | `tools/workflow_tools.py` | Creates an amended copy of a cancelled record. |
| `search_documents` | `SearchDocumentsTool` | `tools/query_tools.py` | Parameterized search with filters, fields, and limits. |
| `get_value` | `GetValueTool` | `tools/query_tools.py` | Fetches specific field values by filter. |
| `get_count` | `GetCountTool` | `tools/query_tools.py` | Counts records matching filters. |
| `get_doc_meta` | `GetDocMetaTool` | `tools/meta_tools.py` | Retrieves live runtime schema, field types, and rules. |
| `check_permission` | `CheckPermissionTool` | `tools/meta_tools.py` | Checks user permission (read/write/create/submit/cancel). |
| `run_report` | `RunReportTool` | `tools/report_tools.py` | Executes standard ERPNext reports. |

---

## 4. Dual-Mode Client Architecture (`FrappeClient`)

All tools delegate execution to `FrappeClient` (`tools/client.py`).
`FrappeClient` detects the execution context:
1. **In-Process Mode**: If `hasattr(frappe, "db") and frappe.db`:
   - Executes natively in Frappe Python process (0ms sub-process latency).
2. **IPC Mode**: If running externally (e.g. from host CLI):
   - Invokes parameterized Docker execution with proper escaping and error capturing.

Every tool returns a structured dictionary:
```json
{
  "success": true,
  "doctype": "Company",
  "name": "Gaurav Manufacturing",
  "data": { ... }
}
```
If an error occurs, it returns:
```json
{
  "success": false,
  "error": "Explanation of failure",
  "exc_type": "DuplicateEntryError"
}
```
