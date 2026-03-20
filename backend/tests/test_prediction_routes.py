import os
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ALLOW_DEMO_AUTH"] = "false"

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.limiter import check_rate_limit
from app.routers.auth import router as auth_router
from app.routers.prediction import compat_router, router as prediction_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(compat_router)
app.dependency_overrides[check_rate_limit] = lambda: None
client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/auth/token", data={"username": "analyst", "password": "analyst123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class DummyTask:
    id = "task-123"


def test_prediction_routes_support_prefixed_and_compat_endpoints():
    with patch("app.routers.prediction.redis_client.get", return_value=None), patch(
        "app.routers.prediction.run_forecast_task.delay",
        return_value=DummyTask(),
    ):
        prefixed = client.post(
            "/prediction/predict",
            json={"question": "Will copper rally?"},
            headers=auth_headers(),
        )
        compat = client.post(
            "/predict",
            json={"question": "Will copper rally?"},
            headers=auth_headers(),
        )

    assert prefixed.status_code == 200
    assert compat.status_code == 200
    assert prefixed.json()["task_id"] == "task-123"
    assert compat.json()["task_id"] == "task-123"
