"""
Google Maps scraper using Playwright to extract organization ratings and operating hours.
"""
import logging
from app.scraping.fetcher import PlaywrightFetcher

logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    """Scrapes Google Maps data via search query."""

    def __init__(self):
        self.fetcher = PlaywrightFetcher(headless=True)

    def scrape(self, org_name: str, city: str = "") -> dict:
        """Search Google for the organization and extract knowledge panel stats."""
        query = f"{org_name} {city} Zimbabwe".strip().replace(" ", "+")
        url = f"https://www.google.com/search?q={query}"
        
        try:
            logger.info(f"[GoogleMaps] Searching: {url}")
            html = self.fetcher.fetch_html(url)
            return self._parse_html(html)
        except Exception as e:
            logger.warning(f"[GoogleMaps] Failed to scrape {org_name}: {e}")
            return {}

    def _parse_html(self, html: str) -> dict:
        data = {}
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for the rating in the knowledge panel (often a span with class 'Aq14fc' or similar, 
        # but class names change. We will use a regex/text search for "out of 5" or just look for the star container).
        # A safer approach for a generic HTML dump is looking for text patterns.
        import re
        text = soup.get_text(" ", strip=True)
        
        # Match rating pattern e.g. "4.5 out of 5" or "Rating: 4.5"
        rating_match = re.search(r"(\d\.\d)[\s]+(?:out of 5|stars)", text, re.IGNORECASE)
        if rating_match:
            try:
                data["rating_avg"] = float(rating_match.group(1))
            except ValueError:
                pass
                
        # Match review count e.g. "1,200 Google reviews"
        review_match = re.search(r"([\d,]+)[\s]+(?:Google )?reviews", text, re.IGNORECASE)
        if review_match:
            try:
                data["review_count"] = int(review_match.group(1).replace(",", ""))
            except ValueError:
                pass
                
        # Look for hours e.g. "Open ⋅ Closes 5 PM"
        hours_match = re.search(r"(?:Open|Closed)[\s⋅]+(?:Closes|Opens)[\s]+(\d{1,2}[:\d]*\s*[AP]M)", text, re.IGNORECASE)
        if hours_match:
            data["operating_hours"] = f"Today: {hours_match.group(0)}"
            
        return data
