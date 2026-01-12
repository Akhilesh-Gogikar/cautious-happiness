import sys
import os
import requests
import json

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Define base URL
BASE_URL = "http://localhost:8000"

def seed_users():
    """Seeds the database with default users for each role."""
    
    roles_and_users = [
        {"email": "trader@alphasignals.com", "password": "trader", "full_name": "Active Trader", "role": "trader"},
        {"email": "risk_manager@alphasignals.com", "password": "risk_manager", "full_name": "Risk Manager", "role": "risk_manager"},
        {"email": "developer@alphasignals.com", "password": "developer", "full_name": "Core Developer", "role": "developer"},
        {"email": "auditor@alphasignals.com", "password": "auditor", "full_name": "Compliance Auditor", "role": "auditor"}
    ]

    print(f"Checking connectivity to {BASE_URL}...")
    try:
        requests.get(f"{BASE_URL}/docs")
    except requests.exceptions.ConnectionError:
        print("Error: Backend is not running. Please start the backend server first (uvicorn app.main:app).")
        return

    print("Seeding users...")
    
    for user in roles_and_users:
        # 1. Register User
        print(f"Processing user: {user['email']} ({user['role']})")
        
        # We need to use the register endpoint. 
        # Assuming typical FastAPI register pattern based on auth_router.py
        
        payload = {
            "email": user["email"],
            "password": user["password"],
            "full_name": user["full_name"],
            "role": user["role"],
            "security_question": "What is your favorite color?",
            "security_answer": "blue"
        }
        
        try:
            # Try to register
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"  [SUCCESS] User {user['email']} created.")
            elif response.status_code == 400 and "already exists" in response.text:
                 print(f"  [SKIP] User {user['email']} already exists.")
            else:
                print(f"  [ERROR] Failed to create {user['email']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  [EXCEPTION] {e}")

if __name__ == "__main__":
    seed_users()
