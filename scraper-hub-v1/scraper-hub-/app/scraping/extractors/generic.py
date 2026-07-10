from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord

class GenericExtractor(BaseExtractor):
    """Generic extractor for unstructured services (utilities, solar, etc.)."""

    def get_entity_name(self) -> str:
        return self._detect_entity_name()

    def get_category(self) -> str:
        if self.source_category:
            return self.source_category
        return "service"

    def extract(self) -> List[ExtractedRecord]:
        records = []
        content_type = self.snapshot.content_type.lower()

        if content_type != 'html' and content_type != 'text':
            return records

        page_text = self.snapshot.content or ''
        if content_type == 'html':
            soup = BeautifulSoup(self.snapshot.content, 'html.parser')
            # Remove noisy tags
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            page_text = soup.get_text(separator='\n')
        else:
            soup = None

        normalized_text = page_text.lower()
        
        # Identify subcategory based on indicators
        subcat = 'general_service'
        if any(k in page_text for k in ['solar', 'inverter', 'battery', 'lithium', 'panel']):
            subcat = 'solar_product'
        elif any(k in page_text for k in ['water', 'electricity', 'refuse', 'rates', 'bill']):
            subcat = 'utility_rate'

        # 1. Structured extraction: Tables (common for tariffs)
        if soup is not None:
            for table in soup.find_all('table'):
                table_records = self._extract_from_table(table)
                for r in table_records:
                    r.subcategory = subcat
                    records.append(r)

            # 2. Structured extraction: Lists
            for ul in soup.find_all(['ul', 'ol']):
                if len(ul.find_all('a')) > len(ul.find_all('li')) / 2: continue
                list_records = self._extract_from_list(ul)
                for r in list_records:
                    r.subcategory = subcat
                    records.append(r)

            containers = []

        # 3. Block-based extraction: Identify repetitive containers
        if soup is not None:
            containers = self._identify_product_containers(soup)
            for container in containers:
                title = self._find_label_for_price(container)
                price_info = self._find_nearby_price(container)
                
                # Additional noise filter for containers
                cont_text = container.get_text().lower()
                if any(noise in cont_text for noise in ['copyright', 'reserved', 'all rights', 'designed by']):
                    continue

                if price_info.get('value') is not None:
                    # Try to extract unit info from the container text
                    unit_info = self._extract_unit_info(container.get_text())
                    
                    record = self._create_record(
                        subcategory=subcat,
                        title=title[:100],
                        description=container.get_text(strip=True)[:200],
                        price_value=price_info['value'],
                        price_currency=price_info['currency'],
                        unit_value=unit_info.get('value'),
                        unit_type=unit_info.get('type'),
                        confidence_score=0.8
                    )
                    if record: records.append(record)

            # 4. Heuristic extraction: Headings + nearby prices
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text(strip=True)
                
                skip_keywords = [
                    'login', 'contact', 'about', 'help', 'search', 'menu', 'navigation', 
                    'terms', 'privacy', 'social', 'follow', 'cookies', 'newsletter'
                ]
                if any(skip in heading_text.lower() for skip in skip_keywords) or len(heading_text) < 5:
                    continue

                price_info = self._find_nearby_price(heading)
                
                if price_info.get('value') is not None:
                    unit_info = self._extract_unit_info(heading_text)
                    
                    record = self._create_record(
                        subcategory=subcat,
                        title=heading_text[:100],
                        description=heading_text, 
                        price_value=price_info['value'],
                        price_currency=price_info['currency'],
                        unit_value=unit_info.get('value'),
                        unit_type=unit_info.get('type'),
                        confidence_score=0.6
                    )
                    if record:
                        records.append(record)

        # 5. Text block extraction: parse raw text paragraphs for price-driven items
        records.extend(self._extract_from_text_blocks(page_text, subcat))

        # Deduplicate
        seen = set()
        unique_records = []
        for r in records:
            key = (r.title.lower(), r.price_value)
            if key not in seen:
                seen.add(key)
                unique_records.append(r)

        return unique_records

    def _extract_unit_info(self, text: str) -> dict:
        """Heuristically extract units from text."""
        import re
        # Look for patterns like 10kg, 1L, 100g, 100ml, 1hr, etc.
        pattern = r'(\d+(?:\.\d+)?)\s*(kg|g|l|ml|m|cm|mm|hr|hr|min|sec|pcs|units|items)'
        match = re.search(pattern, text, re.I)
        if match:
            return {'value': float(match.group(1)), 'type': match.group(2).lower()}
        return {'value': None, 'type': None}

    def _extract_from_text_blocks(self, text: str, subcategory: str) -> List[ExtractedRecord]:
        """Extract prices from raw text paragraphs and fallback paragraphs."""
        import re

        records = []
        if not text or len(text.strip()) < 10:
            return records

        paragraphs = []
        current_lines = []
        for line in text.splitlines():
            normalized = line.strip()
            if not normalized:
                if current_lines:
                    paragraphs.append(' '.join(current_lines))
                    current_lines = []
                continue
            current_lines.append(normalized)
        if current_lines:
            paragraphs.append(' '.join(current_lines))

        for paragraph in paragraphs:
            if len(paragraph) < 20:
                continue
            price_info = self._extract_price_from_text(paragraph)
            if price_info.get('value') is None:
                continue

            # Skip paragraphs that clearly look like navigation, copyright or footer text
            lower = paragraph.lower()
            if any(noise in lower for noise in ['copyright', 'all rights reserved', 'terms', 'privacy', 'cookies', 'follow us', 'site map', 'verification']):
                continue

            title = paragraph.split('.')[:1][0][:120].strip()
            if not title:
                title = paragraph[:120]

            record = self._create_record(
                subcategory=subcategory,
                title=title,
                description=paragraph[:250],
                price_value=price_info['value'],
                price_currency=price_info['currency'],
                confidence_score=0.6
            )
            if record:
                records.append(record)

        return records


