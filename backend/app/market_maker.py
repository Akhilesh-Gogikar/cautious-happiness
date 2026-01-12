import logging
import asyncio
from typing import Optional
from app.market_client import MarketClient

logger = logging.getLogger(__name__)

class MarketMaker:
    """
    Automated Market Maker providing two-sided quotes.
    """
    def __init__(self, market_client: MarketClient, market_id: str, spread: float = 0.04, size_shares: float = 10.0):
        self.market_client = market_client
        self.market_id = market_id # Token ID
        self.spread = spread
        self.size_shares = size_shares
        self.is_running = False
        self.fair_price = 0.5 # Default start
        
    async def start(self):
        """
        Starts the market making loop.
        """
        self.is_running = True
        logger.info(f"Starting Market Maker for {self.market_id} | Size: {self.size_shares} | Spread: {self.spread}")
        
        while self.is_running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Error in MarketMaker cycle: {e}")
            
            # Simple 5-second pulse for MVP
            await asyncio.sleep(5) 

    async def stop(self):
        """
        Stops the loop and cancels open orders.
        """
        self.is_running = False
        logger.info("Stopping Market Maker...")
        # Cleanup
        try:
            self.market_client.cancel_all_orders()
        except Exception as e:
            logger.error(f"Error cancelling orders during stop: {e}")

    async def run_cycle(self):
        """
        Single iteration of the MM logic:
        1. Fetch Book
        2. Determine Fair Price
        3. Calculate Bid/Ask
        4. Replace Orders
        """
        # 1. Get Market Data
        # Blocking call in synchronous client, but fast enough for MVP
        try:
            book = self.market_client.get_order_book(self.market_id)
        except Exception as e:
            logger.warning(f"Failed to fetch book: {e}")
            return

        # 2. Determine Fair Price
        # Strategy: Mid-Market Price. 
        # Future: Use `self.engine.get_forecast()`
        if book.asks and book.bids:
            best_bid = book.bids[0].price
            best_ask = book.asks[0].price
            
            # Simple sanity check
            if best_ask > best_bid:
                self.fair_price = (best_bid + best_ask) / 2.0
            else:
                # Crossed book? Use last known or 0.5
                pass
        else:
            logger.info("Empty book or one-sided. Keeping previous fair price.")

        # 3. Calculate Quotes
        half_spread = self.spread / 2.0
        my_bid = round(self.fair_price - half_spread, 2)
        my_ask = round(self.fair_price + half_spread, 2)
        
        # Bounds check
        if my_bid <= 0.01: my_bid = 0.01
        if my_ask >= 0.99: my_ask = 0.99
        
        if my_bid >= my_ask:
            # Spread too tight or inverted logic
            my_ask = my_bid + 0.01

        # 4. Execute (Cancel-Replace)
        # Note: This is a "Naive" MM. It cancels everything every cycle.
        # Efficient MM would check if current orders are 'close enough' and only move if necessary.
        self.market_client.cancel_all_orders() 

        logger.info(f"MM Quoting: Bid {my_bid:.2f} / Ask {my_ask:.2f} (Fair: {self.fair_price:.2f})")
        
        # Place Bid
        self.market_client.place_limit_order(self.market_id, my_bid, self.size_shares, "BUY")
        
        # Place Ask
        self.market_client.place_limit_order(self.market_id, my_ask, self.size_shares, "SELL")
