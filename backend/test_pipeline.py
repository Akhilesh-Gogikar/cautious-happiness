import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_pipeline():
    print(f"Testing Intelligence Pipeline at {BASE_URL}...")
    
    # 0. Authenticate
    print("[0] Authenticating...")
    token = None
    try:
        auth_res = requests.post(f"{BASE_URL}/auth/token", data={"username": "trader", "password": "trader123"})
        auth_res.raise_for_status()
        token = auth_res.json()["access_token"]
        print("    Authenticated as Trader.")
    except Exception as e:
        print(f"    Authentication Failed: {e}")
        return

    # 1. Trigger Prediction
    print("[1] Triggering Prediction...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        payload = {
            "question": "Brent Crude Oil Physical vs Paper Market Divergence",
            "model": "lfm-thinking"
        }
        res = requests.post(f"{BASE_URL}/predict", json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()
        print(f"    Response: {data}")
    except Exception as e:
        print(f"    FAILED: {e}")
        return

    if data['status'] == 'cached':
        print("[2] Result was CACHED. Skipping polling.")
        print(f"    Critique: {data['result']['critique'][:100]}...")
        return

    task_id = data['task_id']
    print(f"    Task ID: {task_id}")

    # 2. Poll for completion
    print("[2] Polling for results...")
    for i in range(30): # 60 seconds max
        try:
            res = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
            task_data = res.json()
            status = task_data['status']
            print(f"    [{i*2}s] Status: {status}")
            
            if status == 'completed':
                result = task_data['result']
                print(f"[3] SUCCESS! Analysis Complete.")
                print(f"    Initial Forecast: {result['initial_forecast']}")
                print(f"    Adjusted Forecast: {result['adjusted_forecast']}")
                print(f"    Critique: {result['critique'][:100]}...")
                return
            
            if status == 'failed':
                print(f"[3] FAILED! Task failed.")
                return
                
        except Exception as e:
            print(f"    Polling error: {e}")
            
        time.sleep(2)

    print("[3] TIMEOUT! Task did not complete in 60s.")

if __name__ == "__main__":
    test_pipeline()
