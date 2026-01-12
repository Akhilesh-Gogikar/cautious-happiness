import asyncio
import logging
import os
from typing import Dict, Optional
from app.websockets.polymarket import AlphaSignalsWS
from app.websockets.kalshi import KalshiWS
from app.models import OrderBook, OrderBookLevel

logger = logging.getLogger(__name__)

class WebsocketManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebsocketManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        self.initialized = True
        self.live_orderbooks: Dict[str, OrderBook] = {} # market_id -> OrderBook
        self.polymarket_client = AlphaSignalsWS(on_message=self._on_poly_message)
        
        # Check for Kalshi keys
        kalshi_key = os.getenv("KALSHI_API_KEY")
        kalshi_secret = os.getenv("KALSHI_API_SECRET")
        if kalshi_key and kalshi_secret:
            self.kalshi_client = KalshiWS(kalshi_key, kalshi_secret, on_message=self._on_kalshi_message)
        else:
            self.kalshi_client = None
            logger.warning("Kalshi API credentials missing. WS disabled.")

    async def start(self):
        """Start all websocket connections"""
        asyncio.create_task(self.polymarket_client.connect())
        if self.kalshi_client:
            asyncio.create_task(self.kalshi_client.connect())

    async def stop(self):
        await self.polymarket_client.stop()
        if self.kalshi_client:
            await self.kalshi_client.stop()

    async def subscribe_market(self, market_id: str, platform: str = "polymarket"):
        """
        Subscribe to a market to start tracking it live.
        """
        if platform.lower() == "polymarket":
            await self.polymarket_client.subscribe([market_id])
        elif platform.lower() == "kalshi" and self.kalshi_client:
            await self.kalshi_client.subscribe([market_id])

    def get_live_book(self, market_id: str) -> Optional[OrderBook]:
        """
        Get the current in-memory order book for a market.
        Returns None if no live data available (caller should fall back to REST/Mock).
        """
        return self.live_orderbooks.get(market_id)

    async def _on_poly_message(self, data: dict):
        """
        Handle AlphaSignals WS messages.
        Update local orderbook state.
        """
        # Note: Parsing logic depends on exact CLOB message format.
        # This is a simplified handler.
        # Structure often: [ { "event_type": "book", "market": "...", "bids": [], "asks": [] } ]
        
        try:
            # AlphaSignals often sends a list of updates
            if isinstance(data, list):
                for item in data:
                    self._process_poly_item(item)
            elif isinstance(data, dict):
                self._process_poly_item(data)
                
        except Exception as e:
            logger.error(f"Error handling poly msg: {e}")

    def _process_poly_item(self, item: dict):
        # Identify market
        event_type = item.get("event_type")
        market_id = item.get("asset_id") or item.get("market")
        
        if not market_id:
            return

        if event_type == "book": # Snapshot or Update
            # Parse bids/asks
            bids = [OrderBookLevel(price=float(x['price']), amount=float(x['size'])) for x in item.get('bids', [])]
            asks = [OrderBookLevel(price=float(x['price']), amount=float(x['size'])) for x in item.get('asks', [])]
            
            # Update State (Snapshot replace for simplicity, delta merge is better for prod)
            self.live_orderbooks[market_id] = OrderBook(bids=bids, asks=asks)
            
        elif event_type == "price_change" or event_type == "trade":
             # Update last price tracking if we had it
             pass

    async def _on_kalshi_message(self, data: dict):
        # Kalshi logic
        # type: orderbook_snapshot or orderbook_delta
        msg_type = data.get("type")
        market_ticker = data.get("market_ticker") # or sid
        
        if msg_type == "orderbook_snapshot" and market_ticker:
             bids = [OrderBookLevel(price=float(x[0]), amount=float(x[1])) for x in data.get('msg', {}).get('bids', [])]
             asks = [OrderBookLevel(price=float(x[0]), amount=float(x[1])) for x in data.get('msg', {}).get('asks', [])]
             self.live_orderbooks[market_ticker] = OrderBook(bids=bids, asks=asks)

# Global Instance
manager = WebsocketManager()
