
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app

def check_pages():
    client = TestClient(app)
    routes = [
        "/",
        "/sources",
        "/manual-scrape",
        "/records",
        "/catalog",
        "/services",
        "/intelligence",
        "/compare",
        "/health"
    ]
    
    for route in routes:
        print(f"Testing {route}...")
        try:
            response = client.get(route)
            print(f"  Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:500]}")
        except Exception as e:
            print(f"  FAILED to request {route}: {e}")

if __name__ == "__main__":
    check_pages()
