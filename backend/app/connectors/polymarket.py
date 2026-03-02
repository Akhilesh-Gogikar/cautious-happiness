
import httpx
from typing import List, Dict, Any, Optional
from app.connectors.base import BaseConnector, ToolDefinition, ResourceDefinition

class PolymarketConnector(BaseConnector):
    def __init__(self):
        self.gamma_api_url = "https://gamma-api.polymarket.com"
        self.clob_api_url = "https://clob.polymarket.com"
        self.client = httpx.AsyncClient()

    async def connect(self):
        pass

    async def disconnect(self):
        await self.client.aclose()

    async def list_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="polymarket_get_markets",
                description="List available markets on Polymarket with optional filters.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of markets to return", "default": 20},
                        "active": {"type": "boolean", "description": "Filter by active status", "default": True},
                        "closed": {"type": "boolean", "description": "Filter by closed status", "default": False}
                    }
                }
            ),
            ToolDefinition(
                name="polymarket_get_orderbook",
                description="Get the orderbook for a specific Polymarket token ID.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "token_id": {"type": "string", "description": "The token ID (condition ID)"}
                    },
                    "required": ["token_id"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name == "polymarket_get_markets":
            params = {
                "limit": arguments.get("limit", 20),
                "active": "true" if arguments.get("active", True) else "false",
                "closed": "true" if arguments.get("closed", False) else "false"
            }
            response = await self.client.get(f"{self.gamma_api_url}/markets", params=params)
            response.raise_for_status()
            return response.json()

        if name == "polymarket_get_orderbook":
            token_id = arguments.get("token_id")
            if not token_id:
                 raise ValueError("token_id is required")
            
            # Polymarket CLOB orderbook endpoint
            response = await self.client.get(f"{self.clob_api_url}/book", params={"token_id": token_id})
            response.raise_for_status()
            return response.json()

        raise ValueError(f"Tool {name} not found in PolymarketConnector")

    async def list_resources(self) -> List[ResourceDefinition]:
        return []

    async def read_resource(self, uri: str) -> str:
        return "Not implemented"
