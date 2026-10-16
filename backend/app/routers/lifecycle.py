import asyncio
import json
import logging
import os
import time

import redis.asyncio as aioredis
from celery.result import AsyncResult
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.auth import WebSocketAuthError, authenticate_websocket
from app.worker import celery_app

logger = logging.getLogger("alpha_insights")

router = APIRouter()

# The worker publishes task_events:<task_id> with the sync client in app.cache;
# this socket subscribes with an asyncio client so it never blocks the event loop.
async_redis = aioredis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))

POLL_SECONDS = 0.5
# Bounds how long one socket waits on a task, so a socket for an unknown or lost
# task id cannot hold its Redis subscription open forever.
MAX_WAIT_SECONDS = 900


async def _wait_for_disconnect(websocket: WebSocket) -> None:
    # After the sign-in message clients never send on this socket; receive() only
    # returns when they leave.
    try:
        while (await websocket.receive())["type"] != "websocket.disconnect":
            pass
    except (WebSocketDisconnect, RuntimeError):
        pass


# Celery's ready() is also true for these, but they are failures, not results.
FAILED_STATES = {"FAILURE": "The analysis task failed.", "REVOKED": "The analysis task was cancelled."}


@router.websocket("/ws/lifecycle/{task_id}")
async def websocket_lifecycle(websocket: WebSocket, task_id: str):
    await websocket.accept()
    # Signed-in users only (QA-004). Nothing about the task is read or subscribed to first.
    try:
        await authenticate_websocket(websocket)
    except WebSocketAuthError as refused:
        logger.info(f"Lifecycle socket refused with {refused.code}: {task_id}")
        try:
            await websocket.send_json({"event": "failed", "message": refused.message})
            await websocket.close(code=refused.code)
        except Exception:
            pass  # The client already left.
        return

    if task_id.startswith("cached_"):
        await websocket.send_json({"event": "complete", "message": "Analysis complete (Cached)"})
        await websocket.close()
        return

    result = AsyncResult(task_id, app=celery_app)
    channel = f"task_events:{task_id}"
    pubsub = async_redis.pubsub(ignore_subscribe_messages=True)
    client_gone = asyncio.create_task(_wait_for_disconnect(websocket))
    deadline = time.monotonic() + MAX_WAIT_SECONDS

    try:
        await pubsub.subscribe(channel)
        while not client_gone.done():
            message = await pubsub.get_message(timeout=POLL_SECONDS)
            if message:
                data = json.loads(message["data"])
                if data.get("event") == "failed":
                    await websocket.send_json(data)
                    break
                # The worker publishes "complete" before Celery stores the result, so
                # completion is reported below, once the result can actually be read.
                if data.get("event") != "complete":
                    await websocket.send_json(data)

            state = await asyncio.to_thread(lambda: result.state)
            if state == "SUCCESS":
                await websocket.send_json({"event": "complete", "message": "Task finished."})
                break
            if state in FAILED_STATES:
                await websocket.send_json({"event": "failed", "message": FAILED_STATES[state]})
                break
            if time.monotonic() > deadline:
                await websocket.send_json({"event": "failed", "message": "Timed out waiting for the analysis to finish."})
                break
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {task_id}")
    except Exception:
        # e.g. Redis dropped mid-stream: tell the client instead of leaving it waiting.
        logger.exception(f"Lifecycle stream failed: {task_id}")
        try:
            await websocket.send_json({"event": "failed", "message": "Lost track of the analysis task."})
        except Exception:
            pass
    finally:
        client_gone.cancel()
        # aclose() returns the connection to the pool without a network round trip
        # (Redis drops the subscription with the socket); an UNSUBSCRIBE here would
        # raise during a Redis outage and leak the connection.
        try:
            await pubsub.aclose()
        except Exception:
            logger.warning(f"Could not release lifecycle subscription: {task_id}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass
