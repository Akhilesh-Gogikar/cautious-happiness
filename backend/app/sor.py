
import logging
import asyncio
import math
import random
from typing import Optional, List
from app.market_client import MarketClient
from app.models import TradeSignal

logger = logging.getLogger(__name__)

class SmartOrderRouter:
    def __init__(self, market_client: MarketClient):
        self.market_client = market_client
        self.active_orders = {}

    async def execute_twap(self, market_id: str, side: str, total_size_usd: float, duration_minutes: int, chunks: int = 5):
        """
        Time-Weighted Average Price (TWAP) Strategy.
        Splits the total order size into 'chunks' equal parts and executes them at regular intervals
        over 'duration_minutes'.
        """
        chunk_size = total_size_usd / chunks
        interval_seconds = (duration_minutes * 60) / chunks
        
        logger.info(f"SOR: Starting TWAP for {market_id}. Total: ${total_size_usd}, Chunks: {chunks}, Interval: {interval_seconds}s")

        for i in range(chunks):
            # Recalculate remaining to handle floating point drift or exact filling? 
            # For simple TWAP, fixed chunks are fine.
            
            logger.info(f"SOR: TWAP Executing chunk {i+1}/{chunks} (${chunk_size:.2f})")
            order_id = self.market_client.place_order(market_id, chunk_size, side)
            
            if order_id:
                logger.info(f"SOR: Chunk {i+1} placed. ID: {order_id}")
            else:
                logger.error(f"SOR: Failed to place chunk {i+1}")
            
            if i < chunks - 1:
                # Add small jitter to avoid perfect patterns
                wait_time = interval_seconds + random.uniform(-1, 1)
                if wait_time < 0: wait_time = 0
                logger.info(f"SOR: Waiting {wait_time:.2f}s before next chunk...")
                await asyncio.sleep(wait_time)
        
        logger.info(f"SOR: TWAP Completed for {market_id}")

    async def execute_iceberg(self, market_id: str, side: str, total_size_usd: float, visible_size_usd: float, limit_price: Optional[float] = None):
        """
        Iceberg Strategy.
        Places a small 'visible' order. When it fills, places the next chunk, until total is filled.
        This is a simplified version: it assumes "FILLED" status is returned reliably.
        """
        remaining_size = total_size_usd
        
        logger.info(f"SOR: Starting Iceberg for {market_id}. Total: ${total_size_usd}, Visible: ${visible_size_usd}")

        while remaining_size > 1.0: # Minimum order size buffer
            current_order_size = min(visible_size_usd, remaining_size)
            
            # Note: The underlying place_order in market_client.py currently uses a market order / aggressive limit.
            # True iceberg usually requires Limit Orders sitting on the book.
            # We'll assume place_order respects a limit if we passed one, but current signature doesn't support Price.
            # For this prototype, we'll just place the chunk and wait.
            
            logger.info(f"SOR: Iceberg placing visible chunk ${current_order_size:.2f}. Remaining: ${remaining_size:.2f}")
            order_id = self.market_client.place_order(market_id, current_order_size, side)
            
            if not order_id:
                logger.error("SOR: Failed to place Iceberg chunk. Aborting.")
                break
                
            # Wait for fill
            # In a real system, we'd subscribe to WS updates. 
            # Here, we poll.
            filled = False
            retries = 0
            while not filled and retries < 20:
                status = self.market_client.get_order_status(order_id)
                if status == "FILLED":
                    filled = True
                    remaining_size -= current_order_size
                    logger.info(f"SOR: Chunk filled. Remaining: ${remaining_size:.2f}")
                elif status == "CANCELED":
                    logger.warning("SOR: Order canceled externally. Aborting.")
                    return 
                else:
                    await asyncio.sleep(2) # Poll interval
                    retries += 1
            
            if not filled:
                logger.warning("SOR: Chunk timed out or not filled. Cancelling and retrying/aborting.")
                self.market_client.cancel_order(order_id)
                break
                
        logger.info(f"SOR: Iceberg Finished for {market_id}")

