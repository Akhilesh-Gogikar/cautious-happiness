# Backend Service Documentation

## Purpose / Context
The Backend service is the "Central Nervous System" of the Alpha Insights Platform. It orchestrates the RAG pipeline between the local LLM (OpenForecaster), the external verification agent (Critic), and the database.

## 1. Key Technologies
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Task Queue**: Celery + Redis
- **LLM Engine**: LangChain + Ollama

## 2. Directory Structure

```
backend/
├── app/
│   ├── api/            # Route controllers (Versioned, e.g., v1/)
│   ├── core/           # Config, Security, Events
│   ├── db/             # Database models and migrations
│   ├── services/       # Business logic (The "Meat")
│   │   ├── intelligence.py  # RAG Logic
│   │   ├── critic.py        # Gemini Verification
│   │   └── execution.py     # Trade routing
│   └── main.py         # Entry point
├── tests/              # Pytest suite
└── requirements.txt
```

## 3. Core Logic Flows

### A. The Prediction Pipeline
1.  **Trigger**: User requests analysis or Cron job.
2.  **Orchestration**: `services.intelligence.generate_forecast()`
3.  **Step 1 (Generate)**: Call Ollama (Local) -> Get probability (0.00-1.00).
4.  **Step 2 (Verify)**: Pass result to `services.critic.verify_claim()` (Gemini).
5.  **Result**: If verified, save to DB. If rejected, discard.

### B. "The Critic" Verification
- **Input**: A claim string + Citations.
- **Process**: Gemini checks trusted whitelist (Reuters, AP, Claims).
- **Outcome**: `True` (Verified) or `False` (Hallucination).

## 4. Development Guide

### Running Locally (Without Docker)
> [!WARNING]
> We recommend Docker, but for rapid debug:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Adding a New Route
1.  Create route handler in `app/api/v1/endpoints/`.
2.  Register in `app/api/v1/router.py`.
3.  Add strict Pydantic models for Request/Response.

## 5. Troubleshooting
- **Ollama Connection Error**: Ensure Ollama container is healthy (`http://localhost:11434`).
- **Gemini Auth Error**: Check `GEMINI_API_KEY` in `.env`.
