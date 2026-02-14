# Architecture Deep Dive

## Purpose / Context
This document details the technical implementation of the Alpha Insights Platform. It explains how the "Brain" (FastAPI RAG) and "Terminal" (Next.js UI) interact to deliver institutional-grade predictive analytics.

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
        Worker -->|Generation Request| Ollama[OpenForecaster (Local LLM)]
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

### 2. OpenForecaster (The Analyst)
- **Technology**: Ollama (hosting Qwen 2.5 or Llama 3)
- **Role**: **Strictly Local Inference**.
- **Privacy**: No strategy data leaves the local environment during the generation phase.
- **Task**: Ingests unstructured context and outputs a probabilistic forecast (0.00 - 1.00) with confidence intervals.

### 3. The Critic (Risk Manager)
- **Technology**: Google Gemini API
- **Role**: Hallucination Firewall.
- **Function**: Receives the *claims* made by OpenForecaster and cross-references them against a trusted whitelist of data sources. If a claim cannot be verified, the trade is vetoed.

### 4. Intelligence Mirror
- **Technology**: Custom Scrapers + NLP
- **Role**: Competitive counter-intelligence.
- **Function**: analyzes the "information diet" of competitor algorithms to predict crowd-sided trades in physical commodities.

### 5. The Terminal (Frontend)
- **Technology**: Next.js, Tailwind CSS, Reown (WalletConnect)
- **Role**: Human-in-the-loop control interface.
- **Design Philosophy**: "Data Noir" – High contrast, information-dense, focusing on readability and speed.
- **Reference**: [Frontend Docs](frontend.md)

## Infrastructure

The entire stack is containerized via Docker Compose for consistent deployment across development and production environments.

- **Networking**: Internal `poly_net` bridge network isolates database and internal APIs.
- **Proxy**: Nginx acts as the reverse proxy, handling SSL termination and routing.