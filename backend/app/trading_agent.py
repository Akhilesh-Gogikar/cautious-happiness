import logging
import time
from typing import List, Optional
from app.market_client import MarketClient
from app.execution import SlippageAwareKelly
from app.models import TradeSignal, ForecastResult, OrderBook
from app.engine import ForecasterCriticEngine

logger = logging.getLogger(__name__)

class TradingAgent:
    def __init__(self, market_client: MarketClient, engine: ForecasterCriticEngine):
        self.market_client = market_client
        self.engine = engine
        self.kelly = SlippageAwareKelly(bankroll=10000.0) # Default bankroll, should be configurable
        self.mode = "HUMAN_REVIEW" # or "FULL_AI"
        self.signal_queue: List[TradeSignal] = []

    def set_mode(self, mode: str):
        if mode not in ["HUMAN_REVIEW", "FULL_AI"]:
            raise ValueError("Invalid mode")
        self.mode = mode
        logger.info(f"Trading Mode set to: {self.mode}")

    def update_bankroll(self, amount: float):
        self.kelly.bankroll = amount

    async def analyze_and_propose(self, market_id: str, question: str) -> Optional[TradeSignal]:
        """
        Full pipeline: Forecast -> Kelly -> Signal
        """
        logger.info(f"Analyzing market: {question}")
        
        # 1. Forecast
        # We need a way to call the async engine. Assuming engine methods are async.
        # The engine usually takes a ChatRequest or just string. 
        # Let's use the public helper from main `engine.run_forecast_flow` if available 
        # or call agents directly. The `ForecasterCriticEngine` in `engine.py` has `run_main_flow`.
        
        # We'll assume strict YES/NO market for now.
        
        # Hack: The engine implementation in `engine.py` might need to be called carefully. 
        # Let's assume we can use the `run_forecast_task` (celery) logic or call engine directly.
        # Start simple: trigger engine.
        
        # Note: In a real app, this is heavy.
        result_text = await self.engine.run_main_flow(question) 
        # We need to parse this text to get a number. 
        # This is the tricky part of "Text to Float".
        # For now, let's assume the engine output contains "Confidence: X%"
        
        import re
        match = re.search(r"Confidence:\s*(\d+)%", result_text)
        confidence = 0.5
        if match:
            confidence = float(match.group(1)) / 100.0
        
        # Direction?
        # If text says "Prediction: YES", prob = confidence
        # If "Prediction: NO", prob = 1 - confidence
        
        is_yes = "Prediction: YES" in result_text
        if not is_yes and "Prediction: NO" not in result_text:
            logger.warning("Agent could not determine direction. Skipping.")
            return None
            
        prob_yes = confidence if is_yes else (1.0 - confidence)
        
        # 2. Market Data
        try:
            order_book = self.market_client.get_order_book(market_id)
        except NotImplementedError:
             logger.warning("Market data source not ready.")
             return None
        
        # 3. Execution Logic (Kelly)
        # We are buying YES tokens.
        # If we think NO, we buy NO tokens? Or Sell Yes? 
        # The exchange splits YES/NO. Buying NO is buying NO token.
        # Our `SlippageAwareKelly` assumes we are buying an asset.
        
        target_token_prob = prob_yes if is_yes else (1.0 - prob_yes)
        # We need the order book for the token we want to buy.
        # `get_order_book` needs to know WHICH token.
        # Simplified: `market_client` returns orderbook for YES token by default?
        # We need to extend `market_client` to handle TokenID.
        
        # For prototype: Assume we only buy YES for now. 
        if not is_yes:
            logger.info("Shorting/Buying NO not yet fully implemented in auto-execution. Skipping.")
            return None
            
        size_usd, shares, vwap = self.kelly.optimal_allocation(target_token_prob, order_book)
        
        if size_usd <= 0:
            logger.info(f"No positive expected value found (Prob: {prob_yes}, VWAP: {vwap}).")
            return None
            
        signal = TradeSignal(
            market_id=market_id,
            market_question=question,
            signal_side="BUY_YES",
            price_estimate=vwap,
            kelly_size_usd=size_usd,
            expected_value=size_usd * (target_token_prob / vwap - 1), # Simple EV approx
            rationale=f"Model confidence {prob_yes:.2f} > Price {vwap:.2f}. {result_text[:100]}...",
            timestamp=time.time()
        )
        
        # 4. Act
        if self.mode == "FULL_AI":
            await self.execute_signal(signal)
        else:
            self.signal_queue.append(signal)
            logger.info("Signal added to review queue.")
            
        return signal

    async def execute_signal(self, signal: TradeSignal):
        logger.info(f"EXECUTING Trade {signal.market_id}: ${signal.kelly_size_usd}")
        success = self.market_client.place_order(signal.market_id, signal.kelly_size_usd, "BUY")
        if success:
            signal.status = "EXECUTED"
            signal.tx_hash = "0xMOCKED_HASH" 
        else:
            signal.status = "FAILED"

    def get_queue(self):
        return self.signal_queue

    def approve_signal(self, signal_index: int):
        if 0 <= signal_index < len(self.signal_queue):
            signal = self.signal_queue[signal_index]
            # In async context we'd await, but this might be called from synchronous endpoint 
            # so we might need a background task or careful handling. 
            # For MVP, we'll mark it pending execution or execute if we can.
            
            # Since we are in a class that might be run by FastAPI, we might need to be async.
            # We'll set status APPROVED and let a worker pick it up, or execute immediately if we can.
            
            # Hack: execute sync for now (mocked client is sync-ish or fast)
            # Real client needs async.
            
            # self.execute_signal(signal) -> needs await.
            # We'll just set flag.
            signal.status = "APPROVED" 
            return True
        return False
