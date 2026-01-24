import pytest
import os
from app.market_client import RealMarketClient

def test_public_client_init():
    """Verify that RealMarketClient initializes without keys."""
    client = RealMarketClient(api_key=None, secret=None, passphrase=None)
    assert client.client is not None

def test_public_fetch_markets():
    """Verify fetching markets without keys."""
    client = RealMarketClient(api_key=None, secret=None, passphrase=None)
    try:
        # Use underlying clob client to fetch markets
        resp = client.client.get_markets(next_cursor="")
        markets = resp.get('data', [])
        assert isinstance(markets, list)
        if len(markets) > 0:
            assert 'question' in markets[0]
            print(f"Successfully fetched {len(markets)} markets publicly.")
    except Exception as e:
        pytest.fail(f"Public market fetch failed: {e}")

def test_public_order_book():
    """Verify fetching order book for a valid market without keys."""
    client = RealMarketClient(api_key=None, secret=None, passphrase=None)
    
    # helper to get an active market ID
    try:
        resp = client.client.get_markets(next_cursor="")
        markets = resp.get('data', [])
        active_market = next((m for m in markets if m.get('active')), None)
        
        if active_market:
            token_id = active_market['condition_id'] 
            # Note: client.get_order_book uses token_id. 
            # In existing code, market_id arg is roughly condition_id or token_id depending on context
            # We trust the implementation uses the ID passed to it.
            
            # Fetch book
            book = client.get_order_book(token_id)
            assert book is not None
            # It might be empty if illiquid, but object should exist
            print(f"Fetched book for {token_id}")
        else:
            pytest.skip("No active markets found to test order book")

    except Exception as e:
        pytest.fail(f"Public order book fetch failed: {e}")
