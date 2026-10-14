import asyncio

import pytest

from app.core import ai_client as ai_client_module
from app.intelligence.domain import critic as critic_module
from app.intelligence.infrastructure import llm
from app.strategy import service as strategy_module
from app.strategy.models import StrategyGenerationRequest


class RecordingClient:
    """Stands in for app.core.ai_client.ai_client and records each call."""

    def __init__(self, providers, result):
        self.providers = dict.fromkeys(providers)
        self.result = result
        self.calls = []

    async def generate_json(self, prompt, provider="llama-cpp", model="lfm-thinking", **kwargs):
        self.calls.append({"provider": provider, "model": model, **kwargs})
        return self.result

    async def generate(self, prompt, provider="llama-cpp", model="lfm-thinking", **kwargs):
        self.calls.append({"provider": provider, "model": model, **kwargs})
        return self.result


def _critique():
    return asyncio.run(critic_module.CriticService().critique_forecast("Will Brent close above $90?", [], 0.6, "Supply is tight."))


def test_critic_uses_local_model_without_gemini(monkeypatch):
    client = RecordingClient(["ollama", "llama-cpp"], {"critique": "Thin sourcing.", "score": 0.55, "risk_factors": ["OPEC"]})
    monkeypatch.setattr(critic_module, "ai_client", client)
    result = _critique()
    assert client.calls == [{"provider": "llama-cpp", "model": "lfm-thinking", "json_schema": critic_module.CRITIC_SCHEMA}]
    assert (result.critique, result.score, result.risk_factors) == ("Thin sourcing.", 0.55, ["OPEC"])


def test_critic_prefers_gemini_when_configured(monkeypatch):
    client = RecordingClient(["ollama", "llama-cpp", "gemini"], {"critique": "ok", "score": 0.5, "risk_factors": []})
    monkeypatch.setattr(critic_module, "ai_client", client)
    _critique()
    assert [c["provider"] for c in client.calls] == ["gemini"]


def test_critic_falls_back_to_local_model_when_gemini_fails(monkeypatch):
    class GeminiDown(RecordingClient):
        async def generate_json(self, prompt, provider="llama-cpp", model="lfm-thinking", **kwargs):
            if provider == "gemini":
                self.calls.append({"provider": provider})
                raise RuntimeError("400 Bad Request for url ...?key=secret")
            return await super().generate_json(prompt, provider, model, **kwargs)

    client = GeminiDown(["llama-cpp", "gemini"], {"critique": "Local view.", "score": 0.4, "risk_factors": []})
    monkeypatch.setattr(critic_module, "ai_client", client)
    result = _critique()
    assert [c["provider"] for c in client.calls] == ["gemini", "llama-cpp"]
    assert (result.critique, result.score) == ("Local view.", 0.4)
    assert "secret" not in result.model_dump_json()


@pytest.mark.parametrize("score, clamped", [(65, 1.0), (-0.2, 0.0), (0.37, 0.37)])
def test_critic_score_is_clamped(monkeypatch, score, clamped):
    # llama-server's grammar does not enforce minimum/maximum on numbers.
    client = RecordingClient(["llama-cpp"], {"critique": "c", "score": score, "risk_factors": []})
    monkeypatch.setattr(critic_module, "ai_client", client)
    assert _critique().score == clamped


def test_critic_schema_requires_every_field():
    assert set(critic_module.CRITIC_SCHEMA["required"]) == {"critique", "score", "risk_factors"}


@pytest.mark.parametrize(
    "value, key",
    [
        ("", None),
        ("your_gemini_api_key", None),  # what older .env.example files shipped
        ("your_key_here", None),  # what the README used to show
        ("  AIzaRealLookingKey  ", "AIzaRealLookingKey"),
    ],
)
def test_placeholder_gemini_key_counts_as_unset(monkeypatch, value, key):
    monkeypatch.setenv("GEMINI_API_KEY", value)
    assert ai_client_module.gemini_api_key() == key
    client = ai_client_module.AIClient()
    try:
        assert ("gemini" in client.providers) is (key is not None)
    finally:
        asyncio.run(client.close())


@pytest.mark.parametrize(
    "ollama_host, model, provider, sends_schema",
    [
        ("", "lfm-thinking", "llama-cpp", True),
        ("", "lfm-40b", "llama-cpp", True),  # the fallback tier also runs on llama.cpp now
        ("http://ollama:11434", "lfm-40b", "ollama", False),
        ("", "gemini-pro", "gemini", False),
    ],
)
def test_json_schema_goes_to_llama_cpp_only(monkeypatch, ollama_host, model, provider, sends_schema):
    monkeypatch.setenv("OLLAMA_HOST", ollama_host)
    client = RecordingClient(["llama-cpp"], {})
    monkeypatch.setattr(llm, "ai_client", client)
    schema = {"type": "object"}
    asyncio.run(llm.generate_json("q", model, json_schema=schema))
    assert client.calls[0]["provider"] == provider
    assert client.calls[0]["json_schema"] == (schema if sends_schema else None)


def test_strategy_generation_falls_back_to_mock_when_model_is_slow(monkeypatch):
    class SlowClient(RecordingClient):
        async def generate(self, prompt, provider="llama-cpp", model="lfm-thinking", **kwargs):
            await asyncio.sleep(1)
            return "class TooLate(bt.Strategy):\n    pass"

    monkeypatch.setattr(strategy_module, "ai_client", SlowClient(["llama-cpp"], ""))
    monkeypatch.setattr(strategy_module, "LLM_TIMEOUT_SECONDS", 0.05)
    request = StrategyGenerationRequest(prompt="Buy breakouts")
    assert asyncio.run(strategy_module.StrategyFactory().generate_strategy(request)).name == "MockStrategy"


def test_strategy_generation_uses_shared_llama_client(monkeypatch):
    code = "class Breakout(bt.Strategy):\n    pass"
    client = RecordingClient(["llama-cpp"], code)
    monkeypatch.setattr(strategy_module, "ai_client", client)
    request = StrategyGenerationRequest(prompt="Buy breakouts", model="lfm-40b")
    result = asyncio.run(strategy_module.StrategyFactory().generate_strategy(request))
    assert client.calls == [{"provider": "llama-cpp", "model": "lfm-thinking", "n_predict": 1024}]
    assert (result.name, result.code) == ("Breakout", code)


def test_llama_cpp_default_host_is_the_compose_service(monkeypatch):
    monkeypatch.delenv("LLAMA_CPP_HOST", raising=False)
    client = ai_client_module.AIClient()
    try:
        assert client.providers["llama-cpp"].host == "http://text-gen-cpp:8080"
    finally:
        asyncio.run(client.close())


@pytest.mark.parametrize(
    "details, status",
    [
        ({"ollama": True, "redis": True, "database": True, "gemini_configured": False}, "ok"),
        ({"ollama": False, "redis": True, "database": True, "gemini_configured": True}, "degraded"),
        ({"ollama": True, "redis": False, "database": True, "gemini_configured": True}, "degraded"),
        ({"ollama": True, "redis": True, "database": False, "gemini_configured": True}, "degraded"),
    ],
)
def test_health_treats_gemini_as_optional(monkeypatch, details, status):
    from app import main

    async def fake_health():
        return details

    monkeypatch.setattr(main, "get_system_health", fake_health)
    assert asyncio.run(main.health_check()) == {"status": status, "details": details}


def test_semantic_correlations_ask_llama_cpp_for_a_list(monkeypatch):
    from app.intelligence.application import forecasting

    client = RecordingClient(["llama-cpp"], ["WTI > $90", "OPEC+ cut", "Hormuz closure"])
    monkeypatch.setattr(llm, "ai_client", client)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    service = forecasting.IntelligenceService.__new__(forecasting.IntelligenceService)
    assert asyncio.run(service.search_semantic_correlations("Will Brent close above $95?")) == client.result
    assert client.calls[0]["provider"] == "llama-cpp"
    assert client.calls[0]["json_schema"]["type"] == "array"
    assert client.calls[0]["json_schema"]["items"]["minLength"] == 1


@pytest.mark.parametrize(
    "correlations, expected",
    [
        (["WTI > $90", " OPEC+ cut "], "\n\n**Secondary Correlations Discovered:**\n- WTI > $90\n- OPEC+ cut"),
        (["", "  "], ""),
        ([], ""),
        (None, ""),
    ],
)
def test_correlations_render_as_a_list(correlations, expected):
    from app.intelligence.application.engine import format_correlations

    assert format_correlations(correlations) == expected
