# TESTING & VERIFICATION SPECIFICATION

## 1. Test Architecture Overview

The Sarathi Industrial AI Agent test suite validates the entire agent lifecycle from intent recognition down to live database commits and read-back verification:

```
Test Runner: ERPNext_Agent/tests/run_all_tests.py
Total Tests: 46
Status: 100% PASSING (46 / 46)
Runtime: ~115 seconds
Execution Environment: Containerized ERPNext v16 / Host Python 3.12+
```

---

## 2. Test Suite Breakdown (12 Test Suites, 46 Tests)

### 2.1 Intent Routing & Classification (`test_router.py` — 9 Tests)
- `test_route_organization`: Validates queries about company routing to Organization module.
- `test_route_stock_mutation`: Validates material receipt creation routing to Stock.
- `test_route_manufacturing`: Validates Work Order submission routing to Manufacturing.
- `test_route_buying`: Validates supplier and Purchase Order routing.
- `test_route_selling`: Validates Sales Order queries routing to Selling.
- `test_route_accounting`: Validates Journal Entry creation routing to Accounting.
- `test_route_projects`: Validates Project and Task queries routing to Projects.
- `test_route_assets`: Validates Asset status queries routing to Assets.
- `test_route_quality`: Validates Quality Inspection submission routing to Quality.

### 2.2 Dynamic Skill Loading (`test_loader.py` — 2 Tests)
- `test_load_all_13_modules`: Validates that all 13 module skill packages load with valid `SKILL.md`, `rules.json`, `workflows.json`, and `examples.json`.
- `test_context_formatting`: Validates optimized prompt injection context formatting.

### 2.3 Dependency Resolution (`test_resolver.py` — 2 Tests)
- `test_prerequisites_lookup`: Verifies prerequisite detection for Work Order (BOM, Item, Warehouse).
- `test_topological_plan_ordering`: Verifies dependency DAG calculation (Company -> Project -> BOM -> Work Order).

### 2.4 Live Tool Execution (`test_tools_live.py` — 5 Tests)
*(Executed live against container `frappe_docker_main-backend-1` and site `frontend`)*
- `test_live_search_company`: Parameterized search retrieving live Company records (`SarathiAILabs`).
- `test_live_get_value_company`: Fetches specific fields (`abbr: S`, `default_currency: INR`).
- `test_live_get_count_items`: Queries live DocType count (>100 doc types verified).
- `test_live_get_doc_meta_project_custom_fields`: Inspects live schema for `Project` verifying Sarathi custom fields (`custom_sarathi_manufacturing`, `custom_sarathi_bom`).
- `test_live_check_permission`: Tests permission evaluation via `frappe.has_permission`.

### 2.5 Read-Back Verification Engine (`test_validator.py` — 4 Tests)
- `test_verify_status_match`: Confirms successful verification when status matches.
- `test_verify_status_mismatch`: Confirms verification failure when status differs.
- `test_verify_stock_sufficient`: Validates pre-transaction stock sufficiency checks.
- `test_verify_stock_insufficient`: Validates pre-transaction stock shortage alerts.

### 2.6 Stateful Conversational Flow (`test_conversational.py` — 4 Tests)
- `test_turn1_missing_slots_questionnaire_project`: Tests slot discovery for Project.
- `test_turn1_company_slot_intake`: Tests slot discovery for Company.
- `test_company_confirmation_flow`: Tests complete confirmation card generation and cancellation.
- `test_cancellation`: Tests user reset / cancel flow.

### 2.7 End-to-End Workflows (`test_e2e_workflows.py` — 2 Tests)
- `test_e2e_query_company`: Tests natural language company currency inquiry, tool execution, and audit log generation.
- `test_e2e_skill_context_loading`: Tests dynamic skill context extraction for Manufacturing.

### 2.8 LLM Gateway & Provider Abstraction (`test_llm_gateway.py` — 4 Tests)
- `test_gateway_initialization`: Verifies provider registration and active provider selection.
- `test_ollama_provider_health`: Checks Ollama connectivity or graceful unreachable status reporting.
- `test_structured_intent_classification`: Tests Pydantic parsing of intent JSON.
- `test_fallback_on_llm_failure`: Validates deterministic fallback when provider is offline.

### 2.9 Skill Registry Indexing (`test_registry.py` — 4 Tests)
- `test_all_13_skills_indexed`: Verifies that all 13 modules are registered with valid root paths.
- `test_doctype_to_module_mapping`: Validates resolution of DocTypes (e.g. `Work Order` -> `Manufacturing`, `Company` -> `Organization`).
- `test_section_discovery`: Verifies sub-module discovery (e.g. `Accounts Setup`, `BOM`, `Job Card`).
- `test_module_metadata`: Inspects structured metadata dictionary generation.

### 2.10 Controlled Tool Registry (`test_tool_registry.py` — 4 Tests)
- `test_registry_tool_count`: Verifies all 15 atomic tools are registered with schemas.
- `test_safety_level_enforcement`: Validates safety levels (`SAFE`, `CONFIRMATION_REQUIRED`, `HIGH_RISK`).
- `test_permission_gate`: Validates tool refusal when user lacks required Frappe permissions.
- `test_read_tool_execution`: Executes live read tool against ERPNext container.

### 2.11 Audit Logger & Integrity (`test_audit_logger.py` — 3 Tests)
- `test_log_event_creation`: Verifies event writing to `agent_audit.jsonl`.
- `test_secret_masking`: Verifies passwords, API keys, and tokens are scrubbed.
- `test_audit_trail_integrity`: Verifies cryptographic hash generation for audit events.

### 2.12 LangGraph State Machine Workflow (`test_graph_workflow.py` — 3 Tests)
- `test_graph_compilation`: Validates that the 14-node LangGraph compiles successfully.
- `test_graph_single_turn_read`: Executes `understand_request` -> `execute_tool` -> `respond` for stock inquiry.
- `test_graph_company_creation_flow`: Tests multi-turn slot collection, confirmation requirement, and completion.

---

## 3. How to Run the Tests

To run the complete 46-test regression suite:
```bash
python -X utf8 ERPNext_Agent/tests/run_all_tests.py
```

Expected Output:
```
======================================================================
SARATHI INDUSTRIAL AI AGENT — FULL REGRESSION TEST RUNNER
======================================================================
Running 46 tests across 12 test suites...
..............................................
----------------------------------------------------------------------
Ran 46 tests in 114.887s

OK
```

---

## 4. Live Multi-Turn E2E Verification in Container

To run the exact live multi-turn conversation test inside the Frappe container:
```bash
docker exec -w /home/frappe/frappe-bench/sites frappe_docker_main-backend-1 \
  /home/frappe/frappe-bench/env/bin/python -c "
import frappe
frappe.init('frontend')
frappe.connect()
from sarathi_visibility.api.agent_chat import send_message

sid = 'e2e_live_test'
print('Turn 1:', send_message('I want to create a new company.', session_id=sid)['status'])
print('Turn 2:', send_message('Gaurav Robotics.', session_id=sid)['status'])
print('Turn 3:', send_message('GR.', session_id=sid)['status'])
print('Turn 4:', send_message('Yes, confirm and create.', session_id=sid)['status'])
"
```
Expected Output:
```
Turn 1: COLLECTING_SLOTS
Turn 2: COLLECTING_SLOTS
Turn 3: AWAITING_CONFIRMATION
Turn 4: COMPLETED
```
Final payload contains: `verified: true`, `doctype: Company`, `name: Gaurav Robotics`.
