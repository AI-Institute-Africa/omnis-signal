"""
Econet Wireless Zimbabwe - Specialized extractor for data bundles, voice plans, and SMS products.
Handles the structured layout of https://www.econet.co.zw/zwg-data-bundles/
"""
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord


class EconetExtractor(BaseExtractor):
    """Specialized extractor for Econet Wireless Zimbabwe pricing data."""

    def get_entity_name(self) -> str:
        return "Econet Wireless"

    def get_category(self) -> str:
        return "telecom"

    def extract(self) -> List[ExtractedRecord]:
        """Extract Econet products from raw HTML content."""
        records = []

        if self.snapshot.content_type.lower() != 'html':
            return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract different bundle types
        # The page has clear section headings for each category
        text = soup.get_text()
        
        # Verify this is a data bundles page
        if 'data bundle' not in text.lower() and 'econet' not in text.lower():
            return records

        # Extract by category
        social_media_bundles = self._extract_social_media_bundles(soup, text)
        records.extend(social_media_bundles)

        daily_bundles = self._extract_daily_bundles(soup, text)
        records.extend(daily_bundles)

        weekly_bundles = self._extract_weekly_bundles(soup, text)
        records.extend(weekly_bundles)

        monthly_bundles = self._extract_monthly_bundles(soup, text)
        records.extend(monthly_bundles)

        wifi_bundles = self._extract_wifi_bundles(soup, text)
        records.extend(wifi_bundles)

        sms_bundles = self._extract_sms_bundles(soup, text)
        records.extend(sms_bundles)

        return records

    def _extract_social_media_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract Facebook, WhatsApp, Instagram, X bundles."""
        records = []

        if 'facebook' not in full_text.lower() and 'whatsapp' not in full_text.lower():
            return records

        # Pattern for social media bundles
        # Matches: Facebook (25MB) | 24 Hours | 20 | 5 | 4.00
        pattern = r'(Facebook|WhatsApp|Instagram|X)\s*\((\d+(?:MB|GB)?)\)\s*\|\s*(\d+\s*Hours?)\s*\|\s*(\d+)\s*\|\s*(\d+|-)\s*\|\s*([\d.]+)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        
        for match in matches:
            platform = match.group(1).strip()
            data_str = match.group(2).strip()
            validity_str = match.group(3).strip()
            peak_data = match.group(4).strip()
            off_peak_data = match.group(5).strip()
            price_str = match.group(6).strip()

            # Extract numeric values
            data_info = self._parse_data_amount(data_str)
            price_info = self._parse_price(price_str)
            
            if data_info.get('amount') and price_info.get('value'):
                product_name = f"{platform} ({data_str})"
                off_peak_text = f"Off-peak: {off_peak_data}" if off_peak_data != '-' else "Off-peak: None"
                description = f"{validity_str} - Peak: {peak_data}MB, {off_peak_text}"
                
                record = self._create_record(
                    subcategory='social_media_bundle',
                    title=product_name,
                    description=description,
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=data_info.get('amount'),
                    unit_type=data_info.get('unit', 'MB'),
                    billing_period='validity',
                    eligibility=validity_str,
                    confidence_score=0.9
                )
                if record:
                    records.append(record)

        return records

    def _extract_daily_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract daily data bundles (24 hour bundles)."""
        records = []

        if 'daily data bundle' not in full_text.lower():
            return records

        # Pattern: Daily Data Bundle(1200MB) | 24 Hours | 1200 | - | 155.08
        pattern = r'Daily Data (?:Bundle|Bouquet)\s*\((\d+(?:MB|GB)?)\)?\s*\|\s*24 Hours?\s*\|\s*(\d+(?:\.?\d+)?)\s*\|\s*([^\|]+?)\s*\|\s*([\d.]+)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            data_str = match.group(1) or match.group(2)
            price_str = match.group(4)
            
            data_info = self._parse_data_amount(data_str)
            price_info = self._parse_price(price_str)
            
            if data_info.get('amount') and price_info.get('value'):
                product_name = f"Daily Data Bundle ({data_str})"
                record = self._create_record(
                    subcategory='data_bundle',
                    title=product_name,
                    description='24 Hour validity - Daily data bundle',
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=data_info.get('amount'),
                    unit_type=data_info.get('unit', 'MB'),
                    billing_period='24h',
                    eligibility='24 Hours',
                    confidence_score=0.88
                )
                if record:
                    records.append(record)

        return records

    def _extract_weekly_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract weekly data bundles (7 day bundles)."""
        records = []

        if 'weekly data bundle' not in full_text.lower():
            return records

        # Pattern: Weekly Data Bundle(370MB) | 7 Days | 370 | - | 51.80
        pattern = r'Weekly Data Bundle\s*\((\d+(?:MB|GB)?)\)?\s*\|\s*7 Days?\s*\|\s*(\d+(?:\.?\d+)?)\s*\|\s*([^\|]+?)\s*\|\s*([\d.]+)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            data_str = match.group(1) or match.group(2)
            price_str = match.group(4)
            
            data_info = self._parse_data_amount(data_str)
            price_info = self._parse_price(price_str)
            
            if data_info.get('amount') and price_info.get('value'):
                product_name = f"Weekly Data Bundle ({data_str})"
                record = self._create_record(
                    subcategory='data_bundle',
                    title=product_name,
                    description='7 Day validity - Weekly data bundle',
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=data_info.get('amount'),
                    unit_type=data_info.get('unit', 'MB'),
                    billing_period='7d',
                    eligibility='7 Days',
                    confidence_score=0.88
                )
                if record:
                    records.append(record)

        return records

    def _extract_monthly_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract monthly data bundles (30 day bundles)."""
        records = []

        if 'monthly' not in full_text.lower() or 'data monthly bundle' not in full_text.lower():
            return records

        # Pattern: Data Monthly Bundle(1400MB) | 30 Days | 1400 | - | 196.00
        pattern = r'Data Monthly Bundle\s*\((\d+(?:MB|GB)?)\)?\s*\|\s*30 Days?\s*\|\s*(\d+(?:\.?\d+)?)\s*\|\s*([^\|]+?)\s*\|\s*([\d.]+)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            data_str = match.group(1) or match.group(2)
            price_str = match.group(4)
            
            data_info = self._parse_data_amount(data_str)
            price_info = self._parse_price(price_str)
            
            if data_info.get('amount') and price_info.get('value'):
                product_name = f"Data Monthly Bundle ({data_str})"
                record = self._create_record(
                    subcategory='data_bundle',
                    title=product_name,
                    description='30 Day validity - Monthly data bundle',
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=data_info.get('amount'),
                    unit_type=data_info.get('unit', 'MB'),
                    billing_period='month',
                    eligibility='30 Days',
                    confidence_score=0.88
                )
                if record:
                    records.append(record)

        return records

    def _extract_wifi_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract Private WiFi bundles."""
        records = []

        if 'private wifi' not in full_text.lower():
            return records

        # Pattern: Private WiFi Bundle 55GB | 30 Days | 55 | - | 2341.00
        pattern = r'Private WiFi Bundle\s*(\d+(?:\.\d+)?(?:GB|MB)?)\s*\|\s*30 Days?\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*([^\|]+?)\s*\|\s*([\d.]+)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            data_str = match.group(1).strip()
            price_str = match.group(4).strip()
            
            data_info = self._parse_data_amount(data_str)
            price_info = self._parse_price(price_str)
            
            if data_info.get('amount') and price_info.get('value'):
                product_name = f"Private WiFi Bundle {data_str}"
                record = self._create_record(
                    subcategory='broadband_plan',
                    title=product_name,
                    description='30 Day validity - Private WiFi bundle',
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=data_info.get('amount'),
                    unit_type=data_info.get('unit', 'GB'),
                    billing_period='month',
                    eligibility='30 Days',
                    confidence_score=0.85
                )
                if record:
                    records.append(record)

        return records

    def _extract_sms_bundles(self, soup: BeautifulSoup, full_text: str) -> List[ExtractedRecord]:
        """Extract SMS bundles (daily and weekly)."""
        records = []

        if 'sms' not in full_text.lower():
            return records

        # Pattern: SMS Daily | 13 | 1.05 | 1 Day
        # and: SMS Weekly | 94 | 9.19 | 7 Days
        pattern = r'SMS (Daily|Weekly)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*(\d+\s*(?:Day|Week)s?)'
        
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            bundle_type = match.group(1).strip()
            sms_count = int(match.group(2))
            price_str = match.group(3).strip()
            validity = match.group(4).strip()
            
            price_info = self._parse_price(price_str)
            
            if sms_count > 0 and price_info.get('value'):
                product_name = f"SMS {bundle_type} ({sms_count} SMS)"
                billing = '1d' if 'daily' in bundle_type.lower() else '7d' if 'weekly' in bundle_type.lower() else None
                
                record = self._create_record(
                    subcategory='sms_bundle',
                    title=product_name,
                    description=f'{validity} validity - {sms_count} SMS',
                    price_value=price_info.get('value'),
                    price_currency=price_info.get('currency', 'ZWL'),
                    unit_value=sms_count,
                    unit_type='SMS',
                    billing_period=billing,
                    eligibility=validity,
                    confidence_score=0.9
                )
                if record:
                    records.append(record)

        return records

    # Helper methods
    def _parse_data_amount(self, data_str: str) -> Dict[str, Any]:
        """Parse data amount from strings like '25MB', '5GB', '55'."""
        if not data_str:
            return {'amount': None, 'unit': 'MB'}

        # Extract number and unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|GB|TB)?', data_str, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1))
                unit = match.group(2).upper() if match.group(2) else 'MB'
                return {'amount': amount, 'unit': unit}
            except:
                pass

        return {'amount': None, 'unit': 'MB'}

    def _parse_price(self, price_str: str) -> Dict[str, Any]:
        """Parse price from string like '155.08' or '51.80'."""
        if not price_str:
            return {'value': None, 'currency': 'ZWL'}

        # Extract numeric value
        match = re.search(r'([\d.]+)', price_str.strip())
        if match:
            try:
                value = float(match.group(1))
                # Econet uses ZWL (Zimbabwean Dollar)
                return {'value': value, 'currency': 'ZWL'}
            except:
                pass

        return {'value': None, 'currency': 'ZWL'}

    def _find_nearby_price(self, element) -> dict:
        """Find price near an element (inherited from base but overridden for ZWL)."""
        base_result = super()._find_nearby_price(element)
        # Override currency to ZWL for Econet
        if base_result.get('value'):
            base_result['currency'] = 'ZWL'
        return base_result
