from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Source(BaseModel):
    id: str
    url: str
    domain: str
    title: str
    snippet: str
    published_at: Optional[datetime] = None


class Competitor(BaseModel):
    id: str
    name: str
    description: str
    tracked_urls: List[str]
    last_active: Optional[datetime] = None


class AnalysisResult(BaseModel):
    target_id: str
    sentiment_score: float
    crowd_conviction: float
    summary: str
    key_phrases: List[str]
    sources: List[Source] = Field(default_factory=list)
    analysis_status: str = "completed"
    timestamp: datetime = Field(default_factory=datetime.now)
