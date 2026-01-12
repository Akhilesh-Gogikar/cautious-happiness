import logging
import math
from typing import List, Tuple, Optional
# Use string forward references or import carefully
from app.models import OrderBook, OrderBookLevel, ExecutionParameters, ExecutionStrategy

logger = logging.getLogger(__name__)

class SlippageAwareKelly:
    """
    Implements the 'Slippage-Aware Kelly Criterion' from the patent.
    
    Standard Kelly: f* = (p - q) / (b)  where b is odds - 1.
    For binary options (payoff 0 or 1), if we buy at price P_market:
    Win: Payoff = 1 / P_market.  Net Odds b = (1/P - 1) = (1-P)/P.
    Kelly Fraction f = (Prob * (1/P - 1) - (1-Prob)) / (1/P - 1)
                     = (Prob/P - Prob - 1 + Prob) / ((1-P)/P)
                     = (Prob - P) / (1 - P)  <-- Simplified Formula for Binary Options
                     
    Patent Improvement:
    P is not static. P = VWAP(size).
    We iterate size, calc VWAP, recalc Kelly, find max(Size * ExpectedLogUtility).
    However, the simple heuristic in the patent is finding the intersection where Edge = Slippage,
    or simply maximizing the extensive EV / Growth.
    
    The patent claim 2 specifies:
    f_adj* = (P_model - P_vwap) / (1 - P_vwap)
    """
    
    def __init__(self, bankroll: float = 1000.0, max_bankroll_fraction: float = 0.2):
        self.bankroll = bankroll
        self.max_bankroll_fraction = max_bankroll_fraction

    def calculate_vwap(self, order_book: OrderBook, size_shares: float) -> float:
        """
        Calculate Volume Weighted Average Price for a buy order of `size_shares`.
        Assumes order_book.asks is sorted by price ascending.
        """
        remaining = size_shares
        total_cost = 0.0
        
        for level in order_book.asks:
            take = min(remaining, level.amount)
            total_cost += take * level.price
            remaining -= take
            
            if remaining <= 0:
                break
                
        if remaining > 0:
            # Not enough liquidity to fill order
            return 999.0 # Prohibitive price
            
        return total_cost / size_shares

    def optimal_allocation(self, probability: float, order_book: OrderBook) -> Tuple[float, float, float]:
        """
        Determines optimal order size (USD) and shares.
        
        Returns:
            (best_size_usd, best_size_shares, best_vwap)
        """
        # Iterate through discrete share sizes or increments
        # Simple implementation: Walk the order book levels
        
        best_ev = -1.0
        best_size_shares = 0.0
        best_size_usd = 0.0
        best_vwap = 0.0
        
        # Cumulative walk
        current_shares = 0.0
        current_cost = 0.0
        
        # We can simulate stepping through the book
        # For a truly continuous check, we might want fine-grained steps.
        # Here we step by taking each full level from the order book to see "steps"
        
        # Flattener for iteration: decompsing large levels into smaller chunks could be better,
        # but for prototype, we accept the granularity of the order book levels.
        # Actually, let's step by modest increments of USD to be safer (e.g. $10 steps)
        
        increment_usd = 10.0
        max_usd = self.bankroll * self.max_bankroll_fraction
        
        simulated_usd = increment_usd
        
        while simulated_usd <= max_usd:
            # 1. Estimate shares we can buy for this USD (needs iterative solver or simpler approx)
            # Approximation: Get top price, estimate shares, refine.
            # Faster approach: Calculate VWAP for specific share counts.
            
            # Let's pivot: Iterate SHARES instead of USD for cleaner VWAP calc
            # Price ~ 0.5. $1000 bankroll -> max $200 bet -> ~400 shares.
            # Step by 10 shares.
            
            simulated_shares = simulated_usd # rough start, assuming price ~1.0. 
            # If price is 0.1, this is small. If price is 0.9, this is close.
            # Let's just solve for costs.
            
            # Better specific impl:
            # We want to maximize: Expected Growth ~ Kelly * Bankroll? 
            # Or just maximize f_adj * Bankroll? No, f_adj is the fraction.
            # We want to find the size S such that S/Bankroll approx equals f_adj(S).
            
            # Algorithm:
            # 1. Propose Size S (USD)
            # 2. Calc Shares = S / VWAP(shares)? Hard because VWAP depends on shares.
            #    Simpler: Propose Shares Q.
            #    Calc Cost C = sum(p*q).
            #    Calc VWAP = C / Q.
            #    Calc Kelly Fraction f = (Prob - VWAP) / (1 - VWAP).
            #    Calc Optimal Kelly Bet Size K_amt = f * Bankroll.
            #    Discrepancy D = K_amt - C.
            #    If C < K_amt, we can bet more. If C > K_amt, we bet too much.
            #    Find Q where D is effectively 0.
            
            pass
            
            simulated_usd += increment_usd
            
        # Let's implement the iterative convergence:
        # Range of shares: 1 to (Bankroll / BestAsk).
        if not order_book.asks:
            return 0.0, 0.0, 0.0
            
        min_shares = 1.0
        max_shares = self.bankroll / order_book.asks[0].price
        
        # Binary search or coarse-grained linear scan?
        # Linear scan is safer for non-convex books (though books are usually convex cost).
        
        best_shares = 0.0
        
        # Scan 100 points
        step = (max_shares - min_shares) / 50
        if step < 1: step = 1
        
        q = min_shares
        while q <= max_shares:
            vwap = self.calculate_vwap(order_book, q)
            if vwap >= 1.0: # Impossible to profit
                break
                
            # Patent Claim 2 Formula
            kelly_f = (probability - vwap) / (1 - vwap)
            
            target_bet_size = kelly_f * self.bankroll
            actual_cost = vwap * q
            
            # We are looking for the equilibrium where Actual Cost ~= Target Bet Size
            # However, since we simply want to MAXIMIZE expected log utility, 
            # or in the patent's simplified "Constraint" mode:
            # "execute the specific volume that maximizes bankroll growth while maintaining a positive EV"
            
            # Simple check: Is this size VALID by Kelly?
            # i.e. Is ActualCost <= TargetBetSize? 
            # We want the LARGEST q where ActualCost <= TargetBetSize.
            
            if kelly_f > 0 and actual_cost <= target_bet_size:
                # This is a valid bet size. Since Kelly is aggressive, 
                # taking the full Kelly size is the theoretical optimal for log growth.
                # So we want the point where ActualCost == TargetBetSize.
                best_shares = q
                best_vwap = vwap
                best_size_usd = actual_cost
            else:
                # If we breached, we went too far (slippage killed the edge). 
                # Since costs rise monotonically, we can stop or simple break.
                # But maybe local liquidity holes? Unlikely in standard books.
                pass
            
            q += step
            
        return best_size_usd, best_shares, best_vwap

class AlgoOrderManager:
    """
    Manages execution of algorithmic orders (TWAP, VWAP, Iceberg).
    """
    def __init__(self, market_client):
        self.market_client = market_client

    async def execute_step(self, order_id: int, db_session):
        """
        Executes a single step for an active algo order.
        """
        from app.models_db import AlgoOrder
        import datetime
        
        order = db_session.query(AlgoOrder).filter(AlgoOrder.id == order_id).first()
        if not order or order.status != "ACTIVE":
            return

        if order.type == "TWAP":
            await self._handle_twap(order, db_session)
        elif order.type == "VWAP":
            await self._handle_vwap(order, db_session)
        elif order.type == "ICEBERG":
            await self._handle_iceberg(order, db_session)

        db_session.commit()

    async def _handle_twap(self, order, db_session):
        """
        TWAP: Time Weighted Average Price.
        Executes logic: Slice / Time.
        """
        import datetime
        now = datetime.datetime.utcnow()
        
        # Calculate how many intervals we have
        # Interval: 1 minute for simplicity in this prototype
        interval_minutes = 1 
        
        if order.last_executed_at and (now - order.last_executed_at).total_seconds() < 55: # prevent double tap
            return

        # Total intervals = duration_minutes
        # Slice size = total_size / duration_minutes
        slice_usd = order.total_size_usd / order.duration_minutes
        
        # Adjust for remaining
        execution_amount = min(slice_usd, order.remaining_size_usd)
        
        if execution_amount > 0:
            success = self.market_client.place_order(order.market_id, execution_amount, "BUY")
            if success:
                order.remaining_size_usd -= execution_amount
                order.last_executed_at = now
                logger.info(f"TWAP [{order.id}]: Executed ${execution_amount}. Remaining: ${order.remaining_size_usd}")
        
        if order.remaining_size_usd <= 0.01: # threshold for completion
            order.status = "COMPLETED"

    async def _handle_vwap(self, order, db_session):
        """
        VWAP: Volume Weighted Average Price.
        Simplified version: Similar to TWAP for now, but can be improved with volume profiles.
        """
        # For this prototype, we treat VWAP similarly to TWAP but rename for logical separation
        await self._handle_twap(order, db_session)

    async def _handle_iceberg(self, order, db_session):
        """
        Iceberg: Hides total size by only showing a small portion.
        Since we are using a CLOB with 'place_order', we simulate this 
        by only placing the `display_size_usd`.
        """
        import datetime
        now = datetime.datetime.utcnow()

        # If we have an active fill, we wait? 
        # In this simplified exchange model, we assume place_order is immediate fill.
        # If it were a real order book, we'd check if previous display_size was filled.
        
        # For prototype: We place display_size, wait a bit, place next.
        # Real iceberg would monitor the order status.
        
        execution_amount = min(order.display_size_usd, order.remaining_size_usd)
        
        if execution_amount > 0:
            success = self.market_client.place_order(order.market_id, execution_amount, "BUY")
            if success:
                order.remaining_size_usd -= execution_amount
                order.last_executed_at = now
                logger.info(f"ICEBERG [{order.id}]: Executed ${execution_amount}. Remaining: ${order.remaining_size_usd}")

        if order.remaining_size_usd <= 0.01:
            order.status = "COMPLETED"

class SmartOrderRouter:
    """
    Implements Smart Order Routing (SOR) algorithms to minimize market impact.
    """
    def __init__(self, market_client):
        self.market_client = market_client

    def split_twap(self, total_shares: float, duration_minutes: int, interval_seconds: int) -> List[dict]:
        """
        Calculates TWAP chunks.
        """
        if duration_minutes <= 0 or interval_seconds <= 0:
            return [{"shares": total_shares, "delay": 0}]

        total_seconds = duration_minutes * 60
        num_intervals = int(total_seconds // interval_seconds)
        if num_intervals <= 0:
            return [{"shares": total_shares, "delay": 0}]

        shares_per_interval = total_shares / num_intervals
        chunks = []
        for i in range(num_intervals):
            chunks.append({
                "shares": shares_per_interval,
                "delay": interval_seconds if i > 0 else 0
            })
        
        # Handle remainder due to floor division if any (though usually floating point handles it)
        return chunks

    def split_iceberg(self, total_shares: float, display_size: float) -> List[dict]:
        """
        Calculates Iceberg chunks.
        """
        if display_size <= 0 or display_size >= total_shares:
            return [{"shares": total_shares}]

        chunks = []
        remaining = total_shares
        while remaining > 0:
            take = min(remaining, display_size)
            chunks.append({"shares": take})
            remaining -= take
            
        return chunks

    def _get_execution_price_estimate(self, market_id: str) -> float:
        """Helper to get current top price to convert shares -> USD"""
        try:
            book = self.market_client.get_order_book(market_id)
            if book.asks:
                return book.asks[0].price
        except Exception:
            pass
        return 0.5 # Fallback if no book or error, risky but consistent with prototype

    def _place_market_order_shares(self, market_id: str, shares: float, side: str="BUY") -> bool:
        """
        Wraps place_order which takes USD, converting shares to USD estimate.
        """
        price = self._get_execution_price_estimate(market_id)
        if price <= 0: return False
        size_usd = shares * price
        # Add small buffer to size_usd to ensure we get the shares if price moves slightly?
        # or rely on market_client's slippage buffer.
        return self.market_client.place_order(market_id, size_usd, side)

    async def execute_strategy(self, market_id: str, total_shares: float, params: "ExecutionParameters"):
        """
        High-level execution coordinator.
        """
        logger.info(f"Executing SOR strategy: {params.strategy} for {total_shares} shares on {market_id}")
        
        import asyncio
        import time

        if params.strategy == ExecutionStrategy.LIQUIDITY_SNIPE:
            # Audit Log: Strategy Start
            try:
                from app.database import SessionLocal
                from app.audit_logger import AuditLogger
                db = SessionLocal()
                AuditLogger().log_event(db, "TRADE_EXECUTION", {
                    "market_id": market_id,
                    "strategy": "LIQUIDITY_SNIPE", 
                    "total_shares": total_shares,
                    "params": str(params)
                })
                db.close()
            except Exception as e:
                logger.error(f"Audit Log Error: {e}")

            start_time = time.time()
            min_depth_usd = params.min_depth_usd or 1000.0 # Default fallback
            
            logger.info(f"Starting Liquidity Snipe: Waiting for ${min_depth_usd} depth...")
            
            while True:
                # Check liquidity
                try:
                    book = self.market_client.get_order_book(market_id)
                    current_depth_usd = 0.0
                    
                    # Calculate depth up to max price
                    for level in book.asks:
                        if params.snipe_max_price and level.price > params.snipe_max_price:
                            break
                        current_depth_usd += (level.amount * level.price)
                    
                    if current_depth_usd >= min_depth_usd:
                        logger.info(f"Liquidity threshold met (${current_depth_usd:.2f} >= ${min_depth_usd}). Executing!")
                        # Execute full size
                        self._place_market_order_shares(market_id, total_shares, "BUY")
                        break
                        
                except Exception as e:
                    logger.error(f"Error checking liquidity: {e}")
                
                # Check timeout
                if params.duration_minutes and (time.time() - start_time) > (params.duration_minutes * 60):
                    logger.warning("Liquidity Snipe timed out.")
                    break
                
                wait_time = params.interval_seconds if params.interval_seconds is not None else 5
                await asyncio.sleep(wait_time)

        elif params.strategy == ExecutionStrategy.TWAP:
            chunks = self.split_twap(total_shares, params.duration_minutes or 10, params.interval_seconds if params.interval_seconds is not None else 30)
            for chunk in chunks:
                if chunk["delay"] > 0:
                    await asyncio.sleep(chunk["delay"])
                
                success = self._place_market_order_shares(market_id, chunk["shares"], side="BUY")
                if not success:
                    logger.error(f"TWAP chunk failed for {market_id}")
                    break

        elif params.strategy == ExecutionStrategy.ICEBERG:
            chunks = self.split_iceberg(total_shares, params.display_size_shares or (total_shares / 10))
            for chunk in chunks:
                success = self._place_market_order_shares(market_id, chunk["shares"], side="BUY")
                if not success:
                    logger.error(f"Iceberg chunk failed for {market_id}")
                    break
                await asyncio.sleep(2) # Simulate waiting for fill

        else:
            # Fallback to single shot
            self._place_market_order_shares(market_id, total_shares, side="BUY")

