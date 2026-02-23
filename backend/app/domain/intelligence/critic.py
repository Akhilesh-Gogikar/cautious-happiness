import os
from typing import List, Tuple
from app.models import Source
from app.domain.intelligence.dtypes import StructuredCriticResult
from app.core.ai_client import ai_client

class CriticService:
    def __init__(self):
        pass

    async def critique_forecast(self, question: str, sources: List[Source], initial_prob: float, initial_reasoning: str) -> StructuredCriticResult:
        """
        Send the forecast to the unified AI client to check for hallucinations and bias.
        """
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"""
[INST] 
Role: Head of Commodity Risk (Hedge Fund Internal Audit)
Task: Perform a high-fidelity "Intelligence Audit" on the mirror analysis for "{question}".

Market Data:
{news_text}

Proposed Forecast:
- Adjusted Mirror Score: {initial_prob}
- Analyst Reasoning: {initial_reasoning}

OUTPUT SCHEMA (STRICT JSON):
{{
    "critique": "string",
    "score": float,
    "risk_factors": ["string"]
}}
[/INST]
"""
        try:
            # Prefer Gemini for criticism if available, otherwise fallback
            provider = "gemini" if "gemini" in ai_client.providers else "ollama"
            raw_json = await ai_client.generate_json(prompt, provider=provider, model="gemini-1.5-flash" if provider == "gemini" else "ollama-critic")
            return StructuredCriticResult(**raw_json)

        except Exception as e:
            print(f"Critic Failed: {e}")
            return StructuredCriticResult(
                critique=f"Critic unavailable: {str(e)}",
                score=initial_prob,
                risk_factors=[f"System Error: {str(e)}"]
            )
