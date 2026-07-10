import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord

class TransportExtractor(BaseExtractor):
    """Extractor for airlines and logistics (fares, shipping rates)."""

    def get_entity_name(self) -> str:
        url = self.snapshot.url.lower()
        if 'airzimbabwe' in url: return 'Air Zimbabwe'
        if 'fastjet' in url: return 'Fastjet Zimbabwe'
        if 'zupco' in url: return 'ZUPCO'
        if 'dhl' in url: return 'DHL Zimbabwe'
        if 'fedex' in url: return 'FedEx Zimbabwe'
        if 'swift' in url: return 'Swift Zimbabwe'
        if 'unifreight' in url: return 'Unifreight'
        if 'roadrunners' in url: return 'Roadrunners'
        if 'flyafrica' in url: return 'Fly Africa'
        if 'pathfinder' in url: return 'Pathfinder'
        if 'citylink' in url: return 'City Link'
        
        return self._detect_entity_name()


    def get_category(self) -> str:
        return 'transport'

    def extract(self) -> List[ExtractedRecord]:
        records = []
        if self.snapshot.content_type.lower() != 'html': return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')
        


        # 2. Check for Tables (Bus fares/Flight schedules)
        for table in soup.find_all('table'):
            table_records = self._extract_from_table(table)
            for r in table_records:
                r.subcategory = 'transport_fare'
                records.append(r)

        # 3. Text-based heuristic (as fallback)
        if not records:
            page_text = soup.get_text().lower()
            indicators = ['fare', 'flight', 'ticket', 'shipping', 'delivery', 'rate', 'cargo', 'parcel', 'bus', 'fuel', 'petrol', 'diesel']
            if not any(ind in page_text for ind in indicators): return records

            for element in soup.find_all(['div', 'p', 'tr']):
                text = element.get_text().strip()
                if len(text) < 10 or len(text) > 300: continue
                
                if any(ind in text.lower() for ind in indicators):
                    price_info = self._find_nearby_price(element)
                    if price_info.get('value'):
                        record = self._create_record(
                            subcategory='transport_fare',
                            title=text.split('\n')[0][:80],
                            description=text[:200],
                            price_value=price_info['value'],
                            price_currency=price_info['currency'],
                            confidence_score=0.7
                        )
                        if record: records.append(record)
        return records



