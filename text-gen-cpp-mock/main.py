"""Stand-in for llama.cpp's llama-server, for runs without the real model.

docker compose serves the real model; use this through
docker-compose.mock-llm.yml (CI, quick UI work, machines without the GGUF).
It answers the routes the backend calls with canned text, shaped like
llama-server's responses for the LFM2.5 thinking model.
"""
import asyncio
import json
import random
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

MOCK_ANSWER = "I am a hyper-intelligent AI analyst functioning correctly."
# LFM2.5 thinking models write their reasoning first, inside <think> tags.
MOCK_REASONING = "<think>The user wants a status check. Answer briefly.</think>\n\n"


class CompletionRequest(BaseModel):
    prompt: str
    n_predict: int = 2048
    temperature: float = 0.2
    stream: bool = False


class ChatCompletionRequest(BaseModel):
    model: str = "lfm-thinking"
    messages: list[dict]
    n_predict: int = 2048
    temperature: float = 0.2
    stream: bool = False
    json_schema: dict | None = None


def _sample(schema: dict):
    """A small value of the schema's shape (types, required keys, enum, minItems).

    Placeholder data only; other constraints such as ranges are ignored.
    """
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type", "object")
    if isinstance(kind, list):
        kind = kind[0]
    if kind == "object":
        props = schema.get("properties", {})
        return {name: _sample(props[name]) for name in schema.get("required", []) if name in props}
    if kind == "array":
        return [_sample(schema.get("items", {"type": "string"})) for _ in range(schema.get("minItems", 0))]
    return {"string": "mock", "number": 0.5, "integer": 0, "boolean": False, "null": None}.get(kind)


async def _simulate_latency():
    # Simulate processing time, but keep it fast (0.5s - 2s)
    await asyncio.sleep(0.5 + random.random() * 1.5)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    await _simulate_latency()
    if req.json_schema is not None:
        content = json.dumps(_sample(req.json_schema))
    else:
        content = MOCK_REASONING + MOCK_ANSWER
    base = {"id": f"chatcmpl-{uuid.uuid4().hex}", "created": int(time.time()), "model": req.model}

    if not req.stream:
        return {
            **base,
            "object": "chat.completion",
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content}}],
        }

    async def frames():
        pieces = [content[i:i + 8] for i in range(0, len(content), 8)]
        for piece in pieces:
            chunk = {**base, "object": "chat.completion.chunk",
                     "choices": [{"index": 0, "finish_reason": None, "delta": {"content": piece}}]}
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)
        last = {**base, "object": "chat.completion.chunk", "choices": [{"index": 0, "finish_reason": "stop", "delta": {}}]}
        yield f"data: {json.dumps(last)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(frames(), media_type="text/event-stream")


@app.post("/completion")
async def completion(req: CompletionRequest):
    await _simulate_latency()

    return {
        "content": MOCK_ANSWER,
        "generation_settings": {"n_predict": req.n_predict},
        "model": "lfm-thinking-mock",
        "prompt": req.prompt,
        "stopped_eos": True,
        "stopped_limit": False,
        "stopped_word": False,
        "stopping_word": "",
        "timings": {
            "predicted_ms": 1000,
            "predicted_n": 10,
            "predicted_per_second": 10.0,
            "predicted_per_token_ms": 100.0,
            "prompt_ms": 100,
            "prompt_n": 10,
            "prompt_per_second": 100.0,
            "prompt_per_token_ms": 10.0
        },
        "tokens_cached": 0,
        "tokens_evaluated": 10,
        "tokens_predicted": 10,
        "truncated": False
    }


@app.get("/")
async def root():
    return {"status": "Mock llama.cpp API running"}
