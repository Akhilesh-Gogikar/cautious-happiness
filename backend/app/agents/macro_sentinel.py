from typing import Any, Dict
from app.agents.base import BaseAgent
from app.connectors.yahoofinance import YahooFinanceConnector

class MacroSentinelAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Macro-Sentinel", role="Economist")
        self.yf_connector = YahooFinanceConnector()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "BUSY"
        self.current_task = f"Analyzing macro indicators for {input_data.get('query')}"
        self.log(f"Starting macro analysis for: {input_data.get('query')}")

        try:
            # In a real scenario, we'd fetch specific macro tickers
            # For now, let's simulate fetching key indices
            indices = ["^GSPC", "^IXIC", "^DJI"]
            macro_data = {}
            for ticker in indices:
                price = await self.yf_connector.get_price(ticker)
                macro_data[ticker] = {"price": price}

            self.log("Macro data fetched successfully", level="SUCCESS")
            
            # Simple heuristic analysis
            summary = "Global indices show stable momentum." if macro_data.get("^GSPC", {}).get("price", 0) > 0 else "Market volatility detected."
            
            self.status = "COMPLETED"
            return {
                "agent": self.name,
                "summary": summary,
                "indices": macro_data,
                "timestamp": self.logs[-1]["timestamp"]
            }
        except Exception as e:
            self.status = "ERROR"
            self.log(f"Macro analysis failed: {str(e)}", level="ERROR")
            return {"error": str(e)}
