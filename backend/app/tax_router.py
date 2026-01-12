from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database_users import get_db
from app.auth import get_current_user
from app.models_db import User
from app.permissions import requires_trade_view
from app.tax_models import TaxLot, TaxTransaction, TaxSettings, WashSale
from app.tax_lot_service import TaxLotManager
from app.tax_calculator import TaxCalculator

router = APIRouter(prefix="/api/tax", tags=["Tax Accounting"])


# Pydantic Models for API

class TaxSettingsUpdate(BaseModel):
    kalshi_method: Optional[str] = None  # "FIFO", "LIFO", "SPECID"
    polymarket_method: Optional[str] = None
    enable_wash_sale_detection: Optional[bool] = None
    tax_year: Optional[int] = None


class TaxSettingsResponse(BaseModel):
    id: int
    user_id: int
    kalshi_method: str
    polymarket_method: str
    enable_wash_sale_detection: bool
    tax_year: int
    
    class Config:
        from_attributes = True


class TaxLotResponse(BaseModel):
    id: int
    exchange: str
    market_id: str
    asset_id: str
    market_question: Optional[str]
    purchase_date: datetime
    shares_purchased: float
    shares_remaining: float
    cost_basis_per_share: float
    total_cost_basis: float
    is_closed: bool
    
    class Config:
        from_attributes = True


class TaxTransactionResponse(BaseModel):
    id: int
    transaction_type: str
    exchange: str
    market_question: Optional[str]
    transaction_date: datetime
    shares: float
    proceeds: float
    cost_basis: float
    gain_loss: float
    holding_period_days: int
    is_long_term: bool
    tax_year: int
    is_section_1256: bool
    long_term_portion: Optional[float]
    short_term_portion: Optional[float]
    wash_sale_disallowed: float
    matching_method: str
    
    class Config:
        from_attributes = True


class SpecificIdSaleRequest(BaseModel):
    exchange: str
    asset_id: str
    shares: float
    price: float
    lot_ids: List[int]
    market_id: Optional[str] = None
    market_question: Optional[str] = None


# Tax Settings Endpoints

@router.get("/settings", response_model=TaxSettingsResponse)
async def get_tax_settings(
    tax_year: Optional[int] = Query(None, description="Tax year (defaults to current year)"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get user's tax accounting settings.
    """
    if tax_year is None:
        tax_year = datetime.now().year
    
    settings = db.query(TaxSettings).filter(
        TaxSettings.user_id == current_user.id,
        TaxSettings.tax_year == tax_year
    ).first()
    
    if not settings:
        # Create default settings
        settings = TaxSettings(
            user_id=current_user.id,
            tax_year=tax_year,
            kalshi_method="FIFO",
            polymarket_method="FIFO",
            enable_wash_sale_detection=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/settings", response_model=TaxSettingsResponse)
async def update_tax_settings(
    settings_update: TaxSettingsUpdate,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Update tax accounting method preferences.
    """
    tax_year = settings_update.tax_year or datetime.now().year
    
    settings = db.query(TaxSettings).filter(
        TaxSettings.user_id == current_user.id,
        TaxSettings.tax_year == tax_year
    ).first()
    
    if not settings:
        settings = TaxSettings(user_id=current_user.id, tax_year=tax_year)
        db.add(settings)
    
    # Update fields
    if settings_update.kalshi_method:
        if settings_update.kalshi_method not in ["FIFO", "LIFO", "SPECID"]:
            raise HTTPException(400, "Invalid kalshi_method")
        settings.kalshi_method = settings_update.kalshi_method
    
    if settings_update.polymarket_method:
        if settings_update.polymarket_method not in ["FIFO", "LIFO", "SPECID"]:
            raise HTTPException(400, "Invalid polymarket_method")
        settings.polymarket_method = settings_update.polymarket_method
    
    if settings_update.enable_wash_sale_detection is not None:
        settings.enable_wash_sale_detection = settings_update.enable_wash_sale_detection
    
    db.commit()
    db.refresh(settings)
    
    return settings


# Tax Lot Endpoints

@router.get("/lots", response_model=List[TaxLotResponse])
async def get_tax_lots(
    exchange: Optional[str] = Query(None, description="Filter by exchange (KALSHI or POLYMARKET)"),
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    is_closed: Optional[bool] = Query(None, description="Filter by open/closed status"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    List all tax lots with optional filters.
    """
    query = db.query(TaxLot).filter(TaxLot.user_id == current_user.id)
    
    if exchange:
        query = query.filter(TaxLot.exchange == exchange.upper())
    
    if asset_id:
        query = query.filter(TaxLot.asset_id == asset_id)
    
    if is_closed is not None:
        query = query.filter(TaxLot.is_closed == is_closed)
    
    lots = query.order_by(TaxLot.purchase_date.desc()).all()
    return lots


@router.get("/lots/{asset_id}/cost-basis")
async def get_cost_basis(
    asset_id: str,
    exchange: str = Query(..., description="KALSHI or POLYMARKET"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get current cost basis for a specific asset.
    """
    lot_manager = TaxLotManager(db)
    cost_basis = lot_manager.get_cost_basis(
        current_user.id,
        exchange,
        asset_id
    )
    
    return cost_basis


# Tax Transaction Endpoints

@router.get("/transactions/{tax_year}", response_model=List[TaxTransactionResponse])
async def get_tax_transactions(
    tax_year: int,
    exchange: Optional[str] = Query(None, description="Filter by exchange"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get all taxable transactions for a tax year.
    """
    query = db.query(TaxTransaction).filter(
        TaxTransaction.user_id == current_user.id,
        TaxTransaction.tax_year == tax_year
    )
    
    if exchange:
        query = query.filter(TaxTransaction.exchange == exchange.upper())
    
    transactions = query.order_by(TaxTransaction.transaction_date.desc()).all()
    return transactions


# Tax Report Endpoints

@router.get("/summary/{tax_year}")
async def get_tax_summary(
    tax_year: int,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive tax summary for the year.
    """
    calculator = TaxCalculator(db)
    summary = calculator.generate_tax_summary(current_user.id, tax_year)
    return summary


@router.get("/form-6781/{tax_year}")
async def get_form_6781(
    tax_year: int,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Generate Form 6781 data for Section 1256 contracts (Kalshi).
    """
    calculator = TaxCalculator(db)
    form_data = calculator.generate_form_6781_data(current_user.id, tax_year)
    return form_data


@router.get("/form-8949/{tax_year}")
async def get_form_8949(
    tax_year: int,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Generate Form 8949 / Schedule D data for capital gains (AlphaSignals).
    """
    calculator = TaxCalculator(db)
    form_data = calculator.generate_form_8949_data(current_user.id, tax_year)
    return form_data


@router.get("/export/{tax_year}")
async def export_tax_data(
    tax_year: int,
    format: str = Query("json", description="Export format: json, csv"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Export tax data in various formats.
    """
    calculator = TaxCalculator(db)
    summary = calculator.generate_tax_summary(current_user.id, tax_year)
    
    if format == "csv":
        # Convert to CSV format
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write Kalshi transactions
        writer.writerow(["KALSHI - Section 1256 Contracts"])
        writer.writerow(["Date", "Market", "Shares", "Proceeds", "Cost Basis", "Gain/Loss", "LT Portion (60%)", "ST Portion (40%)"])
        
        for txn in summary["kalshi_details"]["transactions"]:
            writer.writerow([
                txn["transaction_date"],
                txn["market_question"],
                txn["shares"],
                txn["proceeds"],
                txn["cost_basis"],
                txn["gain_loss"],
                txn["long_term_portion"],
                txn["short_term_portion"]
            ])
        
        writer.writerow([])
        
        # Write AlphaSignals transactions
        writer.writerow(["POLYMARKET - Capital Gains"])
        writer.writerow(["Date", "Market", "Shares", "Proceeds", "Cost Basis", "Gain/Loss", "Holding Period", "Type"])
        
        for txn in summary["polymarket_details"]["short_term_transactions"]:
            writer.writerow([
                txn["transaction_date"],
                txn["market_question"],
                txn["shares"],
                txn["proceeds"],
                txn["cost_basis"],
                txn["gain_loss"],
                f"{txn['holding_period_days']} days",
                "Short-Term"
            ])
        
        for txn in summary["polymarket_details"]["long_term_transactions"]:
            writer.writerow([
                txn["transaction_date"],
                txn["market_question"],
                txn["shares"],
                txn["proceeds"],
                txn["cost_basis"],
                txn["gain_loss"],
                f"{txn['holding_period_days']} days",
                "Long-Term"
            ])
        
        from fastapi.responses import StreamingResponse
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=tax_report_{tax_year}.csv"}
        )
    
    return summary


# Tax Optimization Endpoints

@router.get("/loss-harvesting")
async def get_loss_harvesting_opportunities(
    min_loss: float = Query(100.0, description="Minimum loss threshold"),
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Identify tax loss harvesting opportunities.
    Note: Requires current market prices to be provided separately.
    """
    # This endpoint would need current prices from the market client
    # For now, return a placeholder response
    return {
        "message": "Tax loss harvesting requires current market prices",
        "instructions": "Use the /tax/loss-harvesting-with-prices endpoint with current price data"
    }


@router.post("/specific-id-sale")
async def execute_specific_id_sale(
    request: SpecificIdSaleRequest,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Execute a sale using specific lot identification.
    This allows users to choose exactly which lots to sell for tax optimization.
    """
    lot_manager = TaxLotManager(db)
    
    try:
        transaction = lot_manager.record_sale(
            user_id=current_user.id,
            exchange=request.exchange,
            asset_id=request.asset_id,
            shares=request.shares,
            price=request.price,
            sale_date=datetime.now(),
            method="SPECID",
            specific_lot_ids=request.lot_ids,
            market_id=request.market_id,
            market_question=request.market_question
        )
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "gain_loss": transaction.gain_loss,
            "tax_treatment": "Section 1256 (60/40)" if transaction.is_section_1256 else "Capital Gains",
            "message": "Sale recorded with specific lot identification"
        }
    
    except Exception as e:
        raise HTTPException(400, str(e))


# Wash Sale Information

@router.get("/wash-sales/{tax_year}")
async def get_wash_sales(
    tax_year: int,
    current_user: User = Depends(requires_trade_view()),
    db: Session = Depends(get_db)
):
    """
    Get all wash sale violations for a tax year.
    """
    calculator = TaxCalculator(db)
    wash_sales = calculator.apply_wash_sale_adjustments(current_user.id, tax_year)
    return wash_sales
