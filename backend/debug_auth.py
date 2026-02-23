import sys
import os
sys.path.append("/root/cautious-happiness/backend")

from app.core.security import get_password_hash, verify_password
import requests

BASE_URL = "http://localhost:8000" # Assuming your FastAPI app runs on this URL

def test_login():
    print(f"Testing login at {BASE_URL}/auth/token")
    # Using 'analyst' from new UserService
    payload = {
        "username": "analyst",
        "password": "analyst123"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=payload)
        if response.status_code == 200:
            token = response.json()
            print("✅ Login Successful")
            print(f"Token: {token['access_token'][:20]}...")
            return token['access_token']
        else:
            print(f"❌ Login Failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Example of direct password hashing/verification (if still needed for other debugging)
    # pwd = "secret"
    # hashed = get_password_hash(pwd)
    # print(f"Hash: {hashed}")
    # is_valid = verify_password(pwd, hashed)
    # print(f"Valid: {is_valid}")

    # Test the login endpoint
    access_token = test_login()
    if access_token:
        print("\nLogin test completed successfully.")
    else:
        print("\nLogin test failed.")
