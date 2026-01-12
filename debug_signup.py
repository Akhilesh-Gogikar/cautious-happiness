
import requests
import json

BASE_URL = "http://localhost:8000/auth/register"

def test_register(payload):
    print(f"Testing payload: {payload}")
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 422:
             print("Validation Error Details:", response.json())
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

# 1. Valid Payload
test_register({
    "email": "test_auth_debug_1@example.com",
    "password": "password123",
    "full_name": "Test User",
    "security_question": "Pet?",
    "security_answer": "Dog"
})

# 2. Invalid Email (No @)
test_register({
    "email": "test_auth_debug_no_at",
    "password": "password123",
    "full_name": "Test User",
    "security_question": "Pet?",
    "security_answer": "Dog"
})

# 3. Missing Fields
test_register({
    "email": "test_auth_debug_missing@example.com",
    "password": "password123"
})

# 4. Empty Strings
test_register({
    "email": "",
    "password": "",
    "full_name": "",
    "security_question": "",
    "security_answer": ""
})
