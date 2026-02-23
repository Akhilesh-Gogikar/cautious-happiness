from fastapi import APIRouter, Depends
from typing import List
from app.models import User
from app.core.auth import get_current_active_user
from app.cache import cache_response

router = APIRouter(
    prefix="/markets",
    tags=["markets"],
)

@router.get("")
@cache_response(ttl_seconds=30)
async def get_markets(current_user: User = Depends(get_current_active_user)):
    """
    Fetch active physical commodity instruments.
    """
    return [
        {
            "id": "brent_crude",
            "question": "Brent Crude Oil (Spot Physical)",
            "volume_24h": 1240000,
            "last_price": 0.82,
            "category": "Energy"
        },
        {
            "id": "wti_crude",
            "question": "WTI Crude Oil (Cushing Delivery)",
            "volume_24h": 980000,
            "last_price": 0.55,
            "category": "Energy"
        },
        {
            "id": "ttf_gas",
            "question": "Dutch TTF Natural Gas (Physical)",
            "volume_24h": 450000,
            "last_price": 0.91,
            "category": "Energy"
        },
        {
            "id": "lme_copper",
            "question": "LME Copper Grade A (Warehouse)",
            "volume_24h": 320000,
            "last_price": 0.42,
            "category": "Metals"
        },
        {
            "id": "iron_ore",
            "question": "Iron Ore 62% Fe (Tianjin Port)",
            "volume_24h": 150000,
            "last_price": 0.28,
            "category": "Metals"
        },
        {
            "id": "soybeans",
            "question": "Soybeans (US No. 2 Yellow)",
            "volume_24h": 85000,
            "last_price": 0.64,
            "category": "Agri"
        }
    ]
