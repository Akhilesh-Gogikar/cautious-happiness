import os
import httpx
from app.strategy.models import StrategyGenerationRequest, StrategyCode
from app.strategy.prompts import STRATEGY_GENERATION_PROMPT

class StrategyFactory:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.llama_cpp_host = os.getenv("LLAMA_CPP_HOST", "http://llama-cpp:8080")

    async def generate_strategy(self, request: StrategyGenerationRequest) -> StrategyCode:
        prompt = STRATEGY_GENERATION_PROMPT.format(user_prompt=request.prompt)
        
        # Try LLM
        code = await self._call_llm(prompt, request.model)
        
        # Fallback Mock if LLM fails or returns empty
        if not code or "Error" in code:
             return self._get_mock_strategy(request.prompt)

        return StrategyCode(
            name="GeneratedStrategy", # TODO: Parse class name from code
            code=code,
            description="AI Generated Strategy",
            logic_summary=request.prompt
        )

    async def _call_llm(self, prompt: str, model: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                # Use Llama.cpp if requested specifically
                if model == "lfm-thinking" or model == "lfm-40b":
                    url = f"{self.llama_cpp_host}/completion"
                    payload = {
                        "prompt": prompt,
                        "n_predict": 1024,
                        "temperature": 0.2,
                        "stop": ["[/INST]"]
                    }
                    response = await client.post(url, json=payload, timeout=60.0)
                    if response.status_code == 200:
                         return response.json().get('content', '')
                
                # Default to Ollama
                url = f"{self.ollama_host}/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2}
                }
                response = await client.post(url, json=payload, timeout=60.0)
                if response.status_code == 200:
                    return response.json().get('response', '')
            except Exception as e:
                print(f"LLM Call Failed: {e}")
                return ""
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
