import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.connectors.polymarket import PolymarketConnector


def test_polymarket_get_markets_passes_filters():
    async def _run():
        connector = PolymarketConnector()

        response = MagicMock()
        response.json.return_value = [{"id": "m1"}]
        response.raise_for_status.return_value = None
        connector.client.get = AsyncMock(return_value=response)

        result = await connector.call_tool(
            "polymarket_get_markets", {"limit": 5, "active": True, "closed": False}
        )

        assert result == [{"id": "m1"}]
        connector.client.get.assert_awaited_once_with(
            f"{connector.gamma_api_url}/markets",
            params={"limit": 5, "active": "true", "closed": "false"},
        )

    asyncio.run(_run())


def test_polymarket_get_orderbook_requires_token_id():
    async def _run():
        connector = PolymarketConnector()
        with pytest.raises(ValueError, match="token_id is required"):
            await connector.call_tool("polymarket_get_orderbook", {})

    asyncio.run(_run())


def test_polymarket_get_orderbook_calls_clob_endpoint():
    async def _run():
        connector = PolymarketConnector()

        response = MagicMock()
        response.json.return_value = {"bids": [], "asks": []}
        response.raise_for_status.return_value = None
        connector.client.get = AsyncMock(return_value=response)

        result = await connector.call_tool("polymarket_get_orderbook", {"token_id": "abc123"})

        assert result == {"bids": [], "asks": []}
        connector.client.get.assert_awaited_once_with(
            f"{connector.clob_api_url}/book", params={"token_id": "abc123"}
        )

    asyncio.run(_run())
