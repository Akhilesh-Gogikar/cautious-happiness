import asyncio

from app.core.ai_client import ai_client
from app.strategy.models import StrategyGenerationRequest, StrategyCode
from app.strategy.prompts import STRATEGY_GENERATION_PROMPT

# One bounded wait: the shared client retries for up to ~15 minutes, but behind
# nginx (proxy_read_timeout 330s) the caller must get the fallback before that.
LLM_TIMEOUT_SECONDS = 300


class StrategyFactory:
    async def generate_strategy(self, request: StrategyGenerationRequest) -> StrategyCode:
        prompt = STRATEGY_GENERATION_PROMPT.format(user_prompt=request.prompt)
        
        # Try LLM
        code = await self._call_llm(prompt, request.model)
        
        # Fallback Mock if LLM fails or returns empty
        if not code or "Error" in code:
             return self._get_mock_strategy(request.prompt)

        # Parse class name from code
        import re
        class_match = re.search(r"class\s+(\w+)\s*\(", code)
        strategy_name = class_match.group(1) if class_match else "GeneratedStrategy"

        return StrategyCode(
            name=strategy_name,
            code=code,
            description="AI Generated Strategy",
            logic_summary=request.prompt
        )

    async def _call_llm(self, prompt: str, model: str) -> str:
        try:
            # The local llama.cpp model, through the shared client (chat template,
            # thinking removed) instead of raw /completion.
            return await asyncio.wait_for(
                ai_client.generate(prompt, provider="llama-cpp", n_predict=1024),
                timeout=LLM_TIMEOUT_SECONDS,
            )
        except Exception as e:
            print(f"LLM Call Failed: {e}")
            return ""

    def _get_mock_strategy(self, prompt: str) -> StrategyCode:
        # Simple Mock for testing frontend integration
        code = """
import backtrader as bt

class MockStrategy(bt.Strategy):
    params = (('period', 15),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()
"""
        return StrategyCode(
            name="MockStrategy",
            code=code.strip(),
            description="Mock Moving Average Crossover",
            logic_summary=f"Mock response for: {prompt}"
        )

strategy_factory = StrategyFactory()
