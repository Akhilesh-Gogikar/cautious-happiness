import asyncio
import time
import logging
import difflib
from typing import List, Dict, Any
from app.connectors.kalshi import KalshiClient
from py_clob_client.client import ClobClient
from app.models import ArbitrageOpportunity
import os

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    def __init__(self):
        self.kalshi = KalshiClient()
        self.poly_api_url = "https://clob.polymarket.com"
        # Public access usually doesn't need keys for market data
        self.poly = ClobClient(self.poly_api_url, chain_id=137)

    async def find_opportunities(self, min_discrepancy: float = 0.02) -> List[ArbitrageOpportunity]:
        """
        Fetches markets from both exchanges and finds price discrepancies using fuzzy matching.
        """
        logger.info("Starting arbitrage detection...")
        
        # 1. Fetch data in parallel
        try:
            kalshi_task = self.kalshi.get_active_markets(limit=200)
            # AlphaSignals get_markets is blocked but we can use our wrapper or just the client
            # The client's get_markets is not async, so we run it in a thread if needed,
            # but for simplicity here we just call it.
            
            # Since Kalshi is async, we await it.
            kalshi_markets_raw = await kalshi_task
            
            # AlphaSignals (blocking call, but we can wrap it)
            def fetch_poly():
                return self.poly.get_markets().get('data', [])
            
            loop = asyncio.get_event_loop()
            poly_markets_raw = await loop.run_in_executor(None, fetch_poly)
            
        except Exception as e:
            logger.error(f"Error during data collection: {e}")
            return []

        # 2. Normalize data formats
        kalshi_markets = [self.kalshi.extract_market_info(m) for m in kalshi_markets_raw]
        poly_markets = []
        for m in poly_markets_raw:
            if m.get('active') and m.get('tokens'):
                yes_token = next((t for t in m['tokens'] if t['outcome'] == 'Yes'), None)
                if yes_token:
                    poly_markets.append({
                        "id": m.get('condition_id'),
                        "question": m.get('question'),
                        "yes_price": float(yes_token.get('price', 0))
                    })

        logger.info(f"Comparing {len(kalshi_markets)} Kalshi markets with {len(poly_markets)} AlphaSignals markets.")

        # 3. Match and compare
        opportunities = []
        for km in kalshi_markets:
            if not km['question']: continue
            
            best_match = None
            best_ratio = 0.0
            
            # Optimized matching: filter candidates by simple keyword if too many
            for pm in poly_markets:
                if not pm['question']: continue
                
                # SequenceMatcher is slow, so we do a quick check first
                if any(word in pm['question'].lower() for word in km['question'].lower().split()[:3]):
                    ratio = difflib.SequenceMatcher(None, km['question'].lower(), pm['question'].lower()).ratio()
                    if ratio > 0.75 and ratio > best_ratio:
                        best_ratio = ratio
                        best_match = pm
            
            if best_match:
                poly_price = best_match['yes_price']
                kalshi_price = km['yes_price']
                
                if poly_price > 0 and kalshi_price > 0:
                    discrepancy = abs(poly_price - kalshi_price)
                    
                    if discrepancy >= min_discrepancy:
                        logger.info(f"Found opportunity: {km['question']} (Poly: {poly_price}, Kalshi: {kalshi_price})")
                        opportunities.append(ArbitrageOpportunity(
                            market_name=km['question'],
                            polymarket_id=best_match['id'],
                            polymarket_price=poly_price,
                            kalshi_id=km['id'],
                            kalshi_price=kalshi_price,
                            discrepancy=round(discrepancy, 4),
                            timestamp=time.time()
                        ))
        
        # Sort by highest discrepancy
        opportunities.sort(key=lambda x: x.discrepancy, reverse=True)
        return opportunities
