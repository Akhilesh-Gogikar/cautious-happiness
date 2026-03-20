import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ALLOW_DEMO_AUTH"] = "false"

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.auth import router as auth_router
from app.routers.markets import router as markets_router
from app.routers.trade import router as trade_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(markets_router)
app.include_router(trade_router)
client = TestClient(app)


def test_login_success():
    response = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "analyst123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_fail():
    response = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_protected_route_no_token():
    response = client.get("/markets")
    assert response.status_code == 401


def test_demo_auth_can_be_enabled(monkeypatch):
    monkeypatch.setenv("ALLOW_DEMO_AUTH", "true")
    response = client.get("/markets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_protected_route_with_token():
    login_res = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "analyst123"}
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/markets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_rbac_trader_only():
    login_res = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "analyst123"}
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/trade/execute", headers=headers, json={"symbol": "WTI", "side": "buy", "quantity": 1})
    assert response.status_code == 403


def test_rbac_admin_success():
    login_res = client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret"}
    )
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/trade/execute", headers=headers, json={"symbol": "WTI", "side": "buy", "quantity": 1})
    assert response.status_code != 403
