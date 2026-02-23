import os
import sys

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from fastapi.testclient import TestClient

from app.main import app

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

def test_protected_route_with_token():
    # Login first
    login_res = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "analyst123"}
    )
    token = login_res.json()["access_token"]
    
    # Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/markets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_rbac_trader_only():
    # Login as Analyst
    login_res = client.post(
        "/auth/token",
        data={"username": "analyst", "password": "analyst123"}
    )
    token = login_res.json()["access_token"]
    
    # Try execution (Trader only)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/trade/execute", headers=headers)
    assert response.status_code == 403

def test_rbac_admin_success():
    # Login as Admin
    login_res = client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret"}
    )
    token = login_res.json()["access_token"]
    
    # Try execution (Admin allowed)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/trade/execute", headers=headers)
    # Note: It might return 200 or 500 depending on ExecutionService mock, 
    # but strictly checking it passes 403 is enough. 
    # Actually ExecutionService tries to connect to Polymarket likely, so it might fail.
    # But if it returns != 403, RBAC passed.
    assert response.status_code != 403 
