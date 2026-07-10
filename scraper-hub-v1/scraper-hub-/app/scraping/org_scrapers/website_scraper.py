"""Website scraper for organizations — extracts contacts, description, SEO meta, social links."""
import re
import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SOCIAL_PATTERNS = {
    "linkedin": r"linkedin\.com/company/[^\"'\s]+",
    "facebook": r"facebook\.com/[^\"'\s]+",
    "twitter": r"(?:twitter|x)\.com/[^\"'\s]+",
    "instagram": r"instagram\.com/[^\"'\s]+",
    "youtube": r"youtube\.com/[^\"'\s]+",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+?263|0)[\s\-]?\d{2}[\s\-]?\d{3}[\s\-]?\d{4}")


class WebsiteScraper:
    """Scrapes an organization's official website for structured data."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; ZimBI/1.0; +https://zimbi.co.zw/bot)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    TIMEOUT = 15

    def scrape(self, url: str) -> dict:
        if not url:
            return {}
        try:
            resp = httpx.get(url, headers=self.HEADERS, timeout=self.TIMEOUT,
                             follow_redirects=True)
            if resp.status_code >= 400:
                logger.warning(f"[WebsiteScraper] {url} returned {resp.status_code}")
                return {}
            return self._parse(url, resp.text)
        except Exception as e:
            logger.warning(f"[WebsiteScraper] Failed to fetch {url}: {e}")
            return {}

    def _parse(self, url: str, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        data = {}

        # Description from meta tags
        desc = (
            self._meta(soup, "description") or
            self._meta(soup, "og:description") or
            self._meta(soup, "twitter:description")
        )
        if desc:
            data["description"] = desc[:800]

        # SEO metadata
        seo = {
            "title": soup.title.string.strip() if soup.title else None,
            "description": self._meta(soup, "description"),
            "og_title": self._meta(soup, "og:title"),
            "og_image": self._meta(soup, "og:image"),
            "canonical": self._attr(soup, "link[rel='canonical']", "href"),
        }
        data["seo_metadata"] = {k: v for k, v in seo.items() if v}

        # Emails
        text = soup.get_text(" ", strip=True)
        emails = list(set(EMAIL_RE.findall(text)))
        emails = [e for e in emails if not e.endswith((".png", ".jpg", ".svg", ".gif"))]
        if emails:
            data["emails"] = emails[:10]

        # Phone numbers (Zimbabwe format)
        phones = list(set(PHONE_RE.findall(text)))
        if phones:
            data["phone_numbers"] = phones[:10]

        # Social media links
        page_str = str(html)
        social = {}
        for platform, pattern in SOCIAL_PATTERNS.items():
            match = re.search(pattern, page_str)
            if match:
                social[platform] = "https://" + match.group(0).lstrip("/")
        if social:
            data["social_links"] = social

        # Tech stack detection
        tech = []
        page_lower = page_str.lower()
        tech_signals = {
            "WordPress": "wp-content",
            "Drupal": "drupal",
            "Joomla": "joomla",
            "Wix": "wixsite.com",
            "Shopify": "shopify",
            "React": "react.min.js",
            "Angular": "angular",
            "Vue.js": "vue.min.js",
            "Bootstrap": "bootstrap",
            "Cloudflare": "cloudflare",
            "Google Analytics": "google-analytics.com",
            "Google Tag Manager": "gtm.js",
            "Facebook Pixel": "fbq(",
        }
        for name, signal in tech_signals.items():
            if signal.lower() in page_lower:
                tech.append(name)
        if tech:
            data["tech_stack"] = tech

        # Logo
        logo = (
            self._meta(soup, "og:image") or
            self._attr(soup, "link[rel='icon']", "href") or
            self._attr(soup, "link[rel='shortcut icon']", "href")
        )
        if logo:
            data["logo_url"] = logo if logo.startswith("http") else url.rstrip("/") + "/" + logo.lstrip("/")

        return data

    def _meta(self, soup, name: str):
        tag = (soup.find("meta", attrs={"name": name}) or
               soup.find("meta", attrs={"property": name}))
        return tag.get("content", "").strip() if tag else None

    def _attr(self, soup, selector: str, attr: str):
        tag = soup.select_one(selector)
        return tag.get(attr) if tag else None
