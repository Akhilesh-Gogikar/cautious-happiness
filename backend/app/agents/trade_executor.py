from typing import Any, Dict
from app.agents.base import BaseAgent
from app.market_client import MockMarketClient
from app.execution import SlippageAwareKelly

class TradeExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Trade-Executor", role="Execution Specialist")
        self.market_client = MockMarketClient()
        self.execution_algo = SlippageAwareKelly(bankroll=1000.0)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "BUSY"
        query = input_data.get("query", "")
        probability = input_data.get("probability", 0.5)
        self.current_task = f"Optimizing execution for {query} (p={probability})"
        self.log(f"Starting execution optimization for: {query}")

        try:
            market_id = input_data.get("market_id", "test_market_123")
            order_book = self.market_client.get_order_book(market_id)
            
            size_usd, shares, vwap = self.execution_algo.optimal_allocation(probability, order_book)
            
            self.log(f"Execution plan: ${size_usd:.2f} @ avg {vwap:.3f}", level="SUCCESS")
            
            self.status = "COMPLETED"
            return {
                "agent": self.name,
                "size_usd": size_usd,
                "shares": shares,
                "vwap": vwap,
                "status": "READY" if size_usd > 0 else "NO_TRADE",
                "timestamp": self.logs[-1]["timestamp"]
            }
        except Exception as e:
            self.status = "ERROR"
            self.log(f"Execution optimization failed: {str(e)}", level="ERROR")
            return {"error": str(e)}
