import asyncio
import os
import argparse
import logging
import sys

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.market_client import RealMarketClient, MockMarketClient
from app.market_maker import MarketMaker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("market_maker_cli")

async def main():
    parser = argparse.ArgumentParser(description="Run Market Maker")
    parser.add_argument("--market_id", type=str, required=True, help="Token ID to trade")
    parser.add_argument("--spread", type=float, default=0.04, help="Spread width (e.g. 0.04 for +/- 0.02)")
    parser.add_argument("--size", type=float, default=10.0, help="Size in shares per quote")
    parser.add_argument("--mock", action="store_true", help="Use Mock Client (default: Real if env vars set)")
    
    args = parser.parse_args()
    
    # Determine Client
    if args.mock or not os.getenv("POLYMARKET_API_KEY"):
        logger.info("Using Mock Market Client")
        client = MockMarketClient()
    else:
        logger.info("Using Real Market Client")
        client = RealMarketClient(
            os.getenv("POLYMARKET_API_KEY"), 
            os.getenv("POLYMARKET_SECRET", ""), 
            os.getenv("POLYMARKET_PASSPHRASE", "")
        )
        
    mm = MarketMaker(client, args.market_id, spread=args.spread, size_shares=args.size)
    
    try:
        await mm.start()
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt detected.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await mm.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
