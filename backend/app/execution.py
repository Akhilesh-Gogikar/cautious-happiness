import logging
import math
from typing import List, Tuple, Optional
from app.models import OrderBook, OrderBookLevel

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
