# SARATHI INDUSTRIAL AI AGENT — SYSTEM ARCHITECTURE

## 1. Executive Summary

The Sarathi Industrial AI Agent is an enterprise-grade, autonomous conversational coordinator designed specifically for ERPNext v16 and Frappe Framework. It converts natural-language business instructions into verified, permission-checked, and auditable ERPNext database transactions across all 13 core ERPNext module domains.

Unlike simplistic chatbots that rely on shallow text generation or brittle regexes, the Sarathi Agent enforces a strict execution pipeline:
```
NATURAL LANGUAGE REQUEST
        │
        ▼
MASTER ERP AGENT & INTENT CLASSIFIER
        │
        ▼
DYNAMIC SKILL ROUTER & LOADER
        │
        ▼
METADATA & SCHEMA INSPECTOR (Frappe Meta)
        │
        ▼
INTERACTIVE SLOT-FILLING DISCOVERY (Multi-Turn)
        │
        ▼
PRE-MUTATION VALIDATION & SAFETY GATE (Permission & Uniqueness)
        │
        ▼
USER CONFIRMATION [Confirm & Create]
        │
        ▼
CONTROLLED TOOL LAYER (Frappe ORM)
        │
        ▼
POST-MUTATION READ-BACK VERIFICATION
        │
        ▼
STRUCTURED AUDIT LOGGER (JSONL)
        │
        ▼
VERIFIED CHAT RESPONSE WITH DESK LINK & LIVE DASHBOARD REFRESH
```

---

## 2. Core Architectural Components

### 2.1 Hybrid Execution Bridge (`FrappeClient`)
The architecture operates seamlessly in two distinct runtime modes:
1. **Native In-Process Mode (Fastest, Web Chat)**:
   - When executing inside the Frappe bench Python worker (Gunicorn / `sarathi_visibility.api.agent_chat`), the agent detects active `frappe.db` and executes transactions directly through Frappe's Python ORM.
   - Eliminates process creation overhead and provides sub-second conversational latency.
2. **IPC Container Bridge Mode (CLI & CI/CD Testing)**:
   - When executing from the external host environment (`run_agent.py` or `unittest` suite), `FrappeClient` communicates securely via parameterized Docker commands (`docker exec -i -w /home/frappe/frappe-bench/sites ...`) executing structured Python wrappers.

### 2.2 Master Agent Coordinator (`MasterERPNextAgent`)
Located in `ERPNext_Agent/core/master_agent.py`, the master agent binds:
- `SkillRouter`: Classifies user intent and maps DocTypes to modules.
- `SkillLoader`: Lazily loads domain knowledge from the 13 skill directories.
- `DependencyResolver`: Calculates topological prerequisite DAGs.
- `ReadBackValidator`: Guarantees post-mutation existence and field accuracy.
- `AuditLogger`: Writes immutable structured JSONL logs.
- `ExecutionPlanner`: Assembles deterministic multi-step tool plans.

### 2.3 Stateful Conversational State Machine (`ConversationalAgent`)
Located in `ERPNext_Agent/core/conversational_agent.py`, manages multi-turn sessions across discrete states:
- `IDLE`: Listening for business requests.
- `COLLECTING_SLOTS`: Active when required fields are missing; discovers parameters interactively.
- `AWAITING_CONFIRMATION`: All mandatory fields collected; pre-checks passed; awaiting user confirmation.
- `COMPLETED`: Transaction executed, verified in database, and reported to user.
- Sessions are persisted in Frappe's Redis cache (`frappe.cache.hget/hset`), surviving across stateless HTTP requests.

### 2.4 Controlled Tool Layer (`ERPNext_Agent/tools/`)
The tool layer exposes strictly validated atomic operations:
- `CreateDocumentTool`: Validated document insertion.
- `GetDocumentTool`: Full record retrieval.
- `UpdateDocumentTool`: Field updates with change tracking.
- `DeleteDocumentTool`: Controlled record deletion.
- `SubmitDocumentTool`: Document submission (`docstatus` 0 -> 1).
- `CancelDocumentTool`: Document cancellation (`docstatus` 1 -> 2).
- `AmendDocumentTool`: Cancel and duplicate workflow.
- `SearchDocumentsTool`: Filtered querying.
- `GetDocMetaTool`: Live Frappe runtime DocType schema inspection.
- `CheckPermissionTool`: User permission verification.

---

## 3. Technology Stack & Deployment

| Layer | Component | Implementation |
|---|---|---|
| Frontend UI | Sarathi Control Tower Chatbot | Vanilla JS, Modern Dark-Glass CSS in `sarathi_dashboard.js` |
| REST API | Frappe Whitelist Bridge | `sarathi_visibility.api.agent_chat.send_message` |
| Backend Container | Frappe / ERPNext v16.33.0 | `frappe_docker_main-backend-1` (Python 3.14) |
| Web Server | Nginx Reverse Proxy | `frappe_docker_main-frontend-1` (Port 8080) |
| Database | MariaDB 11.8 Enterprise | `frappe_docker_main-db-1` |
| Cache & Session | Redis 6.2 Cache | `frappe_docker_main-redis-cache-1` |
| Agent Engine | Python Modular Engine | `ERPNext_Agent/core/`, `ERPNext_Agent/tools/` |
| Audit Trail | Immutable JSONL Logs | `ERPNext_Agent/logs/agent_audit.jsonl` |
