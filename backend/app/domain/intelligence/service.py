import os
import asyncio
from duckduckgo_search import DDGS
from typing import List, Tuple, Optional
from app.models import Source
from app.core.ai_client import ai_client

class IntelligenceService:
    def __init__(self):
        self.ddgs = DDGS()

    async def close(self):
        """Close the underlying HTTPX client."""
        # ai_client is singleton, persistent.
        pass

    async def search_market_news(self, question: str) -> List[Source]:
        """
        Search for live news related to the market question using DuckDuckGo.
        """
        print(f"Searching news for: {question}")
        try:
            results = await asyncio.to_thread(self.ddgs.text, question, max_results=10)
            sources = []
            if results:
                for r in results:
                    sources.append(Source(
                        title=r.get('title', 'Unknown'),
                        url=r.get('href', '#'),
                        snippet=r.get('body', '')
                    ))
            return sources
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    async def search_physical_data(self, question: str) -> List[Source]:
        """
        Retrieve physical market data via the configured provider (currently Mock).
        """
        from app.domain.intelligence.physical_data import MockPhysicalDataProvider
        provider = MockPhysicalDataProvider()
        return await provider.search_physical_data(question)

    async def _call_llm(self, prompt: str, model: str) -> str:
        model = "lfm-thinking" if model == "openforecaster" else model
        provider = "llama-cpp" if model == "lfm-thinking" else "ollama"
        return await ai_client.generate(prompt, provider=provider, model=model)

    async def _call_llm_json(self, prompt: str, model: str) -> dict:
        model = "lfm-thinking" if model == "openforecaster" else model
        provider = "llama-cpp" if model == "lfm-thinking" else "ollama"
        schema = {
            "type": "object",
            "properties": {
                "mirror": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "noise": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "divergence": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "algo": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]}
            },
            "required": ["mirror", "noise", "divergence", "algo"]
        }
        return await ai_client.generate_json(prompt, provider=provider, model=model, json_schema=schema if model == "lfm-thinking" else None)

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], model: str = "lfm-thinking") -> Tuple[float, str, "StructuredAnalysisResult"]:
        try:
            from app.domain.intelligence.swarm import IntelligenceDirectorate
            directorate = IntelligenceDirectorate()
            return await directorate.run_swarm(question, sources)
        except Exception as e:
            print(f"Intelligence Service (Swarm) Error: {e}")
            raise
        except Exception as e:
            print(f"Intelligence Service Error: {e}")
            raise

    async def search_semantic_correlations(self, question: str, model: str = "lfm-thinking") -> List[str]:
        prompt = f"[INST] TASK: Identify 3-5 semantically linked markets for: {question} [/INST]"
        model = "lfm-thinking" if model == "openforecaster" else model
        provider = "llama-cpp" if model == "lfm-thinking" else "ollama"
        try:
            return await ai_client.generate_json(prompt, provider=provider, model=model)
        except:
            return []

    async def chat_with_model(self, req: "ChatRequest", model: str = None) -> str:
        """
        Chat with the model. Improved to handle history and retryable model/provider selection.
        """
        # Orchestrator might pass model as kwarg
        model = model or (req.model if req.model != "openforecaster" else "lfm-thinking")
        
        # Default to llama-cpp for local models unless it's explicitly a known remote provider
        provider = "llama-cpp" 
        if model == "gemini-pro":
            provider = "gemini"
        elif os.getenv("OLLAMA_HOST") and model != "lfm-thinking":
            provider = "ollama"
        
        # Construct primitive history-aware prompt if history exists
        prompt = ""
        if hasattr(req, 'history') and req.history:
            for msg in req.history[-5:]: # Use last 5 for context
                prompt += f"{msg.role.upper()}: {msg.content}\n"
        
        prompt += f"USER: {req.question}\nASSISTANT:"
        
        return await ai_client.generate(prompt, provider=provider, model=model)

