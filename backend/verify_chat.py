
import requests
import json

BASE_URL = "http://localhost:8000"

def get_token(username, password):
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def verify_chat():
    print("--- Chat Interface Verification ---")
    
    # 1. Login
    token = get_token("analyst", "analyst123")
    if not token:
        print("❌ Login failed")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Send Message (Round 1)
    print("\n[1] Sending first message (What is the price of Brent?)...")
    payload1 = {
        "question": "What is the key driver of Brent Crude today?",
        "history": [],
        "context": {"route_path": "/markets"},
        "model": "openforecaster" # Use reliable model
    }
    
    try:
        res1 = requests.post(f"{BASE_URL}/chat", json=payload1, headers=headers)
        if res1.status_code == 200:
            data1 = res1.json()
            response1 = data1.get("response", "")
            print(f"✅ Response 1 (Length {len(response1)}): {response1[:100]}...")
            
            # 3. Send Message (Round 2) - Test History
            print("\n[2] Sending follow-up (Why is that happening?)...")
            history = [
                {"role": "user", "content": payload1["question"], "timestamp": 0},
                {"role": "assistant", "content": response1, "timestamp": 0}
            ]
            payload2 = {
                "question": "Does this impact WTI?",
                "history": history,
                "context": {"route_path": "/markets"},
                "model": "openforecaster"
            }
            res2 = requests.post(f"{BASE_URL}/chat", json=payload2, headers=headers)
            if res2.status_code == 200:
                data2 = res2.json()
                print(f"✅ Response 2: {data2.get('response', '')[:100]}...")
            else:
                print(f"❌ Round 2 Failed: {res2.status_code} - {res2.text}")
                
        else:
            print(f"❌ Round 1 Failed: {res1.status_code} - {res1.text}")
            
    except Exception as e:
         print(f"❌ Exception: {e}")

if __name__ == "__main__":
    verify_chat()
