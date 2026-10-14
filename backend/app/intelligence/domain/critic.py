from __future__ import annotations

import logging
from typing import List

from app.core.ai_client import ai_client
from app.intelligence.domain.dtypes import StructuredCriticResult
from app.models import Source

logger = logging.getLogger("alpha_insights")


CRITIC_SCHEMA = {
    "type": "object",
    "properties": {
        "critique": {"type": "string"},
        # llama-server's grammar ignores minimum/maximum on numbers; the score
        # is clamped after parsing instead.
        "score": {"type": "number"},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["critique", "score", "risk_factors"],
}


class CriticService:
    async def critique_forecast(self, question: str, sources: List[Source], initial_prob: float, initial_reasoning: str) -> StructuredCriticResult:
        news_text = "\n".join([f"- {source.title}: {source.snippet}" for source in sources])
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
    "score": float (the adjusted mirror score, 0.0 to 1.0),
    "risk_factors": ["string"]
}}
[/INST]
"""
        try:
            result = await self._critique(prompt)
            result.score = min(1.0, max(0.0, result.score))
            return result
        except Exception as exc:
            return StructuredCriticResult(
                critique=f"Critic unavailable: {exc}",
                score=initial_prob,
                risk_factors=[f"System Error: {exc}"],
            )

    async def _critique(self, prompt: str) -> StructuredCriticResult:
        if "gemini" in ai_client.providers:
            try:
                return StructuredCriticResult(
                    **await ai_client.generate_json(prompt, provider="gemini", model="gemini-1.5-flash")
                )
            except Exception as exc:
                # Log the type only; the message can include request details.
                logger.warning(f"Gemini critic failed ({type(exc).__name__}); using the local model")
        # The local model that docker compose serves.
        raw_json = await ai_client.generate_json(
            prompt,
            provider="llama-cpp",
            model="lfm-thinking",
            json_schema=CRITIC_SCHEMA,
        )
        return StructuredCriticResult(**raw_json)
