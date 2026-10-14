import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.core.ai_client import LlamaCppProvider, LlamaCppStreamError, ReasoningFilter, parse_llama_cpp_stream_line
from app.services import chat as chat_module
from app.services.chat import ChatService, format_sse


def _frame(content, stop=False, **extra):
    # Field layout of llama.cpp server_task_result_cmpl_partial/final::to_json_non_oaicompat,
    # serialized like llama-server: compact, with non-ASCII written as raw UTF-8.
    body = {"index": 0, "content": content, "tokens": [], "stop": stop, "id_slot": 0,
            "tokens_predicted": 1, "tokens_evaluated": 12, **extra}
    return f"data: {json.dumps(body, ensure_ascii=False, separators=(',', ':'))}\n\n"


def _chat_frame(delta, finish_reason=None, **extra):
    # A /v1/chat/completions stream chunk, laid out as llama-server b11243 sends it.
    body = {"choices": [{"finish_reason": finish_reason, "index": 0, "delta": delta}],
            "created": 1791995667, "id": "chatcmpl-test", "model": "lfm-thinking",
            "system_fingerprint": "b11243-fc07d781e", "object": "chat.completion.chunk", **extra}
    return f"data: {json.dumps(body, ensure_ascii=False, separators=(',', ':'))}\n\n"


def _chat_stream(*deltas):
    return (_chat_frame({"role": "assistant", "content": None})
            + "".join(_chat_frame(d) for d in deltas)
            + _chat_frame({}, "stop", timings={"predicted_n": len(deltas)})
            + "data: [DONE]\n\n")


# Recorded from llama-server (b11243) running an LFM2 model whose chat template
# has no <think> (like LFM2.5's): the thinking arrives inside `content`.
# Plus an SSE keep-alive ping (":\n\n") and multi-byte UTF-8 tokens.
THINK_IN_CONTENT = _chat_stream(
    {"content": "<think>"}, {"content": "Weighing"}, {"content": " supply"}, {"content": " risk"},
    {"content": "</think>"}, {"content": "\n\n"}, {"content": "Brent"}, {"content": " is €"},
    {"content": " range\tbound \"for now\" 😀\n"},
).replace(_chat_frame({"content": " is €"}), ":\n\n" + _chat_frame({"content": " is €"}))
# Same model with a template that mentions <think>: llama-server splits the
# thinking into `reasoning_content`.
THINK_IN_REASONING = _chat_stream(
    {"reasoning_content": "Weighing"}, {"reasoning_content": " supply"}, {"reasoning_content": " risk"},
    {"content": "\n\n"}, {"content": "Brent"}, {"content": " is €"},
    {"content": " range\tbound \"for now\" 😀\n"},
)
EXPECTED = 'Brent is € range\tbound "for now" 😀\n'
LLAMA_CPP_STREAM = THINK_IN_CONTENT


def _stream(body: str, chunk_size: int = 7, status: int = 200, requests: list | None = None) -> list[str]:
    """Run LlamaCppProvider.stream_generate against `body`, delivered in small chunks."""

    async def chunks():
        data = body.encode()
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        payload = json.loads(request.content)
        assert payload["stream"] is True
        if requests is not None:
            requests.append(payload)
        return httpx.Response(status, content=chunks(), headers={"content-type": "text/event-stream"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = LlamaCppProvider(client, host="http://llama")
            return [token async for token in provider.stream_generate("prompt")]

    return asyncio.run(run())


@pytest.mark.parametrize("body", [THINK_IN_CONTENT, THINK_IN_REASONING], ids=["think-in-content", "think-in-reasoning"])
@pytest.mark.parametrize("chunk_size", range(1, 9))
def test_stream_parses_llama_cpp_sse_frames(body, chunk_size):
    # Small chunks split frames, lines, <think> tags and multi-byte UTF-8 sequences.
    assert "".join(_stream(body, chunk_size=chunk_size)) == EXPECTED


def test_stream_sends_chat_request():
    requests = []
    _stream(THINK_IN_CONTENT, requests=requests)
    assert requests == [{
        "model": "lfm-thinking",
        "messages": [{"role": "user", "content": "prompt"}],
        "n_predict": 2048,
        "temperature": 0.2,
        "stream": True,
        "reasoning_budget_tokens": 1024,
    }]


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\x85"])
def test_stream_keeps_tokens_with_unicode_line_separators(separator):
    # llama.cpp leaves these unescaped; only CR/LF may end an SSE line.
    tokens = _stream(_chat_stream({"content": f"a{separator}b"}))
    assert tokens == [f"a{separator}b"]


def test_stream_handles_crlf_framing():
    body = LLAMA_CPP_STREAM.replace("\n", "\r\n")
    assert "".join(_stream(body, chunk_size=3)) == EXPECTED


def test_stream_stops_at_final_frame():
    body = _chat_frame({"content": "ok"}) + _chat_frame({}, "length") + _chat_frame({"content": " ignored"})
    assert _stream(body) == ["ok"]


def test_stream_stops_at_done_marker():
    assert _stream(_chat_frame({"content": "ok"}) + "data: [DONE]\n\n" + _chat_frame({"content": " ignored"})) == ["ok"]


def test_stream_accepts_bare_json_body_from_non_sse_servers():
    # A server that ignores "stream" and answers with one chat.completion document.
    body = json.dumps({"choices": [{"index": 0, "finish_reason": "stop",
                                    "message": {"role": "assistant", "content": "I am a mock."}}]})
    assert _stream(body) == ["I am a mock."]


def test_stream_drops_unfinished_thinking():
    # n_predict ran out inside <think>: there is no answer to show.
    assert _stream(_chat_stream({"content": "<think>"}, {"content": "still going"})) == []


def test_stream_raises_on_error_frame():
    error = {"code": 500, "message": "context size exceeded", "type": "server_error"}
    with pytest.raises(LlamaCppStreamError, match="context size exceeded"):
        _stream(_chat_frame({"content": "partial"}) + f"data: {json.dumps({'error': error})}\n\n")


def test_stream_raises_on_legacy_error_line():
    with pytest.raises(LlamaCppStreamError, match="slot unavailable"):
        _stream('error: {"code": 503, "message": "slot unavailable"}\n\n')


def test_stream_raises_on_http_error_status():
    with pytest.raises(httpx.HTTPStatusError):
        _stream("", status=503)


def _generate(response_json, **kwargs):
    """Run LlamaCppProvider.generate against one chat.completion response."""
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=response_json)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LlamaCppProvider(client, host="http://llama").generate("prompt", **kwargs)

    return asyncio.run(run()), requests


def _completion(content, **message):
    return {"object": "chat.completion",
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": content, **message}}]}


def test_generate_strips_thinking_from_content():
    # Recorded: llama-server b11243, LFM2 template without <think>.
    text, requests = _generate(_completion("<think>Weighing supply risk</think>\n\nBrent looks firm € 😀"))
    assert text == "Brent looks firm € 😀"
    assert requests[0]["stream"] is False and "json_schema" not in requests[0]


def test_generate_ignores_separated_reasoning():
    # Recorded: same server, template with <think>.
    text, _ = _generate(_completion("\n\nBrent looks firm € 😀", reasoning_content="Weighing supply risk"))
    assert text == "Brent looks firm € 😀"


def test_generate_passes_json_schema_and_budget():
    schema = {"type": "object", "properties": {"p": {"type": "number"}}, "required": ["p"]}
    text, requests = _generate(_completion('{"p"\n:0}'), json_schema=schema, n_predict=1024)
    assert json.loads(text) == {"p": 0}
    assert requests[0]["json_schema"] == schema
    assert requests[0]["n_predict"] == 1024 and requests[0]["reasoning_budget_tokens"] == 512


def test_generate_omits_null_json_schema():
    _, requests = _generate(_completion("x"), json_schema=None)
    assert "json_schema" not in requests[0]


def test_generate_handles_null_content():
    text, _ = _generate(_completion(None))
    assert text == ""


@pytest.mark.parametrize(
    "text, expected",
    [
        ("<think>a</think>\n\nAnswer", "Answer"),
        ("  \n<think>a\nb</think>Answer <b>bold</b>", "Answer <b>bold</b>"),
        ("Answer without thinking", "Answer without thinking"),
        ("<b>bold</b> answer", "<b>bold</b> answer"),
        ("<think>never closed", ""),
        ("<thi", "<thi"),
        ("\n\nAnswer after separated reasoning", "Answer after separated reasoning"),
        ("  ", ""),
        ("Not <think>leading</think> here", "Not <think>leading</think> here"),
        ("", ""),
    ],
)
def test_reasoning_filter_at_every_split(text, expected):
    for split in range(len(text) + 1):
        for second in range(split, len(text) + 1):
            reasoning = ReasoningFilter()
            parts = [text[:split], text[split:second], text[second:]]
            out = "".join(reasoning.feed(p) for p in parts) + reasoning.flush()
            assert out == expected, (parts, out)


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
        ('data: {"choices":[{"finish_reason":null,"index":0,"delta":{"content":"a"}}]}', ("a", False)),
        ('data: {"choices":[{"finish_reason":null,"index":0,"delta":{"role":"assistant","content":null}}]}', ("", False)),
        ('data: {"choices":[{"finish_reason":null,"index":0,"delta":{"reasoning_content":"hm"}}]}', ("", False)),
        ('data: {"choices":[{"finish_reason":"stop","index":0,"delta":{}}]}', ("", True)),
        ('data: {"choices":[{"finish_reason":"length","index":0,"delta":{"content":"z"}}]}', ("z", True)),
        ('data: {"choices":[]}', ("", False)),
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
