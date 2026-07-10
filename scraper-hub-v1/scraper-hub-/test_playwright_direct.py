import asyncio
import sys
import os

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from app.services.fetcher import PlaywrightFetcher
from app.config import settings

async def test_playwright():
    print("Initializing PlaywrightFetcher...")
    fetcher = PlaywrightFetcher()
    url = "https://www.google.com"
    print(f"Fetching {url}...")
    try:
        content = await fetcher.fetch_page_content(url)
        print(f"Success! Content length: {len(content)}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright())
