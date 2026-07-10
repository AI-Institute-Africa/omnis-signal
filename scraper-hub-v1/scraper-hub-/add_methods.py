import re

# Read the current file
with open('app/scraping/extractors/telecom.py', 'r') as f:
    content = f.read()

# Add the missing methods
methods = '''
    def _find_nearby_price(self, element) -> dict:
        """Find pricing information near a given element."""
        search_area = [element]

        # Add next few siblings
        current = element
        for _ in range(5):
            current = current.find_next_sibling()
            if current:
                search_area.append(current)
            else:
                break

        # Search for prices
        for elem in search_area:
            price_info = self._find_price_in_element(elem)
            if price_info['value']:
                return price_info

        return {'value': None, 'currency': 'GBP'}

    def _find_price_in_element(self, element) -> dict:
        """Find price information within an element."""
        text = str(element)

        # Enhanced price patterns for telecom
        price_patterns = [
            r'£(\d+(?:,\d{3})*(?:\.\d{2})?)',  # £1,234.56
            r'\\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*pounds?',  # 1234 pounds
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 1234 USD
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*ZWL',  # 1234 ZWL
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*per month',  # 1234 per month
            r'monthly\s*£?\\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # monthly 1234
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price_value = float(price_str)
                    currency = 'GBP' if '£' in text else ('USD' if '$' in text else 'GBP')
                    return {'value': price_value, 'currency': currency}
                except ValueError:
                    continue

        return {'value': None, 'currency': 'GBP'}

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
        data_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB|TB)', text, re.IGNORECASE)
        if data_match:
            amount = float(data_match.group(1))
            unit = data_match.group(2).upper()
            # Convert to GB for consistency
            if unit == 'MB':
                amount = amount / 1024
                unit = 'GB'
            elif unit == 'TB':
                amount = amount * 1024
                unit = 'GB'

            return {'data_gb': amount, 'unit': unit, 'details': f'{amount} {unit} data'}
        return {}

    def _extract_data_amount(self, text: str) -> dict:
        """Extract data amount from text."""
        data_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB|TB)', text, re.IGNORECASE)
        if data_match:
            amount = float(data_match.group(1))
            unit = data_match.group(2).upper()
            return {'amount': amount, 'unit': unit}
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

    def _parse_price(self, price_text: str):
        """Parse price text into value and currency."""
        if not price_text:
            return None, 'GBP'

        # Look for price patterns
        price_patterns = [
            r'£(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'\\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*pounds?',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',
        ]

        for pattern in price_patterns:
            match = re.search(pattern, price_text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price_value = float(price_str)
                    currency = 'GBP' if '£' in price_text else ('USD' if '$' in price_text else 'GBP')
                    return price_value, currency
                except ValueError:
                    continue

        return None, 'GBP'
'''

# Write back with methods added
with open('app/scraping/extractors/telecom.py', 'w') as f:
    f.write(content + methods)

print('Added missing methods to telecom extractor')