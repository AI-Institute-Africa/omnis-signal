from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from app.scraping.schemas import ExtractionResponse
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for all extractors that convert raw snapshots into normalized records."""

    def __init__(self, snapshot: RawSnapshot, source_category: str = None):
        self.snapshot = snapshot
        self.source_category = source_category

    @abstractmethod
    def extract(self) -> List[ExtractedRecord]:
        """Extract normalized records from the raw snapshot.

        Returns:
            List of ExtractedRecord instances
        """
        pass

    @abstractmethod
    def get_entity_name(self) -> str:
        """Get the entity name for this extractor (e.g., 'Vodafone', 'HSBC')."""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Get the category for this extractor (e.g., 'telecom', 'banking')."""
        pass

    def _create_record(self, **kwargs) -> ExtractedRecord:
        """Helper method to create an ExtractedRecord with common fields."""
        source_url = kwargs.pop('source_url', self.snapshot.url)
        confidence_score = kwargs.get('confidence_score', 0.5)
        
        # Detect market
        market = self._detect_market(source_url)
            
        return ExtractedRecord(
            snapshot_id=self.snapshot.id,
            entity_name=self.get_entity_name(),
            category=self.get_category(),
            market=market,
            source_url=source_url,
            **kwargs
        )

    def _detect_market(self, url: str) -> str:
        """Detect if a URL belongs to the local (Zimbabwe) or global market."""
        url = url.lower()
        
        # Zimbabwe indicators
        local_indicators = ['.co.zw', '.ac.zw', '.org.zw', '.gov.zw', '.zw']
        if any(ind in url for ind in local_indicators):
            return "local"
            
        # Zimbabwean company keywords in URL
        local_keywords = ['econet', 'netone', 'telecel', 'telone', 'zesa', 'zera', 'cbz', 'stewardbank', 'fbc', 'nmb', 'stanbicbank.co.zw', 'zb.co.zw', 'cabs.co.zw']
        if any(kw in url for kw in local_keywords):
            return "local"
            
        # Default to local if it's a known ZW entity from get_entity_name
        entity = self.get_entity_name().lower()
        if any(kw in entity for kw in ['zimbabwe', 'zera', 'zesa', 'netone', 'econet', 'telecel', 'telone']):
            return "local"
            
        # Known global domains/keywords
        global_indicators = ['.uk', '.com', '.org', '.net', '.edu'] # Com/Org can be both, but local usually has .zw
        global_keywords = ['vodafone', 'three.co.uk', 'o2.co.uk', 'ee.co.uk', 'att.com', 'verizon', 'hsbc', 'barclays']
        
        if any(kw in url for kw in global_keywords):
            return "global"
            
        # If it has .zw, it's definitely local. If it's a common global keyword, it's global.
        # Otherwise, default to local since this is a Zimbabwe-focused platform.
        return "local"


    def _detect_entity_name(self) -> str:
        """Robust entity detection from URL and content."""
        url = self.snapshot.url.lower()
        content = self.snapshot.content.lower()[:2000]
        
        mapping = {
            # Banking & Finance (Zimbabwe Focus)
            'cbz': 'CBZ Bank',
            'cabs': 'CABS',
            'stanbic': 'Stanbic Bank',
            'steward': 'Steward Bank',
            'fbc': 'FBC Bank',
            'nmb': 'NMB Bank',
            'posb': 'POSB',
            'bancabc': 'BancABC',
            'nedbank': 'Nedbank Zimbabwe',
            'standardchartered': 'Standard Chartered',
            'firstcapital': 'First Capital Bank',
            'metbank': 'Metbank',
            'zb.co.zw': 'ZB Bank',
            'zb bank': 'ZB Bank',
            'stewardbank': 'Steward Bank',
            'ecobank': 'Ecobank Zimbabwe',
            
            # Telecom & Tech (Zimbabwe Focus)
            'econet': 'Econet Wireless',
            'netone': 'NetOne ZW',
            'telecel': 'Telecel Zimbabwe',
            'telone': 'TelOne',
            'liquid': 'Liquid Intelligent Technologies',
            'zolt': 'ZOL Zimbabwe',
            'powertel': 'PowerTel',
            'africom': 'Africom',
            
            # Insurance (Zimbabwe Focus)
            'oldmutual': 'Old Mutual Zimbabwe',
            'zimnat': 'Zimnat',
            'sanlam': 'Sanlam Zimbabwe',
            'fidelity': 'Fidelity Life',
            'nyaradzo': 'Nyaradzo Group',
            'doves': 'Doves Zimbabwe',
            'nico.co.zw': 'NICO General',
            'britam': 'Britam',
            
            # Energy & Utilities (Zimbabwe Focus)
            'zera.co.zw': 'ZERA',
            'zera': 'ZERA',
            'zesa': 'ZESA',
            'zetdc': 'ZETDC',
            'zinwa': 'ZINWA',
            
            # Education (Zimbabwe Focus)
            'uz.ac.zw': 'University of Zimbabwe',
            'nust.ac.zw': 'NUST',
            'msu.ac.zw': 'MSU',
            'gzu.ac.zw': 'GZU',
            'cut.ac.zw': 'CUT',
            'hit.ac.zw': 'HIT',
            
            # Hotels (Zimbabwe)
            'meikles': 'Meikles Hotel',
            'rainbowtowers': 'Rainbow Towers',
            'victoriafalls': 'Victoria Falls Hotel',
            'booking.com/region/zimbabwe': 'Booking.com ZW',
            
            # Government & Regulators
            'rbz': 'Reserve Bank of Zimbabwe',
            'potraz': 'POTRAZ',
            'zimra': 'ZIMRA',
            'zupco': 'ZUPCO',
        }

        
        # Use boundaries for short names to avoid false positives (e.g., 'ee' in 'fees')
        import re
        for key, val in mapping.items():
            if len(key) <= 3:
                pattern = rf'\b{key}\b'
                if re.search(pattern, url) or re.search(pattern, content):
                    return val
            elif key in url or key in content:
                return val
                
        # Fallback to domain
        domain_match = re.search(r'https?://(?:www\.)?([^/.]+)', url)
        if domain_match:
            return domain_match.group(1).capitalize()
            
        return "Unknown Entity"

    def _extract_link(self, element) -> str:

        """Extract a link from an element and make it absolute."""
        if not element: return self.snapshot.url
        link = element.find('a', href=True)
        if link:
            from urllib.parse import urljoin
            return urljoin(self.snapshot.url, link['href'])
        return self.snapshot.url

    def _find_price_universal(self, element) -> dict:
        """Find price within the element itself using universal regex."""
        # Check text within this element
        text = str(element)
        return self._extract_price_from_text(text)

    def _find_nearby_price(self, element) -> dict:
        """Aggressively search for a price in the element, its siblings, or parent."""
        # 1. Search the element itself
        res = self._find_price_universal(element)
        if res.get('value') is not None:
            return res
            
        # 2. Check if we are inside a table row - search other cells in the same row
        tr = element.find_parent('tr')
        if tr:
            for td in tr.find_all(['td', 'th']):
                if td == element: continue
                res = self._find_price_universal(td)
                if res.get('value') is not None:
                    return res

        # 3. Search next siblings (up to 5)
        current = element
        for _ in range(5):
            current = getattr(current, 'find_next_sibling', lambda: None)()
            if not current:
                break
            res = self._find_price_universal(current)
            if res.get('value') is not None:
                return res

        # 4. Search previous siblings (up to 3)
        current = element
        for _ in range(3):
            current = getattr(current, 'find_previous_sibling', lambda: None)()
            if not current:
                break
            res = self._find_price_universal(current)
            if res.get('value') is not None:
                return res

        # 5. Search parent element text and nearby parent siblings
        if getattr(element, 'parent', None):
            res = self._find_price_universal(element.parent)
            if res.get('value') is not None:
                return res
            parent = element.parent
            for _ in range(2):
                parent = getattr(parent, 'find_next_sibling', lambda: None)()
                if not parent:
                    break
                res = self._find_price_universal(parent)
                if res.get('value') is not None:
                    return res

        return {'value': None, 'currency': 'USD'}

    def _extract_price_from_text(self, text: str) -> dict:
        """Helper to extract price from raw text with high robustness."""
        import re
        
        if not text: return {'value': None, 'currency': 'USD'}
        
        # Noise reduction - more aggressive
        noise_keywords = [
            'help', 'contact', 'search', 'menu', 'reset', 'login', 'copyright', 
            'terms', 'privacy', 'cookies', 'navigation', 'skip to', 'sign in',
            'register', 'follow us', 'social media', 'all rights reserved',
            'digital reset', 'looking for help', 'site map', 'accessibility',
            'verification on the ipm website', 'public sector portal',
            'better banking', 'better rewards', 'moving forward', 'with you',
            'inspired to change', 'your partner', 'making life better'
        ]
        if any(noise in text.lower() for noise in noise_keywords):
            return {'value': None, 'currency': 'USD'}

        # Normalize whitespace and common separators
        text = re.sub(r'\s+', ' ', text)
        
        # Check for "From" or "Starting at" patterns
        is_from_price = any(p in text.lower() for p in ['from', 'starting at', 'starts at', 'up to'])


        # Priority patterns for USD and ZWL (common in Zimbabwe)
        # Matches: USD 10.00, $10.00, 10.00 USD, ZWL 1000, 1000 ZWL, USD 1.5k
        priority_patterns = [
            r'(?:USD|US\$|\$)\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)([kKmMbB])?',
            r'ZWL\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)([kKmMbB])?',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)([kKmMbB])?\s*(?:USD|ZWL|US\$|\$)',
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    val_str = match.group(1).replace(',', '')
                    val = float(val_str)
                    suffix = match.group(2)
                    if suffix:
                        suffix = suffix.lower()
                        if suffix == 'k':
                            val *= 1_000
                        elif suffix == 'm':
                            val *= 1_000_000
                        elif suffix == 'b':
                            val *= 1_000_000_000
                    if val > 1_000_000_000: continue
                    currency = 'ZWL' if 'ZWL' in match.group(0).upper() else 'USD'
                    return {'value': val, 'currency': currency, 'is_from': is_from_price}
                except: continue

        # Secondary patterns (international)
        patterns = [
            r'([£€R])\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(GBP|ZAR|EUR|Rands?|Ksh)',
            r'(\d+(?:\.\d+)?)\s*%\s*(APR|AER|Variable|Fixed)',
            r'(\d+(?:\.\d+)?)\s*(?:per|/)?\s*(month|year|week|day|night|semester|term)\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                groups = match.groups()
                # Handle APR case
                if 'APR' in pattern or 'AER' in pattern:
                    try: return {'value': float(groups[0]), 'currency': 'APR'}
                    except: continue
                
                val_str = groups[1] if re.match(r'[£€R]', groups[0]) else groups[0]
                curr_token = groups[0] if re.match(r'[£€R]', groups[0]) else groups[1]
                
                try:
                    val = float(val_str.replace(',', ''))
                    # Filter out tiny values that are likely not prices (except for 0)
                    if 0 < val < 0.01: continue
                    
                    # Filter out very large values that are likely timestamps (e.g., 1730986318457)
                    if val > 1_000_000_000_000: continue

                    curr_token = curr_token.upper()

                    currency = 'USD'
                    if curr_token in ['$', 'USD', 'US$']: currency = 'USD'
                    elif curr_token in ['ZWL']: currency = 'ZWL'
                    elif curr_token in ['£', 'GBP']: currency = 'GBP'
                    elif curr_token in ['€', 'EUR']: currency = 'EUR'
                    elif curr_token in ['R', 'ZAR', 'RAND', 'RANDS']: currency = 'ZAR'
                    elif curr_token in ['KSH']: currency = 'KES'
                    return {'value': val, 'currency': currency, 'is_from': is_from_price}
                except: continue
        
        # Last ditch: look for any number that looks like a price near a currency-ish word
        if any(w in text.lower() for w in ['price', 'cost', 'fee', 'rate', 'tariff', 'amount']):
            num_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
            if num_match:
                try:
                    val = float(num_match.group(1).replace(',', ''))
                    if val > 1_000_000_000: pass
                    else: return {'value': val, 'currency': 'USD', 'is_from': is_from_price}
                except: pass

        return {'value': None, 'currency': 'USD'}


    def _identify_product_containers(self, soup) -> List:
        """Find elements that likely contain products by looking for repeating structures."""
        containers = []
        # Look for repeated divs/articles with similar classes
        class_counts = {}
        for tag in soup.find_all(['div', 'article', 'section']):
            classes = tag.get('class')
            if classes:
                cls_str = " ".join(sorted(classes))
                class_counts[cls_str] = class_counts.get(cls_str, 0) + 1
        
        # Filter for classes that appear multiple times (likely a list/grid)
        potential_classes = [cls for cls, count in class_counts.items() if count >= 3]
        
        for cls in potential_classes:
            # Skip very common generic classes
            if any(generic in cls.lower() for generic in ['row', 'col', 'container', 'wrapper']):
                continue
            
            items = soup.find_all(class_=cls.split())
            # Ensure these items actually contain some data (like a price)
            valid_items = []
            for item in items:
                if self._find_price_universal(item)['value'] is not None:
                    valid_items.append(item)
            
            if len(valid_items) >= 2:
                containers.extend(valid_items)
        
        return containers

    def _find_label_for_price(self, price_element) -> str:
        """Find a descriptive label/title for a price element by looking at context."""
        # Known slogans to skip
        slogans = ['better banking', 'better rewards', 'moving forward', 'with you', 'inspired to change']

        # 1. Look for headings (h1-h6) before this element
        current = price_element
        for _ in range(5): # Look up 5 levels
            parent = current.parent
            if not parent: break
            
            # Search siblings of parent and parent itself for headings
            headings = parent.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'], recursive=True)
            for h in headings:
                txt = h.get_text(strip=True)
                if len(txt) > 3 and not any(s in txt.lower() for s in slogans):
                    return txt
            current = parent
            
        # 2. Look at previous siblings
        prev = price_element.find_previous_sibling()
        if prev:
            txt = prev.get_text(strip=True)
            if len(txt) > 3 and not any(s in txt.lower() for s in slogans):
                return txt
            
        # 3. Last resort: parent's first text node
        if price_element.parent:
            txt = price_element.parent.get_text(strip=True).split('\n')[0][:80]
            if not any(s in txt.lower() for s in slogans):
                return txt
            
        return "Generic Product"

    def _extract_from_table(self, table) -> List[ExtractedRecord]:
        """Generic table extractor that pairs headers with values."""
        records = []
        rows = table.find_all('tr')
        if not rows: return records
        
        # Try to find headers
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        if len(headers) < 2: return records
        
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) != len(headers): continue
            
            row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
            
            # Look for a price in each cell
            for label, value in row_data.items():
                price_info = self._extract_price_from_text(value)
                if price_info['value'] is not None:
                    # The 'title' is either the first cell in the row or the header
                    title = row_data.get(headers[0], label)
                    record = self._create_record(
                        subcategory='table_entry',
                        title=f"{title} - {label}"[:100],
                        description=f"Table extraction: {label}={value}",
                        price_value=price_info['value'],
                        price_currency=price_info['currency'],
                        confidence_score=0.7
                    )
                    if record: records.append(record)
        return records

    def _extract_from_list(self, ul) -> List[ExtractedRecord]:
        """Extract prices from list items."""
        records = []
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            price_info = self._extract_price_from_text(text)
            if price_info['value'] is not None:
                record = self._create_record(
                    subcategory='list_item',
                    title=text[:60],
                    description=text[:200],
                    price_value=price_info['value'],
                    price_currency=price_info['currency'],
                    confidence_score=0.6
                )
                if record: records.append(record)
        return records

    def _extract_with_gemini(self, text: str) -> ExtractionResponse:
        """Call Gemini for highly accurate structured data extraction."""
        try:
            import google.generativeai as genai
        except ImportError:
            print("Warning: google-generativeai not installed. Skipping AI extraction.")
            return ExtractionResponse()

        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-api-key-here":
            print("Warning: GEMINI_API_KEY not configured. Skipping AI extraction.")
            return ExtractionResponse()

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            from app.scraping.taxonomy import TAXONOMY
            
            logger.info(f"Sending text to Gemini (len={len(text)}): {text[:500]}...")
            prompt = f"""
            You are an expert market intelligence analyst focusing on the Zimbabwean market.
            Extract all products, services, and pricing information from the following text.
            
            STRUCTURE AND TAXONOMY:
            Use the following categories and subcategories for classification. For each product/service, 
            determine the correct normalization unit and formula based on this table:
            {json.dumps(TAXONOMY, indent=2)}
            
            Text to analyze:
            {text[:15000]}
            
            Return the data as a JSON object matching this schema:
            {ExtractionResponse.model_json_schema()}
            
            CRITICAL INSTRUCTIONS:
            1. Categorize each item into one of the main categories: {", ".join(TAXONOMY.keys())}.
            2. Map it to the most specific subcategory from the taxonomy above.
            3. Populate the 'price' object with:
               - 'normalized_value': The price converted to the standard unit (e.g., price per GB).
               - 'normalized_unit': The standard unit from the taxonomy.
               - 'formula': The calculation used (e.g., 'price / 10' for a 10GB bundle).
               - Set the appropriate billing cycle flags (e.g., 'daily': true, 'monthly': true) based on the plan duration.
            4. Focus on physical products and service plans/bundles.
            
            Only return valid JSON.
            """
            
            response = model.generate_content(prompt)
            logger.info(f"Gemini Raw Response: {response.text[:500]}...")
            
            # Use a more robust parsing
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            extraction = ExtractionResponse(**data)
            logger.info(f"Gemini parsed {len(extraction.products)} products and {len(extraction.services)} services.")
            return extraction
        except Exception as e:
            print(f"Error during Gemini extraction: {e}")
            return ExtractionResponse()

    def _extract_with_llm_fallback(self, text: str, schema_class=None) -> dict:
        """Deprecated: Use _extract_with_gemini instead."""
        res = self._extract_with_gemini(text)
        return res.model_dump()

