
import requests
import json
import random

BASE_URL = "http://localhost:8000/auth/register"

# Random email to avoid "already registered" error if previous run succeeded (unlikely given the error)
rand_id = random.randint(1000, 9999)
email = f"test_auth_debug_{rand_id}@example.com"

def test_register():
    payload = {
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "security_question": "Pet?",
        "security_answer": "Dog"
    }
    print(f"Testing payload: {payload}")
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
             print("SUCCESS: User registered.")
        else:
             print("FAILURE: Registration failed.")
    except Exception as e:
        print(f"Error: {e}")

test_register()
