from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter(prefix="/api/v1/scanner", tags=["scanner"])

class AssetScanResult(BaseModel):
    symbol: str
    name: str
    asset_class: str
    sector: str
    price: float
    physical_premium: float
    mirror_accuracy: float
    algo_noise: str
    signal: str

import math
import time

# Dynamic data generator for Alpha Scanner avoiding static hard-coding
def generate_mock_assets() -> List[AssetScanResult]:
    assets = [
        {"symbol": "BRENT", "name": "Brent Crude Oil", "class": "commodity", "sector": "energy"},
        {"symbol": "WTI", "name": "WTI Crude Oil", "class": "commodity", "sector": "energy"},
        {"symbol": "NGAS", "name": "Natural Gas", "class": "commodity", "sector": "energy"},
        {"symbol": "XOM", "name": "ExxonMobil", "class": "equity", "sector": "energy"},
        {"symbol": "CVX", "name": "Chevron", "class": "equity", "sector": "energy"},
        {"symbol": "OXY", "name": "Occidental Petroleum", "class": "equity", "sector": "energy"},
        {"symbol": "COP", "name": "ConocoPhillips", "class": "equity", "sector": "energy"},
        {"symbol": "BP", "name": "BP plc", "class": "equity", "sector": "energy"},
        {"symbol": "SHEL", "name": "Shell plc", "class": "equity", "sector": "energy"},
        {"symbol": "HAL", "name": "Halliburton", "class": "equity", "sector": "energy"},
        {"symbol": "SLB", "name": "Schlumberger", "class": "equity", "sector": "energy"},
        {"symbol": "GOLD", "name": "Gold", "class": "commodity", "sector": "metals"},
        {"symbol": "SILV", "name": "Silver", "class": "commodity", "sector": "metals"},
        {"symbol": "COPPER", "name": "Copper", "class": "commodity", "sector": "metals"}
    ]
    
    results = []
    current_time = time.time()
    
    for a in assets:
        # Create a unique but stable phase shift based on symbol
        seed = float(hash(a["symbol"]) % 10000) / 10000.0
        
        # Simulate price moving every second over an hour scale and daily scale
        # Base anchor varies per asset
        anchor_price = 100.0 if a["class"] == "equity" else 50.0
        
        # Fluctuation based on multiple sine waves for realism
        fast_wave = math.sin((current_time / 60.0) + (seed * math.pi * 2)) # Minute frequency
        slow_wave = math.sin((current_time / 3600.0) + (seed * math.pi * 2)) # Hourly frequency
        
        # Price: Anchor + up to 20% variance (10% slow, 10% fast)
        fluctuation = (fast_wave * 0.1) + (slow_wave * 0.1)
        price = anchor_price * (1.0 + fluctuation)
        
        # Energy assets have higher premiums in this simulation
        prem_modifier = 2.5 if a["sector"] == "energy" else 0.5
        phys_premium = (math.cos((current_time / 120.0) + seed) * 3.0 + 2.0) * prem_modifier
        
        # Accuracy fluctuates slightly
        accuracy = 85.0 + (math.sin(current_time / 300.0 + seed) * 14.9)
        
        # Signal changes based on derivative of the fast wave
        momentum = math.cos((current_time / 60.0) + (seed * math.pi * 2))
        
        if momentum > 0.7: signal = "STRONG_BUY"
        elif momentum > 0.2: signal = "BUY"
        elif momentum > -0.2: signal = "NEUTRAL"
        elif momentum > -0.7: signal = "SELL"
        else: signal = "STRONG_SELL"
            
        noise_levels = ["Low", "Medium", "High", "Critical"]
        noise_idx = int(((math.sin(current_time / 45.0 + seed) + 1) / 2) * 3.99)
        
        results.append(AssetScanResult(
            symbol=a["symbol"],
            name=a["name"],
            asset_class=a["class"],
            sector=a["sector"],
            price=round(price, 2),
            physical_premium=round(phys_premium, 2),
            mirror_accuracy=round(accuracy, 1),
            algo_noise=noise_levels[noise_idx],
            signal=signal
        ))
    return results

@router.get("/assets", response_model=List[AssetScanResult])
async def scan_assets(
    min_physical_premium: Optional[float] = Query(None, description="Minimum physical premium threshold"),
    min_mirror_accuracy: Optional[float] = Query(None, description="Minimum mirror accuracy threshold (%)"),
    asset_class: Optional[str] = Query(None, description="Filter by asset class (e.g., commodity, equity)"),
    sector: Optional[str] = Query(None, description="Filter by sector (e.g., energy, metals)")
):
    """
    High-speed screening endpoint to filter assets by proprietary AI metrics.
    """
    filtered_assets = generate_mock_assets()

    if min_physical_premium is not None:
        filtered_assets = [a for a in filtered_assets if a.physical_premium >= min_physical_premium]
        
    if min_mirror_accuracy is not None:
        filtered_assets = [a for a in filtered_assets if a.mirror_accuracy >= min_mirror_accuracy]
        
    if asset_class:
        filtered_assets = [a for a in filtered_assets if a.asset_class.lower() == asset_class.lower()]
        
    if sector:
        filtered_assets = [a for a in filtered_assets if a.sector.lower() == sector.lower()]

    # Sort by mirror accuracy descending by default for best matches first
    filtered_assets.sort(key=lambda x: x.mirror_accuracy, reverse=True)
    
    return filtered_assets
