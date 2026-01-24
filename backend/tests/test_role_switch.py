import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database_users import BaseUsers, get_db
from app import models_db, auth
import os

# Use an in-memory SQLite database for testing to avoid file system issues
# Use Postgres
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    BaseUsers.metadata.drop_all(bind=engine)
    BaseUsers.metadata.create_all(bind=engine)
    yield
    BaseUsers.metadata.drop_all(bind=engine)

def test_update_role():
    # 1. Register a user
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "security_question": "What is your favorite color?",
        "security_answer": "blue"
    })
    
    # 2. Login to get token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Check initial role (should be default 'user')
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "user"
    
    # 4. Update role to 'developer'
    update_response = client.post("/auth/role", json={"role": "developer"}, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "developer"
    
    # 5. Verify role update in /me
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.json()["role"] == "developer"

    # 6. Update to invalid role
    update_response = client.post("/auth/role", json={"role": "hacker"}, headers=headers)
    assert update_response.status_code == 400
