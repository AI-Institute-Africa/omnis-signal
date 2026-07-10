import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord

class EducationExtractor(BaseExtractor):
    """Extractor for universities and schools (fees, tuition)."""

    def get_entity_name(self) -> str:
        url = self.snapshot.url
        if 'uct.ac.za' in url.lower(): return 'University of Cape Town'
        if 'uz.ac.zw' in url.lower(): return 'University of Zimbabwe'
        if 'harvard.edu' in url.lower(): return 'Harvard University'
        return 'Educational Institution'

    def get_category(self) -> str:
        return 'education'

    def extract(self) -> List[ExtractedRecord]:
        records = []
        if self.snapshot.content_type.lower() != 'html': return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')
        
        # Clean up
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        page_text = soup.get_text().lower()
        
        indicators = [
            'tuition', 'fees', 'semester', 'academic', 'undergraduate', 'postgraduate', 
            'admission', 'levy', 'registration', 'boarding', 'enrolment', 'scholarship',
            'tuition fee', 'ancillary fees', 'payment structure', 'fee structure',
            'results', 'ranking', 'pass rate', 'candidates'
        ]
        is_known_entity = any(kw in self.snapshot.url.lower() for kw in ['zimsec', 'resultscouncil', 'uz.ac.zw', 'nust.ac.zw'])
        
        if not any(ind in page_text for ind in indicators) and not is_known_entity: 
            return records


        # 1. Look for fee tables (very common for education)
        for table in soup.find_all('table'):
            # Check if table looks like a fee table or results table
            table_text = table.get_text().lower()
            if any(ind in table_text for ind in ['fee', 'tuition', 'amount', 'cost', 'levy', 'pass rate', 'results']) or is_known_entity:
                table_records = self._extract_from_table(table)
                for r in table_records:
                    # Refine education records
                    is_results = any(kw in r.title.lower() or kw in table_text for kw in ['pass rate', 'results', 'candidates', 'graduated'])
                    r.subcategory = 'academic_results' if (is_results or is_known_entity) else 'tuition_fees'
                    r.billing_period = 'semester' if 'semester' in table_text else 'year'
                    r.confidence_score = 0.8
                    records.append(r)


        # 2. Look for specific containers/blocks
        selectors = ['.fees-box', '.tuition-card', '.pricing-plan', '.fee-item', '.cost-block', '.results-data', '.stats-box']
        for selector in selectors:
            for element in soup.select(selector):
                price_info = self._find_nearby_price(element)
                if price_info.get('value'):
                    records.append(self._create_education_record(element, element.get_text(strip=True), price_info))

        # 3. Look for price patterns in text blocks (divs, paragraphs) near headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text().strip().lower()
            if any(ind in heading_text for ind in indicators):
                price_info = self._find_nearby_price(heading)
                if price_info.get('value'):
                    # Skip if we already found this in a table (avoid duplicates)
                    if not any(r.price_value == price_info['value'] and r.title in heading_text for r in records):
                        records.append(self._create_education_record(heading, heading.get_text().strip(), price_info))

        # 4. NEW: Specific logic for Results and Statistics (ZIMSEC etc.)
        if is_known_entity or any(kw in page_text for kw in ['pass rate', 'percentage', 'statistics', 'results']):
            # Look for percentage patterns in a broader range of tags
            for p in soup.find_all(['p', 'div', 'li', 'td', 'span']):
                text = p.get_text(strip=True)
                if len(text) < 5 or len(text) > 2000: continue
                
                # Match percentages: e.g., 93.3%, 93, 3%
                # Use finditer to catch multiple percentages in one block
                for pass_rate_match in re.finditer(r'(\d{1,3}(?:[.,]\s*\d+)?)\s*%', text):
                    val_str = pass_rate_match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        val = float(val_str)
                        if 0 <= val <= 100:
                            # Try to find context for the title
                            context = text[max(0, pass_rate_match.start()-40):pass_rate_match.end()+40].lower()
                            title = "Academic Pass Rate"
                            if 'candidate' in context: title = "Candidate Pass Rate"
                            if 'school' in context: title = "School Pass Rate"
                            if 'private' in context: title = "Private Candidate Pass Rate"
                            if 'overall' in context: title = "Overall Pass Rate"
                            
                            # Avoid duplicate values from the same block
                            if not any(r.price_value == val and r.title == title for r in records):
                                records.append(self._create_record(
                                    subcategory='academic_results',
                                    title=title,
                                    description=text[:250],
                                    price_value=val,
                                    price_currency='%',
                                    confidence_score=0.75
                                ))
                    except: continue

                # Match large numbers (candidate counts)
                # Matches patterns like: "candidates was 32,764", "candidature of 41 653"
                for candidate_match in re.finditer(r'(?:total\s+)?(?:number\s+of\s+)?(?:candidates|candidature)\s+(?:was|is|sat|of)\s+([\d\s,]{2,10})', text, re.I):
                    val_str = candidate_match.group(1).replace(' ', '').replace(',', '')
                    try:
                        val = float(val_str)
                        if val > 10: # Avoid small numbers
                            title = "Total Candidates"
                            if 'school' in text.lower(): title = "School Candidates"
                            if 'private' in text.lower(): title = "Private Candidates"
                            
                            if not any(r.price_value == val and r.title == title for r in records):
                                records.append(self._create_record(
                                    subcategory='academic_statistics',
                                    title=title,
                                    description=text[:250],
                                    price_value=val,
                                    price_currency='count',
                                    confidence_score=0.75
                                ))
                    except: continue

        return records

    def _create_education_record(self, element, text, price_info) -> ExtractedRecord:
        # Try to find a better title from the text
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        title = lines[0] if lines else "Tuition Fees"
        
        is_results = any(kw in title.lower() or kw in text.lower() for kw in ['pass rate', 'results', 'candidates', 'graduated'])

        return self._create_record(
            subcategory='academic_results' if is_results else 'tuition_fees',
            title=title[:80],
            description=text[:200],
            price_value=price_info['value'],
            price_currency=price_info['currency'],
            billing_period='semester' if 'semester' in text.lower() else 'year',
            confidence_score=0.7
        )




