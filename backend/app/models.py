from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    title: str
    url: str
    snippet: str

class ForecastResult(BaseModel):
    search_query: str
    news_summary: List[Source]
    initial_forecast: float
    critique: str
    adjusted_forecast: float
    reasoning: Optional[str] = None
    error: Optional[str] = None # Added for error handling

class ChatRequest(BaseModel):
    question: str
    context: str # The previous reasoning/news
    user_message: str
    model: str = "openforecaster"

class ChatResponse(BaseModel):
    response: str
