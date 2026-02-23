import pytest
from unittest.mock import MagicMock, patch
from app.connectors.alpaca import AlpacaConnector

@pytest.fixture
def mock_alpaca_client():
    with patch('app.connectors.alpaca.TradingClient') as mock:
        yield mock

@pytest.mark.asyncio
async def test_alpaca_connector_get_account(mock_alpaca_client):
    connector = AlpacaConnector()
    connector.api_key = "test_key"
    connector.secret_key = "test_secret"
    await connector.connect()

    mock_account = MagicMock()
    mock_account.account_number = "12345"
    mock_account.equity = "10000.00"
    mock_account.cash = "5000.00"
    mock_account.buying_power = "20000.00"
    mock_account.currency = "USD"
    
    connector.client.get_account.return_value = mock_account

    result = await connector.call_tool("get_account", {})
    
    assert result["account_number"] == "12345"
    assert result["equity"] == "10000.00"
    assert connector.client.get_account.called

@pytest.mark.asyncio
async def test_alpaca_connector_list_positions(mock_alpaca_client):
    connector = AlpacaConnector()
    connector.api_key = "test_key"
    connector.secret_key = "test_secret"
    await connector.connect()

    mock_position = MagicMock()
    mock_position.symbol = "AAPL"
    mock_position.qty = "10"
    mock_position.avg_entry_price = "150.00"
    mock_position.current_price = "155.00"
    mock_position.unrealized_pl = "50.00"
    
    connector.client.get_all_positions.return_value = [mock_position]

    result = await connector.call_tool("list_positions", {})
    
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["unrealized_pl"] == "50.00"

@pytest.mark.asyncio
async def test_alpaca_connector_place_order(mock_alpaca_client):
    connector = AlpacaConnector()
    connector.api_key = "test_key"
    connector.secret_key = "test_secret"
    await connector.connect()

    mock_order = MagicMock()
    mock_order.id = "order_id_123"
    mock_order.client_order_id = "client_id_456"
    mock_order.status = "accepted"
    mock_order.symbol = "TSLA"
    mock_order.qty = "5"
    mock_order.side = "buy"
    
    connector.client.submit_order.return_value = mock_order

    args = {"symbol": "TSLA", "qty": 5, "side": "buy"}
    result = await connector.call_tool("place_market_order", args)
    
    assert result["id"] == "order_id_123"
    assert result["symbol"] == "TSLA"
    assert connector.client.submit_order.called
