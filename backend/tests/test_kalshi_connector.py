
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.connectors.kalshi import KalshiConnector

@pytest.mark.asyncio
async def test_kalshi_get_markets():
    connector = KalshiConnector()
    
    mock_response_data = {
        "markets": [
            {"ticker": "KXAU-24DEC31-B2400", "title": "Will Gold be above $2400?"},
            {"ticker": "KYOU-24DEC31-B2500", "title": "Will Gold be above $2500?"}
        ]
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    
    with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        result = await connector.call_tool("kalshi_get_markets", {"limit": 2})
        
        assert result == mock_response_data
        mock_get.assert_called_once_with("/markets", params={"limit": 2, "status": "open"})

@pytest.mark.asyncio
async def test_kalshi_get_market():
    connector = KalshiConnector()
    
    mock_response_data = {
        "market": {"ticker": "KXAU-24DEC31-B2400", "title": "Will Gold be above $2400?"}
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    
    with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        
        result = await connector.call_tool("kalshi_get_market", {"ticker": "KXAU-24DEC31-B2400"})
        
        assert result == mock_response_data
        mock_get.assert_called_once_with("/markets/KXAU-24DEC31-B2400")

@pytest.mark.asyncio
async def test_kalshi_invalid_tool():
    connector = KalshiConnector()
    with pytest.raises(ValueError, match="Tool invalid_tool not found in KalshiConnector"):
        await connector.call_tool("invalid_tool", {})
