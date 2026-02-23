from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    target_id: str  # Competitor ID or Market ID
    sentiment_score: float  # -1.0 to 1.0
    crowd_conviction: float  # 0.0 to 1.0
    summary: str
    key_phrases: List[str]
    timestamp: datetime = datetime.now()
