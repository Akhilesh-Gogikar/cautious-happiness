from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Index, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database_users import BaseUsers

class TaxLot(BaseUsers):
    """
    Represents an individual purchase lot for tax cost basis tracking.
    Supports FIFO, LIFO, and Specific Identification methods.
    """
    __tablename__ = "tax_lots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Exchange and Asset Information
    exchange = Column(String, index=True)  # "KALSHI" or "POLYMARKET"
    market_id = Column(String, index=True)  # Condition ID
    asset_id = Column(String, index=True)  # Token ID or specific asset identifier
    market_question = Column(String, nullable=True)
    
    # Lot Details
    purchase_date = Column(DateTime, index=True)
    shares_purchased = Column(Float)  # Original quantity
    shares_remaining = Column(Float)  # Remaining after partial sales
    cost_basis_per_share = Column(Float)  # Price paid per share
    total_cost_basis = Column(Float)  # Total amount paid
    
    # Status
    is_closed = Column(Boolean, default=False, index=True)  # True when shares_remaining = 0
    
    # Metadata
    trade_execution_id = Column(Integer, ForeignKey("trade_executions.id"), nullable=True)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tax_lots")
    transactions = relationship("TaxTransaction", secondary="tax_transaction_lots", back_populates="lots")
    
    __table_args__ = (
        Index('idx_user_exchange_asset', 'user_id', 'exchange', 'asset_id'),
        Index('idx_user_open_lots', 'user_id', 'is_closed', 'purchase_date'),
    )


class TaxTransaction(BaseUsers):
    """
    Records realized taxable events (sales, mark-to-market).
    Links to the specific lots that were sold/closed.
    """
    __tablename__ = "tax_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Transaction Type
    transaction_type = Column(String, index=True)  # "SALE", "MARK_TO_MARKET"
    
    # Exchange and Asset Information
    exchange = Column(String, index=True)  # "KALSHI" or "POLYMARKET"
    market_id = Column(String, index=True)
    asset_id = Column(String, index=True)
    market_question = Column(String, nullable=True)
    
    # Transaction Details
    transaction_date = Column(DateTime, index=True)
    shares = Column(Float)  # Quantity sold/closed
    proceeds = Column(Float)  # Sale price * shares
    cost_basis = Column(Float)  # Total cost basis of sold shares
    gain_loss = Column(Float)  # proceeds - cost_basis
    
    # Tax Classification
    holding_period_days = Column(Integer)  # Days held
    is_long_term = Column(Boolean)  # True if held > 365 days (for AlphaSignals)
    tax_year = Column(Integer, index=True)  # Year for tax reporting
    
    # Section 1256 Treatment (Kalshi)
    is_section_1256 = Column(Boolean, default=False)  # True for Kalshi
    long_term_portion = Column(Float, nullable=True)  # 60% of gain/loss for Section 1256
    short_term_portion = Column(Float, nullable=True)  # 40% of gain/loss for Section 1256
    
    # Wash Sale Adjustment (AlphaSignals only)
    wash_sale_disallowed = Column(Float, default=0.0)  # Loss disallowed due to wash sale
    adjusted_gain_loss = Column(Float, nullable=True)  # gain_loss - wash_sale_disallowed
    
    # Lot Matching
    lot_ids = Column(JSON, default=[])  # Array of TaxLot IDs used in this transaction
    matching_method = Column(String)  # "FIFO", "LIFO", "SPECID"
    
    # Metadata
    trade_execution_id = Column(Integer, ForeignKey("trade_executions.id"), nullable=True)
    notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tax_transactions")
    lots = relationship("TaxLot", secondary="tax_transaction_lots", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_user_tax_year', 'user_id', 'tax_year'),
        Index('idx_user_exchange_year', 'user_id', 'exchange', 'tax_year'),
        Index('idx_transaction_date', 'transaction_date'),
    )


# Association table for many-to-many relationship between TaxTransaction and TaxLot
class TaxTransactionLot(BaseUsers):
    """
    Links tax transactions to the specific lots that were sold.
    Allows tracking which lots contributed to each transaction.
    """
    __tablename__ = "tax_transaction_lots"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("tax_transactions.id"), index=True)
    lot_id = Column(Integer, ForeignKey("tax_lots.id"), index=True)
    shares_from_lot = Column(Float)  # How many shares from this lot were used
    cost_basis_from_lot = Column(Float)  # Cost basis contribution from this lot
    
    __table_args__ = (
        Index('idx_transaction_lot', 'transaction_id', 'lot_id'),
    )


class TaxSettings(BaseUsers):
    """
    User preferences for tax accounting methods.
    Can be configured per exchange and per tax year.
    """
    __tablename__ = "tax_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Accounting Methods
    kalshi_method = Column(String, default="FIFO")  # "FIFO", "LIFO", "SPECID"
    polymarket_method = Column(String, default="FIFO")  # "FIFO", "LIFO", "SPECID"
    
    # Wash Sale Detection (AlphaSignals only)
    enable_wash_sale_detection = Column(Boolean, default=True)
    
    # Tax Year
    tax_year = Column(Integer, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tax_settings")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'tax_year', name='uq_user_tax_year'),
    )


class WashSale(BaseUsers):
    """
    Tracks detected wash sale violations (AlphaSignals only).
    Wash sale: Selling at a loss and repurchasing within 30 days.
    """
    __tablename__ = "wash_sales"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Asset Information
    asset_id = Column(String, index=True)
    market_question = Column(String, nullable=True)
    
    # Wash Sale Details
    sale_transaction_id = Column(Integer, ForeignKey("tax_transactions.id"))
    sale_date = Column(DateTime, index=True)
    repurchase_date = Column(DateTime)
    
    # Financial Impact
    disallowed_loss = Column(Float)  # Loss that cannot be claimed
    adjusted_lot_id = Column(Integer, ForeignKey("tax_lots.id"))  # Lot with adjusted basis
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wash_sales")
    sale_transaction = relationship("TaxTransaction", foreign_keys=[sale_transaction_id])
    adjusted_lot = relationship("TaxLot", foreign_keys=[adjusted_lot_id])
    
    __table_args__ = (
        Index('idx_user_sale_date', 'user_id', 'sale_date'),
        Index('idx_asset_dates', 'asset_id', 'sale_date', 'repurchase_date'),
    )


# Add relationships to User model
from app.models_db import User
User.tax_lots = relationship("TaxLot", back_populates="user")
User.tax_transactions = relationship("TaxTransaction", back_populates="user")
User.tax_settings = relationship("TaxSettings", back_populates="user")
User.wash_sales = relationship("WashSale", back_populates="user")
