# Setup Cautious Happiness Webapp with LLM

Run the `cautious-happiness` webapp with integrated LLM (Ollama).

## User Review Required
> [!IMPORTANT]
> **Docker Installation**: Docker is not installed on this system. I will attempt to install it. If I lack permissions, I will need you to install Docker manually.

> [!NOTE]
> **Gemini API Key**: The "Critic" agent requires a Gemini API key. I will use a placeholder or empty string initially. If you have one, please provide it in the `.env` file after setup.

## Proposed Changes

### System
- Install `docker.io` and `docker-compose-v2` (or equivalent).

### Configuration
- Create `.env` from `.env.example`.
- Configure `OLLAMA_HOST` if needed (defaults should work).

### Execution
- Run `./run.sh` to start services.
- This script will:
    - Build containers.
    - Download `OpenForecaster-8B` model (~5GB).
    - Start Backend, Frontend, Worker, DB, Redis, and Ollama.

## Verification Plan

### Automated Tests
- Check if containers are running: `docker compose ps`
- Check logs for successful startup: `docker compose logs`
- Curl the backend API: `curl http://localhost:8000/docs`

### Manual Verification
- Browsing to `http://localhost:3000` (User will need to port forward or use browser tool if available, but the browser tool runs on the agent side, so I can verify navigation).
