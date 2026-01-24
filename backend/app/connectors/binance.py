import httpx
import logging
from typing import List
from app.connectors.base import DataSource
from app.models import Source

logger = logging.getLogger(__name__)

class BinanceConnector(DataSource):
    """
    Fetches real-time crypto prices from Binance Public API (ticker/24hr).
    """
    @property
    def name(self) -> str:
        return "Binance"

    async def fetch_data(self, query: str) -> List[Source]:
        """
        Fetches 24hr ticker data for major pairs.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Common pairs
                symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
                
                sources = []
                for symbol in symbols:
                    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    price = float(data.get("lastPrice", 0))
                    change = float(data.get("priceChangePercent", 0))
                    
                    sources.append(Source(
                        title=f"{symbol} (Binance)",
                        url=f"https://www.binance.com/en/trade/{symbol}",
                        snippet=f"Price: ${price:,.2f} ({'+' if change >= 0 else ''}{change:.2f}% 24h)"
                    ))
                
                return sources
            except Exception as e:
                logger.error(f"Error fetching data from Binance: {e}")
                return []

    async def get_price(self, symbol: str) -> float:
        """
        Directly fetch price for a symbol.
        """
        async with httpx.AsyncClient() as client:
            try:
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return float(data.get("lastPrice", 0))
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
                return 0.0
