import asyncio
from typing import Any, Dict, List
from app.agents.registry import registry
from app.agents.macro_sentinel import MacroSentinelAgent
from app.agents.alpha_hunter import AlphaHunterAgent
from app.agents.sentiment_spy import SentimentSpyAgent
from app.agents.risk_guard import RiskGuardAgent
from app.agents.trade_executor import TradeExecutorAgent

class StrategyArchitectAgent:
    def __init__(self):
        self.name = "Strategy-Architect"
        self.role = "Orchestrator"
        
        # Initialize and register agents
        self.macro = MacroSentinelAgent()
        self.alpha = AlphaHunterAgent()
        self.sentiment = SentimentSpyAgent()
        self.risk = RiskGuardAgent()
        self.executor = TradeExecutorAgent()
        
        registry.register(self.macro)
        registry.register(self.alpha)
        registry.register(self.sentiment)
        registry.register(self.risk)
        registry.register(self.executor)

    async def coordinate(self, query: str, probability: float = 0.5, portfolio: List[Any] = []) -> Dict[str, Any]:
        print(f"--- [Strategy-Architect] Coordinating Strategy for: {query} ---")
        
        # Run analysts in parallel
        analyst_tasks = [
            self.macro.execute({"query": query}),
            self.alpha.execute({"query": query}),
            self.sentiment.execute({"query": query})
        ]
        analyst_results = await asyncio.gather(*analyst_tasks)
        
        # Now run Risk and Execution based on analysis context
        # We pass the analytical context forward
        risk_task = self.risk.execute({
            "query": query, 
            "probability": probability, 
            "portfolio": portfolio
        })
        executor_task = self.executor.execute({
            "query": query, 
            "probability": probability
        })
        
        control_results = await asyncio.gather(risk_task, executor_task)
        results = analyst_results + control_results
        
        # Resolve consensus
        sentiment_signal = next((r["sentiment_score"] for r in analyst_results if r.get("agent") == "Sentiment-Spy"), 0.5)
        alpha_signal = next((r["signal"] for r in analyst_results if r.get("agent") == "Alpha-Hunter"), "NEUTRAL")
        risk_verdict = next((r["verdict"] for r in control_results if r.get("agent") == "Risk-Guard"), "APPROVED")
        
        consensus = "NEUTRAL"
        if risk_verdict == "REJECTED":
            consensus = "BLOCKED_BY_RISK"
        elif alpha_signal == "BULLISH" and sentiment_signal > 0.6:
            consensus = "HIGH_CONVICTION_BULLISH"
        elif alpha_signal == "BULLISH" or sentiment_signal > 0.6:
            consensus = "CAUTIOUS_BULLISH"
        elif sentiment_signal < 0.4:
            consensus = "BEARISH_SENTIMENT"

        return {
            "query": query,
            "consensus": consensus,
            "agent_results": results
        }

orchestrator = StrategyArchitectAgent()
