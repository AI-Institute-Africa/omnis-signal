import asyncio
import requests
from app.config import settings


class SimpleRequestsFetcher:
    def __init__(self):
        self.timeout = 30

    async def fetch_page_content(self, url: str) -> str:
        """Fetch the HTML content of a web page using requests."""
        def _fetch():
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        
        return await asyncio.to_thread(_fetch)