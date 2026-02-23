from pydantic import BaseModel, Field
from typing import Optional

class StructuredCriticResult(BaseModel):
    critique: str = Field(..., description="A concise risk-adjusted critique of the intelligence.")
    score: float = Field(..., description="The adjusted mirror score (0.0 to 1.0).")
    risk_factors: Optional[list[str]] = Field(default_factory=list, description="List of identified risk factors.")
    adversarial_score: float = Field(default=0.0, description="Thesis fragility score (0-10), where higher means more fragile.")
    logical_fallacies: Optional[list[str]] = Field(default_factory=list, description="Identified gaps or fallacies in the analyst reasoning.")
    counter_arguments: Optional[list[str]] = Field(default_factory=list, description="Specific arguments designed to break the thesis.")

class MirrorAnalysis(BaseModel):
    score: float
    reasoning: str

class NoiseAnalysis(BaseModel):
    score: float
    reasoning: str

class DivergenceAnalysis(BaseModel):
    score: float
    reasoning: str

class AlgoAnalysis(BaseModel):
    score: float
    reasoning: str

class StructuredAnalysisResult(BaseModel):
    mirror: MirrorAnalysis
    noise: NoiseAnalysis
    divergence: DivergenceAnalysis
    algo: AlgoAnalysis
