
from typing import List, Dict, Any, Optional
import asyncio
from app.connectors.base import BaseConnector, ToolDefinition

class AgentOrchestrator:
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}

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
