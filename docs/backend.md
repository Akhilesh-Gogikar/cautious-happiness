# Backend Service Documentation

## Purpose / Context
The Backend service is the "Central Nervous System" of the Alpha Insights Platform. It orchestrates the RAG pipeline between the local forecasting engine, the external verification agent (Critic), and the database.

## 1. Key Technologies
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Task Queue**: Celery + Redis
- **LLM Routing**: Custom `AIClient` with a default llama.cpp-compatible provider (`text-gen-cpp`) and optional Ollama / Gemini adapters

## 2. Runtime model routing

The current checked-in backend runtime behaves as follows:

- **Primary local provider**: `llama-cpp`, backed by `LLAMA_CPP_HOST=http://text-gen-cpp:8080` in Docker Compose.
- **Primary local model**: `lfm-thinking`.
- **Compatibility alias**: `openforecaster` is normalized to `lfm-thinking` in the intelligence service.
- **Secondary fallback identifier**: `lfm-40b` is referenced by the fallback orchestrator, but is not provisioned by the default compose setup.
- **Optional providers**: Ollama and Gemini adapters still exist in code for alternate deployments and verification flows.

## 3. Directory Structure

```text
backend/
├── app/
│   ├── api/            # Route controllers (Versioned, e.g., v1/)
│   ├── core/           # Config, Security, Events
│   ├── db/             # Database models and migrations
│   ├── services/       # Business logic (The "Meat")
│   ├── domain/         # Forecasting, critic, and intelligence flows
│   └── main.py         # Entry point
├── tests/              # Pytest suite
└── requirements.txt
```

## 4. Core Logic Flows

### A. The prediction pipeline
1. **Trigger**: User requests analysis or a scheduled job starts.
2. **Orchestration**: The engine coordinates search, forecasting, and critique services.
3. **Step 1 (Generate)**: Call the local llama.cpp-compatible service on `text-gen-cpp` and request the default `lfm-thinking` model.
4. **Step 2 (Verify)**: Pass result to the Critic service (Gemini).
5. **Result**: If verified, save to DB. If rejected, discard.

### B. The Critic verification
- **Input**: A claim string + citations.
- **Process**: Gemini checks the trusted whitelist.
- **Outcome**: `True` (Verified) or `False` (Hallucination).

### C. Fallback behavior
- The fallback orchestrator first tries `lfm-thinking`.
- If that fails, it can attempt `lfm-40b`.
- Contributors should not assume the fallback tier is available unless they explicitly provision that model in their environment.

## 5. Development Guide

### Running locally (without Docker)
> [!WARNING]
> Docker is the recommended path because the default environment wiring expects Redis, Postgres, and `text-gen-cpp`.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Adding a new route
1. Create the route handler in the relevant router module.
2. Register it in the main API router.
3. Add strict Pydantic models for request / response payloads.
4. Document whether the route expects `lfm-thinking`, an alias such as `openforecaster`, or a non-default provider.

## 6. Troubleshooting
- **Local inference connection error**: Ensure the `text-gen-cpp` container is healthy and reachable at `http://localhost:8080` from the host or `http://text-gen-cpp:8080` in Docker.
- **Unexpected model fallback**: Check whether your environment actually provisions `lfm-40b`; the default compose stack does not.
- **Gemini auth error**: Check `GEMINI_API_KEY` in `.env`.
