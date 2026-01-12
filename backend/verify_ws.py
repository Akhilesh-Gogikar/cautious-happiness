import asyncio
import logging
from app.websockets.manager import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ws_verifier")

async def verify_websockets():
    logger.info("Starting Websocket Verification...")
    
    # 1. Start Manager
    await manager.start()
    
    # Allow connection time
    await asyncio.sleep(5)
    
    # 2. Check AlphaSignals Connection
    if manager.polymarket_client.ws:
        logger.info("PASS: AlphaSignals WS is connected.")
    else:
        logger.error("FAIL: AlphaSignals WS failed to connect.")

    # 3. Check Kalshi (if credentials present)
    if manager.kalshi_client:
        if manager.kalshi_client.ws:
            logger.info("PASS: Kalshi WS is connected.")
        else:
            logger.error("FAIL: Kalshi WS failed to connect.")
    else:
        logger.info("SKIP: Kalshi WS skipped (no credentials).")

    # 4. Cleanup
    await manager.stop()
    logger.info("Verification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_websockets())
