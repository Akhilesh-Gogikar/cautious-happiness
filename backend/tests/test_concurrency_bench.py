import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from app.engine import IntelligenceMirrorEngine
from app.models import Source

async def benchmark_concurrency():
    engine = IntelligenceMirrorEngine()
    
    # Mock services to simulate processing time
    async def slow_search(q):
        await asyncio.sleep(1)
        return [Source(title="News", snippet="Snippet", url="url")]
    
    async def slow_forecast(q, s, model):
        await asyncio.sleep(2)
        return (0.5, "Reasoning", {"analysis": "data"})
    
    async def slow_correlation(q, model="lfm-thinking"):
        await asyncio.sleep(2)
        return "Found correlations"
    
    async def slow_critic(q, s, sc, r):
        await asyncio.sleep(1)
        res = MagicMock()
        res.critique = "Audit done"
        res.score = 0.5
        return res

    engine.intelligence_service.search_market_news = AsyncMock(side_effect=slow_search)
    engine.intelligence_service.search_physical_data = AsyncMock(side_effect=slow_search)
    engine.intelligence_service.generate_forecast_with_reasoning = AsyncMock(side_effect=slow_forecast)
    engine.intelligence_service.search_semantic_correlations = AsyncMock(side_effect=slow_correlation)
    engine.critic_service.critique_forecast = AsyncMock(side_effect=slow_critic)

    print("Starting concurrent analysis...")
    start_time = time.perf_counter()
    
    result = await engine.run_analysis("Will oil hit $100?")
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    
    print(f"Total duration: {total_duration:.2f}s")
    
    # Expectations:
    # 1. Search: 1s (Parallel)
    # 2. Forecast (2s) + Correlations (2s) : 2s (Parallel)
    # 3. Critic: 1s (Sequential because it needs reasoning)
    # Total expected: ~1 + 2 + 1 = 4s
    # If sequential: 1 + 1 + 2 + 2 + 1 = 7s
    
    if total_duration < 5.0:
        print("SUCCESS: Concurrency verified. Pipeline took < 5s (Expected ~4s).")
    else:
        print(f"FAILURE: Pipeline took {total_duration:.2f}s, which suggests sequential execution (Expected < 5s).")

if __name__ == "__main__":
    asyncio.run(benchmark_concurrency())
