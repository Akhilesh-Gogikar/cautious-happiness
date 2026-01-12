import asyncio
import json
import logging
import websockets
import time
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

class KalshiWS:
    """
    Kalshi WebSocket Client.
    """
    WS_URL = "wss://api.elections.kalshi.com/trade-api/ws/v2"

    def __init__(self, api_key: str, api_secret: str, on_message: Optional[Callable[[dict], None]] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.on_message_callback = on_message
        self.subscriptions: List[str] = [] # Tickers
        self.ws = None
        self.running = False

    async def connect(self):
        logger.info(f"Connecting to Kalshi WS: {self.WS_URL}")
        self.running = True
        try:
            async with websockets.connect(self.WS_URL) as ws:
                self.ws = ws
                logger.info("Connected to Kalshi WS")

                # TODO: Implement Auth Handshake if required immediately
                # For Kalshi, you often send auth frame first.
                
                # Resubscribe
                if self.subscriptions:
                    await self.subscribe(self.subscriptions)

                async for message in ws:
                    if not self.running: 
                        break
                    try:
                        data = json.loads(message)
                        if self.on_message_callback:
                            await self.on_message_callback(data)
                    except Exception as e:
                        logger.error(f"Error processing Kalshi message: {e}")

        except Exception as e:
            logger.error(f"Kalshi WS Connection Error: {e}")
            self.ws = None
            if self.running:
                logger.info("Reconnecting in 5s...")
                await asyncio.sleep(5)
                asyncio.create_task(self.connect())

    async def subscribe(self, tickers: List[str]):
        """
        Subscribe to markets (tickers).
        """
        self.subscriptions.extend(tickers)
        self.subscriptions = list(set(self.subscriptions))
        
        if self.ws:
            # Example Kalshi Subscription Protocol
            # { "id": 1, "cmd": "subscribe", "params": { "channels": ["ticker", "orderbook_delta"], "market_tickers": [...] } }
            payload = {
                "id": int(time.time()),
                "cmd": "subscribe",
                "params": {
                    "channels": ["orderbook_delta", "trade"],
                    "market_tickers": tickers
                }
            }
            await self.ws.send(json.dumps(payload))
            logger.info(f"Subscribed to Kalshi tickers: {len(tickers)}")

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()
