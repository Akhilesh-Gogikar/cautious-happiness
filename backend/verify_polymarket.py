
import asyncio
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))
# Or just use the root for app imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.agents.orchestrator import AgentOrchestrator
from app.core.ai_client import ai_client
from unittest.mock import AsyncMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock the AI client for verification
ai_client.generate = AsyncMock(return_value="Insight: Polymarket spread is tightening. Put-Call parity suggests a 2% basis benefit. Predicted movement: Up. Score: 0.85")

async def main():
    orchestrator = AgentOrchestrator()
    
    logger.info("Starting Polymarket Pipeline Verification...")
    result = await orchestrator.run_polymarket_pipeline()
    logger.info(f"Pipeline Result: {result}")
    
    # Check if data was actually stored (optional check here if we wanted to query DB)
    logger.info("Verification complete.")

if __name__ == "__main__":
    asyncio.run(main())
