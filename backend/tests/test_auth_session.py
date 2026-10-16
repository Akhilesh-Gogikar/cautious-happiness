from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.core import security
from app.routers import auth


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("ALLOW_DEMO_AUTH", raising=False)
    app = FastAPI()
    app.include_router(auth.router)
    return TestClient(app)


def _sign_in(client, username="analyst", password="analyst123"):
    return client.post("/auth/token", data={"username": username, "password": password})


def test_signing_in_returns_a_token_for_the_users_account(client):
    token = _sign_in(client).json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json() == {"username": "analyst", "email": "analyst@example.com", "disabled": False, "role": "analyst"}


def test_wrong_password_is_refused(client):
    assert _sign_in(client, password="nope").status_code == 401


@pytest.mark.parametrize(
    "headers",
    [
        {},  # no token
        {"Authorization": "Bearer not-a-jwt"},
    ],
)
def test_me_needs_a_valid_token(client, headers):
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_expired_tokens_are_refused(client):
    token = security.create_access_token({"sub": "analyst", "role": "analyst"}, timedelta(minutes=-1))
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_tokens_signed_with_the_old_public_default_key_are_refused(client):
    forged = jwt.encode(
        {"sub": "admin", "role": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "dev_secret_key_change_in_prod_73847384",
        algorithm=security.ALGORITHM,
    )
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


@pytest.mark.parametrize(
    "value",
    [None, "", "  ", "dev_secret_key_change_in_prod_73847384", "generate_a_secure_random_secret_key"],
)
def test_public_or_missing_secret_keys_are_replaced_by_a_random_one(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SECRET_KEY", value)
    first, second = security._load_secret_key(), security._load_secret_key()
    assert first != second and len(first) >= 64
    assert first not in security._PUBLIC_SECRET_KEYS


def test_a_configured_secret_key_is_used(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-long-private-value-from-the-env-file")
    assert security._load_secret_key() == "a-long-private-value-from-the-env-file"


@pytest.mark.parametrize("value, minutes", [(None, 30), ("1440", 1440), ("abc", 30), ("0", 1)])
def test_token_lifetime_comes_from_the_environment(monkeypatch, value, minutes):
    if value is None:
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    else:
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", value)
    assert security._load_token_minutes() == minutes
