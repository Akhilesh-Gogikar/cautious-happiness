from __future__ import annotations

import os
from typing import AsyncIterator

from app.core.ai_client import ai_client


def resolve_model_provider(model: str | None) -> tuple[str, str]:
    resolved_model = "lfm-thinking" if model in {None, "openforecaster"} else model
    provider = "llama-cpp"
    if resolved_model == "gemini-pro":
        provider = "gemini"
    elif os.getenv("OLLAMA_HOST") and resolved_model != "lfm-thinking":
        provider = "ollama"
    return resolved_model, provider


async def generate_text(prompt: str, model: str) -> str:
    resolved_model, provider = resolve_model_provider(model)
    return await ai_client.generate(prompt, provider=provider, model=resolved_model)


async def generate_json(prompt: str, model: str, json_schema: dict | None = None):
    resolved_model, provider = resolve_model_provider(model)
    return await ai_client.generate_json(prompt, provider=provider, model=resolved_model, json_schema=json_schema if resolved_model == "lfm-thinking" else None)


async def stream_text(prompt: str, model: str) -> AsyncIterator[str]:
    resolved_model, provider = resolve_model_provider(model)
    async for chunk in ai_client.stream_generate(prompt, provider=provider, model=resolved_model):
        yield chunk


def extract_json_object(response_text: str) -> str | None:
    start_idx = response_text.find("{")
    end_idx = response_text.rfind("}")
    if start_idx == -1 or end_idx == -1:
        return None
    return response_text[start_idx:end_idx + 1]
