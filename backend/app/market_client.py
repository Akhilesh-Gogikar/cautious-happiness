import logging
import random
import os
from typing import List, Optional
from app.models import OrderBook, OrderBookLevel
from py_clob_client.client import ClobClient

logger = logging.getLogger(__name__)

class MarketClient:
    def get_order_book(self, market_id: str) -> OrderBook:
        raise NotImplementedError
    
    def place_order(self, market_id: str, size_usd: float, side: str = "BUY") -> bool:
        raise NotImplementedError

class RealMarketClient(MarketClient):
    def __init__(self, api_key: str, secret: str, passphrase: str):
        self.client = ClobClient(
            "https://clob.polymarket.com", 
            key=api_key, 
            secret=secret, 
            passphrase=passphrase, 
            chain_id=137
        )
        
    def get_order_book(self, market_id: str) -> OrderBook:
        """
        Fetches the order book for a specific token (represented by market_id/token_id).
        Note: terminology overlap. Polymarket has ConditionID and TokenID.
        We assume 'market_id' passed here is the TokenID (Asset ID) we want to trade.
        """
        try:
            # Polymarket CLOB client expects token_id for 'get_order_book'
            book_data = self.client.get_order_book(market_id)
            
            asks = [OrderBookLevel(price=float(x.price), amount=float(x.size)) for x in book_data.asks]
            bids = [OrderBookLevel(price=float(x.price), amount=float(x.size)) for x in book_data.bids]
            return OrderBook(asks=asks, bids=bids)
        except Exception as e:
            logger.error(f"Error fetching real order book: {e}")
            return OrderBook(asks=[], bids=[])

    def place_order(self, market_id: str, size_usd: float, side: str = "BUY") -> bool:
        """
        Places a market order (or aggressive limit) to fill the size.
        """
        try:
            # 1. Fetch book to estimate price for limit
            book = self.get_order_book(market_id)
            if not book.asks and side == "BUY":
                logger.error("No liquidity to buy.")
                return False
                
            # Simple aggressive limit: Take top ask + slippage buffer
            # Or use market order if supported (FOK/IOC with worse price)
            top_price = book.asks[0].price
            limit_price = round(top_price * 1.05, 2) # 5% slippage tolerance
            if limit_price > 1.0: limit_price = 1.0
            
            # Calculate quantity
            # size_usd is roughly target spend. 
            # quantity = size_usd / price
            quantity = size_usd / top_price
            
            logger.info(f"REAL: Placing BUY for {quantity:.2f} shares of {market_id} @ max {limit_price}")
            
            resp = self.client.create_and_post_order(
                app_order_id=str(random.randint(1, 1000000)), # better ID generation needed in prod
                token_id=market_id,
                price=limit_price,
                side=side,
                size=quantity
            )
            logger.info(f"Order Response: {resp}")
            return True
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False

    def get_portfolio(self):
        """
        Fetches user balance and positions.
        """
        try:
            # Balance
            # client.get_balance() might not exist in this wrapper, checking simplified usage
            # Usually we check USDC balance on chain or via CLOB API if available
            # Placeholder: 0 balance if failed
            balance = 0.0
            
            # Positions
            # client.get_trades() or derived? 
            # For now returning empty to avoid crash if API doesn't support easy portfolio fetch
            return {"balance": balance, "positions": []}
        except Exception as e:
             logger.error(f"Portfolio fetch error: {e}")
             return {"balance": 0.0, "positions": []}

class MockMarketClient(MarketClient):
    """
    Simulates a market for testing execution logic without funds.
    """
    def get_order_book(self, market_id: str) -> OrderBook:
        # Generate a fake order book with some slippage
        # Price starts at 0.40 and ramps up to 0.60
        asks = []
        current_price = 0.40
        for i in range(10):
            amount = 100 + (i * 50) # Increasing liquidity at depth? or random.
            asks.append(OrderBookLevel(price=round(current_price, 2), amount=amount))
            current_price += 0.02 # Steep slippage for testing
            
        return OrderBook(asks=asks, bids=[]) 
        
    def place_order(self, market_id: str, size_usd: float, side: str = "BUY") -> bool:
        logger.info(f"MOCK EXECUTION: Placed {side} order for ${size_usd} on {market_id}")
        return True
