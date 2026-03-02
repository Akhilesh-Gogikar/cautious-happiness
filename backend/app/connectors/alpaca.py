import os
import logging
from typing import List, Dict, Any, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from .base import BaseConnector, ToolDefinition, ResourceDefinition

logger = logging.getLogger(__name__)

class AlpacaConnector(BaseConnector):
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.base_url = base_url or os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        self.client: Optional[TradingClient] = None

    async def connect(self):
        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca credentials missing. Connector will be inactive.")
            return
        
        try:
            # alpaca-py TradingClient is synchronous, but we'll use it within our async connector
            self.client = TradingClient(self.api_key, self.secret_key, paper=True if "paper" in self.base_url else False)
            logger.info("Alpaca connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")

    async def disconnect(self):
        self.client = None

    async def list_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_account",
                description="Fetch Alpaca account summary (balance, buying power, etc.)",
                input_schema={}
            ),
            ToolDefinition(
                name="list_positions",
                description="List all currently open positions",
                input_schema={}
            ),
            ToolDefinition(
                name="place_market_order",
                description="Place a market order for a given symbol and quantity",
                input_schema={
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "qty": {"type": "number"},
                        "side": {"type": "string", "enum": ["buy", "sell"]}
                    },
                    "required": ["symbol", "qty", "side"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if not self.client:
            raise Exception("Alpaca connector not connected.")

        if name == "get_account":
            account = self.client.get_account()
            return {
                "account_number": account.account_number,
                "equity": account.equity,
                "cash": account.cash,
                "buying_power": account.buying_power,
                "currency": account.currency
            }
        
        elif name == "list_positions":
            positions = self.client.get_all_positions()
            return [
                {
                    "symbol": p.symbol,
                    "qty": p.qty,
                    "avg_entry_price": p.avg_entry_price,
                    "current_price": p.current_price,
                    "unrealized_pl": p.unrealized_pl
                } for p in positions
            ]

        elif name == "place_market_order":
            symbol = arguments.get("symbol")
            qty = arguments.get("qty")
            side = OrderSide.BUY if arguments.get("side") == "buy" else OrderSide.SELL
            
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.GTC
            )
            order = self.client.submit_order(order_data)
            return {
                "id": str(order.id),
                "client_order_id": order.client_order_id,
                "status": str(order.status),
                "symbol": order.symbol,
                "qty": order.qty,
                "side": str(order.side)
            }
        
        raise ValueError(f"Tool {name} not found in AlpacaConnector")

    async def list_resources(self) -> List[ResourceDefinition]:
        return []

    async def read_resource(self, uri: str) -> str:
        raise NotImplementedError("AlpacaConnector does not support resources.")
