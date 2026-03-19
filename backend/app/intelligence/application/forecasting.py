from __future__ import annotations

import json
from typing import AsyncIterator, List, Tuple

from app.models import AlgoAnalysis, DivergenceAnalysis, MirrorAnalysis, NoiseAnalysis, Source, StructuredAnalysisResult
from app.intelligence.infrastructure.llm import generate_json, resolve_model_provider
from app.intelligence.infrastructure.physical_data import MockPhysicalDataProvider, PhysicalDataInterface
from app.intelligence.infrastructure.search import DuckDuckGoSearchGateway
from app.core.ai_client import ai_client


class IntelligenceService:
    def __init__(
        self,
        search_gateway: DuckDuckGoSearchGateway | None = None,
        physical_data_provider: PhysicalDataInterface | None = None,
    ):
        self.search_gateway = search_gateway or DuckDuckGoSearchGateway()
        self.physical_data_provider = physical_data_provider or MockPhysicalDataProvider()

    async def close(self):
        """Close underlying clients if they become stateful in the future."""
        return None

    async def search_market_news(self, question: str) -> List[Source]:
        try:
            results = await self.search_gateway.search_text(question, max_results=10)
            return [
                Source(
                    title=result.get("title", "Unknown"),
                    url=result.get("href", "#"),
                    snippet=result.get("body", ""),
                )
                for result in results
            ]
        except Exception:
            return []

    async def search_physical_data(self, question: str) -> List[Source]:
        return await self.physical_data_provider.search_physical_data(question)

    async def _call_llm(self, prompt: str, model: str) -> str:
        resolved_model, provider = resolve_model_provider(model)
        return await ai_client.generate(prompt, provider=provider, model=resolved_model)

    async def _call_llm_json(self, prompt: str, model: str) -> dict:
        schema = {
            "type": "object",
            "properties": {
                "mirror": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "noise": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "divergence": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
                "algo": {"type": "object", "properties": {"score": {"type": "number"}, "reasoning": {"type": "string"}}, "required": ["score", "reasoning"]},
            },
            "required": ["mirror", "noise", "divergence", "algo"],
        }
        return await generate_json(prompt, model=model, json_schema=schema)

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], model: str = "lfm-thinking") -> Tuple[float, str, StructuredAnalysisResult]:
        from app.intelligence.domain.swarm import IntelligenceDirectorate

        try:
            directorate = IntelligenceDirectorate()
            return await directorate.run_swarm(question, sources)
        except Exception:
            try:
                raw_json = await self._call_llm_json(question, model)
                analysis = StructuredAnalysisResult(
                    mirror=MirrorAnalysis(**raw_json["mirror"]),
                    noise=NoiseAnalysis(**raw_json["noise"]),
                    divergence=DivergenceAnalysis(**raw_json["divergence"]),
                    algo=AlgoAnalysis(**raw_json["algo"]),
                )
                avg_score = (analysis.mirror.score + (1 - analysis.noise.score) + analysis.divergence.score + analysis.algo.score) / 4
                reasoning = (
                    f"Mirror: {analysis.mirror.reasoning}\n"
                    f"Noise: {analysis.noise.reasoning}\n"
                    f"Divergence: {analysis.divergence.reasoning}\n"
                    f"Algo: {analysis.algo.reasoning}"
                )
                return avg_score, reasoning, analysis
            except Exception as exc:
                fallback_component = {"score": 0.5, "reasoning": f"Error: {exc}"}
                analysis = StructuredAnalysisResult(
                    mirror=MirrorAnalysis(**fallback_component),
                    noise=NoiseAnalysis(**fallback_component),
                    divergence=DivergenceAnalysis(**fallback_component),
                    algo=AlgoAnalysis(**fallback_component),
                )
                return 0.5, f"Error: {exc}", analysis

    async def search_semantic_correlations(self, question: str, model: str = "lfm-thinking") -> List[str]:
        prompt = f"[INST] TASK: Identify 3-5 semantically linked markets for: {question} [/INST]"
        try:
            result = await generate_json(prompt, model=model)
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [json.dumps(result)]
            return []
        except Exception:
            return []

    async def chat_with_model(self, req: "ChatRequest", model: str = None) -> str:
        model = model or req.model
        prompt = self._build_chat_prompt(req)
        chunks: list[str] = []
        async for chunk in self.ai_stream(prompt, model=model):
            chunks.append(chunk)
        return "".join(chunks).strip()

    async def ai_stream(self, prompt: str, model: str, provider: str | None = None) -> AsyncIterator[str]:
        resolved_model, resolved_provider = resolve_model_provider(model)
        stream_provider = provider or resolved_provider
        async for chunk in ai_client.stream_generate(prompt, provider=stream_provider, model=resolved_model):
            yield chunk

    def _build_chat_prompt(self, req: "ChatRequest") -> str:
        prompt_lines: List[str] = []
        messages = getattr(req, "messages", None)
        if messages:
            for msg in messages:
                role = getattr(msg, "role", "user").upper()
                content = getattr(msg, "content", "")
                if content:
                    prompt_lines.append(f"{role}: {content}")

            if prompt_lines and not prompt_lines[-1].startswith("ASSISTANT:"):
                prompt_lines.append("ASSISTANT:")
            return "\n".join(prompt_lines)

        history = getattr(req, "history", None)
        if history:
            for msg in history[-5:]:
                prompt_lines.append(f"{msg.role.upper()}: {msg.content}")

        question = getattr(req, "question", "")
        if question:
            prompt_lines.append(f"USER: {question}")

        prompt_lines.append("ASSISTANT:")
        return "\n".join(prompt_lines)
