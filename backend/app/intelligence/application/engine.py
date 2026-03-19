from __future__ import annotations

import asyncio

from app.models import ChatRequest, ForecastResult
from app.intelligence.application.forecasting import IntelligenceService
from app.intelligence.domain.critic import CriticService


class FallbackModelOrchestrator:
    def __init__(self, primary: str = "lfm-thinking", secondaries: list[str] | None = None):
        self.tiers = [primary] + (secondaries or ["lfm-40b"])

    async def run_with_fallback(self, func, *args, **kwargs):
        last_error = None
        for model in self.tiers:
            try:
                kwargs["model"] = model
                timeout = 300 if model == self.tiers[0] else 30
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                last_error = Exception(f"Model {model} timed out")
                continue
            except Exception as exc:
                last_error = exc
                continue

        raise last_error


class IntelligenceMirrorEngine:
    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.critic_service = CriticService()
        self.orchestrator = FallbackModelOrchestrator()

    async def close(self):
        await self.intelligence_service.close()

    async def run_analysis(self, question: str, model: str = "lfm-thinking", status_callback=None) -> ForecastResult:
        try:
            if status_callback:
                await status_callback("Searching news and physical signals...")

            async with asyncio.TaskGroup() as task_group:
                news_task = task_group.create_task(self.intelligence_service.search_market_news(question))
                physical_task = task_group.create_task(self.intelligence_service.search_physical_data(question))

            all_sources = news_task.result() + physical_task.result()

            if status_callback:
                await status_callback("Generating forecast and auditing sources...")

            async with asyncio.TaskGroup() as task_group:
                forecast_task = task_group.create_task(
                    self.orchestrator.run_with_fallback(
                        self.intelligence_service.generate_forecast_with_reasoning,
                        question,
                        all_sources,
                    )
                )
                correlation_task = task_group.create_task(
                    self.intelligence_service.search_semantic_correlations(question)
                )

            avg_score, reasoning, analysis = forecast_task.result()
            correlations = correlation_task.result()
            if correlations:
                reasoning += f"\n\n**Secondary Correlations Discovered:**\n{correlations}"

            if status_callback:
                await status_callback("Running intelligence audit...")

            critic_result = await self.critic_service.critique_forecast(
                question,
                all_sources,
                avg_score,
                reasoning,
            )

            if status_callback:
                await status_callback("Analysis complete.")

            return ForecastResult.from_analysis(
                question=question,
                all_sources=all_sources,
                avg_score=avg_score,
                critique=critic_result.critique,
                adj_prob=critic_result.score,
                reasoning=reasoning,
                analysis=analysis,
                critue_data=critic_result,
            )
        except Exception as exc:
            return ForecastResult(
                search_query=question,
                news_summary=[],
                initial_forecast=0,
                critique="Error",
                adjusted_forecast=0,
                reasoning=str(exc),
                error="unknown_error",
            )

    async def chat_with_model(self, req: ChatRequest) -> str:
        return await self.orchestrator.run_with_fallback(self.intelligence_service.chat_with_model, req)
