import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord

class HospitalityExtractor(BaseExtractor):
    """Extractor for hotels and hospitality websites."""

    def get_entity_name(self) -> str:
        return self._detect_entity_name()

    def get_category(self) -> str:
        return 'hotels'

    def extract(self) -> List[ExtractedRecord]:
        records = []
        if self.snapshot.content_type.lower() != 'html': return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')
        
        # Clean up
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # 1. Structured extraction: Tables (very common for rate cards)
        for table in soup.find_all('table'):
            table_text = table.get_text().lower()
            if any(ind in table_text for ind in ['room', 'suite', 'rate', 'night', 'accommodation']):
                table_records = self._extract_from_table(table)
                for r in table_records:
                    if r.price_value and 10 < r.price_value < 5000: # Realistic room rates
                        r.subcategory = 'hotel_rate'
                        r.billing_period = 'night'
                        # Try to detect room type from title
                        if 'deluxe' in r.title.lower(): r.item_name = 'Deluxe Room'
                        elif 'standard' in r.title.lower(): r.item_name = 'Standard Room'
                        elif 'suite' in r.title.lower(): r.item_name = 'Suite'
                        records.append(r)

        # 2. Component-based extraction (Existing cards/items)
        selectors = [
            '.room-item', '.room-card', '.accommodation-card', '.property-card', 
            '.room-type', '.rate-plan', '[class*="room"]', '[class*="accommodation"]'
        ]
        found_elements = []
        for selector in selectors:
            found_elements.extend(soup.select(selector))
            
        for element in found_elements:
            element_text = element.get_text().lower()
            if any(k in element_text for k in ['rating', 'stars', 'reviews', 'guest rating', 'map']):
                continue

            price_info = self._find_nearby_price(element)
            if price_info['value'] and 10 < price_info['value'] < 5000:
                title = self._extract_title(element)
                record = self._create_record(
                    subcategory='hotel_room',
                    title=title,
                    description=element.get_text().strip()[:200],
                    price_value=price_info['value'],
                    price_currency=price_info['currency'],
                    billing_period='night',
                    source_url=self._extract_link(element),
                    confidence_score=0.8
                )
                if record:
                    # Detect room type
                    if 'deluxe' in title.lower(): record.item_name = 'Deluxe Room'
                    elif 'standard' in title.lower(): record.item_name = 'Standard Room'
                    elif 'executive' in title.lower(): record.item_name = 'Executive Room'
                    elif 'suite' in title.lower(): record.item_name = 'Suite'
                    records.append(record)

        # 3. Fallback: Heuristic extraction for remaining headings
        hospitality_indicators = ['room', 'suite', 'stay', 'accommodation', 'booking', 'nightly', 'rate', 'per night']
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text().strip().lower()
            if any(ind in heading_text for ind in hospitality_indicators):
                if any(r.title.lower() == heading_text for r in records): continue
                if any(k in heading_text for k in ['rating', 'review', 'stars', 'policy', 'terms']): continue

                price_info = self._find_nearby_price(heading)
                if price_info['value'] and 10 < price_info['value'] < 5000:
                    record = self._create_record(
                        subcategory='hotel_room',
                        title=heading.get_text().strip()[:80],
                        description=self._extract_description_from_heading(heading),
                        price_value=price_info['value'],
                        price_currency=price_info['currency'],
                        billing_period='night',
                        confidence_score=0.7
                    )
                    if record: records.append(record)

        # Deduplicate
        seen = set()
        unique_records = []
        for r in records:
            key = (r.title.lower(), r.price_value)
            if key not in seen:
                seen.add(key)
                unique_records.append(r)
        
        return unique_records




    def _extract_title(self, element) -> str:
        h = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'span'])
        if h: return h.get_text().strip()[:80]
        return "Hotel Room"

    def _extract_description_from_heading(self, heading) -> str:
        description = ""
        current = heading
        for _ in range(3):
            current = current.find_next_sibling(['p', 'div', 'span'])
            if current:
                text = current.get_text().strip()
                if text and len(text) > 10:
                    description += text + " "
                    if len(description) > 150: break
            else: break
        return description.strip()
