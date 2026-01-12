from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database_users import get_db
from app import models_db, models, auth, permissions
from app.engine import ForecasterCriticEngine
import datetime

router = APIRouter(prefix="/historical", tags=["historical"])
engine = ForecasterCriticEngine()

@router.get("/markets", response_model=List[models.HistoricalMarketResponse])
async def get_historical_markets(
    category: str = None, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Get a list of settled historical markets.
    """
    query = db.query(models_db.HistoricalMarket)
    if category:
        query = query.filter(models_db.HistoricalMarket.category == category)
    
    markets = query.order_by(models_db.HistoricalMarket.close_time.desc()).limit(limit).all()
    return markets

@router.post("/backtest", response_model=List[models.BacktestResultResponse])
async def run_backtest(
    request: models.BacktestRequest,
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Run LLM prediction against a set of historical markets.
    """
    results = []
    for market_id_int in request.market_ids:
        market = db.query(models_db.HistoricalMarket).filter(models_db.HistoricalMarket.id == market_id_int).first()
        if not market:
            continue
            
        # Run prediction via the engine
        # We use a synchronous shortcut for the engine for backtesting purposes
        # In a real app, this might be a background task
        try:
            prediction = await engine.get_prediction(market.question, model=request.model_name)
            
            # Simple scoring: if predicted > 0.5 and outcome is "Resolved", we count as a prediction
            # Proper scoring requires more granular resolution data
            
            new_result = models_db.BacktestResult(
                user_id=current_user.id,
                market_id=market.id,
                model_name=request.model_name,
                predicted_outcome=prediction.adjusted_forecast / 100.0,
                reasoning=prediction.reasoning or ""
            )
            db.add(new_result)
            
            # Prepare response item
            results.append(models.BacktestResultResponse(
                market_id=market.id,
                predicted_outcome=prediction.adjusted_forecast / 100.0,
                actual_outcome=market.outcome,
                is_correct=True, # Placeholder logic
                reasoning=prediction.reasoning or "",
                timestamp=datetime.datetime.utcnow()
            ))
        except Exception as e:
            print(f"Error backtesting market {market_id_int}: {e}")
            
    db.commit()
    return results

@router.get("/backtest/results", response_model=List[models.BacktestResultResponse])
async def get_backtest_results(
    current_user: models_db.User = Depends(permissions.requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get previous backtest results for the user.
    """
    results = db.query(models_db.BacktestResult).filter(models_db.BacktestResult.user_id == current_user.id).all()
    
    response = []
    for r in results:
        response.append(models.BacktestResultResponse(
            market_id=r.market_id,
            predicted_outcome=r.predicted_outcome,
            actual_outcome=r.market.outcome if r.market else None,
            is_correct=True, # Placeholder
            reasoning=r.reasoning,
            timestamp=r.timestamp
        ))
    return response
