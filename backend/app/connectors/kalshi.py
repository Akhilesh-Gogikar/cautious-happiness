import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class KalshiClient:
    def __init__(self):
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"

    async def get_active_markets(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetches active markets from Kalshi.
        """
        async with httpx.AsyncClient() as client:
            try:
                # status=open filtering
                params = {"status": "open", "limit": limit}
                response = await client.get(f"{self.base_url}/markets", params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("markets", [])
            except Exception as e:
                logger.error(f"Error fetching Kalshi markets: {e}")
                return []

    def extract_market_info(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplifies Kalshi market data for comparison.
        """
        return {
            "id": market.get("ticker"),
            "question": market.get("title"),
            "yes_price": (market.get("yes_ask", 0) / 100.0) if market.get("yes_ask") else 0.0,
            "no_price": (market.get("no_ask", 0) / 100.0) if market.get("no_ask") else 0.0,
            "close_time": market.get("close_time"),
        }
