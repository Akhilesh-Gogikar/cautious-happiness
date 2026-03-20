from __future__ import annotations

import json
from datetime import datetime
from typing import List

from app.intelligence.infrastructure.llm import extract_json_object, generate_text
from app.intelligence.infrastructure.search import DuckDuckGoSearchGateway
from app.mirror.models import AnalysisResult, Competitor, Source


class MirrorService:
    def __init__(self, search_gateway: DuckDuckGoSearchGateway | None = None, model: str = "lfm-thinking"):
        self.model = model
        self.search_gateway = search_gateway or DuckDuckGoSearchGateway()
        self.competitors = [
            Competitor(
                id="comp_citadel_commodity",
                name="Citadel (Commodities)",
                description="High-frequency algorithmic trading desk.",
                tracked_urls=["reuters.com", "bloomberg.com"],
                last_active=datetime.now(),
            ),
            Competitor(
                id="comp_glencore_algo",
                name="Glencore (Algo Desk)",
                description="Physical-backed algorithmic hedging strategies.",
                tracked_urls=["platts.com", "argusmedia.com"],
                last_active=datetime.now(),
            ),
        ]

    async def get_competitors(self) -> List[Competitor]:
        return self.competitors

    async def analyze_target(self, target_query: str, target_id: str) -> AnalysisResult:
        sources = await self._search_intelligence(target_query)
        sentiment, conviction, summary, phrases = await self._analyze_with_llm(target_query, sources)
        return AnalysisResult(
            target_id=target_id,
            sentiment_score=sentiment,
            crowd_conviction=conviction,
            summary=summary,
            key_phrases=phrases,
            sources=sources,
            analysis_status="completed" if sources else "no_sources",
            timestamp=datetime.now(),
        )

    async def _search_intelligence(self, query: str) -> List[Source]:
        try:
            results = await self.search_gateway.search_text(f"{query} news analysis", max_results=5)
            return [
                Source(
                    id=f"src_{index}",
                    title=result.get("title", "Unknown"),
                    url=result.get("href", "#"),
                    domain=result.get("href", "").split("/")[2] if result.get("href") else "unknown",
                    snippet=result.get("body", ""),
                    published_at=datetime.now(),
                )
                for index, result in enumerate(results)
            ]
        except Exception:
            return []

    async def _analyze_with_llm(self, target: str, sources: List[Source]) -> tuple[float, float, str, List[str]]:
        news_text = "\n".join([f"- {source.title}: {source.snippet}" for source in sources])
        if not news_text:
            return 0.0, 0.0, "No intelligence found.", []

        prompt = f"""
        [INST] Role: Counter-Intelligence Algorithm
        Target: {target}

        Intel Sources:
        {news_text}

        Task: Analyze the 'Crowd Sentiment' of the market participants regarding {target}.

        Output valid JSON only:
        {{
            "sentiment_score": <float -1.0 (Bearish) to 1.0 (Bullish)>,
            "crowd_conviction": <float 0.0 (Uncertain) to 1.0 (Certain)>,
            "summary": "<Short executive summary of what the crowd thinks>",
            "key_phrases": ["<phrase1>", "<phrase2>", "<phrase3>"]
        }}
        [/INST]
        """

        try:
            response_text = await generate_text(prompt, self.model)
            json_payload = extract_json_object(response_text)
            if json_payload:
                parsed = json.loads(json_payload)
                return (
                    float(parsed.get("sentiment_score", 0.0)),
                    float(parsed.get("crowd_conviction", 0.0)),
                    parsed.get("summary", "No summary."),
                    parsed.get("key_phrases", []),
                )
            return 0.0, 0.0, response_text[:200] or "Analysis failed.", []
        except Exception:
            return 0.0, 0.0, "Analysis failed.", []
