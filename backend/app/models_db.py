from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    security_question = relationship("SecurityQuestion", back_populates="user", uselist=False)
    logs = relationship("ActionLog", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, default="")
    role = Column(String, default="user") # 'user', 'admin', 'institution'
    preferences = Column(JSON, default={})
    
    user = relationship("User", back_populates="profile")

class SecurityQuestion(Base):
    __tablename__ = "security_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(String)
    hashed_answer = Column(String)

    user = relationship("User", back_populates="security_question")

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # e.g. "LOGIN", "TRADE", "VIEW_PROFILE"
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={}) # Stores specific info about the action (e.g. trade_id)

    user = relationship("User", back_populates="logs")
