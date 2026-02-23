from sqlalchemy import Column, Integer, String, Float, Text, DateTime
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
