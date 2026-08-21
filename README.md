# Alpha Insights Platform

> Research dashboard for testing prediction-market and commodities intelligence workflows with local-model forecasting and a review loop.

The **Alpha Insights Platform** is a containerized FastAPI and Next.js project for builders evaluating how market questions move through forecasting, source gathering, task status tracking, and critique. It is useful for exploring architecture and product direction before hardening the system for trading or production use.

## For AI Agents

> [!IMPORTANT]
> **AI Contributors**: Please consult [docs/AGENTS.md](docs/AGENTS.md) before making changes. It contains specific instructions on repository structure, testing, and "Rules of Engagement".

## Core Capabilities

- **Local forecasting path**: `POST /prediction/predict` queues market questions through Celery and the default compose stack routes model calls to the local `text-gen-cpp` / llama.cpp-compatible service.
- **Critic review loop**: The Critic agent scores stored market insights and records written critique text for follow-up analysis.
- **Intelligence APIs**: The backend exposes market, news, mirror, scanner, strategy, trade, chat, and tool routes for experimenting with research workflows.
- **Data-dense UI**: The Next.js dashboard gives visitors a frontend surface for the backend workflows and product framing.

## Runtime Reality Check

The repository historically used names such as **OpenForecaster**, **Ollama**, and **Qwen 2.5** in docs and model setup notes. The current checked-in runtime is different:

- **Inference container**: `text-gen-cpp` in `docker-compose.yml`, exposed internally via `LLAMA_CPP_HOST=http://text-gen-cpp:8080`.
- **Default local model**: `lfm-thinking`, downloaded by `backend/setup_model.sh` into the shared model volume.
- **Alias behavior in code**: Some backend paths still accept `openforecaster` as a request alias, but normalize it to `lfm-thinking`.
- **Fallback note**: `lfm-40b` still appears as a secondary fallback identifier in code, but it is **not** provisioned by the default compose stack.

If you are onboarding or automating this repo, treat `text-gen-cpp` + `lfm-thinking` as the source of truth for the default local inference path.

## System Architecture

The platform operates as a containerized microservices architecture:

- **Frontend**: Next.js + React (Data Noir Design System)
- **Backend**: FastAPI (Python) for orchestration and business logic
- **Inference Engine**: `text-gen-cpp` (llama.cpp-compatible HTTP service) for the default local model path
- **Verification Layer**: Google Gemini API for the Critic agent
- **Data Layer**: PostgreSQL (Persistence) + Redis (Cache/Queue)

For a detailed technical breakdown, please refer to [Architecture Deep Dive](docs/ARCHITECTURE.md).

## Quick Start

### Prerequisites
- **Docker & Docker Compose**: Essential for container orchestration.
- **Gemini API Key**: Required for the **Critic** agent's verification capabilities.

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Akhilesh-Gogikar/cautious-happiness.git
    cd cautious-happiness
    ```

2.  **Configuration**
    The system creates a `.env` file on first run. You must populate it with your credentials.
    ```bash
    # Required for 'Critic' verification agent
    GEMINI_API_KEY=your_key_here
    
    # Optional: Polymarket execution
    POLYMARKET_API_KEY=...
    POLYMARKET_SECRET=...
    POLYMARKET_PASSPHRASE=...
    ```

3.  **Launch System**
    Execute the startup script to initialize the environment and pull the default local model.
    ```bash
    ./run.sh
    ```
    > [!NOTE]
    > **Initial Setup**: The first launch downloads the default `lfm-thinking` GGUF model (roughly 1-5 GB depending on the selected artifact and cache state). Review progress with `docker compose logs -f setup_model`.

### Access Points
- **Terminal Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Current Maturity Snapshot

The repository already demonstrates a credible control plane: the core FastAPI/Next.js stack exists, the forecasting + critique pipeline is wired, and the product direction is documented in the backlog and vision artifacts. At the same time, several moat-defining capabilities are still explicitly tracked as unfinished work, so the platform should be presented as a strong foundation rather than a fully locked-down execution engine.

### What is already working
- **Control plane foundations**: containerized backend/frontend architecture, local-model orchestration, and prediction workflow scaffolding.
- **Verification pattern**: a dedicated Critic layer exists as a first-class concept in both the architecture and codebase.
- **Product discipline**: roadmap, backlog, and strategic artifacts already identify the highest-value next steps.

### What still needs to be locked down
- **Critic hardening**: verification reliability and structured output enforcement remain active work items.
- **Structured parsing**: the roadmap still calls for replacing brittle parsing paths with schema-driven extraction.
- **Live frontend state sync**: portions of the UI still need to move from mock or isolated state to live backend-backed synchronization.
- **Async orchestration refactor**: concurrency/orchestration improvements are still part of the implementation roadmap.
- **Unified intelligence domain cleanup**: intelligence logic consolidation remains a key maintainability and moat-protection task.

This framing is intentional: the repo shows strong direction and meaningful implementation progress, while the backlog honestly documents the remaining engineering needed to fully harden the defensibility-critical mechanics.

## Documentation Index

- **Start Here**: [Agent Instructions](docs/AGENTS.md)
- **Technical Deep Dive**: [Architecture](docs/ARCHITECTURE.md)
- **Backend Service**: [Backend Docs](docs/backend.md)
- **Frontend Service**: [Frontend Docs](docs/frontend.md)
- **Design System**: [Style Guide](docs/style_guide.md)
- **Product Framing**: [Product Framework](docs/PRODUCT_FRAMEWORK.md)
- **Execution Plan**: [YC-Style Product Development Plan](docs/YC_PRODUCT_DEVELOPMENT_PLAN.md)
- **Strategic Vision**: [Vision & Roadmap](vision.md)
- **Legal/IP**: [Patent Documentation](Patent.md)

## License
Proprietary & Confidential.
