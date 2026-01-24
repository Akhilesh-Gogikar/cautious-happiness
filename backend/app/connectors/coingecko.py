import httpx
import logging
from typing import List
from app.connectors.base import DataSource
from app.models import Source

logger = logging.getLogger(__name__)

class CoinGeckoConnector(DataSource):
    """
    Fetches real-time crypto market data from CoinGecko Public API.
    """
    @property
    def name(self) -> str:
        return "CoinGecko"

    async def fetch_data(self, query: str) -> List[Source]:
        """
        Fetches price info for major assets related to the query.
        For now, defaults to BTC, ETH, SOL for global context if query is generic.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Map common keywords to CoinGecko IDs
                asset_map = {
                    "btc": "bitcoin",
                    "eth": "ethereum",
                    "sol": "solana",
                    "crypto": "bitcoin,ethereum,solana",
                    "bitcoin": "bitcoin",
                    "ethereum": "ethereum",
                    "solana": "solana"
                }
                
                ids = asset_map.get(query.lower(), "bitcoin,ethereum,solana")
                
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    "ids": ids,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true"
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                sources = []
                for asset_id, prices in data.items():
                    price = prices.get("usd")
                    change = prices.get("usd_24h_change", 0)
                    sources.append(Source(
                        title=f"{asset_id.upper()} Market Price",
                        url=f"https://www.coingecko.com/en/coins/{asset_id}",
                        snippet=f"Current Price: ${price:,.2f} ({'+' if change >= 0 else ''}{change:.2f}% 24h)"
                    ))
                
                return sources
            except Exception as e:
                logger.error(f"Error fetching data from CoinGecko: {e}")
                return []
