import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models_db, database_users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_attribution_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

from app.database_users import get_db
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for API requests."""
    # Create test user
    models_db.BaseUsers.metadata.create_all(bind=engine)
    
    # Register user
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "security_question": "Test Q",
        "security_answer": "Test A"
    })

    # Update role to developer for testing
    db = TestingSessionLocal()
    user = db.query(models_db.User).filter(models_db.User.email == "test@example.com").first()
    if user and user.profile:
        user.profile.role = "developer"
        db.commit()
    db.close()
    
    # Login to get token
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.status_code} - {response.text}")
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_attribution_summary(client, auth_headers):
    """Test GET /api/attribution/summary endpoint."""
    response = client.get("/api/attribution/summary", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "total_trades" in data
    assert "total_pnl" in data
    assert "realized_pnl" in data
    assert "unrealized_pnl" in data
    assert "win_rate" in data
    assert "avg_pnl_per_trade" in data

def test_get_attribution_by_model(client, auth_headers):
    """Test GET /api/attribution/by-model endpoint."""
    response = client.get("/api/attribution/by-model", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "breakdown" in data
    assert isinstance(data["breakdown"], list)

def test_get_attribution_by_source(client, auth_headers):
    """Test GET /api/attribution/by-source endpoint."""
    response = client.get("/api/attribution/by-source", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "breakdown" in data
    assert isinstance(data["breakdown"], list)

def test_get_attribution_by_strategy(client, auth_headers):
    """Test GET /api/attribution/by-strategy endpoint."""
    response = client.get("/api/attribution/by-strategy", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "breakdown" in data
    assert isinstance(data["breakdown"], list)

def test_get_attribution_by_category(client, auth_headers):
    """Test GET /api/attribution/by-category endpoint."""
    response = client.get("/api/attribution/by-category", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "breakdown" in data
    assert isinstance(data["breakdown"], list)

def test_get_attribution_timeseries(client, auth_headers):
    """Test GET /api/attribution/timeseries endpoint."""
    response = client.get("/api/attribution/timeseries?interval=day", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "timeseries" in data
    assert isinstance(data["timeseries"], list)

def test_get_attribution_trades(client, auth_headers):
    """Test GET /api/attribution/trades endpoint."""
    response = client.get("/api/attribution/trades?limit=10", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert "trades" in data
    assert isinstance(data["trades"], list)

def test_get_attribution_trades_with_filters(client, auth_headers):
    """Test GET /api/attribution/trades with filters."""
    response = client.get(
        "/api/attribution/trades?model_used=openforecaster&strategy_type=KELLY&is_closed=false",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "trades" in data

def test_attribution_endpoints_require_auth(client):
    """Test that attribution endpoints require authentication."""
    endpoints = [
        "/api/attribution/summary",
        "/api/attribution/by-model",
        "/api/attribution/by-source",
        "/api/attribution/by-strategy",
        "/api/attribution/timeseries",
        "/api/attribution/trades"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401  # Unauthorized

def test_attribution_summary_with_date_range(client, auth_headers):
    """Test attribution summary with date range filters."""
    response = client.get(
        "/api/attribution/summary?start_date=2024-01-01T00:00:00&end_date=2024-12-31T23:59:59",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_trades" in data
