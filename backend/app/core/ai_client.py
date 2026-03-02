import os
import httpx
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger("ai_client")

class AIProvider(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        pass

    async def _safe_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Helper to run requests with retries."""
        last_error = None
        for attempt in range(3):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                last_error = e
                wait = (attempt + 1) * 2
                logger.warning(f"AI Provider request failed (attempt {attempt+1}/3): {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
        
        logger.error(f"AI Provider request failed after 3 attempts: {last_error}")
        raise last_error

class OllamaProvider(AIProvider):
    def __init__(self, client: httpx.AsyncClient, host: str = "http://ollama:11434"):
        super().__init__(client)
        self.host = host

    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        response = await self._safe_request(
            "POST",
            f"{self.host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            },
            timeout=120.0
        )
        return response.json().get("response", "")

class GeminiProvider(AIProvider):
    def __init__(self, client: httpx.AsyncClient, api_key: str):
        super().__init__(client)
        self.api_key = api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

    async def generate(self, prompt: str, model: str = "gemini-pro", **kwargs) -> str:
        response = await self._safe_request(
            "POST",
            self.url,
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            },
            timeout=60.0
        )
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Error parsing Gemini response"

class LlamaCppProvider(AIProvider):
    def __init__(self, client: httpx.AsyncClient, host: str = "http://text-gen-cpp:8080"):
        super().__init__(client)
        self.host = host

    async def generate(self, prompt: str, model: str = "lfm-thinking", **kwargs) -> str:
        payload = {
            "prompt": prompt,
            "n_predict": kwargs.get("n_predict", 2048),
            "temperature": kwargs.get("temperature", 0.2),
            "stream": False
        }
        if "json_schema" in kwargs:
            payload["json_schema"] = kwargs["json_schema"]
        
        response = await self._safe_request(
            "POST", 
            f"{self.host}/completion", 
            json=payload,
            timeout=300.0
        )
        return response.json().get("content", "").strip()

class AIClient:
    def __init__(self):
        # Persistent client for connection pooling
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=300.0
        )
        self.providers: Dict[str, AIProvider] = {}
        
        ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.providers["ollama"] = OllamaProvider(self.client, ollama_host)
        
        llama_cpp_host = os.getenv("LLAMA_CPP_HOST", "http://172.19.0.3:8080")
        self.providers["llama-cpp"] = LlamaCppProvider(self.client, llama_cpp_host)
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.providers["gemini"] = GeminiProvider(self.client, gemini_key)

    async def close(self):
        await self.client.aclose()

    async def generate(self, prompt: str, provider: str = "llama-cpp", model: str = "lfm-thinking", **kwargs) -> str:
        p = self.providers.get(provider)
        if not p:
            p = self.providers.get("llama-cpp")
            logger.warning(f"Provider {provider} not found. Falling back to llama-cpp")
        
        return await p.generate(prompt, model, **kwargs)

    async def generate_json(self, prompt: str, provider: str = "llama-cpp", model: str = "lfm-thinking", **kwargs) -> dict:
        raw_text = await self.generate(prompt, provider, model, **kwargs)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from AI response: {raw_text}")
            raise

ai_client = AIClient()
