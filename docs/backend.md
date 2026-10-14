# Backend Service Documentation

## Purpose / Context
The Backend service is the "Central Nervous System" of the Alpha Insights Platform. It orchestrates the RAG pipeline between the local forecasting engine, the external verification agent (Critic), and the database.

## 1. Key Technologies
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Task Queue**: Celery + Redis
- **LLM Routing**: Custom `AIClient` with a default llama.cpp provider (`text-gen-cpp`, OpenAI-compatible chat route) and optional Ollama / Gemini adapters

## 2. Runtime model routing

The current checked-in backend runtime behaves as follows:

- **Primary local provider**: `llama-cpp`, backed by `LLAMA_CPP_HOST=http://text-gen-cpp:8080` in Docker Compose.
- **Primary local model**: `lfm-thinking`.
- **Compatibility alias**: `openforecaster` is normalized to `lfm-thinking` in the intelligence service.
- **Secondary fallback identifier**: `lfm-40b` is referenced by the fallback orchestrator. With `OLLAMA_HOST` empty, as compose sets it, it runs on the same local llama.cpp model.
- **Optional providers**: Ollama (used when `OLLAMA_HOST` is set) and Gemini (when `GEMINI_API_KEY` is set; the critic then prefers it).
- **Thinking output**: `lfm-thinking` reasons inside `<think>` tags before answering. `LlamaCppProvider` caps that at half of `n_predict` (`reasoning_budget_tokens`) and drops it from the text it returns. Requests with a `json_schema` are constrained by llama-server's grammar, so the reply parses as JSON.

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
4. **Step 2 (Verify)**: Pass result to the Critic service (the local model, or Gemini when configured).
5. **Result**: If verified, save to DB. If rejected, discard.

### B. The Critic verification
- **Input**: A claim string + citations.
- **Process**: The critic model (local `lfm-thinking`, or Gemini when configured) checks the trusted whitelist.
- **Outcome**: `True` (Verified) or `False` (Hallucination).

### C. Fallback behavior
- The fallback orchestrator first tries `lfm-thinking`.
- If that fails, it can attempt `lfm-40b`.
- Contributors should not assume the fallback tier is available unless they explicitly provision that model in their environment.

## 5. Development Guide

### Running with Docker Compose
Compose runs the backend and worker from the code built into their image; it does not mount the source or auto-reload. After changing backend code, rebuild them with `docker compose up -d --build backend worker` (`./run.sh` rebuilds everything). For a reload-on-save loop, run the backend outside Docker as below.

### Running locally (without Docker)
> [!WARNING]
> Docker is the recommended path because the default environment wiring expects Redis, Postgres, and `text-gen-cpp`.
> Compose does not publish Postgres or Redis on the host, so a backend run this way needs its own instances: point `DATABASE_URL` and `REDIS_URL` at them.

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
- **Inspecting Postgres or Redis**: compose does not publish their ports on the host. Open a shell inside the containers instead: `docker compose exec db psql -U postgres polymarket` or `docker compose exec redis redis-cli`.
- **Local inference connection error**: Ensure the `text-gen-cpp` container is healthy and reachable at `http://localhost:8080` from the host or `http://text-gen-cpp:8080` in Docker. It answers `/health` with 503 until the model has loaded; `docker compose logs text-gen-cpp` shows load errors. If it reports a bad model file, run `docker compose down`, remove the `ollama_downloads` volume (`docker volume ls` shows its full name) and start again so `setup_model` downloads the model afresh.
- **Unexpected model fallback**: `lfm-40b` goes to Ollama only when `OLLAMA_HOST` is set; compose sets it empty, so it runs on the local llama.cpp model.
- **Gemini auth error**: Check `GEMINI_API_KEY` in `.env`, or leave it empty to run the critic on the local model.
