import os
import httpx
import asyncio
from duckduckgo_search import DDGS
from typing import List, Optional
from datetime import datetime
from app.mirror.models import Source, AnalysisResult, Competitor

class MirrorService:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.ddgs = DDGS()
        
        # Mock Competitor Database
        self.competitors = [
            Competitor(
                id="comp_citadel_commodity",
                name="Citadel (Commodities)",
                description="High-frequency algorithmic trading desk.",
                tracked_urls=["reuters.com", "bloomberg.com"],
                last_active=datetime.now()
            ),
             Competitor(
                id="comp_glencore_algo",
                name="Glencore (Algo Desk)",
                description="Physical-backed algorithmic hedging strategies.",
                tracked_urls=["platts.com", "argusmedia.com"],
                last_active=datetime.now()
            )
        ]

    async def get_competitors(self) -> List[Competitor]:
        return self.competitors

    async def analyze_target(self, target_query: str, target_id: str) -> AnalysisResult:
        """
        Performs a 'Mirror Analysis' on a specific target (Commodity or Competitor).
        1. Scrapes recent news/discussions using DDG.
        2. Uses Ollama to estimate 'Crowd Sentiment' & 'Crowd Conviction'.
        """
        # 1. Gather Intelligence (Mocking a 'Scraper' via Search)
        sources = await self._search_intelligence(target_query)
        
        # 2. Analyze Intelligence with Ollama
        sentiment, conviction, summary, phrases = await self._analyze_with_llm(target_query, sources)
        
        return AnalysisResult(
            target_id=target_id,
            sentiment_score=sentiment,
            crowd_conviction=conviction,
            summary=summary,
            key_phrases=phrases,
            timestamp=datetime.now()
        )

    async def _search_intelligence(self, query: str) -> List[Source]:
        print(f"Mirror: Searching intel for {query}")
        try:
            # Run blocking DDGS in a thread
            results = await asyncio.to_thread(self.ddgs.text, f"{query} news analysis", max_results=5)
            
            sources = []
            if results:
                for i, r in enumerate(results):
                    sources.append(Source(
                        id=f"src_{i}",
                        title=r.get('title', 'Unknown'),
                        url=r.get('href', '#'),
                        domain=r.get('href', '').split('/')[2] if r.get('href') else 'unknown',
                        snippet=r.get('body', ''),
                        published_at=datetime.now() # Mock time as DDG doesn't always give it clean
                    ))
            return sources
        except Exception as e:
            print(f"Mirror Search Error: {e}")
            return []

    async def _analyze_with_llm(self, target: str, sources: List[Source]) -> tuple[float, float, str, List[str]]:
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
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
        
        # Default fallback
        sentiment = 0.0
        conviction = 0.0
        summary = "Analysis failed."
        phrases = []

        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.ollama_host}/completion"
                payload = {
                    "prompt": prompt,
                    "n_predict": 1024,
                    "stream": False,
                    "temperature": 0.1
                }
                
                # Check environment for model override
                if os.getenv("OLLAMA_MODEL"):
                    payload["model"] = os.getenv("OLLAMA_MODEL")

                response = await client.post(url, json=payload, timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '{}') if "response" in data else data.get('content', '{}') # Handle both Ollama and Llama.cpp formats if possible
                    
                    import json
                    try:
                        # Find the first { and last } to extract JSON
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            json_str = response_text[start_idx:end_idx+1]
                            parsed = json.loads(json_str)
                            sentiment = float(parsed.get("sentiment_score", 0.0))
                            conviction = float(parsed.get("crowd_conviction", 0.0))
                            summary = parsed.get("summary", "No summary.")
                            phrases = parsed.get("key_phrases", [])
                        else:
                            # Fallback if no JSON found
                            summary = response_text[:200]
                    except Exception as e:
                        print(f"Mirror: Failed to parse JSON from LLM: {e}")
                        summary = response_text[:200] + "..."
            except Exception as e:
                print(f"Mirror LLM Error: {e}")
        
        return sentiment, conviction, summary, phrases
