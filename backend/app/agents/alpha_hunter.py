from typing import Any, Dict
from app.agents.base import BaseAgent
from app.connectors.binance import BinanceConnector

class AlphaHunterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Alpha-Hunter", role="Technical Analyst")
        self.binance_connector = BinanceConnector()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "BUSY"
        self.current_task = f"Scanning for alpha in {input_data.get('query')}"
        self.log(f"Starting technical scan for: {input_data.get('query')}")

        try:
            # Simulate scanning for crypto alpha
            symbol = "BTCUSDT"
            # Use the new get_price method
            price = await self.binance_connector.get_price(symbol)
            
            self.log(f"Technical data for {symbol} retrieved: ${price}", level="SUCCESS")
            
            # price is already a float from get_price
            signal = "BULLISH" if price > 90000 else "NEUTRAL" # Simple logic check
            
            self.status = "COMPLETED"
            return {
                "agent": self.name,
                "signal": signal,
                "asset": symbol,
                "price": price,
                "timestamp": self.logs[-1]["timestamp"]
            }
        except Exception as e:
            self.status = "ERROR"
            self.log(f"Technical scan failed: {str(e)}", level="ERROR")
            return {"error": str(e)}
