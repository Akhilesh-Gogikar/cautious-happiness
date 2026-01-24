from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app import models_db, database_users, permissions

router = APIRouter(
    prefix="/proposed-trades",
    tags=["proposed-trades"]
)

class ProposedTradeResponse(BaseModel):
    id: int
    title: str
    description: str
    link: str
    pub_date: datetime
    ai_analysis: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProposedTradeResponse])
def get_proposed_trades(
    status_filter: Optional[str] = "NEW",
    db: Session = Depends(database_users.get_db),
    current_user: models_db.User = Depends(permissions.get_current_active_user)
):
    """
    Get all proposed trades, optionally filtered by status.
    """
    query = db.query(models_db.ProposedTrade)
    if status_filter:
        query = query.filter(models_db.ProposedTrade.status == status_filter)
    
    return query.order_by(models_db.ProposedTrade.pub_date.desc()).all()

@router.post("/{trade_id}/dismiss")
def dismiss_trade(
    trade_id: int,
    db: Session = Depends(database_users.get_db),
    current_user: models_db.User = Depends(permissions.requires_trade_execute())
):
    """
    Dismiss a proposed trade.
    """
    trade = db.query(models_db.ProposedTrade).filter(models_db.ProposedTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    trade.status = "DISMISSED"
    db.commit()
    return {"status": "success", "message": "Trade dismissed"}

@router.post("/{trade_id}/accept")
def accept_trade(
    trade_id: int,
    db: Session = Depends(database_users.get_db),
    current_user: models_db.User = Depends(permissions.requires_trade_execute())
):
    """
    Accept a proposed trade (marks as ACCEPTED).
    In a full implementation, this might trigger creating a Thread or AlgoOrder.
    """
    trade = db.query(models_db.ProposedTrade).filter(models_db.ProposedTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    trade.status = "ACCEPTED"
    db.commit()
    return {"status": "success", "message": "Trade accepted"}
