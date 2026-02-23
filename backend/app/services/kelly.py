import math
from typing import List, Dict, Any, Tuple

class SlippageAwareKellyEngine:
    """
    Implements the 'Slippage-Aware Kelly Criterion' as described in the patent.
    Formula: f*_adj = (P_model - P_vwap) / (1 - P_vwap)
    """

    def calculate_optimal_size(
        self, 
        model_probability: float, 
        order_book: List[Dict[str, float]], 
        bankroll: float,
        step_size: float = 10.0,
        max_steps: int = 100
    ) -> Dict[str, Any]:
        """
        Walks the order book to find the optimal order size where marginal edge = marginal slippage.
        
        Args:
            model_probability: LLM derived probability (0.0 to 1.0)
            order_book: List of ask levels [{'price': 0.8, 'size': 100}, ...]
            bankroll: Total available capital
            step_size: Increment for simulation
            max_steps: Safeguard against infinite loops
            
        Returns:
            Dict containing optimal_size, expected_vwap, and kelly_fraction.
        """
        best_size = 0.0
        max_ev = -1.0
        best_vwap = 0.0
        best_kelly = 0.0

        # Sort order book by price (Asks)
        sorted_asks = sorted(order_book, key=lambda x: x['price'])

        for i in range(1, max_steps + 1):
            sim_size = i * step_size
            if sim_size > bankroll:
                break

            vwap = self._calculate_vwap(sim_size, sorted_asks)
            
            # If vwap >= model_prob, there is no edge
            if vwap >= model_probability:
                break
            
            # Patent Formula: Kelly Fraction (adjusted for binary price odds)
            # Standard Kelly: (bp - q) / b
            # Here b (odds) is represented by the price. 
            # In prediction markets (0/1), price P implies decimal odds 1/P.
            # f* = (P_model - P_market) / (1 - P_market)
            kelly_fraction = (model_probability - vwap) / (1 - vwap)
            
            # Clamp kelly fraction (safety buffer 0.5 fractional Kelly)
            kelly_fraction = max(0, min(kelly_fraction, 0.5))
            
            expected_bet = kelly_fraction * bankroll
            
            # If the simulated bet size is close to what Kelly suggests at this VWAP
            # the 'actual' EV is maximized when we hit the equilibrium point.
            # Simplified for MVP: Find the size that yields highest (Prob * Profit - (1-Prob) * Loss)
            # where Profit = (1-VWAP)/VWAP and Loss = 1
            ev = (model_probability * (1 - vwap)) - ((1 - model_probability) * vwap)
            
            if ev > max_ev:
                max_ev = ev
                best_size = sim_size
                best_vwap = vwap
                best_kelly = kelly_fraction
            else:
                # Diminishing returns hit
                break

        return {
            "optimal_size": best_size,
            "expected_vwap": best_vwap,
            "kelly_fraction": best_kelly,
            "expected_value": max_ev
        }

    def _calculate_vwap(self, target_size: float, sorted_asks: List[Dict[str, float]]) -> float:
        """
        Simulates walking the order book to calculate Volume Weighted Average Price.
        """
        remaining_size = target_size
        total_cost = 0.0
        filled_size = 0.0

        for level in sorted_asks:
            price = level['price']
            size_at_level = level['size']

            fill = min(remaining_size, size_at_level)
            total_cost += fill * price
            filled_size += fill
            remaining_size -= fill

            if remaining_size <= 0:
                break
        
        # If order book is thin, use last price for remaining
        if remaining_size > 0 and filled_size > 0:
            total_cost += remaining_size * sorted_asks[-1]['price']
            filled_size += remaining_size
        elif filled_size == 0:
            return 1.0 # Infinitely expensive if no liquidity

        return total_cost / filled_size
