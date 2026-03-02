from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.db.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(Float, default=lambda: datetime.utcnow().timestamp())
    
    # Vector embedding for semantic search (Dimension 1536 for OpenAI/many models, adjusting to 768 for local Llama if needed)
    # Using 4096 for Llama 3 / Mistral often, but 1024 or 768 common for smaller.
    # We will use 1024 as a safe default for now, or matched to the embedding model.
    # For now, just placeholder or specific size if known.
    embedding = Column(Vector(1024), nullable=True) 

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    name = Column(String)
    key_hash = Column(String, unique=True, index=True)
    prefix = Column(String)  # First a few chars for display
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class IpWhitelist(Base):
    __tablename__ = "ip_whitelists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    ip_address = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    action = Column(String, index=True) # e.g. LOGIN, TRADE, API_KEY_CREATED
    ip_address = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PolymarketMarket(Base):
    __tablename__ = "polymarket_markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condition_id = Column(String, unique=True, index=True)
    question = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String) # 'open', 'closed', 'resolved'
    category = Column(String, index=True)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class PolymarketOrderbook(Base):
    __tablename__ = "polymarket_orderbook"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("polymarket_markets.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    bids = Column(JSON) # List of [price, size]
    asks = Column(JSON) # List of [price, size]
    mid_price = Column(Float)
    spread = Column(Float)

class MarketInsight(Base):
    __tablename__ = "market_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("polymarket_markets.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    insight_type = Column(String) # 'basis', 'spread_movement', 'prediction'
    content = Column(Text)
    raw_data = Column(JSON)
    critic_score = Column(Float, nullable=True)
    critic_analysis = Column(Text, nullable=True)
    is_presented = Column(Boolean, default=False)

class NewsDocument(Base):
    __tablename__ = "news_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    content = Column(Text)
    source_url = Column(String, nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String, index=True) # e.g., 'geopolitics', 'policy', 'macro'
    
    # pgvector column for semantic search over news
    embedding = Column(Vector(1024), nullable=True)
