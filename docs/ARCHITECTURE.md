# Architecture Deep Dive

## Purpose / Context
This document details the technical implementation of the Alpha Insights Platform. It explains how the "Brain" (FastAPI RAG) and "Terminal" (Next.js UI) interact to deliver institutional-grade predictive analytics.

## Runtime Baseline

Before reading the component breakdown, anchor on the current checked-in runtime:

- The default local inference service in `docker-compose.yml` is **`text-gen-cpp`**, not an Ollama container.
- The default local model identifier used across the frontend and backend is **`lfm-thinking`**.
- The string **`openforecaster`** still exists in some request paths as a compatibility alias and is normalized to `lfm-thinking` at runtime.
- The fallback identifier **`lfm-40b`** remains in code as a secondary tier, but the default compose stack does not provision that model.

## Component Diagram

```mermaid
graph TD
    User[Trader / Risk Manager] -->|Interact| UI[Frontend Terminal (Next.js)]
    UI -->|API Requests| API[Backend Engine (FastAPI)]
    
    subgraph "Core Logic"
        API -->|Task Queue| Worker[Celery Worker]
        API -->|Cache/PubSub| Redis
        API -->|Persistence| DB[(PostgreSQL)]
    end
    
    subgraph "Intelligence Layer"
        Worker -->|Generation Request| LlamaCpp[text-gen-cpp / llama.cpp-compatible service]
        Worker -->|Verification Request| Gemini[The Critic (Gemini API)]
    end

    subgraph "External World"
        Worker -->|Market Data| Poly[Polymarket API]
        Worker -->|News/Sentiment| Tools[Search/Scraper Tools]
    end
```

## Service Descriptions

### 1. The Brain (Backend & RAG Engine)
- **Technology**: Python FastAPI
- **Role**: Central nervous system. Orchestrates data ingestion, strategy generation, and trade execution.
- **Key Function**: Manages the lifecycle of a "Prediction Event" from discovery to execution.
- **Reference**: [Backend Docs](backend.md)

### 2. Local Forecasting Engine
- **Technology**: `text-gen-cpp` / llama.cpp-compatible HTTP service
- **Role**: **Strictly local inference by default**.
- **Privacy**: No strategy data leaves the local environment during the generation phase when the local model path is used.
- **Task**: Ingests unstructured context and outputs probabilistic reasoning.
- **Naming note**: "OpenForecaster" is still used in some docs and request aliases, but contributors should treat `lfm-thinking` on `text-gen-cpp` as the active default runtime.

### 3. The Critic (Risk Manager)
- **Technology**: Google Gemini API
- **Role**: Hallucination firewall.
- **Function**: Receives the claims made by the local forecaster and cross-references them against a trusted whitelist of data sources. If a claim cannot be verified, the trade is vetoed.

### 4. Intelligence Mirror
- **Technology**: Custom scrapers + NLP
- **Role**: Competitive counter-intelligence.
- **Function**: Analyzes the "information diet" of competitor algorithms to predict crowd-sided trades in physical commodities.

### 5. The Terminal (Frontend)
- **Technology**: Next.js, Tailwind CSS, Reown (WalletConnect)
- **Role**: Human-in-the-loop control interface.
- **Design Philosophy**: "Data Noir" – high contrast, information-dense, focusing on readability and speed.
- **Reference**: [Frontend Docs](frontend.md)

## Infrastructure

The entire stack is containerized via Docker Compose for consistent deployment across development and production environments.

- **Networking**: Internal `alphainsights-net` bridge network isolates database and internal APIs.
- **Proxy**: Nginx acts as the reverse proxy, handling SSL termination and routing.
- **Model bootstrap**: `setup_model` downloads the default GGUF artifact before the local inference container starts.
