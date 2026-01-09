# Hedge Fund Dashboard 🚀

A Bloomberg-terminal style predictive analytics dashboard for Polymarket, powered by generic AI Agents.

## Stack
- **Frontend**: Next.js, Tailwind, Glassmorphism UI
- **Backend**: FastAPI, Celery, Redis
- **AI**: Ollama (OpenForecaster), Gemini (Critic)
- **Infrastructure**: Docker Compose

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Gemini API Key for "Critic" functionality

### 1. Clone & Setup
```bash
git clone <repo-url>
cd hedge-fund
```

### 2. Launch
The startup script handles configuration and model downloading automatically.

```bash
./run.sh
```

**First Run Notice**: The system will automatically download the `OpenForecaster-8B` model (~5GB). This may take 5-10 minutes depending on your connection. Check logs with `docker compose logs -f setup_model`.

### 3. Access
- **Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## ⚙️ Configuration
The first run creates a `.env` file from `.env.example`. Edit this file to add API keys:

```bash
# Required for "Critic" agent
GEMINI_API_KEY=your_key_here

# Optional: Real Trading on Polymarket
POLYMARKET_API_KEY=...
POLYMARKET_SECRET=...
POLYMARKET_PASSPHRASE=...
```

## 🏗️ Architecture
- `backend/`: FastAPI + Celery workers.
- `frontend/`: Next.js dashboard.
- `docker-compose.yml`: Orchestrates the stack including Ollama sidecars.
