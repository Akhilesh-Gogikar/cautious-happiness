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
| **MGMT-003** | Done | High | YC-Style Product Development Plan | Added a dedicated execution plan document covering ICP, MVP scope, metrics, roadmap, and the first 90 days of pilot preparation. |
| INFRA-006 | Done | High | Shared Persistent HTTPX Client | Refactor IntelligenceService to use a singleton AsyncClient for connection pooling. |
| INFRA-007 | Done | High | Speculative Pipeline Execution | Enable parallel source auditing and forecast generation in IntelligenceMirrorEngine. |
| DEBT-005 | Done | Medium | Unified Schema Serialization | Automate Pydantic model instantiation from LLM JSON to eliminate manual unpacking boilerplate. |
| **DEBT-ARCH-001** | Todo | High | Unified Intelligence Domain | Consolidate `services/intelligence.py` and `app/intelligence/` into a cohesive `domain/intelligence` module to fix split logic and circular dependency risks. |
| **FEAT-CRITIC-001** | Todo | High | Structured Critic Output | Replace brittle regex parsing in `CriticService` with Pydantic-based `StructuredCriticResult` using generic schema enforcement. |
| **INFRA-OBS-001** | Todo | High | Structured Logging & Telemetry | Replace `print` debugging with `logger.error` and structured JSON logs across `engine.py` and services. |
| **MGMT-004** | Done | High | Full QA Pass + Per-Feature PM Plan | Tested every page, view, component and endpoint at `eb728a0`. See [QA_TEST_REPORT.md](docs/QA_TEST_REPORT.md) (56 defects) and [PRODUCT_MANAGEMENT_PLAN.md](docs/PRODUCT_MANAGEMENT_PLAN.md) (feature cards + phased roadmap). |
| **QA-P0-01** | Todo | High | API Boots From Clean Clone | Fix circular import (`app/intelligence/api/news.py` ↔ `app/domain/intelligence/__init__.py`), undefined `async_session`, undeclared `sentence-transformers`; CI import smoke test. Plan: PL-01. Defects: QA-001, QA-002. |
| **QA-P0-02** | Todo | High | Real Login End to End | Frontend password login via `/auth/token`, `/auth/me`, token on every call, remove email-based admin. Plan: PG-02, SV-01, X-2. Defects: QA-003–006, QA-035. |
| **QA-P0-03** | Todo | High | Rotate & Purge Committed Secrets | Rotate TLS/NPM keys, remove `nginx/data`, `server.key`, `backend_logs.txt` from tree and history, enable secret scanning, enforce `SECRET_KEY`. Plan: PL-02. Defect: QA-007. |
| **QA-P0-04** | Todo | High | Lock Down Unauthenticated & Order Endpoints | Auth on every non-public route; RBAC deny-by-default; gate `/tools/call` orders and `/trade/execute` behind `FEATURE_EXECUTION`; remove false-success trade UI. Plan: SV-02, SV-11, SV-13. Defects: QA-011–014. |
| **QA-P0-05** | Todo | High | Forecast Lifecycle Completes in UI | Async Redis pub/sub WebSocket, true failed state, cache write, ownership check, polling fallback. Plan: VW-01b, SV-04. Defects: QA-008, QA-015–018. |
| **QA-P0-06** | Todo | High | Chat Works Against Real llama.cpp | Parse SSE `data:` frames; contract test with recorded stream; error events. Plan: SV-06, VW-08, GC-07. Defect: QA-009. |
| **QA-P0-07** | Todo | High | Compose Serves the Real Model | Real llama.cpp server mounting the GGUF; mock moved to test profile; nginx WS/SSE config; local critic default. Plan: PL-01, SV-05. Defects: QA-010, QA-052, QA-054. |
| **QA-P0-08** | Todo | High | Migrations Baseline + CI | Alembic baseline incl. `vector` extension; GitHub Actions (tsc/lint/build, hermetic pytest, E2E smoke). Plan: PL-03, PL-04. Defects: QA-022, QA-034. |
| **QA-P1-01** | Todo | High | Runs & Decision Memo | Persist forecast runs, citations, critic verdict/override, memo export (PDF/MD). Plan: VW-01c, SV-04, SV-05. |
| **QA-P1-02** | Todo | High | Pilot Mode / Demo-Data Policy | `PILOT_MODE` hides mock surfaces; `DEMO` badge elsewhere; real KPI stat cards; accurate status dropdown; cut wallet connect. Plan: X-1, GC-02–04, GC-08, VW-01e/f. Defects: QA-028–030, QA-047. |
| **QA-P1-03** | Todo | High | Intelligence Mirror on Real Sources | Tracked-target CRUD, persisted snapshots, critic review, "run forecast with this context", no fabricated fallbacks. Plan: VW-07, SV-07. |
| **QA-P1-04** | Todo | High | Security & Audit View | Mount security router; API keys, IP allowlist, audit log viewer, users/roles. Plan: VW-10, SV-02. Defect: QA-023. |
| **QA-P1-05** | Todo | Medium | URL Routing, Nav & Layout Fixes | `/dashboard/[view]`, accessible nav, z-index scale, single scroll container, hide locked items. Plan: PG-03, GC-01. Defects: QA-029, QA-043, QA-045. |
| **QA-P1-06** | Todo | Medium | Single Chat Experience | Merge Analyst Chat, sidebar chat, Discuss-findings and Strategy CLI into one grounded chat with persisted conversations. Plan: VW-08, VW-01d, GC-07. Defects: QA-036, QA-037, QA-044. |
| **QA-P1-07** | Todo | Medium | Server-Side Settings & Secrets | Move Alpaca/Gemini/model config server-side; remove localStorage secrets; Settings page replaces Config placeholder. Plan: GC-06, VW-11. Defects: QA-040–042. |
| **QA-P1-08** | Todo | Medium | Real Markets Data Service | Scheduled ingestion of commodity prices + Polymarket/Kalshi signals with source/as-of. Plan: SV-03, SV-12, VW-01a. |
