import os
import re
import httpx
import json
import logging
import asyncio
from typing import AsyncIterator, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger("ai_client")

class AIProvider(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @abstractmethod
    async def generate(self, prompt: str, model: str, **kwargs) -> str:
        pass

    async def stream_generate(self, prompt: str, model: str, **kwargs) -> AsyncIterator[str]:
        """Default streaming fallback for providers that only support full responses."""
        text = await self.generate(prompt, model, **kwargs)
        if text:
            yield text

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

    async def stream_generate(self, prompt: str, model: str, **kwargs) -> AsyncIterator[str]:
        async with self.client.stream(
            "POST",
            f"{self.host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True, **kwargs},
            timeout=120.0,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = data.get("response", "")
                if token:
                    yield token

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
    """llama.cpp's llama-server, through its OpenAI-compatible chat route.

    The chat route applies the chat template stored in the GGUF; the raw
    /completion route does not, so a chat-tuned model like LFM2.5 would see
    untemplated text.
    """

    def __init__(self, client: httpx.AsyncClient, host: str = "http://text-gen-cpp:8080"):
        super().__init__(client)
        self.host = host

    def _payload(self, prompt: str, model: str, stream: bool, kwargs: dict) -> dict:
        n_predict = kwargs.get("n_predict", 2048)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "n_predict": n_predict,
            "temperature": kwargs.get("temperature", 0.2),
            "stream": stream,
        }
        if n_predict > 0:
            # Thinking models spend tokens on <think> first; cap that at half the
            # budget so an answer always fits (llama-server closes the block).
            payload["reasoning_budget_tokens"] = max(n_predict // 2, 1)
        if kwargs.get("json_schema") is not None:
            payload["json_schema"] = kwargs["json_schema"]
        return payload

    async def generate(self, prompt: str, model: str = "lfm-thinking", **kwargs) -> str:
        response = await self._safe_request(
            "POST",
            f"{self.host}/v1/chat/completions",
            json=self._payload(prompt, model, False, kwargs),
            timeout=300.0
        )
        data = response.json()
        try:
            content = data["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError, TypeError, AttributeError):
            content = data.get("content", "") if isinstance(data, dict) else ""
        reasoning = ReasoningFilter()
        return (reasoning.feed(content) + reasoning.flush()).strip()

    async def stream_generate(self, prompt: str, model: str = "lfm-thinking", **kwargs) -> AsyncIterator[str]:
        async with self.client.stream(
            "POST",
            f"{self.host}/v1/chat/completions",
            json=self._payload(prompt, model, True, kwargs),
            timeout=300.0,
        ) as response:
            response.raise_for_status()
            reasoning = ReasoningFilter()
            async for line in _iter_sse_lines(response):
                token, done = parse_llama_cpp_stream_line(line)
                if token:
                    token = reasoning.feed(token)
                    if token:
                        yield token
                if done:
                    break
            tail = reasoning.flush()
            if tail:
                yield tail


class ReasoningFilter:
    """Drops a leading <think>...</think> block from streamed model output.

    llama-server moves thinking into `reasoning_content` only when the model's
    chat template mentions <think>; otherwise LFM2.5 thinking models write it
    into the answer itself. Feed chunks in order, then call flush() once.
    """

    OPEN, CLOSE = "<think>", "</think>"

    def __init__(self):
        self._state = "start"  # start -> thinking -> after_think -> answer
        self._buffer = ""

    def feed(self, chunk: str) -> str:
        if self._state == "answer":
            return chunk
        self._buffer += chunk
        if self._state == "start":
            head = self._buffer.lstrip()
            if not head or (len(head) < len(self.OPEN) and self.OPEN.startswith(head)):
                return ""  # could still be the start of <think>
            if not head.startswith(self.OPEN):
                self._buffer = head  # leading blank lines are never answer text
                return self._emit()
            self._state, self._buffer = "thinking", head[len(self.OPEN):]
        if self._state == "thinking":
            _, closed, rest = self._buffer.partition(self.CLOSE)
            if not closed:
                return ""
            self._state, self._buffer = "after_think", rest
        # The answer usually starts with blank lines after </think>.
        self._buffer = self._buffer.lstrip()
        return self._emit() if self._buffer else ""

    def flush(self) -> str:
        if self._state == "thinking":
            # Ran out of tokens while still thinking: there is no answer.
            self._buffer = ""
        return self._emit().lstrip() if self._state == "start" else self._emit()

    def _emit(self) -> str:
        self._state, text, self._buffer = "answer", self._buffer, ""
        return text


_SSE_LINE_BREAK = re.compile(r"\r\n|\r|\n")


async def _iter_sse_lines(response: httpx.Response) -> AsyncIterator[str]:
    """Yield lines split only on CRLF, LF or CR, the SSE line terminators.

    httpx's aiter_lines() also splits on U+2028, U+2029 and U+0085, which
    llama.cpp writes unescaped inside its JSON, so it would cut a frame in two.
    """
    pending = ""
    async for text in response.aiter_text():
        *lines, pending = _SSE_LINE_BREAK.split(pending + text)
        for line in lines:
            yield line
    if pending:
        yield pending


class LlamaCppStreamError(RuntimeError):
    """llama.cpp reported an error in the middle of a streamed completion."""


def parse_llama_cpp_stream_line(line: str) -> tuple[str, bool]:
    """Return (token, done) for one line of a llama.cpp stream.

    llama.cpp streams Server-Sent Events. On /v1/chat/completions each frame is
    `data: {"choices": [{"delta": {"content": ...}, "finish_reason": null}]}`
    (thinking arrives as `delta.reasoning_content`, which is not answer text),
    the last one has a `finish_reason`, then `data: [DONE]`. On /completion a
    frame is `data: {"content": ..., "stop": false}` and the last has
    `"stop": true`. Both send `:` keep-alive comments and `data: {"error": {...}}`
    on failure (older builds send an `error: {...}` line). Bare JSON lines, as
    sent by non-SSE servers, are accepted too.
    """
    line = line.strip()
    if not line or line.startswith(":"):
        return "", False
    if line.startswith("error:"):
        raise LlamaCppStreamError(line[len("error:"):].strip())
    if line.startswith("data:"):
        line = line[len("data:"):].strip()
    elif line.startswith(("event:", "id:", "retry:")):
        return "", False
    if line == "[DONE]":
        return "", True

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return "", False
    if not isinstance(data, dict):
        return "", False
    if "error" in data:
        raise LlamaCppStreamError(json.dumps(data["error"]))

    choices = data.get("choices")
    if isinstance(choices, list):
        choice = choices[0] if choices and isinstance(choices[0], dict) else {}
        message = choice.get("delta") or choice.get("message") or {}
        token = message.get("content") if isinstance(message, dict) else None
        return token if isinstance(token, str) else "", choice.get("finish_reason") is not None

    token = data.get("content") or data.get("token") or ""
    return token, data.get("stop") is True

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
        
        llama_cpp_host = os.getenv("LLAMA_CPP_HOST", "http://text-gen-cpp:8080")
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

    async def stream_generate(self, prompt: str, provider: str = "llama-cpp", model: str = "lfm-thinking", **kwargs) -> AsyncIterator[str]:
        p = self.providers.get(provider)
        if not p:
            p = self.providers.get("llama-cpp")
            logger.warning(f"Provider {provider} not found. Falling back to llama-cpp")

        async for chunk in p.stream_generate(prompt, model, **kwargs):
            if chunk:
                yield chunk

ai_client = AIClient()
