# LLM Subsystem Architecture — Sarathi ERPNext AI Agent

## 1. Overview & Provider Abstraction
The Sarathi AI Agent decouples all LLM operations from specific model runtimes via the `BaseLLMProvider` abstract interface and unified `LLMGateway`. 
The rest of the agent (LangGraph workflow nodes, HybridRouter, parameter extraction) communicates exclusively through `LLMGateway`, ensuring zero vendor lock-in and seamless transition between local and cloud LLM runtimes without modifying orchestrator or tool code.

```
+-------------------------------------------------------------------+
|                         Agent Workflow                            |
|             (HybridRouter, LangGraph Parameter Extractor)         |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                           LLMGateway                              |
|   - Automatic Docker vs Host URL detection                        |
|   - Latency tracking & health checks                              |
|   - Fallback to deterministic regex & schemas if offline          |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                        BaseLLMProvider                            |
|    - generate()                                                   |
|    - generate_structured(schema: BaseModel)                       |
|    - is_available()                                               |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                         OllamaProvider                            |
|   - Model: configurable via OLLAMA_MODEL (e.g. llama3.2, mistral) |
|   - Endpoints: http://localhost:11434 (Host),                     |
|                http://host.docker.internal:11434 (Container)      |
|   - Native JSON Schema enforcement                                |
+-------------------------------------------------------------------+
```

---

## 2. Directory Structure
```
ERPNext_Agent/llm/
├── __init__.py
├── base.py         # Abstract BaseLLMProvider definition
├── gateway.py      # LLMGateway routing, health checks, & fallbacks
├── ollama.py       # OllamaProvider implementation with JSON schemas
├── schemas.py      # Pydantic schemas (intent, extraction, health)
└── prompts/        # System prompts & classification guidelines
```

---

## 3. Pydantic Structured Outputs
Every LLM call produces strictly validated Pydantic models:

### 3.1 `LLMIntentClassification`
```python
class LLMIntentClassification(BaseModel):
    action: str = Field(description="Action intent: CREATE, UPDATE, DELETE, SUBMIT, CANCEL, QUERY, REPORT")
    primary_module: str = Field(description="One of the 13 ERPNext modules")
    target_doctype: Optional[str] = Field(description="Canonical ERPNext DocType name")
    secondary_doctypes: List[str] = Field(default_factory=list, description="Associated secondary entities")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    reasoning: Optional[str] = Field(description="Brief deduction summary")
```

### 3.2 `LLMParameterExtraction`
```python
class LLMParameterExtraction(BaseModel):
    doctype: str = Field(description="Target DocType")
    extracted_parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted entity key-value attributes")
    missing_mandatory: List[str] = Field(default_factory=list, description="Fields required by metadata not provided")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")
```

### 3.3 `LLMHealthStatus`
```python
class LLMHealthStatus(BaseModel):
    provider: str
    available: bool
    base_url: str
    model: str
    latency_ms: float
    error: Optional[str] = None
```

---

## 4. Fail-Safe Behavior & Offline Resilience
The AI Agent operates under a strict principle:
> **The LLM is an advisor for natural language understanding and parameter extraction; it is NEVER the execution authority.**

If the Ollama service is unreachable or encounters timeouts:
1. `LLMGateway.is_available()` returns `False`.
2. `HybridRouter` falls back instantly to deterministic regex, keyword heuristics, and live ERPNext metadata mapping.
3. `node_extract_parameters` falls back to key-value pattern extraction and interactive questionnaire slot intake.
4. **No unsafe mutation is ever executed blindly when the LLM is offline.**

---

## 5. Environment & Model Configuration
Configuration is passed via environment variables without hardcoded secrets:
- `OLLAMA_BASE_URL`: Base URL (default: `http://localhost:11434` or `http://host.docker.internal:11434`).
- `OLLAMA_MODEL`: Target model (e.g. `llama3.2`, `mistral`, `qwen2.5`).
- `LLM_TIMEOUT`: Request timeout in seconds (default: 30s).
