import os
import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger("ai_client")

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        pass

class OllamaProvider(AIProvider):
    def __init__(self, host: str = "http://ollama:11434"):
        self.host = host

    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json().get("response", "")

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

    async def generate(self, prompt: str, model: str = "gemini-pro", **kwargs) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                }
            )
            response.raise_for_status()
            data = response.json()
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexOfError):
                return "Error parsing Gemini response"

class LlamaCppProvider(AIProvider):
    def __init__(self, host: str = "http://llama-cpp:8080"):
        self.host = host

    async def generate(self, prompt: str, model: str = "lfm-thinking", **kwargs) -> str:
        async with httpx.AsyncClient(timeout=300.0) as client:
            payload = {
                "prompt": prompt,
                "n_predict": kwargs.get("n_predict", 2048),
                "temperature": kwargs.get("temperature", 0.2),
                "stream": False
            }
            if "json_schema" in kwargs:
                payload["json_schema"] = kwargs["json_schema"]
            
            response = await client.post(f"{self.host}/completion", json=payload)
            response.raise_for_status()
            return response.json().get("content", "").strip()

class AIClient:
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        
        ollama_host = os.getenv("OLLAMA_HOST", "http://text-gen-cpp:8080")
        self.providers["ollama"] = LlamaCppProvider(ollama_host)
        
        llama_cpp_host = os.getenv("LLAMA_CPP_HOST", "http://text-gen-cpp:8080")
        self.providers["llama-cpp"] = LlamaCppProvider(llama_cpp_host)
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            self.providers["gemini"] = GeminiProvider(gemini_key)

    async def generate(self, prompt: str, provider: str = "ollama", model: str = "lfm-thinking", **kwargs) -> str:
        p = self.providers.get(provider)
        if not p:
            p = self.providers.get("ollama")
            logger.warning(f"Provider {provider} not found. Falling back to Ollama")
        
        return await p.generate(prompt, model, **kwargs)

    async def generate_json(self, prompt: str, provider: str = "ollama", model: str = "lfm-thinking", **kwargs) -> dict:
        raw_text = await self.generate(prompt, provider, model, **kwargs)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from AI response: {raw_text}")
            raise

ai_client = AIClient()
