
import asyncio
import logging
from datetime import datetime
from typing import List
from app.connectors.polymarket import PolymarketConnector
from app.db.session import AsyncSessionLocal
from app.db.models import PolymarketMarket, PolymarketOrderbook
from sqlalchemy.future import select

logger = logging.getLogger(__name__)

class ScrapingAgent:
    def __init__(self, connector: PolymarketConnector):
        self.connector = connector
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("ScrapingAgent started.")
        while self.is_running:
            try:
                await self.scrape_active_markets()
                # Poll every 5 minutes for new data
                await asyncio.sleep(300) 
            except Exception as e:
                logger.error(f"Error in ScrapingAgent: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        self.is_running = False
        logger.info("ScrapingAgent stopped.")

    async def scrape_active_markets(self):
        logger.info("Fetching active markets from Polymarket...")
        markets_data = await self.connector.call_tool("polymarket_get_markets", {"limit": 50, "active": True})
        
        async with AsyncSessionLocal() as session:
            for m_data in markets_data:
                # Update or Create Market
                condition_id = m_data.get("conditionId")
                if not condition_id:
                    continue
                
                stmt = select(PolymarketMarket).where(PolymarketMarket.condition_id == condition_id)
                result = await session.execute(stmt)
                db_market = result.scalar_one_or_none()
                
                if not db_market:
                    db_market = PolymarketMarket(
                        condition_id=condition_id,
                        question=m_data.get("question"),
                        description=m_data.get("description"),
                        status="open",
                        category=m_data.get("category"),
                        end_date=datetime.fromisoformat(m_data.get("endDate").replace("Z", "+00:00")) if m_data.get("endDate") else None
                    )
                    session.add(db_market)
                    await session.flush() # Ensure db_market has an ID
                
                # Fetch Orderbook for high-volume or specific markers?
                # For this demo, we fetch for all active ones we just found.
                try:
                    # In Polymarket, "Yes" and "No" tokens have different IDs. 
                    # We usually care about the "Yes" token for probability.
                    # This is a simplification.
                    token_id = m_data.get("tokens", [{}])[0].get("token_id")
                    if token_id:
                        book_data = await self.connector.call_tool("polymarket_get_orderbook", {"token_id": token_id})
                        
                        bids = book_data.get("bids", [])
                        asks = book_data.get("asks", [])
                        
                        best_bid = float(bids[0].get("price", 0)) if bids else 0
                        best_ask = float(asks[0].get("price", 0)) if asks else 0
                        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else (best_bid or best_ask)
                        spread = best_ask - best_bid if best_bid and best_ask else 0
                        
                        orderbook_entry = PolymarketOrderbook(
                            market_id=db_market.id,
                            bids=bids,
                            asks=asks,
                            mid_price=mid_price,
                            spread=spread
                        )
                        session.add(orderbook_entry)
                except Exception as e:
                    logger.error(f"Error fetching orderbook for market {condition_id}: {e}")
            
            await session.commit()
            logger.info("Scraping cycle complete.")
