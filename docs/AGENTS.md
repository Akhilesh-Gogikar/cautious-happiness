# Agentic Instruction Manual (AGENTS.md)

## Purpose / Context
**Attention AI Agent:** This file is your primary source of truth for understanding the **Alpha Insights Platform** repository. It outlines the repo structure, standard workflows, and "Rules of Engagement" to ensure your contributions align with the project's institutional standards.

> [!IMPORTANT]
> **Primary Directive**: This is a production-grade financial platform. Accuracy, privacy, and "Institutional" code quality are non-negotiable.

## 1. Repository Map

| Path | Description | Key Tech |
|------|-------------|----------|
| `/backend` | Core logic, API, and RAG engine. | FastAPI, Python 3.11+, LangChain |
| `/frontend` | User interface and data visualization. | Next.js 14, React, Tailwind |
| `/nginx` | Reverse proxy and SSL termination. | Nginx |
| `/docs` | Detailed documentation. | Markdown |
| `docker-compose.yml` | Orchardstration for all services. | Docker |

## 2. Standard Workflows

### A. Environment Setup
The system interacts with external APIs (Gemini, Polymarket). Ensure you verify the existence of `.env` before running the app.
- **Check**: `cat .env` (If missing, look for `.env.example`)

### B. Running the App
Always use the provided script which handles container orchestration.
```bash
./run.sh
```
*Note: The first run downloads large models (~5GB). Be patient.*

### C. Testing
- **Backend**: `pytest` is the standard.
  ```bash
  docker compose exec backend pytest
  ```
- **Frontend**: Currently relies on build checks.
  ```bash
  cd frontend && npm run build
  ```

## 3. Rules of Engagement

1.  **Strict Privacy**: never log, print, or output simulated trading strategies or "Alpha" to the console unless explicitly asked.
2.  **The "Critic" Pattern**: All generative features must include a verification step. If you add a new LLM feature, you MUST add a corresponding validator.
3.  **UI Aesthetics**: The "Data Noir" design system is strict.
    - Dark mode by default.
    - High contrast text (White/Grey).
    - No "toy" colors (bright pinks/greens) unless semantically meaningful (Profit/Loss).
4.  **No "Magic" Strings**: Use constants or config files for all system prompts and configuration values.

## 4. Common Tasks & Cheat Sheet

- **Restart Backend**: `docker compose restart backend`
- **View Logs**: `docker compose logs -f backend`
- **Rebuild Container**: `docker compose up -d --build <service_name>`

## 5. Related Documentation
- [Architecture Deep Dive](file:///root/cautious-happiness/docs/ARCHITECTURE.md) *(Note: check if moved)*
- [Style Guide](file:///root/cautious-happiness/docs/style_guide.md)
- [Backend Documentation](file:///root/cautious-happiness/docs/backend.md)
- [Frontend Documentation](file:///root/cautious-happiness/docs/frontend.md)
