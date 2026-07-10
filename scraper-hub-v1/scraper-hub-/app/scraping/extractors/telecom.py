import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord


class TelecomExtractor(BaseExtractor):
    """Extractor for telecom company websites (mobile plans, broadband, etc.)."""

    def get_entity_name(self) -> str:
        # Use robust detection from base class first
        name = self._detect_entity_name()
        if name != "Unknown Entity":
            return name
            
        url = self.snapshot.url.lower()
        if 'econet' in url: return 'Econet Wireless'
        if 'netone' in url: return 'NetOne ZW'
        if 'telecel' in url: return 'Telecel Zimbabwe'
        if 'telone' in url: return 'TelOne'
        if 'liquid' in url: return 'Liquid Intelligent Technologies'
        if 'zol' in url: return 'ZOL Zimbabwe'
        if 'powertel' in url: return 'PowerTel'
        if 'africom' in url: return 'Africom'
        
        domain_match = re.search(r'https?://(?:www\.)?([^/.]+)', url)
        if domain_match: return domain_match.group(1).capitalize()
        return 'Telecom Provider'

    def get_category(self) -> str:
        return 'telecom'

    def extract(self) -> List[ExtractedRecord]:
        """Extract telecom products from HTML content."""
        records = []

        if self.snapshot.content_type.lower() != 'html':
            return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Only extract from pages that clearly contain telecom products
        page_text = soup.get_text().lower()

        # Check if this page actually contains telecom products
        product_indicators = [
            'data bundle', 'mobile plan', 'voice tariff', 'broadband plan',
            'pay monthly', 'contract', 'unlimited data', 'gb data', 'mb data',
            'minutes', 'texts', 'calls', 'tariff', 'plan'
        ]

        has_products = any(indicator in page_text for indicator in product_indicators)

        # Additional check: must have at least 2 different product indicators
        # and some pricing information
        price_indicators = ['£', '$', 'per month', 'monthly', 'price', 'cost', 'fee']
        has_pricing = any(indicator in page_text for indicator in price_indicators)

        if not (has_products and has_pricing):
            return records  # Don't extract from non-product pages

        # Look for specific telecom products with improved methods
        # Mobile plans - improved
        mobile_plans = self._extract_mobile_plans_improved(soup)
        records.extend(mobile_plans)

        # Data bundles - new
        data_bundles = self._extract_data_bundles(soup)
        records.extend(data_bundles)

        # Voice plans
        voice_plans = self._extract_voice_plans(soup)
        records.extend(voice_plans)

        # Broadband plans
        broadband_plans = self._extract_broadband_plans(soup)
        records.extend(broadband_plans)

        return records

    def _extract_mobile_plans_improved(self, soup) -> List[ExtractedRecord]:
        """Extract mobile phone plans with improved detection."""
        records = []

        # Look for text content with plan keywords
        page_text = soup.get_text().lower()
        plan_keywords = ['plan', 'tariff', 'monthly', 'contract', 'pay monthly', 'sim only']
        has_plan_content = any(keyword in page_text for keyword in plan_keywords)

        if has_plan_content:
            # Extract from headings that might be plan names - be more selective
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text().strip()

                # Skip navigation/legal content
                skip_keywords = [
                    'login', 'contact', 'about', 'help', 'search', 'menu', 'navigation',
                    'skip to', 'terms', 'conditions', 'privacy', 'cookie', 'footer',
                    'header', 'verification', 'trade-in', 'warranty', 'guarantee',
                    'roaming', 'inclusive destinations', 'lifetime', 'battery',
                    'refresh', 'bonus', 'apply', 'substantiation', 'telegraph',
                    'public sector', 'portal', 'awards', 'numerous', 'manage',
                    'products', 'our story', 'board', 'sustainability', 'faqs',
                    'shop locator', 'web self-care', 'customer experience', 'shareholders',
                    'back to', 'my account', 'sign in', 'forgot password', 'register',
                    'site map', 'accessibility', 'cookie settings', 'legal', 'compliance'
                ]

                if any(skip.lower() in heading_text.lower() for skip in skip_keywords):
                    continue

                # Must be a reasonable length and contain plan-related keywords
                plan_indicators = ['unlimited', 'data', 'minutes', 'calls', 'texts', 'plan', 'tariff', 'monthly', 'contract', 'bundle', 'wifi', 'broadband']
                if (8 <= len(heading_text) <= 80 and  # Reasonable length for product names
                    any(indicator in heading_text.lower() for indicator in plan_indicators)):

                    # Look for pricing near this heading
                    price_info = self._find_nearby_price(heading)

                    # Only create record if we found pricing AND the heading looks like a product
                    if price_info.get('value') and price_info.get('value') > 0:
                        # Additional check: ensure this isn't just a generic heading
                        # Look for specific product patterns
                        product_patterns = [
                            r'\d+\s*(GB|MB|minutes?|calls?|texts?)',  # Contains quantities
                            r'(unlimited|bundle|plan|tariff)',  # Contains product keywords
                        ]

                        is_product = any(re.search(pattern, heading_text, re.IGNORECASE) for pattern in product_patterns)

                        if is_product or 'bundle' in heading_text.lower() or 'plan' in heading_text.lower():
                            # Look for data/minutes info
                            data_info = self._extract_data_info(heading)

                            record = self._create_record(
                                subcategory='mobile_plan',
                                title=heading_text,
                                description=self._extract_description_from_heading(heading),
                                price_value=price_info.get('value'),
                                price_currency=price_info.get('currency', 'USD'),
                                billing_period='month',
                                unit_value=data_info.get('data_gb'),
                                unit_type='GB' if data_info.get('data_gb') else None,
                                eligibility=data_info.get('details'),
                                source_url=self._extract_link(heading),
                                confidence_score=0.9
                            )
                            if record:
                                records.append(record)

        return records

    def _extract_data_bundles(self, soup) -> List[ExtractedRecord]:
        """Extract data bundle products."""
        records = []

        # Look for data bundle content
        page_text = soup.get_text().lower()
        data_keywords = ['data bundle', 'data pack', 'internet bundle', 'megabyte', 'gigabyte', 'gb', 'mb']

        if any(keyword in page_text for keyword in data_keywords):
            # Find elements containing data bundle info - be more selective
            for element in soup.find_all(['div', 'section', 'article', 'li']):
                element_text = element.get_text().strip()

                # Skip if too short or too long
                if len(element_text) < 10 or len(element_text) > 200:
                    continue

                # Skip navigation elements
                if any(skip in element_text.lower() for skip in ['menu', 'navigation', 'header', 'footer', 'contact', 'about']):
                    continue

                # Must contain data amount AND price
                data_info = self._extract_data_amount(element_text)
                price_info = self._find_nearby_price(element)

                if data_info.get('amount') and price_info.get('value') and price_info.get('value') > 0:
                    # Look for a reasonable title
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                    title = title_elem.get_text().strip() if title_elem else element_text.split('\n')[0].strip()

                    # Skip if title is too generic
                    if len(title) < 5 or any(generic in title.lower() for generic in ['menu', 'personal', 'business', 'about', 'contact']):
                        continue

                    record = self._create_record(
                        subcategory='data_bundle',
                        title=title[:80],
                        description=element_text[:200],
                        price_value=price_info.get('value'),
                        price_currency=price_info.get('currency', 'USD'),
                        unit_value=data_info.get('amount'),
                        unit_type=data_info.get('unit', 'GB'),
                        source_url=self._extract_link(element),
                        confidence_score=0.8
                    )
                    if record:
                        records.append(record)

        return records

    def _extract_voice_plans(self, soup) -> List[ExtractedRecord]:
        """Extract voice/call plans."""
        records = []

        # Look for voice plan content
        page_text = soup.get_text().lower()
        voice_keywords = ['voice plan', 'call plan', 'minutes', 'voice tariff', 'calling plan']

        if any(keyword in page_text for keyword in voice_keywords):
            # Find elements containing voice plan info
            for element in soup.find_all(['div', 'section', 'article', 'li']):
                element_text = element.get_text().lower()
                if any(keyword in element_text for keyword in voice_keywords):
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                    title = title_elem.get_text().strip() if title_elem else element_text[:100]

                    price_info = self._find_nearby_price(element)
                    minutes_info = self._extract_minutes_info(element_text)

                    record = self._create_record(
                        subcategory='voice_plan',
                        title=title,
                        description=element_text[:200],
                        price_value=price_info.get('value'),
                        price_currency=price_info.get('currency', 'USD'),
                        unit_value=minutes_info.get('minutes'),
                        unit_type='minutes' if minutes_info.get('minutes') else None,
                        confidence_score=0.7
                    )
                    if record:
                        records.append(record)

        return records

    def _extract_broadband_plans(self, soup) -> List[ExtractedRecord]:
        """Extract broadband plans from the page."""
        records = []

        # Look for broadband-related content
        broadband_keywords = ['broadband', 'internet', 'wifi', 'fibre', 'adsl', 'vdsl', 'fttc', 'ftth']
        page_text = soup.get_text().lower()

        if not any(keyword in page_text for keyword in broadband_keywords):
            return records

        # Look for plan-like structures
        for element in soup.find_all(['div', 'section', 'article']):
            element_text = element.get_text().strip()

            # Check if this looks like a broadband plan
            if any(keyword in element_text.lower() for keyword in broadband_keywords):
                # Look for speed information (Mbps)
                speed_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:mbps|mb)', element_text, re.IGNORECASE)
                speed = float(speed_match.group(1)) if speed_match else None

                # Look for price
                price_info = self._find_nearby_price(element)

                if speed or price_info.get('value'):
                    title = element.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                    title_text = title.get_text().strip() if title else f'Broadband Plan ({speed} Mbps)' if speed else 'Broadband Plan'

                    record = self._create_record(
                        subcategory='broadband_plan',
                        title=title_text,
                        description=element_text[:200],
                        price_value=price_info.get('value'),
                        price_currency=price_info.get('currency', 'GBP'),
                        unit_value=speed,
                        unit_type='Mbps' if speed else None,
                        confidence_score=0.7
                    )
                    if record:
                        records.append(record)

        return records


    def _extract_data_info(self, heading) -> dict:
        """Extract data amount and details from around a heading."""
        # Look for data amounts in GB/MB
        text = str(heading) + " "
        current = heading
        for _ in range(3):
            current = current.find_next_sibling(['p', 'div', 'span'])
            if current:
                text += str(current) + " "
            else:
                break

        # Look for data patterns
        pattern = r'(\d+(?:\.\d+)?)\s*(GB|MB|TB|Gig|Meg|Gigabyte|Megabyte)'
        data_match = re.search(pattern, text, re.IGNORECASE)
        if data_match:
            try:
                amount_str = data_match.group(1)
                amount = float(amount_str)
                unit_raw = data_match.group(2).lower()
                
                # Normalize unit to GB for consistency
                display_unit = 'GB'
                if unit_raw.startswith('m'):
                    amount = amount / 1024
                    display_unit = 'GB'
                elif unit_raw.startswith('t'):
                    amount = amount * 1024
                    display_unit = 'GB'
                
                return {'data_gb': amount, 'unit': display_unit, 'details': f'{amount_str} {data_match.group(2)} data'}
            except: pass
        return {}

    def _extract_data_amount(self, text: str) -> dict:
        """Extract data amount from text."""
        # More robust regex for data amounts: handles mashed text, spaces, and full names
        pattern = r'(\d+(?:\.\d+)?)\s*(GB|MB|TB|Gig|Meg|Gigabyte|Megabyte|Gbps|Mbps)'
        data_match = re.search(pattern, text, re.IGNORECASE)
        if data_match:
            try:
                amount_str = data_match.group(1)
                amount = float(amount_str)
                unit_raw = data_match.group(2).lower()
                
                unit = 'GB'
                if unit_raw.startswith('m'): unit = 'MB'
                elif unit_raw.startswith('t'): unit = 'TB'
                elif unit_raw.startswith('g'): unit = 'GB'
                
                return {'amount': amount, 'unit': unit}
            except: pass
            
        if 'unlimited' in text.lower():
            return {'amount': 999, 'unit': 'GB'}
            
        return {'amount': None, 'unit': 'GB'}

    def _extract_minutes_info(self, text: str) -> dict:
        """Extract minutes information from text."""
        minutes_match = re.search(r'(\d+(?:\.\d+)?)\s*(minutes?|mins?)', text, re.IGNORECASE)
        if minutes_match:
            minutes = float(minutes_match.group(1))
            return {'minutes': minutes}
        return {'minutes': None}

    def _extract_description_from_heading(self, heading) -> str:
        """Extract description text from around a heading."""
        description = ""

        current = heading
        for _ in range(3):
            current = current.find_next_sibling(['p', 'div', 'span'])
            if current:
                text = current.get_text().strip()
                if text and len(text) > 10:
                    description += text + " "
                    if len(description) > 150:
                        break
            else:
                break

        return description.strip()

    def _extract_text(self, element, selectors) -> str:
        """Extract text from element using multiple selectors."""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found.get_text(strip=True)
        return element.get_text(strip=True) if element.get_text(strip=True) else ''
