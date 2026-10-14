import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.core.ai_client import LlamaCppProvider, LlamaCppStreamError, parse_llama_cpp_stream_line
from app.services import chat as chat_module
from app.services.chat import ChatService, format_sse


def _frame(content, stop=False, **extra):
    # Field layout of llama.cpp server_task_result_cmpl_partial/final::to_json_non_oaicompat,
    # serialized like llama-server: compact, with non-ASCII written as raw UTF-8.
    body = {"index": 0, "content": content, "tokens": [], "stop": stop, "id_slot": 0,
            "tokens_predicted": 1, "tokens_evaluated": 12, **extra}
    return f"data: {json.dumps(body, ensure_ascii=False, separators=(',', ':'))}\n\n"


# What llama-server sends for POST /completion with "stream": true, including an
# SSE keep-alive ping (":\n\n") between tokens and multi-byte UTF-8 tokens.
LLAMA_CPP_STREAM = (
    _frame("Brent")
    + _frame(" is €")
    + ":\n\n"
    + _frame(" range\tbound \"for now\" 😀\n")
    + _frame("", stop=True, timings={"predicted_ms": 12.5})
)
EXPECTED = 'Brent is € range\tbound "for now" 😀\n'


def _stream(body: str, chunk_size: int = 7, status: int = 200) -> list[str]:
    """Run LlamaCppProvider.stream_generate against `body`, delivered in small chunks."""

    async def chunks():
        data = body.encode()
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/completion"
        assert json.loads(request.content)["stream"] is True
        return httpx.Response(status, content=chunks(), headers={"content-type": "text/event-stream"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = LlamaCppProvider(client, host="http://llama")
            return [token async for token in provider.stream_generate("prompt")]

    return asyncio.run(run())


@pytest.mark.parametrize("chunk_size", range(1, 9))
def test_stream_parses_llama_cpp_sse_frames(chunk_size):
    # Small chunks split frames, lines and multi-byte UTF-8 sequences.
    assert "".join(_stream(LLAMA_CPP_STREAM, chunk_size=chunk_size)) == EXPECTED


@pytest.mark.parametrize("separator", [" ", " ", "\x85"])
def test_stream_keeps_tokens_with_unicode_line_separators(separator):
    # llama.cpp leaves these unescaped; only CR/LF may end an SSE line.
    tokens = _stream(_frame(f"a{separator}b") + _frame("", stop=True))
    assert tokens == [f"a{separator}b"]


def test_stream_handles_crlf_framing():
    body = LLAMA_CPP_STREAM.replace("\n", "\r\n")
    assert "".join(_stream(body, chunk_size=3)) == EXPECTED


def test_stream_stops_at_final_frame():
    assert "".join(_stream(LLAMA_CPP_STREAM + _frame(" ignored"))) == EXPECTED


def test_stream_stops_at_done_marker():
    assert _stream(_frame("ok") + "data: [DONE]\n\n" + _frame(" ignored")) == ["ok"]


def test_stream_accepts_bare_json_body_from_non_sse_servers():
    # text-gen-cpp-mock ignores "stream" and returns one JSON document.
    body = json.dumps({"content": "I am a mock.", "stopped_eos": True})
    assert _stream(body) == ["I am a mock."]


def test_stream_raises_on_error_frame():
    error = {"code": 500, "message": "context size exceeded", "type": "server_error"}
    with pytest.raises(LlamaCppStreamError, match="context size exceeded"):
        _stream(_frame("partial") + f"data: {json.dumps({'error': error})}\n\n")


def test_stream_raises_on_legacy_error_line():
    with pytest.raises(LlamaCppStreamError, match="slot unavailable"):
        _stream('error: {"code": 503, "message": "slot unavailable"}\n\n')


def test_stream_raises_on_http_error_status():
    with pytest.raises(httpx.HTTPStatusError):
        _stream("", status=503)


@pytest.mark.parametrize(
    "line, expected",
    [
        ("", ("", False)),
        (":", ("", False)),
        ("event: completion", ("", False)),
        ("id: 7", ("", False)),
        ("retry: 1000", ("", False)),
        ("data: not json", ("", False)),
        ("data: [1, 2]", ("", False)),
        ('data: {"content": "x", "stop": false}', ("x", False)),
        ('data:{"content":"y","stop":true}', ("y", True)),
        ('data: {"token": "z"}', ("z", False)),
        ("data: [DONE]", ("", True)),
    ],
)
def test_parse_llama_cpp_stream_line(line, expected):
    assert parse_llama_cpp_stream_line(line) == expected


def test_format_sse_produces_parseable_json_for_any_token():
    token = 'tab\there, cr\rhere, quote " backslash \\ newline\n bell \x07 unicode é'
    event = format_sse("token", {"token": token})
    assert event.startswith("event: token\ndata: ") and event.endswith("\n\n")
    data_line = event.split("\n")[1]
    assert json.loads(data_line[len("data: "):]) == {"token": token}


# --- ChatService.stream_message: what /chat/stream actually sends ---------------------

class _FakeSession:
    def __init__(self):
        self.saved = []

    def add(self, obj):
        self.saved.append(obj)

    async def commit(self):
        pass

    async def execute(self, stmt):
        return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: []))


def _run_stream_message(monkeypatch, ai_stream):
    session = _FakeSession()

    async def fake_get_db():
        yield session

    monkeypatch.setattr(chat_module, "get_db", fake_get_db)
    service = SimpleNamespace(_build_chat_prompt=lambda request: "prompt", ai_stream=ai_stream)
    chat_service = ChatService(SimpleNamespace(intelligence_service=service))
    request = SimpleNamespace(question="How is Brent?", model="lfm-thinking", history=[])

    async def collect():
        return "".join([part async for part in chat_service.stream_message("analyst", request)])

    return asyncio.run(collect()), session


def _events(body):
    """Parse SSE the way frontend/lib/api.ts chatWithModelStream does."""
    events = []
    for raw in body.split("\n\n"):
        lines = raw.split("\n")
        event = next((l[6:].strip() for l in lines if l.startswith("event:")), None)
        data = next((l[5:].strip() for l in lines if l.startswith("data:")), None)
        if event and data:
            events.append((event, json.loads(data)))
    return events


def test_stream_message_round_trips_control_characters(monkeypatch):
    tokens = ["tab\t", "cr\r", 'quote " ', "bell\x07", "nl\n\nend"]

    async def ai_stream(prompt, provider=None, model=None):
        for token in tokens:
            yield token

    body, session = _run_stream_message(monkeypatch, ai_stream)
    events = _events(body)
    assert [e for e, _ in events] == ["thinking"] + ["token"] * len(tokens) + ["done"]
    assert [d["token"] for e, d in events if e == "token"] == tokens
    assert events[-1][1]["response"] == "".join(tokens).strip()
    assert [m.role for m in session.saved] == ["user", "assistant"]


def test_stream_message_reports_model_errors_in_band(monkeypatch):
    async def ai_stream(prompt, provider=None, model=None):
        yield "Brent is "
        raise LlamaCppStreamError('{"code": 500, "message": "Compute error."}')

    body, session = _run_stream_message(monkeypatch, ai_stream)
    events = _events(body)
    assert [e for e, _ in events] == ["thinking", "token", "error"]
    assert "Compute error" not in body  # upstream details stay in the server log
    # The partial reply is still saved, so the stored history keeps alternating.
    assert [(m.role, m.content) for m in session.saved] == [("user", "How is Brent?"), ("assistant", "Brent is")]
