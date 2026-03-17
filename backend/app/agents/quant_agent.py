import logging
import json
from types import SimpleNamespace
from app.domain.intelligence.service import IntelligenceService
from app.agents.news_agent import NewsAgent
from app.connectors.polymarket import PolymarketConnector
from app.db.session import async_session
from sqlalchemy.future import select
from app.db.models import PolymarketMarket, PolymarketOrderbook

logger = logging.getLogger("quant_agent")

class QuantAgent:
    def __init__(self, polymarket_connector: PolymarketConnector, news_agent: NewsAgent):
        self.polymarket = polymarket_connector
        self.news_agent = news_agent
        self.intelligence_service = IntelligenceService()

    async def generate_trade_suggestions(self, target_scenario: str) -> dict:
        """
        Synthesize RAG context from NewsAgent and Polymarket predictions to generate multi-timeframe trade recommendations.
        Uses Liquid AI multi-concurrency llama.cpp backend via `IntelligenceService`.
        """
        logger.info(f"QuantAgent analyzing scenario: {target_scenario}")
        
        # 1. Retrieve RAG Context
        news_context = await self.news_agent.retrieve_context(target_scenario, limit=10)
        
        # 2. Retrieve related Polymarket contextual data (e.g., active geopolitics markets)
        polymarket_context = ""
        async with async_session() as session:
            stmt = select(PolymarketMarket).where(PolymarketMarket.status == "open").limit(5)
            result = await session.execute(stmt)
            markets = result.scalars().all()
            for m in markets:
                polymarket_context += f"- Market: {m.question} (Category: {m.category})\n"

        # 3. Formulate the LLM Prompt
        system_prompt = """
        You are a highly sophisticated Quant Trade Recommendations Agent.
        Your task is to analyze global macro events and prediction market odds to output structural 
        trade recommendations spread across different asset classes and time horizons.
        
        You MUST return your output as a pure JSON object corresponding to this exact structure:
        {
          "scenario_analysis": "A brief 2-3 sentence analysis of the current scenario based on the provided context.",
          "timeframes": {
            "week": [{"asset_class": "commodities", "trade": "Buy Oil Futures", "reasoning": "Immediate supply shock"}],
            "month": [{"asset_class": "equities", "trade": "Short Airlines", "reasoning": "Prolonged higher fuel costs"}],
            "quarter": [{"asset_class": "crypto", "trade": "Long BTC", "reasoning": "Flight to non-sovereign assets as instability rises"}],
            "half_year": [{"asset_class": "fixed_income", "trade": "Short long-duration bonds", "reasoning": "Inflationary pressures from supply constraints"}],
            "year": [{"asset_class": "equities", "trade": "Long Defense Contractors", "reasoning": "Structurally higher defense spending"}]
          }
        }
        
        Output ONLY the valid JSON, NO markdown wrappers, NO extra text.
        """
        
        # We explicitly supply context into the prompt
        user_prompt = f"""
        Target Scenario: {target_scenario}
        
        News & RAG Context:
        {news_context if news_context else "No direct news context found in DB."}
        
        Polymarket Active Markets:
        {polymarket_context if polymarket_context else "No active Polymarket data found."}
        
        Generate the trade recommendations based on this data.
        """

        # 4. Invoke LLM via `lfm-thinking` using the message-aware IntelligenceService path.
        req = SimpleNamespace(
            messages=[
                SimpleNamespace(role="system", content=system_prompt),
                SimpleNamespace(role="user", content=user_prompt)
            ],
            model="lfm-thinking"
        )
        
        try:
            raw_response = await self.intelligence_service.chat_with_model(req)
            # Try to parse the JSON output
            # Clean possible markdown formatting
            if raw_response.startswith("```json"):
                raw_response = raw_response.replace("```json", "", 1)
            if raw_response.endswith("```"):
                raw_response = raw_response[:raw_response.rfind("```")]
            
            trade_data = json.loads(raw_response.strip())
            return trade_data
        except Exception as e:
            logger.error(f"Failed to generate structured quant recommendations: {e}")
            # Fallback mock response for the demo pipeline if LLM parsing fails
            return {
                "scenario_analysis": "Error parsing LLM response or LLM unavailable.",
                "error": str(e)
            }
