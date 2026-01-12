import logging
import random
import time
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from app.models import OrderBook, OrderBookLevel, PortfolioSummary, PortfolioPosition
from app.market_client import MarketClient
import requests

logger = logging.getLogger(__name__)


class PaperTradingClient(MarketClient):
    """
    Simulates realistic market execution for paper trading.
    
    Features:
    - Fetches live order book data for realism
    - Simulates slippage based on order size
    - Tracks virtual portfolio (positions, balance, P&L)
    - Supports all order types (market, limit, TWAP, VWAP, iceberg)
    - Simulates execution delays
    """
    
    def __init__(self, initial_balance: float = 10000.0, session_id: Optional[int] = None):
        """
        Initialize paper trading client.
        
        Args:
            initial_balance: Starting virtual USDC balance
            session_id: Database session ID for persistence
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.session_id = session_id
        
        # Virtual portfolio state
        self.positions: Dict[str, Dict] = {}  # market_id -> {shares, avg_price, side}
        self.open_orders: Dict[str, Dict] = {}  # order_id -> order details
        self.trade_history: List[Dict] = []
        
        # Performance tracking
        self.total_pnl = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.num_trades = 0
        self.winning_trades = 0
        
        # Execution simulation parameters
        self.execution_delay_ms = (50, 200)  # Random delay range
        self.slippage_factor = 0.001  # Base slippage: 0.1%
        
        logger.info(f"PaperTradingClient initialized with ${initial_balance:.2f} balance")
    
    def get_order_book(self, market_id: str) -> OrderBook:
        """
        Fetch live order book data from AlphaSignals for realistic simulation.
        Falls back to mock data if API unavailable.
        """
        try:
            # Try to fetch real order book from AlphaSignals CLOB API
            # Token ID format for AlphaSignals
            url = f"https://clob.polymarket.com/book?token_id={market_id}"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                
                asks = [
                    OrderBookLevel(price=float(ask['price']), amount=float(ask['size']))
                    for ask in data.get('asks', [])[:20]  # Top 20 levels
                ]
                bids = [
                    OrderBookLevel(price=float(bid['price']), amount=float(bid['size']))
                    for bid in data.get('bids', [])[:20]
                ]
                
                if asks or bids:
                    return OrderBook(asks=asks, bids=bids)
        except Exception as e:
            logger.warning(f"Failed to fetch live order book for {market_id}: {e}")
        
        # Fallback to simulated order book
        return self._generate_mock_order_book()
    
    def _generate_mock_order_book(self) -> OrderBook:
        """Generate realistic mock order book for testing."""
        base_price = 0.45 + (random.random() * 0.3)  # 0.45 to 0.75
        
        asks = []
        current_price = base_price
        for i in range(10):
            amount = 100 + (i * 50) + random.randint(-20, 20)
            asks.append(OrderBookLevel(price=round(current_price, 3), amount=amount))
            current_price += 0.01 + (random.random() * 0.01)
        
        bids = []
        current_price = base_price - 0.01
        for i in range(10):
            amount = 100 + (i * 50) + random.randint(-20, 20)
            bids.append(OrderBookLevel(price=round(current_price, 3), amount=amount))
            current_price -= 0.01 + (random.random() * 0.01)
        
        return OrderBook(asks=asks, bids=bids)
    
    def _simulate_execution_delay(self):
        """Simulate realistic execution latency."""
        delay_ms = random.randint(*self.execution_delay_ms)
        time.sleep(delay_ms / 1000.0)
    
    def _calculate_slippage(self, size_usd: float, order_book: OrderBook) -> float:
        """
        Calculate realistic slippage based on order size and liquidity.
        
        Returns:
            Slippage multiplier (e.g., 1.02 means 2% slippage)
        """
        if not order_book.asks:
            return 1.0
        
        # Calculate total liquidity in first 5 levels
        total_liquidity = sum(
            level.price * level.amount 
            for level in order_book.asks[:5]
        )
        
        if total_liquidity == 0:
            return 1.0
        
        # Slippage increases with order size relative to liquidity
        size_ratio = size_usd / total_liquidity
        slippage = self.slippage_factor * (1 + size_ratio * 10)
        
        return 1.0 + slippage
    
    def _calculate_vwap_with_slippage(self, order_book: OrderBook, size_usd: float) -> Tuple[float, float]:
        """
        Calculate VWAP and actual shares filled considering slippage.
        
        Returns:
            (vwap_price, shares_filled)
        """
        remaining_usd = size_usd
        total_cost = 0.0
        total_shares = 0.0
        
        for level in order_book.asks:
            if remaining_usd <= 0:
                break
            
            # Apply slippage to this level
            slippage = self._calculate_slippage(size_usd, order_book)
            effective_price = level.price * slippage
            
            # How much can we buy at this level?
            max_shares_at_level = level.amount
            max_cost_at_level = max_shares_at_level * effective_price
            
            if remaining_usd >= max_cost_at_level:
                # Take entire level
                total_cost += max_cost_at_level
                total_shares += max_shares_at_level
                remaining_usd -= max_cost_at_level
            else:
                # Partial fill at this level
                shares = remaining_usd / effective_price
                total_cost += remaining_usd
                total_shares += shares
                remaining_usd = 0
        
        if total_shares == 0:
            return 0.0, 0.0
        
        vwap = total_cost / total_shares
        return vwap, total_shares
    
    def place_order(self, market_id: str, size_usd: float, side: str = "BUY", 
                   wallet_address: Optional[str] = None, validator=None) -> bool:
        """
        Simulate order execution in paper trading mode.
        
        Args:
            market_id: Market/token ID
            size_usd: Order size in USD
            side: "BUY" or "SELL"
            wallet_address: Ignored in paper trading
            validator: Optional validator (applied if provided)
        
        Returns:
            True if order executed successfully
        """
        try:
            # Check balance
            if size_usd > self.balance:
                logger.warning(f"Insufficient paper balance: ${self.balance:.2f} < ${size_usd:.2f}")
                return False
            
            # Fetch order book
            order_book = self.get_order_book(market_id)
            
            if not order_book.asks:
                logger.error(f"No liquidity available for {market_id}")
                return False
            
            # Apply validator if provided
            if validator:
                try:
                    validator.validate_order(
                        order_size_usd=size_usd,
                        order_price=order_book.asks[0].price,
                        order_book=order_book,
                        market_id=market_id
                    )
                except Exception as validation_error:
                    logger.error(f"Paper order validation failed: {validation_error}")
                    return False
            
            # Simulate execution delay
            self._simulate_execution_delay()
            
            # Calculate fill with slippage
            vwap, shares = self._calculate_vwap_with_slippage(order_book, size_usd)
            
            if shares == 0:
                logger.error(f"Could not fill order for {market_id}")
                return False
            
            actual_cost = vwap * shares
            
            # Update balance
            self.balance -= actual_cost
            
            # Update position
            if market_id not in self.positions:
                self.positions[market_id] = {
                    'shares': 0.0,
                    'avg_price': 0.0,
                    'side': side,
                    'total_cost': 0.0
                }
            
            pos = self.positions[market_id]
            
            if side == "BUY":
                # Add to position
                new_total_shares = pos['shares'] + shares
                new_total_cost = pos['total_cost'] + actual_cost
                pos['shares'] = new_total_shares
                pos['avg_price'] = new_total_cost / new_total_shares if new_total_shares > 0 else 0
                pos['total_cost'] = new_total_cost
            else:
                # Reduce position (selling)
                pos['shares'] -= shares
                if pos['shares'] <= 0:
                    # Position closed
                    realized_pnl = actual_cost - (shares * pos['avg_price'])
                    self.realized_pnl += realized_pnl
                    self.balance += actual_cost
                    del self.positions[market_id]
            
            # Record trade
            trade = {
                'market_id': market_id,
                'side': side,
                'shares': shares,
                'price': vwap,
                'cost': actual_cost,
                'timestamp': datetime.utcnow(),
                'order_type': 'MARKET'
            }
            self.trade_history.append(trade)
            self.num_trades += 1
            
            logger.info(
                f"PAPER TRADE: {side} {shares:.2f} shares of {market_id} @ ${vwap:.3f} "
                f"(Total: ${actual_cost:.2f}, Balance: ${self.balance:.2f})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Paper order execution failed: {e}")
            return False
    
    def place_limit_order(self, market_id: str, price: float, size_shares: float, side: str) -> Optional[str]:
        """
        Simulate limit order placement.
        
        In paper trading, we simplify by immediately checking if the order would fill.
        """
        order_id = f"paper_limit_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        order_book = self.get_order_book(market_id)
        
        # Check if order would immediately fill
        if side == "BUY" and order_book.asks:
            best_ask = order_book.asks[0].price
            if price >= best_ask:
                # Would fill immediately as market order
                size_usd = price * size_shares
                success = self.place_order(market_id, size_usd, side)
                return order_id if success else None
        
        # Otherwise, store as open order (simplified - would need matching engine for full simulation)
        self.open_orders[order_id] = {
            'market_id': market_id,
            'price': price,
            'size': size_shares,
            'side': side,
            'status': 'OPEN',
            'created_at': datetime.utcnow()
        }
        
        logger.info(f"PAPER LIMIT ORDER: {side} {size_shares} shares @ ${price} (Order ID: {order_id})")
        return order_id
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open paper order."""
        if order_id in self.open_orders:
            self.open_orders[order_id]['status'] = 'CANCELLED'
            logger.info(f"PAPER ORDER CANCELLED: {order_id}")
            return True
        return False
    
    def get_order_status(self, order_id: str) -> str:
        """Get status of a paper order."""
        if order_id in self.open_orders:
            return self.open_orders[order_id]['status']
        return "UNKNOWN"
    
    def get_market_details(self, condition_id: str) -> dict:
        """Fetch market details (delegates to real API)."""
        try:
            url = f"https://gamma-api.polymarket.com/markets/{condition_id}"
            resp = requests.get(url, timeout=2)
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
        """Cancel all open paper orders."""
        for order_id in list(self.open_orders.keys()):
            self.open_orders[order_id]['status'] = 'CANCELLED'
        logger.info(f"PAPER: Cancelled {len(self.open_orders)} open orders")
        return True
    
    def get_portfolio(self) -> PortfolioSummary:
        """
        Get current paper portfolio state.
        
        Returns:
            PortfolioSummary with current positions and balance
        """
        positions = []
        total_exposure = 0.0
        
        for market_id, pos in self.positions.items():
            # Fetch current price from order book
            try:
                book = self.get_order_book(market_id)
                current_price = book.asks[0].price if book.asks else pos['avg_price']
            except:
                current_price = pos['avg_price']
            
            current_value = pos['shares'] * current_price
            pnl = current_value - pos['total_cost']
            
            positions.append(PortfolioPosition(
                asset_id=market_id,
                condition_id=market_id,
                question=f"Market {market_id}",  # Would fetch from API in production
                outcome=pos['side'],
                price=current_price,
                size=pos['shares'],
                svalue=current_value,
                pnl=pnl
            ))
            
            total_exposure += current_value
        
        # Update unrealized P&L
        self.unrealized_pnl = sum(p.pnl for p in positions)
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        
        return PortfolioSummary(
            balance=self.balance,
            exposure=total_exposure,
            positions=positions
        )
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics for the paper trading session.
        
        Returns:
            Dictionary with performance metrics
        """
        portfolio = self.get_portfolio()
        
        # Calculate win rate
        win_rate = (self.winning_trades / self.num_trades * 100) if self.num_trades > 0 else 0.0
        
        # Calculate total return
        total_value = self.balance + portfolio.exposure
        total_return = ((total_value - self.initial_balance) / self.initial_balance * 100)
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.balance,
            'total_value': total_value,
            'total_pnl': self.total_pnl,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_return_pct': total_return,
            'num_trades': self.num_trades,
            'win_rate': win_rate,
            'num_positions': len(self.positions),
            'total_exposure': portfolio.exposure
        }
    
    def reset(self):
        """Reset paper trading state (for testing or new session)."""
        self.balance = self.initial_balance
        self.positions.clear()
        self.open_orders.clear()
        self.trade_history.clear()
        self.total_pnl = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.num_trades = 0
        self.winning_trades = 0
        logger.info("Paper trading state reset")
