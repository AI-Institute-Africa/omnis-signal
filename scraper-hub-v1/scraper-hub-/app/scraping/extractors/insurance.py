import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord

class InsuranceExtractor(BaseExtractor):
    """Extractor for insurance company websites (policies, premiums, coverage)."""

    PRODUCT_INDICATORS = [
        'premium', 'policy', 'cover', 'insurance', 'claim', 'benefit',
        'life assurance', 'funeral cover', 'medical aid', 'car insurance',
        'motor insurance', 'home insurance', 'plan', 'life cover',
        'group life', 'accident', 'disability', 'income protection',
        'term life', 'whole life', 'endowment', 'annuity', 'pension'
    ]

    SKIP_KEYWORDS = [
        'login', 'sign in', 'register', 'contact us', 'about us',
        'privacy policy', 'terms', 'cookie', 'follow us', 'social media',
        'navigation', 'menu', 'loading', 'javascript'
    ]

    def get_entity_name(self) -> str:
        return self._detect_entity_name()

    def get_category(self) -> str:
        return 'insurance'

    def extract(self) -> List[ExtractedRecord]:
        records = []
        if self.snapshot.content_type.lower() != 'html':
            return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        page_text = soup.get_text().lower()
        
        # Quick relevance check
        if not any(ind in page_text for ind in self.PRODUCT_INDICATORS):
            return records

        # 1. Tables with premium/rate data
        for table in soup.find_all('table'):
            table_text = table.get_text().lower()
            if any(k in table_text for k in ['premium', 'rate', 'amount', 'cover', 'policy', 'benefit']):
                table_records = self._extract_from_table(table)
                for r in table_records:
                    r.subcategory = 'insurance_premium'
                    r.billing_period = 'month'
                    records.append(r)

        # 2. CSS-class targeted product blocks
        product_selectors = [
            '.product-card', '.plan-card', '.insurance-plan', '.cover-option',
            '[class*="plan"]', '[class*="product"]', '[class*="cover"]',
            '[class*="policy"]', '[class*="premium"]'
        ]
        for selector in product_selectors:
            for el in soup.select(selector):
                el_text = el.get_text().lower()
                if any(noise in el_text for noise in ['cookie', 'social', 'newsletter']):
                    continue
                if any(ind in el_text for ind in self.PRODUCT_INDICATORS):
                    price_info = self._find_nearby_price(el)
                    if price_info.get('value'):
                        record = self._create_record(
                            subcategory='insurance_plan',
                            title=self._extract_title(el)[:80] or 'Insurance Plan',
                            description=el.get_text(strip=True)[:200],
                            price_value=price_info['value'],
                            price_currency=price_info['currency'],
                            billing_period='month',
                            source_url=self._extract_link(el),
                            confidence_score=0.85
                        )
                        if record: records.append(record)

        # 3. Heading-based extraction
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text().strip()
            if not text or len(text) < 5 or len(text) > 120:
                continue
            if any(skip in text.lower() for skip in self.SKIP_KEYWORDS):
                continue
            if not any(ind in text.lower() for ind in self.PRODUCT_INDICATORS):
                continue
            if any(r.title.lower() == text.lower() for r in records):
                continue

            price_info = self._find_nearby_price(heading)
            if price_info.get('value'):
                record = self._create_record(
                    subcategory='insurance_plan',
                    title=text[:80],
                    description=self._extract_description_from_heading(heading),
                    price_value=price_info['value'],
                    price_currency=price_info['currency'],
                    billing_period='month',
                    confidence_score=0.8
                )
                if record: records.append(record)

        # 4. Fallback: capture product descriptions even without prices
        # (Zimbabwe insurance sites often list products without displayed prices)
        if not records:
            for heading in soup.find_all(['h2', 'h3']):
                text = heading.get_text().strip()
                if not text or len(text) < 5 or len(text) > 100:
                    continue
                if any(skip in text.lower() for skip in self.SKIP_KEYWORDS):
                    continue
                if not any(ind in text.lower() for ind in self.PRODUCT_INDICATORS):
                    continue

                desc = self._extract_description_from_heading(heading)
                if desc and len(desc) > 20:
                    record = self._create_record(
                        subcategory='insurance_product',
                        title=text[:80],
                        description=desc[:300],
                        price_value=None,
                        price_currency='USD',
                        billing_period='month',
                        confidence_score=0.4  # Low confidence — no price
                    )
                    if record: records.append(record)

        # Deduplicate
        seen = set()
        unique = []
        for r in records:
            key = (r.title.lower(), r.price_value)
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique

    def _extract_description_from_heading(self, heading) -> str:
        description = ""
        current = heading
        for _ in range(4):
            current = current.find_next_sibling(['p', 'div', 'span', 'ul', 'li'])
            if current:
                text = current.get_text().strip()
                if text and len(text) > 10:
                    description += text + " "
                    if len(description) > 250: break
            else:
                break
        return description.strip()

