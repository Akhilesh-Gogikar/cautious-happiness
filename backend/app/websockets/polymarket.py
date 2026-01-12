import asyncio
import json
import logging
import websockets
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

class AlphaSignalsWS:
    """
    AlphaSignals WebSocket Client for CLOB data.
    """
    WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

    def __init__(self, on_message: Optional[Callable[[dict], None]] = None):
        self.on_message_callback = on_message
        self.subscriptions: List[str] = []
        self.ws = None
        self.running = False
        self._lock = asyncio.Lock()

    async def connect(self):
        """Establish connection to the websocket"""
        logger.info(f"Connecting to AlphaSignals WS: {self.WS_URL}")
        self.running = True
        try:
            async with websockets.connect(self.WS_URL) as ws:
                self.ws = ws
                logger.info("Connected to AlphaSignals WS")
                
                # Resubscribe if we had previous subs
                if self.subscriptions:
                    await self._send_subscription(self.subscriptions)

                async for message in ws:
                    if not self.running:
                        break
                    try:
                        data = json.loads(message)
                        if self.on_message_callback:
                            await self.on_message_callback(data)
                        else:
                            # Default logging if no callback
                            # logger.debug(f"Poly Msg: {data}")
                            pass
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode Poly message: {message}")
                    except Exception as e:
                        logger.error(f"Error processing Poly message: {e}")

        except Exception as e:
            logger.error(f"AlphaSignals WS Connection Error: {e}")
            self.ws = None
            if self.running:
                logger.info("Reconnecting in 5s...")
                await asyncio.sleep(5)
                asyncio.create_task(self.connect())

    async def subscribe(self, asset_ids: List[str]):
        """
        Subscribe to orderbook/trades for specific asset IDs (token_ids).
        AlphaSignals channels typically ask for assets.
        """
        # CLOB usage: 
        # {
        #     "assets_ids": ["..."],
        #     "type": "market" 
        # }
        # Note: Check documentation for exact "subscribe" payload structure.
        # Based on research, it's often implicit or explicit subscribe message.
        # Here we assume standard subscription pattern.
        
        self.subscriptions.extend(asset_ids)
        self.subscriptions = list(set(self.subscriptions)) # Unique
        
        if self.ws:
            await self._send_subscription(asset_ids)

    async def _send_subscription(self, asset_ids: List[str]):
        if not self.ws:
            return
            
        payload = {
            "assets_ids": asset_ids,
            "type": "market"
        }
        await self.ws.send(json.dumps(payload))
        logger.info(f"Subscribed to AlphaSignals assets: {len(asset_ids)}")

    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()
