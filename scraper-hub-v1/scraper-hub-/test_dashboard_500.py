from fastapi.testclient import TestClient
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app

def test_dashboard():
    client = TestClient(app)
    try:
        response = client.get("/")
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard()
