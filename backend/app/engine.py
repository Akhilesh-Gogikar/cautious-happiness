import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from app.models import Source, ForecastResult, ChatRequest, ChatResponse
from app.domain.intelligence.service import IntelligenceService
from app.domain.intelligence.critic import CriticService

load_dotenv()

class FallbackModelOrchestrator:
    def __init__(self, primary="lfm-thinking", secondaries=["lfm-40b"]):
        self.tiers = [primary] + secondaries

    async def run_with_fallback(self, func, *args, **kwargs):
        last_error = None
        for model in self.tiers:
            try:
                kwargs['model'] = model
                # Implement dynamic timeout per tier: 
                # Primary (Thinking) gets more time, secondaries are faster.
                timeout = 60 if model == self.tiers[0] else 30
                
                print(f"Neural Resilience: Attempting with {model} (timeout={timeout}s)...")
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                
            except asyncio.TimeoutError:
                print(f"Fallback: Model {model} timed out after {timeout}s.")
                last_error = Exception(f"Model {model} timed out")
                continue
            except Exception as e:
                print(f"Fallback: Model {model} failed with: {e}")
                last_error = e
                continue
        
        print("Neural Resilience: All models failed. Escalating to system error.")
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
            # 1. Concurrent Data Gathering
            if status_callback: await status_callback("Searching news and physical signals...")
            
            async with asyncio.TaskGroup() as tg:
                news_task = tg.create_task(self.intelligence_service.search_market_news(question))
                physical_task = tg.create_task(self.intelligence_service.search_physical_data(question))
            
            sources_news = news_task.result()
            sources_physical = physical_task.result()
            all_sources = sources_news + sources_physical
            
            # 2. Speculative/Concurrent Forecast & Audit
            # We run forecast, semantic correlations, and a "pre-audit" of sources in parallel.
            if status_callback: await status_callback("Generating forecast and auditing sources...")
            
            async with asyncio.TaskGroup() as tg:
                # Primary pole: Generating the actual forecast
                forecast_task = tg.create_task(
                    self.orchestrator.run_with_fallback(
                        self.intelligence_service.generate_forecast_with_reasoning,
                        question, 
                        all_sources
                    )
                )
                
                # Speculative pole 1: Semantic Correlation search (Hidden edge discovery)
                correlation_task = tg.create_task(
                    self.intelligence_service.search_semantic_correlations(question)
                )

            # Extract forecast results
            avg_score, reasoning, analysis = forecast_task.result()
            correlations = correlation_task.result()
            
            # Append correlations to reasoning if found
            if correlations:
                reasoning += f"\n\n**Secondary Correlations Discovered:**\n{correlations}"

            # 3. Intelligence Audit (Critic)
            # This requires the reasoning, so it follows the forecast but can be overlapping with UI updates.
            if status_callback: await status_callback("Running intelligence audit...")

            critic_result = await self.critic_service.critique_forecast(
                question, 
                all_sources, 
                avg_score, 
                reasoning
            )
            
            audit_text = critic_result.critique
            adj_prob = critic_result.score
            
            if status_callback: await status_callback("Analysis complete.")
            
            return ForecastResult.from_analysis(
                question=question,
                all_sources=all_sources,
                avg_score=avg_score,
                critique=audit_text,
                adj_prob=adj_prob,
                reasoning=reasoning,
                analysis=analysis,
                critue_data=critic_result
            )
        except Exception as e:
            print(f"Engine Error: {e}")
            return ForecastResult(
                search_query=question,
                news_summary=[],
                initial_forecast=0,
                critique="Error",
                adjusted_forecast=0,
                reasoning=str(e),
                error="unknown_error"
            )

    async def chat_with_model(self, req: ChatRequest) -> str:
        """
        Chat with the model about a specific forecast context.
        Delegates to IntelligenceService.
        """
        return await self.intelligence_service.chat_with_model(req)
