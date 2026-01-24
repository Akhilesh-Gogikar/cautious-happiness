import sys
import os
import requests
import time

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def wait_for_server(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(f"{url}/health")
            print("Server is up!")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

def test_auth_flow():
    base_url = "http://localhost:8000"
    if not wait_for_server(base_url):
        print("Server timed out")
        return False
    
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "password123"
    test_name = "Test User"
    test_question = "What is your favorite color?"
    test_answer = "Blue"
    
    print(f"Testing with email: {test_email}")
    
    # 1. Register
    reg_resp = requests.post(f"{base_url}/auth/register", json={
        "email": test_email,
        "password": test_password,
        "full_name": test_name,
        "security_question": test_question,
        "security_answer": test_answer
    })
    print(f"Register status: {reg_resp.status_code}")
    if reg_resp.status_code != 200:
        print(reg_resp.text)
        return False
    
    # 2. Login
    login_resp = requests.post(f"{base_url}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    print(f"Login status: {login_resp.status_code}")
    if login_resp.status_code != 200:
        return False
        
    # 3. Recover Init
    rec_init_resp = requests.post(f"{base_url}/auth/recover-init", json={
        "email": test_email
    })
    print(f"Recover Init status: {rec_init_resp.status_code}")
    if rec_init_resp.status_code != 200:
        return False
    print(f"Question: {rec_init_resp.json()['question']}")
    
    # 4. Recover Verify
    new_password = "newpassword123"
    rec_ver_resp = requests.post(f"{base_url}/auth/recover-verify", json={
        "email": test_email,
        "answer": test_answer,
        "new_password": new_password
    })
    print(f"Recover Verify status: {rec_ver_resp.status_code}")
    if rec_ver_resp.status_code != 200:
        return False
        
    # 5. Login with new password
    login_new_resp = requests.post(f"{base_url}/auth/login", json={
        "email": test_email,
        "password": new_password
    })
    print(f"Login with new password status: {login_new_resp.status_code}")
    if login_new_resp.status_code != 200:
        return False
        
    print("Auth flow test PASSED")
    
    # 6. Check Database Files
    # 6. Check Database Files
    # Skipped file check as we are using Postgres now
    print("Database check skipped (Postgres in use)")
    return True

        
    return True

if __name__ == "__main__":
    if test_auth_flow():
        sys.exit(0)
    else:
        sys.exit(1)
