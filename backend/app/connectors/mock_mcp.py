
from typing import List, Dict, Any
from app.connectors.base import BaseConnector, ToolDefinition, ResourceDefinition
import asyncio

class MockMCPConnector(BaseConnector):
    def __init__(self, name: str = "Mock Financial Data"):
        self.name = name
        self.connected = False

    async def connect(self):
        # Simulate connection delay
        await asyncio.sleep(0.5)
        self.connected = True
        print(f"[{self.name}] Connected via Mock MCP Protocol.")

    async def disconnect(self):
        self.connected = False
        print(f"[{self.name}] Disconnected.")

    async def list_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="get_stock_price",
                description="Get the current price of a stock ticker",
                input_schema={
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock symbol (e.g. AAPL)"}
                    },
                    "required": ["ticker"]
                }
            ),
            ToolDefinition(
                name="get_fed_rate",
                description="Get the current Federal Reserve Interest Rate",
                input_schema={"type": "object", "properties": {}}
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if not self.connected:
            raise ConnectionError("Not connected")
        
        await asyncio.sleep(1.0) # Simulate network lag

        if name == "get_stock_price":
            ticker = arguments.get("ticker", "UNKNOWN")
            # Mock data
            prices = {"AAPL": 150.0, "GOOGL": 2800.0, "TSLA": 700.0}
            return {"price": prices.get(ticker, 100.0), "currency": "USD"}
        
        if name == "get_fed_rate":
            return {"rate": 5.25, "unit": "percent"}

        raise ValueError(f"Tool {name} not found")

    async def list_resources(self) -> List[ResourceDefinition]:
        return [
            ResourceDefinition(uri="mcp://finance/market_summary", name="Daily Market Summary"),
            ResourceDefinition(uri="mcp://finance/watch_list", name="User Watch List")
        ]

    async def read_resource(self, uri: str) -> str:
        if uri == "mcp://finance/market_summary":
            return "Market is bullish. Tech sector leading gains."
        return "Resource not found."
