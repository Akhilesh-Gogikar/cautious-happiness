from typing import Dict, Any, List
from app.services.kelly import SlippageAwareKellyEngine

class ExecutionService:
    def __init__(self):
        self.kelly_engine = SlippageAwareKellyEngine()

    async def construct_trade_payload(
        self, 
        provider: str = "polymarket",
        probability_score: float = 0.5,
        order_book: List[Dict[str, float]] = None,
        bankroll: float = 1000.0
    ) -> Dict[str, Any]:
        """
        Constructs a transaction payload for the frontend to sign or execute.
        Now includes optimal sizing via the Slippage-Aware Kelly Engine.
        """
        # Default order book if none provided (for demo/fallback)
        if not order_book:
            order_book = [
                {"price": 0.80, "size": 100},
                {"price": 0.82, "size": 200},
                {"price": 0.85, "size": 500}
            ]

        # Calculate optimal size
        sizing_result = self.kelly_engine.calculate_optimal_size(
            model_probability=probability_score,
            order_book=order_book,
            bankroll=bankroll
        )

        if provider == "alpaca":
            return {
                "status": "alpaca_ready",
                "message": f"Alpaca trade triggered for {sizing_result['optimal_size']} units.",
                "provider": "alpaca",
                "sizing": sizing_result
            }

        return {
            "status": "ready_to_sign",
            "provider": "polymarket",
            "sizing": sizing_result,
            "tx_payload": {
                "to": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E", # Polymarket CTF Exchange
                "data": "0x095ea7b3000000000000000000000000...", # Mock Hex data
                "value": str(int(sizing_result['optimal_size'] * 10**6)), # USDC Decimals
                "chainId": 137 # Polygon
            }
        }
