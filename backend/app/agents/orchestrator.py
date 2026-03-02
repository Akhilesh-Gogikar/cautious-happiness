
from typing import List, Dict, Any, Optional
import asyncio
from app.connectors.base import BaseConnector, ToolDefinition
from app.connectors.polymarket import PolymarketConnector
from app.agents.scraping_agent import ScrapingAgent
from app.agents.insight_agent import InsightAgent
from app.agents.critic_agent import CriticAgent
from app.agents.news_agent import NewsAgent
from app.agents.quant_agent import QuantAgent

class AgentOrchestrator:
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        # Initialize internal agents
        self.polymarket_connector = PolymarketConnector()
        self.register_connector("polymarket", self.polymarket_connector)
        
        self.scraping_agent = ScrapingAgent(self.polymarket_connector)
        self.insight_agent = InsightAgent()
        self.critic_agent = CriticAgent()
        
        self.news_agent = NewsAgent()
        self.quant_agent = QuantAgent(self.polymarket_connector, self.news_agent)

    def register_connector(self, connector_id: str, connector: BaseConnector):
        """Register a new data connector (MCP, API, etc)."""
        self.connectors[connector_id] = connector

    async def list_all_tools(self) -> List[ToolDefinition]:
        """Aggregate tools from all registered connectors."""
        all_tools = []
        for cid, connector in self.connectors.items():
            try:
                tools = await connector.list_tools()
                # Prefix tool names to avoid collision? Or keep as is.
                # For now, keep as is.
                all_tools.extend(tools)
            except Exception as e:
                print(f"Error listing tools for {cid}: {e}")
        return all_tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Find the connector that has this tool and execute it."""
        # Naive linear search for MVP
        for cid, connector in self.connectors.items():
            try:
                tools = await connector.list_tools()
                if any(t.name == tool_name for t in tools):
                    print(f"Executing {tool_name} on connector {cid}...")
                    return await connector.call_tool(name=tool_name, arguments=arguments)
            except Exception as e:
                print(f"Error checking tools on {cid}: {e}")
        
        raise ValueError(f"Tool '{tool_name}' not found in any active connector.")

    async def plan_and_execute(self, query: str):
        """
        Simple reasoning loop to select a tool based on query.
        (Placeholder for full ReAct loop).
        """
        # Hardcoded logic for demo
        if "price" in query.lower() and "stock" in query.lower():
            # Extract ticker?
            ticker = "AAPL" # Default
            if "goog" in query.lower(): ticker = "GOOGL"
            if "tsla" in query.lower(): ticker = "TSLA"
            
            return await self.execute_tool("get_stock_price", {"ticker": ticker})
            
        if "rate" in query.lower() or "fed" in query.lower():
            return await self.execute_tool("get_fed_rate", {})

        return None

    async def run_polymarket_pipeline(self):
        """Run the full autonomous Polymarket pipeline."""
        # 1. Scrape data
        await self.scraping_agent.scrape_active_markets()
        
        # 2. Generate insights
        if self.llm_service:
            await self.insight_agent.generate_insights()
            
            # 3. Critique insights
            await self.critic_agent.critique_insights()
        
        return {"status": "success", "message": "Polymarket pipeline run complete."}

    async def run_demo_pipeline(self, scenario: str) -> dict:
        """
        Run the multi-agent Demo Pipeline:
        1. Ingest/Query News via pgvector RAG (NewsAgent)
        2. Query active Polymarket Odds
        3. QuantAgent synthesizes data and outputs Trade Recommendations
        """
        print(f"Orchestrator: Running Demo Pipeline for scenario '{scenario}'")
        
        # 1. Scrape specific Polymarket Markets (Mocking scraping pipeline trigger here)
        # await self.scraping_agent.scrape_active_markets()

        # 2. Trigger QuantAgent to evaluate RAG & Market Context
        trade_suggestions = await self.quant_agent.generate_trade_suggestions(scenario)
        
        return {
            "status": "success",
            "scenario": scenario,
            "trade_recommendations": trade_suggestions
        }
