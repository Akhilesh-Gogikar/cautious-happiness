import asyncio
import logging
from dotenv import load_dotenv
from app.models import ForecastResult, ChatRequest
from app.domain.intelligence.service import IntelligenceService
from app.domain.intelligence.critic import CriticService

load_dotenv()
logger = logging.getLogger("alpha_insights.engine")


class FallbackModelOrchestrator:
    def __init__(self, primary="lfm-thinking", secondaries=None):
        if secondaries is None:
            secondaries = ["lfm-40b"]
        self.tiers = [primary] + secondaries

    async def run_with_fallback(self, func, *args, **kwargs):
        last_error = None
        total_models = len(self.tiers)
        for attempt_index, model in enumerate(self.tiers, start=1):
            try:
                kwargs["model"] = model
                timeout = 300 if model == self.tiers[0] else 30

                logger.info(
                    "Fallback model attempt started",
                    extra={
                        "event": "fallback_attempt_started",
                        "model": model,
                        "timeout_seconds": timeout,
                        "attempt": attempt_index,
                        "total_models": total_models,
                    },
                )
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)

            except asyncio.TimeoutError:
                last_error = Exception(f"Model {model} timed out")
                logger.warning(
                    "Fallback model attempt timed out",
                    extra={
                        "event": "fallback_attempt_timed_out",
                        "model": model,
                        "timeout_seconds": timeout,
                        "attempt": attempt_index,
                        "total_models": total_models,
                    },
                )
                continue
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Fallback model attempt failed",
                    extra={
                        "event": "fallback_attempt_failed",
                        "model": model,
                        "timeout_seconds": timeout,
                        "attempt": attempt_index,
                        "total_models": total_models,
                        "error": str(exc),
                    },
                    exc_info=True,
                )
                continue

        logger.error(
            "All fallback models failed",
            extra={
                "event": "fallback_exhausted",
                "total_models": total_models,
                "final_error": str(last_error) if last_error else None,
            },
        )
        raise last_error


class IntelligenceMirrorEngine:
    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.critic_service = CriticService()
        self.orchestrator = FallbackModelOrchestrator()

    async def close(self):
        """Close underlying services."""
        await self.intelligence_service.close()

    async def run_analysis(self, question: str, model: str = "lfm-thinking", status_callback=None) -> ForecastResult:
        """
        Run the full speculative pipeline:
        1. Multi-source Search
        2. Parallel (Forecast + Source Audit + Semantic Correlation)
        3. Synthesis
        """
        try:
            if status_callback:
                await status_callback("Searching news and physical signals...")

            async with asyncio.TaskGroup() as tg:
                news_task = tg.create_task(self.intelligence_service.search_market_news(question))
                physical_task = tg.create_task(self.intelligence_service.search_physical_data(question))

            sources_news = news_task.result()
            sources_physical = physical_task.result()
            all_sources = sources_news + sources_physical

            if status_callback:
                await status_callback("Generating forecast and auditing sources...")

            async with asyncio.TaskGroup() as tg:
                forecast_task = tg.create_task(
                    self.orchestrator.run_with_fallback(
                        self.intelligence_service.generate_forecast_with_reasoning,
                        question,
                        all_sources,
                    )
                )
                correlation_task = tg.create_task(
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

            audit_text = critic_result.critique
            adj_prob = critic_result.score

            if status_callback:
                await status_callback("Analysis complete.")

            return ForecastResult.from_analysis(
                question=question,
                all_sources=all_sources,
                avg_score=avg_score,
                critique=audit_text,
                adj_prob=adj_prob,
                reasoning=reasoning,
                analysis=analysis,
                critue_data=critic_result,
            )
        except Exception as exc:
            logger.exception(
                "Engine analysis failed",
                extra={
                    "event": "engine_analysis_failed",
                    "question": question,
                    "requested_model": model,
                    "error": str(exc),
                },
            )
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
        """
        Chat with the model about a specific forecast context.
        Delegates to IntelligenceService with fallback orchestration.
        """
        return await self.orchestrator.run_with_fallback(
            self.intelligence_service.chat_with_model,
            req,
        )
