# Alpha Insights Platform

> **Institutional-Grade Predictive Analytics & Competitive Intelligence**

The **Alpha Insights Platform** is a specialized research environment designed to provide hedge funds with a competitive edge in prediction markets and physical commodities trading. It mirrors the capabilities of algorithmic traders by leveraging a local, calibrated Large Language Model (**OpenForecaster**) for probability estimation and a verification agent (**Critic**) for hallucination control.

## For AI Agents

> [!IMPORTANT]
> **AI Contributors**: Please consult [docs/AGENTS.md](docs/AGENTS.md) before making changes. It contains specific instructions on repository structure, testing, and "Rules of Engagement".

## Core Capabilities

- **OpenForecaster Module**: A locally-hosted LLM tuned for probabilistic forecasting, allowing for privacy-preserving strategy generation.
- **The Critic (Risk Management)**: A secondary agent (Gemini-powered) that cross-references OpenForecaster's citations against a trusted whitelist to prevent hallucination-based trading.
- **Intelligence Mirror**: A competitive intelligence suite that reverse-engineers the "noise" and signals being fed to competitor algorithms, specifically for physical commodities markets.
- **Data Noir Terminal**: A high-performance, low-latency UI designed for data-dense visualization and rapid decision-making.

## System Architecture

The platform operates as a containerized microservices architecture:

- **Frontend**: Next.js + React (Data Noir Design System)
- **Backend**: FastAPI (Python) for orchestration and business logic
- **Inference Engine**: Ollama running strictly local models (e.g., Qwen 2.5) for OpenForecaster
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
    git clone <repo-url>
    cd alpha-insights
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
    Execute the startup script to initialize the environment and pull necessary models.
    ```bash
    ./run.sh
    ```
    > [!NOTE]
    > **Initial Setup**: The first launch will automatically download the `OpenForecaster` model (~5GB). This process may take 5-10 minutes. Review progress with `docker compose logs -f setup_model`.

### Access Points
- **Terminal Dashboard**: [http://localhost:3000](http://localhost:3000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Documentation Index

- **Start Here**: [Agent Instructions](docs/AGENTS.md)
- **Technical Deep Dive**: [Architecture](docs/ARCHITECTURE.md)
- **Strategic Vision**: [Vision & Roadmap](vision.md)
- **Design System**: [Style Guide](docs/style_guide.md)
- **Legal/IP**: [Patent Documentation](Patent.md)

## License
Proprietary & Confidential.
