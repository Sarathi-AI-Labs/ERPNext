# ARCHITECTURE AUDIT REPORT: SARATHI INDUSTRIAL AI AGENT

**Document:** Comprehensive Codebase & Architecture Audit  
**Workspace:** `D:\SarathiAiLabs\Industrial_Projects\Frappe_docker_main`  
**Agent Workspace:** `D:\SarathiAiLabs\Industrial_Projects\Frappe_docker_main\ERPNext_Agent`  
**Git Branch:** `Skills`  
**Date:** 2026-10-01  
**Status:** COMPLETE 15-POINT ARCHITECTURE AUDIT  

---

## 1. Current Architecture Overview

The system consists of two primary operational domains running across a hybrid Host/Docker deployment:

1. **Frappe / ERPNext v16 Engine (`frappe_docker_main`)**:
   - **Frontend / Reverse Proxy:** `frappe_docker_main-frontend-1` serving port `8080`.
   - **Python Application Server:** `frappe_docker_main-backend-1` running Frappe v16.33.0 on Python 3.14.3 (`/home/frappe/frappe-bench/env/bin/python`).
   - **Database:** MariaDB 11.8 (`frappe_docker_main-db-1`) storing transactional data.
   - **Caching / Queues:** Redis cache (`redis-cache`), Redis queue (`redis-queue`), and Socket.io websocket.
   - **Custom App:** `sarathi_visibility` (mounted at `/home/frappe/frappe-bench/apps/sarathi_visibility/sarathi_visibility`).
   - **Active Site:** `frontend` (`/home/frappe/frappe-bench/sites/frontend`).

2. **Agent Layer (`ERPNext_Agent`)**:
   - Located on host at `d:\SarathiAiLabs\Industrial_Projects\Frappe_docker_main\ERPNext_Agent` and mirrored to container `/home/frappe/frappe-bench/apps/ERPNext_Agent/`.
   - Structured around 13 core business modules (Organization to Users and System).
   - Core sub-packages: `core/` (state, router, loader, planner, resolver, validator, audit, conversational agent), `tools/` (client, document_tools, meta_tools, query_tools, workflow_tools, report_tools), `tests/`, and CLI `run_agent.py`.
   - Web API Bridge: `sarathi_visibility/sarathi_visibility/api/agent_chat.py`.

---

## 2. Current Agent Flow

The request-response lifecycle from natural language to database and back:
1. **User Input:** User submits a prompt through the Sarathi Chatbox UI or the CLI (`run_agent.py`).
2. **Web Entrypoint:** `sarathi_visibility.api.agent_chat.send_message` receives `message`, `session_id`, `company`, `customer`, `project`.
3. **Session Restoration:** Fetches active `ChatSession` from Frappe Redis cache (`sarathi_agent_sessions`).
4. **Intent & Skill Routing:** `SkillRouter` maps natural language to one of 13 modules and determines action (CREATE, QUERY, SUBMIT, etc.).
5. **Skill Metadata Loading:** `SkillLoader` loads `SKILL.md`, `rules.json`, `workflows.json`, and `section_info.json`.
6. **Slot Discovery / Questionnaire:** If mandatory parameters are missing, returns `status: "COLLECTING_SLOTS"` with missing field prompts.
7. **Pre-checks & Validation:**
   - Uniqueness check via `frappe.db.exists`.
   - Permission check via `frappe.has_permission(doctype, "create")`.
   - Dependency check via `DependencyResolver`.
8. **Confirmation Gate:** If pre-checks pass, transitions to `AWAITING_CONFIRMATION` and renders interactive `[✓ Confirm & Create]` / `[✕ Cancel]` card.
9. **Mutation Execution:** Upon user confirmation, controlled Frappe tool (`CreateDocumentTool`) creates document through Frappe ORM (`frappe.new_doc()`, `doc.insert()`).
10. **Post-Mutation Read-Back:** `ReadBackValidator` reads back the record from MariaDB, verifying persisted attributes and `docstatus`.
11. **Immutable Audit:** `AuditLogger` appends structured JSONL record to `logs/agent_audit.jsonl`.
12. **Frontend Update:** Returns verified response (`status: "COMPLETED"`, `verified: true`) with direct Desk link.

---

## 3. Existing Skills (13 Modules & 98 Submodules)

The 13 business domain skill folders are completely organized:
1. **Organization:** Company, Branch, Department, Letter Head, Role Permissions, Email Account, Sarathi Customer Organization, User.
2. **Assets:** Asset, Depreciation Schedule, Asset Capitalization, Asset Movement, Maintenance, Reports, Setup, Settings.
3. **Buying:** Material Request, Request for Quotation, Supplier Quotation, Purchase Order, Purchase Invoice, Setup, Reports, Settings.
4. **Manufacturing:** BOM, Work Order, Job Card, Stock Entry, Material Planning, Tools, Reports, Setup, Settings.
5. **Projects:** Project, Task, Timesheet, Setup, Reports, Settings.
6. **Quality:** Quality Inspection, Quality Goals, Quality Reviews, Non Conformance, Quality Feedback, Setup.
7. **Selling:** Quotation, Sales Order, Sales Invoice, POS, Items and Pricing, Setup, Reports, Settings.
8. **Subcontracting:** Subcontracting BOM, Inward Order, Outward Order, Setup, Reports, Settings.
9. **Accounting:** Invoicing, Payments, Financial Reports, Accounts Setup, Taxes, Banking, Budget, Subscription, Share Management.
10. **Stock:** Stock Entry, Purchase Receipt, Delivery Note, Material Request, Pick List, Tools, Setup, Reports, Settings.
11. **ERPNext Settings:** Global Defaults, System Settings, Accounts Settings, POS Settings, Selling Settings, Buying Settings, Stock Settings, Manufacturing Settings, Projects Settings, Other Settings.
12. **Framework:** DocType, Page, Report, Workspace, Customization, Server Scripts, Client Scripts.
13. **Users and System:** Users, Roles, Permissions, Audits, System Settings.

---

## 4. Existing Tools

Controlled, atomic tools implemented in `ERPNext_Agent/tools/`:
- **Document Mutation Tools:** `CreateDocumentTool`, `GetDocumentTool`, `UpdateDocumentTool`, `DeleteDocumentTool`.
- **Workflow Tools:** `SubmitDocumentTool`, `CancelDocumentTool`, `AmendDocumentTool`.
- **Query Tools:** `SearchDocumentsTool`, `GetValueTool`, `GetCountTool`.
- **Metadata Tools:** `GetDocMetaTool`, `CheckPermissionTool`.
- **Report Tools:** `RunReportTool`.
- **Bridge:** `FrappeClient` operating natively inside container and via Docker IPC on host.

---

## 5. Existing LLM Capability

- Ollama is active on the host machine at `http://localhost:11434` (and accessible from the container at `http://host.docker.internal:11434`).
- Currently, intent classification and parameter extraction in `router.py` and `conversational_agent.py` rely primarily on deterministic regexes and keyword heuristics.
- Target requirement: Introduce `LLMGateway` abstraction in `ERPNext_Agent/llm/` supporting Ollama, structured Pydantic outputs, and graceful deterministic fallback when LLM is unavailable.

---

## 6. Existing Frappe Integration

- Integrated through whitelisted endpoint `@frappe.whitelist(methods=["POST"]) def send_message`.
- Hybrid runtime client in `client.py` auto-detects `hasattr(frappe, 'db') and frappe.db`.
- Database access is strictly mediated by Frappe ORM (`frappe.new_doc`, `frappe.get_doc`, `frappe.db.get_value`, `frappe.db.count`, `frappe.db.exists`).
- The AI Agent NEVER directly manipulates MariaDB.

---

## 7. Existing Frontend

- Integrated in `sarathi_visibility` single-page application (`sarathicontroltower`).
- Chatbox modal (`#sarathiAiChatModal`) styled in `sarathi_dashboard.css` and powered by `sarathi_dashboard.js`.
- Features:
  - Real-time animated execution status banner.
  - Interactive Confirmation Card (`.sd-ai-card-confirmation`) with checklist and `[Confirm & Create]` / `[Cancel]` buttons.
  - Live activity feed (`.sd-ai-card-changes`).
  - Follow-up action chips.
  - Auto-refresh of dashboard upon record completion.

---

## 8. Existing Security

- MariaDB database is completely behind Frappe ORM. No raw SQL execution.
- No arbitrary `exec()` / `eval()` / shell execution is accessible to natural language tools.
- Validation gate rejects mutations if required fields are missing or duplicate records exist.
- Audit logger redacts sensitive values and records immutable JSONL logs.
- Need enhancement: Ensure permission checks use the real authenticated user (`frappe.session.user`) instead of defaulting to `Administrator`.

---

## 9. Existing Testing

- Unit test suite: `ERPNext_Agent/tests/run_all_tests.py` containing 32 tests across router, loader, resolver, validator, live tools, and conversational flows (100% passing).
- Live verification against Docker MariaDB database successfully verified Company creation (`Gaurav Manufacturing`) and Project creation (`PROJ-0009`).

---

## 10. Problems Identified

1. **Hardcoded Field Definitions vs Live Metadata:** While `frappe.get_meta()` tool exists, `SLOT_DEFINITIONS` in `conversational_agent.py` still serves as the primary schema reference. Live Frappe metadata must become the runtime source of truth.
2. **Regex-Only Intent & Extraction:** Natural language with unusual phrasing can fail regex bounds. Needs `HybridRouter` combining deterministic patterns with LLM structured classification.
3. **Absence of Formal LangGraph State Orchestration:** The current state machine is a custom Python class. LangGraph + Pydantic `AgentState` needs to be formalized as the primary orchestrator.
4. **LLM Gateway Layer Missing:** No formal `ERPNext_Agent/llm/` abstraction layer to decouple Ollama from the agent logic.
5. **Permission User Context:** Some tool tests still default to `Administrator` rather than enforcing `frappe.session.user`.

---

## 11. Components to Preserve

1. `FrappeClient` (`tools/client.py`) hybrid execution architecture.
2. All 13 module folders and their sub-sections (`SKILL.md`, `rules.json`, `workflows.json`, `section_info.json`).
3. `ReadBackValidator` (`core/validator.py`) post-mutation verification.
4. `AuditLogger` (`core/audit.py`) immutable structured logging.
5. `DependencyResolver` (`core/resolver.py`) DAG topological sorting.
6. Sarathi AI Chatbox UI and CSS in `sarathi_visibility`.
7. Existing atomic tools (`document_tools`, `workflow_tools`, `query_tools`, `meta_tools`, `report_tools`).

---

## 12. Components to Refactor

1. `ERPNext_Agent/core/conversational_agent.py` ➔ Refactor into LangGraph state graph nodes.
2. `ERPNext_Agent/core/router.py` ➔ Upgrade to `HybridRouter` using LLM classification + deterministic fallbacks.
3. `sarathi_visibility/sarathi_visibility/api/agent_chat.py` ➔ Pass authenticated `frappe.session.user` and dispatch structured agent events.
4. `ERPNext_Agent/tools/meta_tools.py` ➔ Create `MetadataService` that provides live ERPNext schemas as runtime source of truth.

---

## 13. Components to Deprecate

1. Hardcoded `SLOT_DEFINITIONS` as the runtime schema authority (retain only as fallback/UX hints).
2. Ad-hoc string parsing for field values in favor of Pydantic structured output.
3. Hardcoded `Administrator` defaults in permission checking.

---

## 14. Target Architecture

```
USER
  ↓
SARATHI AI CHATBOX (sarathi_dashboard.js)
  ↓
FRAPPE API (agent_chat.py)
  ↓
MASTER AI AGENT (master_agent.py)
  ↓
LANGGRAPH WORKFLOW (14-Node State Graph)
  ↓
LLM GATEWAY (llm/gateway.py) ➔ OLLAMA (Local LLM)
  ↓
HYBRID ROUTER (Deterministic + LLM + Live Metadata)
  ↓
SKILL REGISTRY & DYNAMIC LOADER
  ↓
LIVE FRAPPE METADATA SERVICE (frappe.get_meta())
  ↓
PYDANTIC PARAMETER EXTRACTION
  ↓
DEPENDENCY RESOLVER (DAG ordering)
  ↓
VALIDATION & AUTHENTICATED PERMISSION CHECK
  ↓
EXPLICIT SAFETY CONFIRMATION GATE
  ↓
CONTROLLED TOOL REGISTRY (Pydantic Tools)
  ↓
FRAPPE ORM / API (frappe.new_doc, doc.insert, doc.save)
  ↓
ERPNEXT ➔ MARIADB
  ↓
READ-BACK VALIDATOR (Verified == True)
  ↓
AUDIT LOGGER (Immutable JSONL)
  ↓
STRUCTURED AGENT EVENTS (REQUEST_RECEIVED -> COMPLETED)
  ↓
SARATHI AI CHATBOX
```

---

## 15. Migration Plan

- **Step 1:** Create `ERPNext_Agent/llm/` with `base.py`, `gateway.py`, `ollama.py`, `schemas.py`, and prompts.
- **Step 2:** Create `ERPNext_Agent/core/state.py` with Pydantic `AgentState`.
- **Step 3:** Implement `MetadataService` (`core/metadata_service.py`) using `frappe.get_meta()`.
- **Step 4:** Implement `SkillRegistry` (`core/registry.py`) and connect to `SkillLoader`.
- **Step 5:** Build `HybridRouter` (`core/hybrid_router.py`) combining deterministic rules and LLM intent classification.
- **Step 6:** Construct LangGraph workflow graph (`core/workflow.py`) with complete node pipeline.
- **Step 7:** Implement `ToolRegistry` (`tools/tool_registry.py`) with Pydantic tool schemas and permission enforcement.
- **Step 8:** Integrate with `agent_chat.py` and `sarathi_dashboard.js` with structured agent events.
- **Step 9:** Execute Golden Path Company E2E test and verify against Docker MariaDB.
- **Step 10:** Synchronize container, run full regression test suite, and update documentation.
