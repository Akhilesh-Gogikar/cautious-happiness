from types import SimpleNamespace

from app.domain.intelligence.service import IntelligenceService


def test_build_prompt_from_messages():
    service = IntelligenceService()
    req = SimpleNamespace(
        messages=[
            SimpleNamespace(role="system", content="You are a trading copilot."),
            SimpleNamespace(role="user", content="Find opportunities in oil markets."),
        ]
    )

    prompt = service._build_chat_prompt(req)

    assert "SYSTEM: You are a trading copilot." in prompt
    assert "USER: Find opportunities in oil markets." in prompt
    assert prompt.endswith("ASSISTANT:")


def test_build_prompt_from_history_and_question():
    service = IntelligenceService()
    req = SimpleNamespace(
        history=[
            SimpleNamespace(role="user", content="What changed overnight?"),
            SimpleNamespace(role="assistant", content="FX moved after hours."),
        ],
        question="Any implication for prediction markets?",
    )

    prompt = service._build_chat_prompt(req)

    assert "USER: What changed overnight?" in prompt
    assert "ASSISTANT: FX moved after hours." in prompt
    assert "USER: Any implication for prediction markets?" in prompt
    assert prompt.endswith("ASSISTANT:")
