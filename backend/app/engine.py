import os
import json
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from app.models import Source, ForecastResult, ChatRequest, ChatResponse
from app.services.intelligence import IntelligenceService
from app.services.critic import CriticService

load_dotenv()

class IntelligenceMirrorEngine:
    def __init__(self):
        self.intelligence_service = IntelligenceService()
        self.critic_service = CriticService()

    async def run_analysis(self, question: str, model: str = "lfm-thinking") -> ForecastResult:
        """
        Run the full pipeline: Search -> Forecast (w/ Reasoning) -> Critique.
        """
        try:
            # 1. Search Logic
            sources = self.intelligence_service.search_market_news(question)
            
            # 2. Forecast Logic
            init_prob, reasoning = await self.intelligence_service.generate_forecast_with_reasoning(question, sources, model=model)
            
            # If forecast failed specifically due to model missing
            if "model 'openforecaster' not found" in reasoning:
                 return ForecastResult(
                    search_query=question,
                    news_summary=sources,
                    initial_forecast=0.0,
                    critique="N/A",
                    adjusted_forecast=0.0,
                    reasoning=None,
                    error="model_missing"
                )

            # 3. Critique Logic
            critique, adj_prob = await self.critic_service.critique_forecast(question, sources, init_prob, reasoning)
            
            return ForecastResult(
                search_query=question,
                news_summary=sources,
                initial_forecast=init_prob,
                critique=critique,
                adjusted_forecast=adj_prob,
                reasoning=reasoning
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
