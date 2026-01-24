import httpx
import logging
import re
from typing import List
from app.connectors.base import DataSource
from app.models import Source

logger = logging.getLogger(__name__)

class YahooFinanceConnector(DataSource):
    """
    Fetches market data from Yahoo Finance using public query API.
    """
    @property
    def name(self) -> str:
        return "Yahoo Finance"

    async def fetch_data(self, query: str) -> List[Source]:
        """
        Fetches basic market indicators using the chart endpoint which is often more stable.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Common tickers: S&P 500 (^GSPC), Gold (GC=F), DXY (DX-Y.NYB)
                tickers = ["%5EGSPC", "GC%3DF", "DX-Y.NYB"]
                
                sources = []
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
                }

                for ticker in tickers:
                    try:
                        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
                        response = await client.get(url, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            result = data.get("chart", {}).get("result", [{}])[0]
                            meta = result.get("meta", {})
                            price = meta.get("regularMarketPrice")
                            prev_close = meta.get("previousClose")
                            
                            if price and prev_close:
                                change = ((price - prev_close) / prev_close) * 100
                                name = ticker.replace("%5E", "").replace("%3DF", "")
                                sources.append(Source(
                                    title=f"{name} Index",
                                    url=f"https://finance.yahoo.com/quote/{ticker}",
                                    snippet=f"Level: {price:,.2f} ({'+' if change >= 0 else ''}{change:.2f}%)"
                                ))
                    except Exception as inner_e:
                        logger.warning(f"Failed to fetch {ticker}: {inner_e}")

                # Fallback if Yahoo is entirely down
                if not sources:
                    sources.append(Source(
                        title="Macro Market Indicators",
                        url="https://finance.yahoo.com",
                        snippet="Global macro indicators are currently fluctuating. Check external terminals for real-time depth."
                    ))

                return sources
                return sources
            except Exception as e:
                logger.error(f"Error fetching data from Yahoo Finance: {e}")
                return []

    async def get_price(self, ticker: str) -> float:
        """
        Directly fetch price for a symbol.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Yahoo tickers often need encoding if they have ^
                encoded_ticker = ticker.replace("^", "%5E")
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_ticker}?interval=1d&range=1d"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
                }
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("chart", {}).get("result", [{}])[0]
                    meta = result.get("meta", {})
                    return float(meta.get("regularMarketPrice", 0))
                return 0.0
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")
                return 0.0
