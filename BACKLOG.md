# Product Backlog

| ID | Status | Priority | Description | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **STRAT-001** | Todo | High | Prototype Demo | Showcase existing Prediction generation + Criticism capabilities. (From VISION.md) |
| **STRAT-002** | Todo | High | Data Integration | Define specific commodity data sources (shipping manifests, satellite imagery) for "Physicals" context. (From VISION.md) |
| **FEAT-001** | Todo | High | Intelligence Mirror | Implement competitive intelligence dashboard components (scrapers + NLP for competitor analysis). (From ARCHITECTURE.md & History) |
| **FEAT-002** | Todo | High | The Critic Verification | Ensure "Hallucination Firewall" using Gemini is fully implemented and operational. (From ARCHITECTURE.md) |
| **FEAT-003** | In Progress | High | OpenForecaster Integration | Ensure local LLM (Ollama) integration is robust and private. (From ARCHITECTURE.md) |
| **FEAT-004** | Todo | Medium | Frontend "Data Noir" UI | Implement strict "Data Noir" design system across all views. Dark mode, high contrast, monospace data. (From frontend.md) |
| **DEBT-001** | In Progress | Medium | Refactor Backend Services | Align backend code with `backend.md` architecture (Service-oriented: `intelligence.py`, `critic.py`). (From History) |
| **DEBT-002** | Todo | Low | Code Editor Component | Improve `CodeEditor.tsx` functionality and integration. (From History) |
| **DEBT-003** | Todo | Low | Parse Strategy Class Name | `# TODO: Parse class name from code` in `backend/app/strategy/service.py`. |
| **INFRA-001** | Todo | Medium | Nginx SSL Setup | Configure self-signed certificates for secure local deployment. (From History) |
| **INFRA-002** | Todo | Medium | Docker Orchestration | Ensure all services (Backend, Frontend, Ollama, Redis, DB) spin up correctly via `run.sh`. (From AGENTS.md) |
| **INFRA-003** | Todo | High | Asynchronous Pipeline Orchestration | Refactor IntelligenceMirrorEngine to use concurrent execution for search/forecast/critique steps. |
| **DEBT-004** | Todo | Medium | Unified Schema & Serialization | Centralize Pydantic models and unify response serialization in `main.py` to eliminate boilerplate. |
| **FEAT-005** | Todo | High | Real-time State Synchronization | Replace frontend mock data in Portfolio/Order Flow with live API calls to backend services. |
| **FEAT-006** | REPLACED | High | [Diverged to FEAT-JSON-PARSER] | Migrated to structured JSON engine. |
| **FEAT-007** | REPLACED | Medium | [Diverged to FEAT-WS-STREAM] | Migrated to WebSocket event stream. |
| **INFRA-004** | REPLACED | High | [Diverged to INFRA-SMART-FALLBACK] | Migrated to Neural Resilience Layer. |
| **FEAT-008** | Todo | High | [FEAT-JSON-PARSER] Reliable Structured Data Engine | Replace regex parsing with Pydantic + GBNF for 100% reliable extraction. |
| **FEAT-009** | Todo | Medium | [FEAT-WS-STREAM] Real-time Prediction Lifecycle Stream | Implement WebSocket-based updates (Searching -> Thinking -> Critiquing) for low-latency UX. |
| **INFRA-005** | Todo | High | [INFRA-SMART-FALLBACK] Neural Resilience Layer | Implement tier-based model fallback system (Local High -> Local Fast -> Cloud). |
| **MGMT-001** | In Progress | High | Product Management Framework | Setup framework docs and populate backlog. (From existing BACKLOG.md) |
| **MGMT-002** | Todo | High | Narrative Honesty on Product Maturity | Reflect in external-facing docs that the platform has a strong control plane, but moat-critical hardening remains unfinished across Critic reliability, structured parsing, live state sync, orchestration, and intelligence-domain cleanup. |
| INFRA-006 | Done | High | Shared Persistent HTTPX Client | Refactor IntelligenceService to use a singleton AsyncClient for connection pooling. |
| INFRA-007 | Done | High | Speculative Pipeline Execution | Enable parallel source auditing and forecast generation in IntelligenceMirrorEngine. |
| DEBT-005 | Done | Medium | Unified Schema Serialization | Automate Pydantic model instantiation from LLM JSON to eliminate manual unpacking boilerplate. |
| **DEBT-ARCH-001** | Todo | High | Unified Intelligence Domain | Consolidate `services/intelligence.py` and `app/intelligence/` into a cohesive `domain/intelligence` module to fix split logic and circular dependency risks. |
| **FEAT-CRITIC-001** | Todo | High | Structured Critic Output | Replace brittle regex parsing in `CriticService` with Pydantic-based `StructuredCriticResult` using generic schema enforcement. |
| **INFRA-OBS-001** | Todo | High | Structured Logging & Telemetry | Replace `print` debugging with `logger.error` and structured JSON logs across `engine.py` and services. |
