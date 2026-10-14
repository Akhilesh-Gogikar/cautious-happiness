import asyncio
import json
import logging

import httpx
import pytest

from app.core import ai_client as ai_client_module
from app.core.ai_client import DEFAULT_GEMINI_MODEL, GeminiProvider, gemini_model
from app.intelligence.domain import critic as critic_module

KEY = "AIzaTESTSECRET1234567890"


def _call(response, monkeypatch, **kwargs):
    """Run GeminiProvider.generate against `response` and return (result, requests)."""
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response

    async def no_sleep(_):
        pass

    monkeypatch.setattr(ai_client_module.asyncio, "sleep", no_sleep)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await GeminiProvider(client, KEY).generate("Critique this.", **kwargs)

    return asyncio.run(run()), requests


def _reply(text):
    return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": text}]}}]})


def test_key_is_sent_in_a_header_not_the_url(monkeypatch):
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    text, requests = _call(_reply("ok"), monkeypatch)
    assert text == "ok"
    request = requests[0]
    assert request.headers["x-goog-api-key"] == KEY
    assert KEY not in str(request.url)
    assert request.url.path == f"/v1beta/models/{DEFAULT_GEMINI_MODEL}:generateContent"


def test_key_never_reaches_error_text_or_logs(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    response = httpx.Response(400, json={"error": {"code": 400, "message": "API key not valid."}})
    with pytest.raises(httpx.HTTPStatusError) as raised:
        _call(response, monkeypatch)
    assert KEY not in str(raised.value)
    records = [r.getMessage() for r in caplog.records]
    assert any("generateContent" in m for m in records)  # the request was logged...
    assert not any(KEY in m for m in records)  # ...without the key


def test_json_requests_ask_for_a_json_response(monkeypatch):
    _, requests = _call(_reply("{}"), monkeypatch, json_schema={"type": "object"})
    assert json.loads(requests[0].content)["generationConfig"] == {"responseMimeType": "application/json"}
    _, requests = _call(_reply("hi"), monkeypatch)
    assert "generationConfig" not in json.loads(requests[0].content)


@pytest.mark.parametrize(
    "requested, configured, expected",
    [
        (None, None, DEFAULT_GEMINI_MODEL),
        (None, "gemini-3.8-flash", "gemini-3.8-flash"),
        ("gemini-pro", "gemini-3.8-flash", "gemini-3.8-flash"),  # retired; the chat UI still sends it
        ("gemini-1.5-flash", None, DEFAULT_GEMINI_MODEL),  # retired; the critic used to send it
        ("gemini-1.0-pro", None, DEFAULT_GEMINI_MODEL),
        ("lfm-thinking", None, DEFAULT_GEMINI_MODEL),  # not a Gemini model
        ("gemini-pro-latest", None, "gemini-pro-latest"),
        ("gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.6-flash"),
        (None, "../../other:method", DEFAULT_GEMINI_MODEL),  # not a model name
    ],
)
def test_gemini_model_resolution(monkeypatch, requested, configured, expected):
    if configured is None:
        monkeypatch.delenv("GEMINI_MODEL", raising=False)
    else:
        monkeypatch.setenv("GEMINI_MODEL", configured)
    assert gemini_model(requested) == expected


def test_configured_model_is_used_in_the_request(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")
    _, requests = _call(_reply("ok"), monkeypatch, model="gemini-pro")
    assert requests[0].url.path == "/v1beta/models/gemini-3.8-flash:generateContent"


def test_critic_asks_gemini_for_json_with_the_configured_model(monkeypatch):
    calls = []

    class Client:
        providers = {"gemini": None, "llama-cpp": None}

        async def generate_json(self, prompt, provider="llama-cpp", model="lfm-thinking", **kwargs):
            calls.append({"provider": provider, "model": model, **kwargs})
            return {"critique": "ok", "score": 0.5, "risk_factors": []}

    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setattr(critic_module, "ai_client", Client())
    asyncio.run(critic_module.CriticService().critique_forecast("q", [], 0.5, "r"))
    assert calls == [{"provider": "gemini", "model": "gemini-3.8-flash", "json_schema": critic_module.CRITIC_SCHEMA}]


def test_critic_failure_text_names_the_error_type_only(monkeypatch):
    class Client:
        providers = {"llama-cpp": None}

        async def generate_json(self, *args, **kwargs):
            raise RuntimeError("upstream said: key=SECRET at http://internal-host/path")

    monkeypatch.setattr(critic_module, "ai_client", Client())
    result = asyncio.run(critic_module.CriticService().critique_forecast("q", [], 0.42, "r"))
    assert result.critique == "Critic unavailable (RuntimeError)."
    assert result.risk_factors == ["System Error: RuntimeError"]
    assert result.score == 0.42
    assert "SECRET" not in result.model_dump_json() and "internal-host" not in result.model_dump_json()
