from fastapi import APIRouter
from typing import List

from app.domain.intelligence.feed_manager import feed_manager
from app.domain.intelligence.models import NewsItem

router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
    responses={404: {"description": "Not found"}},
)


# Plain def: FastAPI runs it in the threadpool, so the RSS fetches and the first
# (lazy) FinBERT load do not block the event loop.
@router.get("/news", response_model=List[NewsItem])
def get_news():
    return feed_manager.fetch_news()


@router.get("/status")
async def get_status():
    from app.domain.intelligence.sentiment import sentiment_analyzer

    return {
        "model_loaded": sentiment_analyzer.pipeline is not None,
        "model_name": sentiment_analyzer.model_name,
    }
