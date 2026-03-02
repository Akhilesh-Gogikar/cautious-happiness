
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

        import time
        import math
        current_time = time.time()

        if name == "get_stock_price":
            ticker = arguments.get("ticker", "UNKNOWN")
            
            # Dynamic mock data
            base_prices = {"AAPL": 150.0, "GOOGL": 2800.0, "TSLA": 700.0}
            base = base_prices.get(ticker, 100.0)
            
            # Create a unique phase shift for the ticker
            seed = float(hash(ticker) % 1000) / 1000.0
            
            # Simulate a continuous price movement based on time
            # Fast flutter (minutes) + slow trend (hours)
            flutter = math.sin((current_time / 60.0) + (seed * math.pi * 2)) * 0.02
            trend = math.cos((current_time / 3600.0) + (seed * math.pi * 2)) * 0.05
            
            current_price = base * (1.0 + flutter + trend)
            
            return {"price": round(current_price, 2), "currency": "USD"}
        
        if name == "get_fed_rate":
            # Realistically fed rates change slowly, so we'll simulate a very slow cycle 
            # over a period of many days, starting from a base 5.25%
            cycle = math.sin(current_time / (86400.0 * 30.0)) * 0.75 # +/- 0.75% over months
            current_rate = 5.25 + cycle
            return {"rate": round(current_rate, 2), "unit": "percent"}

        raise ValueError(f"Tool {name} not found")

    async def list_resources(self) -> List[ResourceDefinition]:
        return [
            ResourceDefinition(uri="mcp://finance/market_summary", name="Daily Market Summary"),
            ResourceDefinition(uri="mcp://finance/watch_list", name="User Watch List")
        ]

    async def read_resource(self, uri: str) -> str:
        if uri == "mcp://finance/market_summary":
            import time
            import math
            current_time = time.time()
            sentiment = math.sin(current_time / 3600.0)
            
            if sentiment > 0.5:
                return "Market is strongly bullish today. Tech sector and energy leading gains."
            elif sentiment > -0.5:
                return "Market is trading sideways with mixed signals across sectors."
            else:
                return "Market is bearish. Yields are rising and tech stocks are selling off."
            
        return "Resource not found."
