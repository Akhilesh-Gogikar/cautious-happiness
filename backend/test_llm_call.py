import asyncio
from app.strategy.service import strategy_factory
from app.strategy.models import StrategyGenerationRequest

async def main():
    req = StrategyGenerationRequest(prompt="moving average crossover", model="lfm-40b")
    try:
        res = await strategy_factory.generate_strategy(req)
        print("Success:", res)
    except Exception as e:
        print("Exception:", e)

asyncio.run(main())
