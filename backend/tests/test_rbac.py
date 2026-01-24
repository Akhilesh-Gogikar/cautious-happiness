import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app as fastapi_app
from app.database_users import BaseUsers, get_db
from app import models_db, auth
from datetime import timedelta

# Test database setup
# Test database setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure models are loaded
import app.models_db

BaseUsers.metadata.drop_all(bind=engine)
BaseUsers.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db
client = TestClient(fastapi_app)


@pytest.fixture
def setup_users():
    """Create test users with different roles."""
    db = TestingSessionLocal()
    
    # Clear existing users
    db.query(models_db.User).delete()
    db.query(models_db.UserProfile).delete()
    db.commit()
    
    # Create users with different roles
    users = []
    roles = ["trader", "risk_manager", "developer", "auditor"]
    
    for role in roles:
        user = models_db.User(
            email=f"{role}@test.com",
            hashed_password=auth.get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        profile = models_db.UserProfile(
            user_id=user.id,
            full_name=f"Test {role.title()}",
            role=role
        )
        db.add(profile)
        db.commit()
        
        users.append((user, role))
    
    db.close()
    return users


def get_auth_token(email: str, password: str = "password123"):
    """Helper to get authentication token."""
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_trader_can_execute_trades(setup_users):
    """Test that traders can execute trades."""
    token = get_auth_token("trader@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trader should be able to create algo orders
    response = client.post(
        "/trade/algo",
        json={
            "market_id": "test_market",
            "type": "TWAP",
            "total_size_usd": 100.0,
            "duration_minutes": 60
        },
        headers=headers
    )
    assert response.status_code == 200


def test_trader_can_view_own_trades(setup_users):
    """Test that traders can view their own trades."""
    token = get_auth_token("trader@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trader should be able to view signals
    response = client.get("/signals", headers=headers)
    assert response.status_code == 200


def test_auditor_cannot_execute_trades(setup_users):
    """Test that auditors cannot execute trades."""
    token = get_auth_token("auditor@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Auditor should NOT be able to create algo orders
    response = client.post(
        "/trade/algo",
        json={
            "market_id": "test_market",
            "type": "TWAP",
            "total_size_usd": 100.0,
            "duration_minutes": 60
        },
        headers=headers
    )
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]


def test_auditor_can_view_all_trades(setup_users):
    """Test that auditors can view all trades."""
    token = get_auth_token("auditor@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Auditor should be able to view signals (read-only)
    response = client.get("/signals", headers=headers)
    assert response.status_code == 200


def test_risk_manager_can_set_limits(setup_users):
    """Test that risk managers can set risk limits."""
    token = get_auth_token("risk_manager@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Risk manager should be able to update exposure limits
    response = client.put(
        "/risk/limits",
        json={
            "factor": "Politics.Trump",
            "limit_usd": 1000.0
        },
        headers=headers
    )
    assert response.status_code == 200


def test_trader_cannot_set_limits(setup_users):
    """Test that traders cannot set risk limits."""
    token = get_auth_token("trader@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trader should NOT be able to update exposure limits
    response = client.put(
        "/risk/limits",
        json={
            "factor": "Politics.Trump",
            "limit_usd": 1000.0
        },
        headers=headers
    )
    assert response.status_code == 403


def test_developer_has_all_permissions(setup_users):
    """Test that developers have all permissions."""
    token = get_auth_token("developer@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Developer should be able to execute trades
    response = client.post(
        "/trade/algo",
        json={
            "market_id": "test_market",
            "type": "TWAP",
            "total_size_usd": 100.0,
            "duration_minutes": 60
        },
        headers=headers
    )
    assert response.status_code == 200
    
    # Developer should be able to set risk limits
    response = client.put(
        "/risk/limits",
        json={
            "factor": "Politics.Trump",
            "limit_usd": 1000.0
        },
        headers=headers
    )
    assert response.status_code == 200
    
    # Developer should be able to ingest alt data
    response = client.post(
        "/alt-data/ingest",
        params={"signal_type": "SATELLITE"},
        headers=headers
    )
    assert response.status_code == 200


def test_auditor_cannot_ingest_data(setup_users):
    """Test that auditors cannot ingest alternative data."""
    token = get_auth_token("auditor@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Auditor should NOT be able to ingest alt data
    response = client.post(
        "/alt-data/ingest",
        params={"signal_type": "SATELLITE"},
        headers=headers
    )
    assert response.status_code == 403


def test_unauthenticated_access_denied(setup_users):
    """Test that unauthenticated users cannot access protected routes."""
    # No token provided
    response = client.get("/signals")
    assert response.status_code == 401
    
    response = client.post(
        "/trade/algo",
        json={
            "market_id": "test_market",
            "type": "TWAP",
            "total_size_usd": 100.0,
            "duration_minutes": 60
        }
    )
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
