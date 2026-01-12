import logging
from typing import Optional, Dict, Any
from app.models import OrderBook

logger = logging.getLogger(__name__)


class OrderValidationError(Exception):
    """Raised when an order fails fat finger validation."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class FatFingerValidator:
    """
    Pre-trade risk checks to prevent erroneous orders.
    
    Validates orders against:
    - Price deviation from last traded price
    - Maximum order size limits
    """
    
    def __init__(
        self, 
        max_price_deviation_pct: float = 10.0,
        max_order_size_usd: float = 10000.0,
        enabled: bool = True
    ):
        """
        Initialize the validator with risk parameters.
        
        Args:
            max_price_deviation_pct: Maximum allowed price deviation percentage (default: 10%)
            max_order_size_usd: Maximum order size in USD (default: $10,000)
            enabled: Whether validation is active (default: True)
        """
        self.max_price_deviation_pct = max_price_deviation_pct
        self.max_order_size_usd = max_order_size_usd
        self.enabled = enabled
        
    def validate_order(
        self, 
        order_size_usd: float,
        order_price: Optional[float],
        order_book: Optional[OrderBook],
        market_id: str
    ) -> None:
        """
        Validate an order against fat finger rules.
        
        Args:
            order_size_usd: Order size in USD
            order_price: Limit price for the order (None for market orders)
            order_book: Current order book for the market
            market_id: Market identifier
            
        Raises:
            OrderValidationError: If validation fails
        """
        if not self.enabled:
            logger.debug("Fat finger validation disabled, skipping checks")
            return
            
        # Check 1: Order Size Limit
        self._check_size_limit(order_size_usd, market_id)
        
        # Check 2: Price Deviation (only for limit orders with order book data)
        if order_price is not None and order_book is not None:
            self._check_price_deviation(order_price, order_book, market_id)
            
        logger.info(f"Order validation passed for market {market_id}")
        
    def _check_size_limit(self, order_size_usd: float, market_id: str) -> None:
        """
        Check if order size exceeds maximum limit.
        
        Args:
            order_size_usd: Order size in USD
            market_id: Market identifier
            
        Raises:
            OrderValidationError: If size exceeds limit
        """
        if order_size_usd > self.max_order_size_usd:
            error_msg = (
                f"Order size ${order_size_usd:,.2f} exceeds maximum allowed "
                f"${self.max_order_size_usd:,.2f}"
            )
            logger.warning(f"FAT FINGER BLOCK: {error_msg} for market {market_id}")
            raise OrderValidationError(
                message=error_msg,
                error_code="SIZE_LIMIT_EXCEEDED",
                details={
                    "order_size_usd": order_size_usd,
                    "max_order_size_usd": self.max_order_size_usd,
                    "market_id": market_id
                }
            )
            
    def _check_price_deviation(
        self, 
        order_price: float, 
        order_book: OrderBook, 
        market_id: str
    ) -> None:
        """
        Check if order price deviates significantly from last traded price.
        
        Args:
            order_price: Limit price for the order
            order_book: Current order book
            market_id: Market identifier
            
        Raises:
            OrderValidationError: If price deviation exceeds threshold
        """
        last_traded_price = self._get_last_traded_price(order_book)
        
        if last_traded_price is None:
            logger.warning(f"Cannot determine last traded price for {market_id}, skipping price check")
            return
            
        # Calculate deviation percentage
        deviation_pct = abs((order_price - last_traded_price) / last_traded_price) * 100
        
        if deviation_pct > self.max_price_deviation_pct:
            error_msg = (
                f"Order price ${order_price:.4f} deviates {deviation_pct:.2f}% from "
                f"last traded price ${last_traded_price:.4f} (max allowed: "
                f"{self.max_price_deviation_pct:.2f}%)"
            )
            logger.warning(f"FAT FINGER BLOCK: {error_msg} for market {market_id}")
            raise OrderValidationError(
                message=error_msg,
                error_code="PRICE_DEVIATION_EXCEEDED",
                details={
                    "order_price": order_price,
                    "last_traded_price": last_traded_price,
                    "deviation_pct": deviation_pct,
                    "max_deviation_pct": self.max_price_deviation_pct,
                    "market_id": market_id
                }
            )
            
    def _get_last_traded_price(self, order_book: OrderBook) -> Optional[float]:
        """
        Extract reference price from order book.
        
        Uses mid-price (average of best bid and best ask) as proxy for last traded price.
        
        Args:
            order_book: Current order book
            
        Returns:
            Last traded price, or None if cannot be determined
        """
        if not order_book.asks or not order_book.bids:
            return None
            
        best_ask = order_book.asks[0].price
        best_bid = order_book.bids[0].price
        
        # Use mid-price as reference
        mid_price = (best_ask + best_bid) / 2.0
        
        logger.debug(f"Reference price (mid): ${mid_price:.4f} (bid: ${best_bid:.4f}, ask: ${best_ask:.4f})")
        return mid_price
        
    def update_parameters(
        self,
        max_price_deviation_pct: Optional[float] = None,
        max_order_size_usd: Optional[float] = None,
        enabled: Optional[bool] = None
    ) -> None:
        """
        Update risk parameters dynamically.
        
        Args:
            max_price_deviation_pct: New maximum price deviation percentage
            max_order_size_usd: New maximum order size
            enabled: Whether to enable/disable validation
        """
        if max_price_deviation_pct is not None:
            self.max_price_deviation_pct = max_price_deviation_pct
            logger.info(f"Updated max_price_deviation_pct to {max_price_deviation_pct}%")
            
        if max_order_size_usd is not None:
            self.max_order_size_usd = max_order_size_usd
            logger.info(f"Updated max_order_size_usd to ${max_order_size_usd:,.2f}")
            
        if enabled is not None:
            self.enabled = enabled
            logger.info(f"Fat finger validation {'enabled' if enabled else 'disabled'}")
