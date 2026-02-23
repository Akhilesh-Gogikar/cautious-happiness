import pytest
import asyncio
from app.connectors.mcp import MCPConnector

@pytest.mark.asyncio
async def test_mcp_connection():
    connector = MCPConnector("Financial News")
    await connector.connect()
    
    assert connector.connected is True
    tools = await connector.list_tools()
    assert len(tools) > 0
    assert tools[0].name == "get_market_sentiment"
    
    resources = await connector.list_resources()
    assert len(resources) > 0
    assert resources[0].name == "Daily Briefing"

@pytest.mark.asyncio
async def test_mcp_tool_call():
    connector = MCPConnector("Financial News")
    await connector.connect()
    
    result = await connector.call_tool("get_market_sentiment", {"ticker": "AAPL"})
    assert result["status"] == "success"
    assert "AAPL" in result["data"]["ticker"]

@pytest.mark.asyncio
async def test_mcp_disconnected():
    connector = MCPConnector("Financial News")
    # Not connected
    with pytest.raises(ConnectionError):
        await connector.call_tool("some_tool", {})
