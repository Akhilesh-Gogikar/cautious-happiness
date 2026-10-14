from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.connectors import alpaca as alpaca_module
from app.core.auth import get_current_active_user
from app.models import User
from app.routers import tools

BROWSER_HEADERS = {"x-alpaca-api-key": "BROWSER_KEY", "x-alpaca-secret": "BROWSER_SECRET"}


class FakeTradingClient:
    instances = []

    def __init__(self, api_key, secret_key, paper):
        self.credentials = (api_key, secret_key, paper)
        FakeTradingClient.instances.append(self)

    def get_account(self):
        return SimpleNamespace(account_number="PA123", equity="1000", cash="500", buying_power="2000", currency="USD")

    def submit_order(self, order):
        self.order = order
        return SimpleNamespace(id="ord-1", client_order_id="c-1", status="accepted", symbol=order.symbol,
                               qty=order.qty, side=order.side)


@pytest.fixture
def client(monkeypatch):
    FakeTradingClient.instances = []
    monkeypatch.setattr(alpaca_module, "TradingClient", FakeTradingClient)
    for name in ("ALPACA_API_KEY", "ALPACA_SECRET_KEY", "ALPACA_SECRET", "ALPACA_BASE_URL"):
        monkeypatch.delenv(name, raising=False)
    app = FastAPI()
    app.include_router(tools.router)
    app.dependency_overrides[get_current_active_user] = lambda: User(username="analyst")
    return TestClient(app)


def _call(client, name="get_account", headers=None, arguments=None):
    body = {"connector": "alpaca", "name": name, "arguments": arguments or {}}
    return client.post("/tools/call", json=body, headers=headers or {})


def _as_role(client, role):
    client.app.dependency_overrides[get_current_active_user] = lambda: User(username=f"{role}-user", role=role)


ORDER = {"symbol": "AAPL", "qty": 1, "side": "buy"}


def test_keys_sent_by_a_browser_are_ignored(client):
    response = _call(client, headers=BROWSER_HEADERS)
    assert response.status_code == 503
    assert response.json()["detail"] == tools.ALPACA_NOT_CONFIGURED
    assert FakeTradingClient.instances == []


def test_calls_use_the_server_credentials(client, monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY", "SERVER_KEY")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "SERVER_SECRET")
    response = _call(client, headers=BROWSER_HEADERS)
    assert response.status_code == 200
    assert response.json()["account_number"] == "PA123"
    assert [c.credentials for c in FakeTradingClient.instances] == [("SERVER_KEY", "SERVER_SECRET", True)]


@pytest.mark.parametrize(
    "env, expected",
    [
        ({}, {"configured": False, "paper": True}),
        ({"ALPACA_API_KEY": "k"}, {"configured": False, "paper": True}),
        ({"ALPACA_API_KEY": "k", "ALPACA_SECRET_KEY": "s"}, {"configured": True, "paper": True}),
        ({"ALPACA_API_KEY": "k", "ALPACA_SECRET": "s"}, {"configured": True, "paper": True}),  # older .env name
        ({"ALPACA_API_KEY": "k", "ALPACA_SECRET_KEY": "s", "ALPACA_BASE_URL": "https://api.alpaca.markets"},
         {"configured": True, "paper": False}),
    ],
)
def test_status_reports_server_configuration(client, monkeypatch, env, expected):
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    assert client.get("/tools/alpaca/status").json() == expected


def test_status_requires_a_signed_in_user(client):
    client.app.dependency_overrides.clear()
    assert client.get("/tools/alpaca/status").status_code == 401


@pytest.fixture
def configured(client, monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY", "SERVER_KEY")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "SERVER_SECRET")
    return client


@pytest.mark.parametrize("role", ["analyst", "risk_manager", "viewer"])
def test_orders_are_refused_without_a_trading_role(configured, role, caplog):
    _as_role(configured, role)
    response = _call(configured, "place_market_order", arguments=ORDER)
    assert response.status_code == 403
    assert FakeTradingClient.instances == []  # refused before touching Alpaca
    assert any(f"{role}-user" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("role", ["admin", "trader"])
def test_trading_roles_can_place_orders(configured, role, caplog):
    caplog.set_level("INFO")
    _as_role(configured, role)
    response = _call(configured, "place_market_order", arguments=ORDER)
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
    assert FakeTradingClient.instances[0].order.symbol == "AAPL"
    assert any(f"{role}-user" in r.getMessage() and "place_market_order" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("role", ["analyst", "risk_manager"])
def test_every_role_can_read_the_account(configured, role):
    _as_role(configured, role)
    assert _call(configured, "get_account").status_code == 200


def test_unknown_alpaca_tools_need_a_trading_role(configured):
    # Deny by default: a tool added later is not open to every user by accident.
    _as_role(configured, "analyst")
    assert _call(configured, "cancel_all_orders").status_code == 403
