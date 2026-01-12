from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database_users import get_db
from app import models_db, permissions
from app.risk_engine import RiskEngine
from pydantic import BaseModel

router = APIRouter(prefix="/risk", tags=["risk"])
risk_engine = RiskEngine()


class ExposureLimitUpdate(BaseModel):
    factor: str
    limit_usd: float


class CorrelationMatrixUpdate(BaseModel):
    factor1: str
    factor2: str
    correlation: float


@router.get("/limits")
async def get_exposure_limits(
    current_user: models_db.User = Depends(permissions.requires_all_trade_view())
):
    """
    Get current exposure limits.
    Risk Managers and Developers can view limits.
    """
    return {"exposure_limits": risk_engine.exposure_limits}


@router.put("/limits")
async def update_exposure_limit(
    update: ExposureLimitUpdate,
    current_user: models_db.User = Depends(permissions.requires_risk_limit_set())
):
    """
    Update exposure limit for a specific factor.
    Only Risk Managers and Developers can update limits.
    """
    risk_engine.exposure_limits[update.factor] = update.limit_usd
    
    # Log the action
    return {
        "status": "success",
        "factor": update.factor,
        "new_limit": update.limit_usd
    }


@router.get("/correlation-matrix")
async def get_correlation_matrix(
    current_user: models_db.User = Depends(permissions.requires_all_trade_view())
):
    """
    Get the current correlation matrix.
    Risk Managers and Developers can view the correlation matrix.
    """
    return {"correlation_matrix": risk_engine.correlation_matrix}


@router.put("/correlation-matrix")
async def update_correlation(
    update: CorrelationMatrixUpdate,
    current_user: models_db.User = Depends(permissions.requires_risk_limit_set())
):
    """
    Update correlation between two factors.
    Only Risk Managers and Developers can update correlations.
    """
    if update.factor1 not in risk_engine.correlation_matrix:
        risk_engine.correlation_matrix[update.factor1] = {}
    
    risk_engine.correlation_matrix[update.factor1][update.factor2] = update.correlation
    
    # Also update the reverse for symmetry
    if update.factor2 not in risk_engine.correlation_matrix:
        risk_engine.correlation_matrix[update.factor2] = {}
    risk_engine.correlation_matrix[update.factor2][update.factor1] = update.correlation
    
    return {
        "status": "success",
        "factor1": update.factor1,
        "factor2": update.factor2,
        "correlation": update.correlation
    }


@router.get("/max-correlated-exposure")
async def get_max_correlated_exposure(
    current_user: models_db.User = Depends(permissions.requires_all_trade_view())
):
    """
    Get the maximum allowed correlated exposure.
    """
    return {"max_correlated_exposure": risk_engine.max_correlated_exposure}


@router.put("/max-correlated-exposure")
async def update_max_correlated_exposure(
    max_exposure: float,
    current_user: models_db.User = Depends(permissions.requires_risk_limit_set())
):
    """
    Update the maximum allowed correlated exposure.
    Only Risk Managers and Developers can update this.
    """
    risk_engine.max_correlated_exposure = max_exposure
    return {
        "status": "success",
        "max_correlated_exposure": max_exposure
    }


# Fat Finger Protection Endpoints
from app.models import RiskParametersRequest, RiskParametersResponse


@router.get("/fat-finger/parameters", response_model=RiskParametersResponse)
async def get_fat_finger_parameters(
    current_user: models_db.User = Depends(permissions.requires_all_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get fat finger protection parameters for the current user.
    Falls back to global defaults if user-specific parameters don't exist.
    """
    # Try to get user-specific parameters
    params = db.query(models_db.RiskParameter).filter(
        models_db.RiskParameter.user_id == current_user.id
    ).first()
    
    # Fall back to global defaults
    if not params:
        params = db.query(models_db.RiskParameter).filter(
            models_db.RiskParameter.user_id.is_(None)
        ).first()
    
    # If still no params, create default global params
    if not params:
        params = models_db.RiskParameter(
            user_id=None,
            max_order_size_usd=10000.0,
            max_price_deviation_pct=10.0,
            enabled=True
        )
        db.add(params)
        db.commit()
        db.refresh(params)
    
    return params


@router.put("/fat-finger/parameters", response_model=RiskParametersResponse)
async def update_fat_finger_parameters(
    req: RiskParametersRequest,
    current_user: models_db.User = Depends(permissions.requires_risk_limit_set()),
    db: Session = Depends(get_db)
):
    """
    Update fat finger protection parameters for the current user.
    Only Risk Managers and Developers can update parameters.
    """
    # Get or create user-specific parameters
    params = db.query(models_db.RiskParameter).filter(
        models_db.RiskParameter.user_id == current_user.id
    ).first()
    
    if not params:
        params = models_db.RiskParameter(user_id=current_user.id)
        db.add(params)
    
    # Update only provided fields
    if req.max_order_size_usd is not None:
        params.max_order_size_usd = req.max_order_size_usd
    if req.max_price_deviation_pct is not None:
        params.max_price_deviation_pct = req.max_price_deviation_pct
    if req.enabled is not None:
        params.enabled = req.enabled
    
    db.commit()
    db.refresh(params)
    
    return params


@router.put("/fat-finger/global-parameters", response_model=RiskParametersResponse)
async def update_global_fat_finger_parameters(
    req: RiskParametersRequest,
    current_user: models_db.User = Depends(permissions.requires_risk_limit_set()),
    db: Session = Depends(get_db)
):
    """
    Update global default fat finger protection parameters.
    Only Risk Managers and Developers can update global defaults.
    """
    # Get or create global parameters (user_id = NULL)
    params = db.query(models_db.RiskParameter).filter(
        models_db.RiskParameter.user_id.is_(None)
    ).first()
    
    if not params:
        params = models_db.RiskParameter(user_id=None)
        db.add(params)
    
    # Update only provided fields
    if req.max_order_size_usd is not None:
        params.max_order_size_usd = req.max_order_size_usd
    if req.max_price_deviation_pct is not None:
        params.max_price_deviation_pct = req.max_price_deviation_pct
    if req.enabled is not None:
        params.enabled = req.enabled
    
    db.commit()
    db.refresh(params)
    
    return params
