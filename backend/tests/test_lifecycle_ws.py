import asyncio
import contextlib
import json
import time
from datetime import timedelta

import pytest
import redis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from starlette.websockets import WebSocketDisconnect

from app.core import auth, security
from app.models import UserInDB
from app.routers import lifecycle


class FakePubSub:
    """Mirrors the parts of redis.asyncio.client.PubSub the handler relies on."""

    def __init__(self, messages, ignore_subscribe_messages=False, fail_after_subscribe=False):
        self.messages = list(messages)
        self.ignore_subscribe_messages = ignore_subscribe_messages
        self.fail_after_subscribe = fail_after_subscribe
        self.subscribed = []
        self.closed = False

    async def subscribe(self, channel):
        self.subscribed.append(channel)
        if not self.ignore_subscribe_messages:
            # Real Redis confirms every SUBSCRIBE with a message of its own.
            self.messages.insert(0, {"type": "subscribe", "channel": channel.encode(), "data": 1})

    async def unsubscribe(self, channel):
        if self.fail_after_subscribe:
            raise redis.exceptions.ConnectionError("Connection closed by server.")
        self.subscribed.remove(channel)

    async def get_message(self, timeout=0.0):
        await asyncio.sleep(0)
        if self.fail_after_subscribe:
            raise redis.exceptions.ConnectionError("Connection closed by server.")
        if self.messages:
            message = self.messages.pop(0)
            if message.get("type") == "subscribe":
                return message
            return {"type": "message", "data": json.dumps(message).encode()}
        await asyncio.sleep(min(timeout, 0.01))
        return None

    async def aclose(self):
        await asyncio.sleep(0)
        self.subscribed = []
        self.closed = True


class FakeRedis:
    def __init__(self, **pubsub_kwargs):
        self.pubsub_kwargs = pubsub_kwargs
        self.instance = None

    def pubsub(self, ignore_subscribe_messages=False):
        self.instance = FakePubSub(ignore_subscribe_messages=ignore_subscribe_messages, **self.pubsub_kwargs)
        return self.instance


class FakeResult:
    """Celery AsyncResult stand-in: PENDING until `finish_after` state checks, then `final_state`."""

    def __init__(self, finish_after=None, final_state="SUCCESS"):
        self.finish_after = finish_after
        self.final_state = final_state
        self.checks = 0

    @property
    def state(self):
        self.checks += 1
        if self.finish_after is not None and self.checks >= self.finish_after:
            return self.final_state
        return "PENDING"


def _auth_message(token):
    return json.dumps({"type": "auth", "token": token})


def _token(username="analyst", **claims):
    return security.create_access_token({"sub": username, **claims})


@pytest.fixture
def results_requested():
    return []


@pytest.fixture
def connect(monkeypatch, results_requested):
    monkeypatch.delenv("ALLOW_DEMO_AUTH", raising=False)
    monkeypatch.setattr(lifecycle, "POLL_SECONDS", 0.01)
    app = FastAPI()
    app.include_router(lifecycle.router)
    client = TestClient(app)

    def fake_async_result(task_id, app, result):
        results_requested.append(task_id)
        return result or FakeResult()

    @contextlib.contextmanager
    def _session(task_id, first_message):
        with client.websocket_connect(f"/ws/lifecycle/{task_id}") as ws:
            if first_message is not None:
                ws.send_text(first_message)
            yield ws

    def _connect(task_id, messages=(), result=None, first_message="signed-in", **pubsub_kwargs):
        # first_message: the client's first frame; by default an auth message with a valid token.
        fake_redis = FakeRedis(messages=messages, **pubsub_kwargs)
        monkeypatch.setattr(lifecycle, "async_redis", fake_redis)
        monkeypatch.setattr(lifecycle, "AsyncResult", lambda task_id, app: fake_async_result(task_id, app, result))
        if first_message == "signed-in":
            first_message = _auth_message(_token())
        return _session(task_id, first_message), fake_redis

    return _connect


def _receive_all(ws):
    return _receive_until_closed(ws)[0]


def _receive_until_closed(ws):
    events = []
    while True:
        try:
            events.append(ws.receive_json())
        except WebSocketDisconnect as closed:
            return events, closed.code


def _wait_until(predicate, timeout=2.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def test_cached_task_reports_complete(connect):
    session, _ = connect("cached_abc123")
    with session as ws:
        assert _receive_all(ws) == [{"event": "complete", "message": "Analysis complete (Cached)"}]


def test_status_events_are_forwarded_and_complete_waits_for_result(connect):
    status = {"event": "status", "message": "Searching sources", "timestamp": ""}
    worker_complete = {"event": "complete", "message": "Analysis finished.", "timestamp": ""}
    result = FakeResult(finish_after=5)
    session, fake_redis = connect("task-1", messages=[status, worker_complete], result=result)
    with session as ws:
        events = _receive_all(ws)
    # The worker's own "complete" is not forwarded: it is published before Celery
    # stores the result, so the client could fetch a result that is not there yet.
    # (The subscribe confirmation is not forwarded either.)
    assert events == [status, {"event": "complete", "message": "Task finished."}]
    assert result.checks == 5
    assert _wait_until(lambda: fake_redis.instance.closed)


@pytest.mark.parametrize(
    "final_state, message",
    [("FAILURE", "The analysis task failed."), ("REVOKED", "The analysis task was cancelled.")],
)
def test_failed_celery_states_are_reported_as_failed(connect, final_state, message):
    # e.g. a worker child killed mid-task: Celery stores FAILURE and nothing publishes "failed".
    session, _ = connect("task-crashed", result=FakeResult(finish_after=2, final_state=final_state))
    with session as ws:
        assert _receive_all(ws) == [{"event": "failed", "message": message}]


def test_failed_event_is_terminal(connect):
    failed = {"event": "failed", "message": "LLM unavailable", "timestamp": ""}
    session, fake_redis = connect("task-2", messages=[failed], result=FakeResult())
    with session as ws:
        assert _receive_all(ws) == [failed]
    assert _wait_until(lambda: fake_redis.instance.closed)


def test_client_disconnect_releases_subscription(connect):
    session, fake_redis = connect("unknown-task", result=FakeResult())
    with session as ws:
        assert _wait_until(lambda: fake_redis.instance and fake_redis.instance.subscribed == ["task_events:unknown-task"])
        ws.close()
        # Checked inside the block, before TestClient tears the app down on exit.
        assert _wait_until(lambda: fake_redis.instance.closed)


def test_redis_outage_reports_failure_and_releases_connection(connect):
    session, fake_redis = connect("task-3", result=FakeResult(), fail_after_subscribe=True)
    with session as ws:
        assert _receive_all(ws) == [{"event": "failed", "message": "Lost track of the analysis task."}]
    assert _wait_until(lambda: fake_redis.instance.closed)


def test_gives_up_after_max_wait(connect, monkeypatch):
    monkeypatch.setattr(lifecycle, "MAX_WAIT_SECONDS", 0.05)
    session, fake_redis = connect("never-finishes", result=FakeResult())
    with session as ws:
        events = _receive_all(ws)
    assert events == [{"event": "failed", "message": "Timed out waiting for the analysis to finish."}]
    assert _wait_until(lambda: fake_redis.instance.closed)


REFUSED = {
    "nothing sent": (None, auth.WS_CLOSE_POLICY_VIOLATION),
    "not JSON": ("hello", auth.WS_CLOSE_POLICY_VIOLATION),
    "JSON that is not an object": ('["auth"]', auth.WS_CLOSE_POLICY_VIOLATION),
    "object without the auth type": (lambda: json.dumps({"token": _token()}), auth.WS_CLOSE_POLICY_VIOLATION),
    "auth message without a token": ('{"type": "auth"}', auth.WS_CLOSE_UNAUTHORIZED),
    "empty token": (lambda: _auth_message(""), auth.WS_CLOSE_UNAUTHORIZED),
    "token that is not a string": (lambda: _auth_message(123), auth.WS_CLOSE_UNAUTHORIZED),
    "malformed token": (lambda: _auth_message("not-a-jwt"), auth.WS_CLOSE_UNAUTHORIZED),
    "expired token": (
        lambda: _auth_message(security.create_access_token({"sub": "analyst"}, expires_delta=timedelta(minutes=-1))),
        auth.WS_CLOSE_UNAUTHORIZED,
    ),
    "token signed with another key": (
        lambda: _auth_message(jwt.encode({"sub": "admin"}, "some-other-key", algorithm=security.ALGORITHM)),
        auth.WS_CLOSE_UNAUTHORIZED,
    ),
    "token for an unknown user": (lambda: _auth_message(_token("nobody")), auth.WS_CLOSE_UNAUTHORIZED),
}


@pytest.mark.parametrize("task_id", ["task-9", "cached_abc123"])
@pytest.mark.parametrize("case", list(REFUSED))
def test_socket_without_a_valid_sign_in_is_refused_before_the_task_is_read(
    connect, monkeypatch, results_requested, task_id, case
):
    monkeypatch.setattr(auth, "WS_AUTH_TIMEOUT_SECONDS", 0.05)
    first_message, code = REFUSED[case]
    if callable(first_message):
        first_message = first_message()
    session, fake_redis = connect(task_id, result=FakeResult(finish_after=1), first_message=first_message)
    with session as ws:
        events, closed_with = _receive_until_closed(ws)
    assert [e["event"] for e in events] == ["failed"]
    assert closed_with == code
    # Neither Celery nor Redis was asked about the task.
    assert results_requested == []
    assert fake_redis.instance is None


def test_binary_first_frame_is_refused(connect, results_requested):
    session, fake_redis = connect("task-9", first_message=None)
    with session as ws:
        ws.send_bytes(_auth_message(_token()).encode())
        assert _receive_until_closed(ws)[1] == auth.WS_CLOSE_POLICY_VIOLATION
    assert results_requested == [] and fake_redis.instance is None


def test_disabled_account_is_refused(connect, monkeypatch, results_requested):
    disabled = UserInDB(username="analyst", role="analyst", disabled=True, hashed_password="x")
    monkeypatch.setattr(auth.user_service, "get_user", lambda username: disabled)
    session, fake_redis = connect("task-9")
    with session as ws:
        events, closed_with = _receive_until_closed(ws)
    assert events == [{"event": "failed", "message": "This account is disabled."}]
    assert closed_with == auth.WS_CLOSE_FORBIDDEN
    assert results_requested == [] and fake_redis.instance is None


def test_client_leaving_before_signing_in_reads_nothing(connect, results_requested):
    session, fake_redis = connect("task-9", first_message=None)
    with session as ws:
        ws.close()
    assert results_requested == [] and fake_redis.instance is None


def test_signed_in_user_follows_the_task(connect, results_requested):
    session, _ = connect("task-4", result=FakeResult(finish_after=2), first_message=_auth_message(_token("trader")))
    with session as ws:
        events, closed_with = _receive_until_closed(ws)
    assert events == [{"event": "complete", "message": "Task finished."}]
    assert closed_with == 1000
    assert results_requested == ["task-4"]


def test_demo_auth_accepts_an_auth_message_without_a_token(connect, monkeypatch):
    monkeypatch.setenv("ALLOW_DEMO_AUTH", "true")
    session, _ = connect("task-5", result=FakeResult(finish_after=1), first_message='{"type": "auth", "token": null}')
    with session as ws:
        assert _receive_all(ws) == [{"event": "complete", "message": "Task finished."}]


@pytest.mark.parametrize(
    "first_message, code",
    [
        (None, auth.WS_CLOSE_POLICY_VIOLATION),
        ("hello", auth.WS_CLOSE_POLICY_VIOLATION),
        (_auth_message("not-a-jwt"), auth.WS_CLOSE_UNAUTHORIZED),
    ],
)
def test_demo_auth_still_needs_an_auth_message_and_refuses_bad_tokens(
    connect, monkeypatch, results_requested, first_message, code
):
    # As on HTTP routes: demo auth stands in only for a missing token, never for a rejected one.
    monkeypatch.setenv("ALLOW_DEMO_AUTH", "true")
    monkeypatch.setattr(auth, "WS_AUTH_TIMEOUT_SECONDS", 0.05)
    session, _ = connect("task-6", result=FakeResult(finish_after=1), first_message=first_message)
    with session as ws:
        assert _receive_until_closed(ws)[1] == code
    assert results_requested == []
