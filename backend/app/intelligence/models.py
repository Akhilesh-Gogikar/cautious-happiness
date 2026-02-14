from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SentimentScore(BaseModel):
    label: str  # "positive", "negative", "neutral"
    score: float # Confidence score (0.0 - 1.0)

class NewsItem(BaseModel):
    id: str
    title: str
    link: str
    published_at: datetime
    source: str
    summary: Optional[str] = None
    sentiment: Optional[SentimentScore] = None
