
import logging
from typing import List, Dict, Any
from app.db.session import AsyncSessionLocal
from app.db.models import PolymarketMarket, PolymarketOrderbook, MarketInsight
from sqlalchemy.future import select
from sqlalchemy import desc
from app.core.ai_client import ai_client

logger = logging.getLogger(__name__)

class InsightAgent:
    def __init__(self):
        pass

    async def generate_insights(self):
        logger.info("Generating market insights...")
        async with AsyncSessionLocal() as session:
            # Fetch active markets
            stmt = select(PolymarketMarket).where(PolymarketMarket.status == "open")
            result = await session.execute(stmt)
            markets = result.scalars().all()
            
            for market in markets:
                # Fetch recent orderbook entries
                stmt = select(PolymarketOrderbook).where(PolymarketOrderbook.market_id == market.id).order_by(desc(PolymarketOrderbook.timestamp)).limit(10)
                result = await session.execute(stmt)
                entries = result.scalars().all()
                
                if not entries:
                    continue
                
                # Analyze spreads and Basis (Put-Call Parity)
                # In Polymarket, P(Yes) + P(No) should be 1. 
                # If we only have Yes token mid-price, we can check its volatility.
                # If we had both, we'd check for deviations (Basis).
                
                # Prepare data for LLM
                obs_data = [
                    {"timestamp": e.timestamp.isoformat(), "mid_price": e.mid_price, "spread": e.spread}
                    for e in entries
                ]
                
                prompt = f"""
                Analyze the following Polymarket data for the market: "{market.question}"
                
                Data (Recent 10 snapshots):
                {obs_data}
                
                Calculate:
                1. Spread movement and its implications for liquidity.
                2. Predicted market movement based on asset pricing theory (e.g., if spread tightens while price rises, it suggests strong buy conviction).
                3. Market "Basis" benefit: How far is the current price from the theoretical parity (if applicable).
                
                Provide an investment thesis with specific reasoning.
                """
                
                insight_content = await ai_client.generate(prompt)
                
                insight = MarketInsight(
                    market_id=market.id,
                    insight_type="prediction",
                    content=insight_content,
                    raw_data={"observations": obs_data}
                )
                session.add(insight)
            
            await session.commit()
            logger.info("Insight generation complete.")
