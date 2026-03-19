from __future__ import annotations

import asyncio
import json
from typing import List, Tuple

from app.core.ai_client import ai_client
from app.models import AlgoAnalysis, DivergenceAnalysis, MirrorAnalysis, NoiseAnalysis, Source, StructuredAnalysisResult


class BaseSwarmAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def analyze(self, question: str, sources: List[Source]) -> str:
        raise NotImplementedError


class GeopoliticalAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__("Geopolitical Analyst", "Expert in global politics, sanctions, and macro-stability.")

    async def analyze(self, question: str, sources: List[Source]) -> str:
        snippets = [source.snippet for source in sources]
        prompt = f"""
[INST]
Role: {self.role}
Task: Analyze the geopolitical implications for the following market event: "{question}"
Data Sources: {json.dumps(snippets)}

Focus only on geopolitical risks, state-actor moves, and regulatory shifts.
Provide a concise reasoning and a probabilistic impact score (0-1).
[/INST]
"""
        return await ai_client.generate(prompt, model="lfm-thinking")


class SupplyChainAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__("Supply-Chain Analyst", "Expert in logistics, production constraints, and physical commodity flows.")

    async def analyze(self, question: str, sources: List[Source]) -> str:
        snippets = [source.snippet for source in sources]
        prompt = f"""
[INST]
Role: {self.role}
Task: Analyze physical supply chain constraints for: "{question}"
Data Sources: {json.dumps(snippets)}

Focus on production bottlenecks, shipping disruptions, and inventory cycles.
Provide a concise reasoning and a probabilistic impact score (0-1).
[/INST]
"""
        return await ai_client.generate(prompt, model="lfm-thinking")


class DerivativesFlowAgent(BaseSwarmAgent):
    def __init__(self):
        super().__init__("Derivatives Flow Analyst", "Expert in market positioning, institutional flows, and technical derivatives data.")

    async def analyze(self, question: str, sources: List[Source]) -> str:
        snippets = [source.snippet for source in sources]
        prompt = f"""
[INST]
Role: {self.role}
Task: Analyze market positioning and derivatives flows for: "{question}"
Data Sources: {json.dumps(snippets)}

Focus on gamma levels, short interest, institutional hedging, and options sensitivity.
Provide a concise reasoning and a probabilistic impact score (0-1).
[/INST]
"""
        return await ai_client.generate(prompt, model="lfm-thinking")


class IntelligenceDirectorate:
    def __init__(self):
        self.agents = [GeopoliticalAgent(), SupplyChainAgent(), DerivativesFlowAgent()]

    async def run_swarm(self, question: str, sources: List[Source]) -> Tuple[float, str, StructuredAnalysisResult]:
        agent_reports = await asyncio.gather(*[agent.analyze(question, sources) for agent in self.agents])
        debate_context = "\n\n".join([
            f"--- {agent.name} Report ---\n{report}"
            for agent, report in zip(self.agents, agent_reports)
        ])

        synthesis_prompt = f"""
[INST]
Role: Intelligence Directorate (Synthesizer)
Task: Review the following specialized agent reports and produce a master, probabilistically weighted forecast for: "{question}"

REPORTS:
{debate_context}

The objective is to resolve internal contradictions between agents and present a unified, high-fidelity analysis.

OUTPUT SCHEMA (STRICT JSON):
{{
    "mirror": {{"score": float, "reasoning": "string"}},
    "noise": {{"score": float, "reasoning": "string"}},
    "divergence": {{"score": float, "reasoning": "string"}},
    "algo": {{"score": float, "reasoning": "string"}}
}}
[/INST]
"""
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
        raw_json = await ai_client.generate_json(synthesis_prompt, model="lfm-thinking", json_schema=schema)
        analysis = StructuredAnalysisResult(**raw_json)
        avg_score = (analysis.mirror.score + (1 - analysis.noise.score) + analysis.divergence.score + analysis.algo.score) / 4
        collaborative_reasoning = (
            "Directorate Consensus Strategy:\n"
            f"- Geopolitical Impact: {analysis.mirror.reasoning}\n"
            f"- Supply-Chain Risks: {analysis.noise.reasoning}\n"
            f"- Derivatives Outlook: {analysis.divergence.reasoning}\n"
            f"- Final Probabilistic weighting: {analysis.algo.reasoning}"
        )
        return avg_score, collaborative_reasoning, analysis
