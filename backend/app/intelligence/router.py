from fastapi import APIRouter, HTTPException
from typing import List
from app.intelligence.models import NewsItem
from app.intelligence.feed_manager import feed_manager

router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
    responses={404: {"description": "Not found"}},
)

@router.get("/news", response_model=List[NewsItem])
async def get_news():
    """
    Get latest news with sentiment analysis.
    """
    return feed_manager.fetch_news()

@router.get("/status")
async def get_status():
    """
    Check status of the intelligence module (e.g., model loaded).
    """
    from app.intelligence.sentiment import sentiment_analyzer
    return {
        "model_loaded": sentiment_analyzer.pipeline is not None,
        "model_name": sentiment_analyzer.model_name
    }
