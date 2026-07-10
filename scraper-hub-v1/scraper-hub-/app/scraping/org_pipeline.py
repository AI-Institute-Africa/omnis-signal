"""
OrgScrapePipeline — orchestrates all scrapers for a single organization.
Phase 3 implementation: website scraper is active; others are stubs ready for expansion.
"""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models.organization import Organization

logger = logging.getLogger(__name__)


class OrgScrapePipeline:
    """Runs all data collection stages for one organization."""

    def __init__(self, db: Session):
        self.db = db

    def run(self, org: Organization):
        logger.info(f"[Pipeline] Starting scrape for: {org.name}")
        collected = {}

        # Stage 1: Website scraper
        website_text = ""
        try:
            from app.scraping.org_scrapers.website_scraper import WebsiteScraper
            data = WebsiteScraper().scrape(org.website or "")
            if data:
                collected.update(data)
                logger.info(f"[Pipeline] Website scraper got {len(data)} fields for {org.name}")
            # Try to fetch raw text for AI
            import httpx, bs4
            resp = httpx.get(org.website, timeout=10, follow_redirects=True)
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            website_text = soup.get_text(" ", strip=True)[:15000]
        except Exception as e:
            logger.warning(f"[Pipeline] Website scraper failed for {org.name}: {e}")

        # Stage 2: Google Maps
        try:
            from app.scraping.org_scrapers.google_maps_scraper import GoogleMapsScraper
            maps_data = GoogleMapsScraper().scrape(org.name)
            if maps_data:
                collected.update(maps_data)
                logger.info(f"[Pipeline] Google Maps scraper got {len(maps_data)} fields for {org.name}")
        except Exception as e:
            logger.warning(f"[Pipeline] Google Maps scraper failed for {org.name}: {e}")

        # Stage 3: Social media
        try:
            if "social_links" in collected:
                from app.scraping.org_scrapers.social_scraper import SocialScraper
                SocialScraper().scrape(collected["social_links"])
        except Exception as e:
            logger.warning(f"[Pipeline] Social scraper failed for {org.name}: {e}")

        # Apply scraped data to org before AI (so AI has access to it)
        self._apply(org, collected)
        self.db.commit()

        # Stage 4: AI enrichment & Catalog Extraction
        try:
            from app.services.org_intelligence_service import OrgIntelligenceService
            ai_data = OrgIntelligenceService(self.db).enrich_organization(org, website_text)
            if ai_data:
                self._apply(org, ai_data)
                logger.info(f"[Pipeline] AI Enrichment completed for {org.name}")
        except Exception as e:
            logger.error(f"[Pipeline] AI enrichment failed for {org.name}: {e}")

        # Update metadata
        org.last_scraped_at = datetime.now(timezone.utc)
        org.data_completeness = self._calc_completeness(org)
        self.db.commit()
        logger.info(f"[Pipeline] Done for {org.name}. Completeness: {org.data_completeness:.0f}%")

    def _apply(self, org: Organization, data: dict):
        """Write collected fields onto the org model."""
        for field, value in data.items():
            if hasattr(org, field) and value is not None:
                if isinstance(value, (list, dict)):
                    setattr(org, field, json.dumps(value))
                else:
                    setattr(org, field, value)

    def _calc_completeness(self, org: Organization) -> float:
        """Score data completeness 0–100 based on filled fields."""
        fields = [
            org.description, org.emails, org.phone_numbers, org.physical_addresses,
            org.ceo, org.employee_size, org.services_offered, org.social_links,
            org.gps_lat, org.operating_hours, org.tech_stack, org.ai_summary,
            org.rating_avg, org.logo_url, org.registration_number,
        ]
        filled = sum(1 for f in fields if f is not None and f != "[]" and f != "{}")
        return round((filled / len(fields)) * 100, 1)
