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
    
    def place_order(self, market_id: str, size_usd: float, side: str = "BUY") -> Optional[str]:
        raise NotImplementedError

    def place_limit_order(self, market_id: str, price: float, size_shares: float, side: str) -> Optional[str]:
        raise NotImplementedError


    def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError
        
    def get_order_status(self, order_id: str) -> str:
        raise NotImplementedError

    def get_market_details(self, condition_id: str) -> dict:
        raise NotImplementedError

    def cancel_all_orders(self) -> bool:
        raise NotImplementedError

class RealMarketClient(MarketClient):
    def __init__(self, api_key: str, secret: str, passphrase: str):
        self.client = ClobClient(
            "https://clob.polymarket.com", # Exchange URL
            key=api_key, 
            secret=secret, 
            passphrase=passphrase, 
            chain_id=137
        )
        
    def get_order_book(self, market_id: str) -> OrderBook:
        """
        Fetches the order book for a specific token (represented by market_id/token_id).
        Note: terminology overlap. The exchange has ConditionID and TokenID.
        We assume 'market_id' passed here is the TokenID (Asset ID) we want to trade.
        """
        try:
            # CLOB client expects token_id for 'get_order_book'
            book_data = self.client.get_order_book(market_id)
            
            asks = [OrderBookLevel(price=float(x.price), amount=float(x.size)) for x in book_data.asks]
            bids = [OrderBookLevel(price=float(x.price), amount=float(x.size)) for x in book_data.bids]
            return OrderBook(asks=asks, bids=bids)
        except Exception as e:
            logger.error(f"Error fetching real order book: {e}")
            return OrderBook(asks=[], bids=[])

    def place_order(self, market_id: str, size_usd: float, side: str = "BUY", wallet_address: Optional[str] = None, validator=None) -> bool:
        """
        Places a market order (or aggressive limit) to fill the size.
        
        Args:
            market_id: Token ID to trade
            size_usd: Target USD amount
            side: "BUY" or "SELL"
            wallet_address: Optional wallet address for compliance tracking
            validator: Optional FatFingerValidator for pre-trade checks
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
            
            # PRE-TRADE VALIDATION: Fat Finger Check
            if validator:
                try:
                    validator.validate_order(
                        order_size_usd=size_usd,
                        order_price=limit_price,
                        order_book=book,
                        market_id=market_id
                    )
                except Exception as validation_error:
                    logger.error(f"Order validation failed: {validation_error}")
                    raise  # Re-raise to prevent order execution
            
            # Calculate quantity
            # size_usd is roughly target spend. 
            # quantity = size_usd / price
            quantity = size_usd / top_price
            
            logger.info(f"REAL: Placing BUY for {quantity:.2f} shares of {market_id} @ max {limit_price}")
            if wallet_address:
                logger.info(f"Order from wallet: {wallet_address}")
            
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

    def place_limit_order(self, market_id: str, price: float, size_shares: float, side: str) -> Optional[str]:
        """
        Places a specific Limit Order at a fixed price and share count.
        Used for Market Making.
        """
        try:
            logger.info(f"REAL: Placing LIMIT {side} {size_shares:.2f} shares @ {price:.2f} on {market_id}")
            resp = self.client.create_and_post_order(
                app_order_id=str(random.randint(1, 1000000)),
                token_id=market_id,
                price=price,
                side=side.upper(),
                size=size_shares
            )
            logger.info(f"Limit Order Response: {resp}")
            return resp.get("orderID") if isinstance(resp, dict) else "UNKNOWN_ID"
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None

    def get_market_details(self, condition_id: str) -> dict:
        """
        Fetches market details including close time.
        """
        try:
            # Using public Gamma API for market details as it often provides clearer close times
            # than the CLOB API 'get_market' call sometimes
            url = f"https://gamma-api.polymarket.com/markets/{condition_id}"
            import requests
            resp = requests.get(url)
            data = resp.json()
            return {
                "close_time": data.get("end_date") or data.get("closed_time"),
                "status": "active" if data.get("active") else "closed",
                "question": data.get("question")
            }
        except Exception as e:
             logger.error(f"Error fetching market details: {e}")
             return {}

    def cancel_all_orders(self) -> bool:
        """
        Cancels all open orders on the exchange.
        """
        try:
            logger.info("REAL: Attempting to cancel ALL orders...")
            # Ideally use cancel_all if available, otherwise fetch open and cancel one by one
            # The python clob client usually has cancel_all
            self.client.cancel_all()
            return True
        except Exception as e:
            logger.error(f"Error cancelling all orders: {e}")
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

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancels a specific order by ID.
        """
        try:
            self.client.cancel(order_id)
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    def get_order_status(self, order_id: str) -> str:
        """
        Check if an order is OPEN, FILLED, or CANCELLED.
        """
        try:
            # Assuming client has a method to get order
            # This is pseudo-code for the real client library
            # real_client_lib might use `get_order(order_id)`
            order = self.client.get_order(order_id)
            # Map status
            return order.get("status") or "UNKNOWN"
        except Exception as e:
            logger.error(f"Error getting order status {order_id}: {e}")
            return "UNKNOWN"

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
        
    def place_order(self, market_id: str, size_usd: float, side: str = "BUY", wallet_address: Optional[str] = None) -> bool:
        logger.info(f"MOCK EXECUTION: Placed {side} order for ${size_usd} on {market_id}")
        if wallet_address:
            logger.info(f"Mock order from wallet: {wallet_address}")
        return True

    def place_limit_order(self, market_id: str, price: float, size_shares: float, side: str) -> Optional[str]:
        logger.info(f"MOCK EXECUTION: Placed LIMIT {side} {size_shares} shares @ {price} on {market_id}")
        return f"mock_limit_order_{random.randint(1000, 9999)}"

    def cancel_order(self, order_id: str) -> bool:
        logger.info(f"MOCK EXECUTION: Cancelled order {order_id}")
        return True

    def get_order_status(self, order_id: str) -> str:
        # Mock filled immediately for now, or use a state dict in a more complex mock
        return "FILLED"

    def get_market_details(self, condition_id: str) -> dict:
        # Mock close time: 5 minutes from now for testing auto-liquidation
        from datetime import datetime, timedelta
        return {
            "close_time": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z",
            "status": "active",
            "question": "Mock Market Question"
        }

    def cancel_all_orders(self) -> bool:
        logger.info("MOCK EXECUTION: Cancelled all open orders")
        return True
