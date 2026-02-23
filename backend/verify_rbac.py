
import requests

BASE_URL = "http://localhost:8000"

def get_token(username, password):
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def test_rbac():
    print("--- RBAC Verification: Trade Execution ---")
    
    # 1. Test ANALYST (Should Fail)
    print("\n[1] Testing Analyst Access...")
    analyst_token = get_token("analyst", "analyst123")
    if not analyst_token:
        print("❌ Failed to login as analyst")
        return

    headers = {"Authorization": f"Bearer {analyst_token}"}
    try:
        res = requests.post(f"{BASE_URL}/trade/execute", headers=headers)
        if res.status_code == 403:
             print("✅ Success: Analyst WAS denied (403 Forbidden).")
        else:
             print(f"❌ Failure: Analyst got {res.status_code} (Expected 403).")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. Test TRADER (Should Succeed)
    print("\n[2] Testing Trader Access...")
    trader_token = get_token("trader", "trader123")
    if not trader_token:
        print("❌ Failed to login as trader")
        return

    headers = {"Authorization": f"Bearer {trader_token}"}
    try:
        res = requests.post(f"{BASE_URL}/trade/execute", headers=headers)
        if res.status_code == 200:
             print("✅ Success: Trader WAS allowed (200 OK).")
        else:
             print(f"❌ Failure: Trader got {res.status_code} (Expected 200).")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rbac()
