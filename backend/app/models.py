from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    title: str
    url: str
    snippet: str

class AnalysisComponent(BaseModel):
    reasoning: str
    score: float

class MirrorAnalysis(AnalysisComponent):
    pass

class NoiseAnalysis(AnalysisComponent):
    pass

class DivergenceAnalysis(AnalysisComponent):
    pass

class AlgoAnalysis(AnalysisComponent):
    pass

class StructuredAnalysisResult(BaseModel):
    mirror: MirrorAnalysis
    noise: NoiseAnalysis
    divergence: DivergenceAnalysis
    algo: AlgoAnalysis

class ForecastResult(BaseModel):
    search_query: str
    news_summary: List[Source]
    initial_forecast: float
    critique: str
    adjusted_forecast: float
    reasoning: Optional[str] = None
    error: Optional[str] = None
    # Modular components
    mirror: Optional[MirrorAnalysis] = None
    noise: Optional[NoiseAnalysis] = None
    divergence: Optional[DivergenceAnalysis] = None
    algo: Optional[AlgoAnalysis] = None
    # Adversarial Red-Teaming fields
    adversarial_score: float = 0.0
    logical_fallacies: List[str] = []
    counter_arguments: List[str] = []

    @classmethod
    def from_analysis(cls, question: str, all_sources: List[Source], avg_score: float, critique: str, adj_prob: float, reasoning: str, analysis: Optional[StructuredAnalysisResult] = None, critue_data=None):
        """Builds a ForecastResult from analysis components, automating mapping."""
        return cls(
            search_query=question,
            news_summary=all_sources,
            initial_forecast=avg_score,
            critique=critique,
            adjusted_forecast=adj_prob,
            reasoning=reasoning,
            mirror=analysis.mirror if analysis else None,
            noise=analysis.noise if analysis else None,
            divergence=analysis.divergence if analysis else None,
            algo=analysis.algo if analysis else None,
            adversarial_score=getattr(critue_data, 'adversarial_score', 0.0) if hasattr(critue_data, 'adversarial_score') else 0.0,
            logical_fallacies=getattr(critue_data, 'logical_fallacies', []) if hasattr(critue_data, 'logical_fallacies') else [],
            counter_arguments=getattr(critue_data, 'counter_arguments', []) if hasattr(critue_data, 'counter_arguments') else []
        )

# Auth Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None
    role: str = "analyst"  # admin, trader, analyst, risk_manager

class UserInDB(User):
    hashed_password: str

# Chat Models
class ChatContext(BaseModel):
    route_path: str
    client_state: Optional[dict] = None  # Key-value pairs of current view state

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: float

class ChatRequest(BaseModel):
    question: str
    history: List[ChatMessage] = []
    context: Optional[ChatContext] = None
    model: str = "lfm-thinking"

class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[dict]] = None

