from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.main import app
from app.main import app
from app.database_users import BaseUsers, get_db
from app import models_db

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    BaseUsers.metadata.create_all(bind=engine)
    yield
    BaseUsers.metadata.drop_all(bind=engine)

def test_register_user(setup_db):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "strongpassword",
            "full_name": "Test User",
            "security_question": "What is your pet's name?",
            "security_answer": "Fluffy"
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_user(setup_db):
    # Depending on test order, user might already exist.
    # If not, register first.
    # But pytest runs sequentially here.
    
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "strongpassword"
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(setup_db):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401

def test_recover_init(setup_db):
    response = client.post(
        "/auth/recover-init",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["question"] == "What is your pet's name?"

def test_recover_verify(setup_db):
    response = client.post(
        "/auth/recover-verify",
        json={
            "email": "test@example.com",
            "answer": "Fluffy",
            "new_password": "newstrongpassword"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Login with new password
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "newstrongpassword"
        },
    )
    assert response.status_code == 200
