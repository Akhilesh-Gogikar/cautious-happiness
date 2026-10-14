import asyncio
import json
import time

import pytest
import redis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

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


@pytest.fixture
def connect(monkeypatch):
    monkeypatch.setattr(lifecycle, "POLL_SECONDS", 0.01)
    app = FastAPI()
    app.include_router(lifecycle.router)
    client = TestClient(app)

    def _connect(task_id, messages=(), result=None, **pubsub_kwargs):
        fake_redis = FakeRedis(messages=messages, **pubsub_kwargs)
        monkeypatch.setattr(lifecycle, "async_redis", fake_redis)
        monkeypatch.setattr(lifecycle, "AsyncResult", lambda task_id, app: result or FakeResult())
        return client.websocket_connect(f"/ws/lifecycle/{task_id}"), fake_redis

    return _connect


def _receive_all(ws):
    events = []
    while True:
        try:
            events.append(ws.receive_json())
        except WebSocketDisconnect:
            return events


def _wait_until(predicate, timeout=2.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def test_cached_task_reports_complete(connect):
    ws, _ = connect("cached_abc123")
    with ws:
        assert _receive_all(ws) == [{"event": "complete", "message": "Analysis complete (Cached)"}]


def test_status_events_are_forwarded_and_complete_waits_for_result(connect):
    status = {"event": "status", "message": "Searching sources", "timestamp": ""}
    worker_complete = {"event": "complete", "message": "Analysis finished.", "timestamp": ""}
    result = FakeResult(finish_after=5)
    ws, fake_redis = connect("task-1", messages=[status, worker_complete], result=result)
    with ws:
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
    ws, _ = connect("task-crashed", result=FakeResult(finish_after=2, final_state=final_state))
    with ws:
        assert _receive_all(ws) == [{"event": "failed", "message": message}]


def test_failed_event_is_terminal(connect):
    failed = {"event": "failed", "message": "LLM unavailable", "timestamp": ""}
    ws, fake_redis = connect("task-2", messages=[failed], result=FakeResult())
    with ws:
        assert _receive_all(ws) == [failed]
    assert _wait_until(lambda: fake_redis.instance.closed)


def test_client_disconnect_releases_subscription(connect):
    ws, fake_redis = connect("unknown-task", result=FakeResult())
    with ws:
        assert _wait_until(lambda: fake_redis.instance and fake_redis.instance.subscribed == ["task_events:unknown-task"])
        ws.close()
        # Checked inside the block, before TestClient tears the app down on exit.
        assert _wait_until(lambda: fake_redis.instance.closed)


def test_redis_outage_reports_failure_and_releases_connection(connect):
    ws, fake_redis = connect("task-3", result=FakeResult(), fail_after_subscribe=True)
    with ws:
        assert _receive_all(ws) == [{"event": "failed", "message": "Lost track of the analysis task."}]
    assert _wait_until(lambda: fake_redis.instance.closed)


def test_gives_up_after_max_wait(connect, monkeypatch):
    monkeypatch.setattr(lifecycle, "MAX_WAIT_SECONDS", 0.05)
    ws, fake_redis = connect("never-finishes", result=FakeResult())
    with ws:
        events = _receive_all(ws)
    assert events == [{"event": "failed", "message": "Timed out waiting for the analysis to finish."}]
    assert _wait_until(lambda: fake_redis.instance.closed)
