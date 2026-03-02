from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import random

app = FastAPI()

class CompletionRequest(BaseModel):
    prompt: str
    n_predict: int = 2048
    temperature: float = 0.2
    stream: bool = False

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/completion")
async def completion(req: CompletionRequest):
    # Simulate processing time based on prompt length, but keep it fast (0.5s - 2s)
    await asyncio.sleep(0.5 + random.random() * 1.5)
    
    return {
        "content": "I am a hyper-intelligent AI analyst functioning correctly.",
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
