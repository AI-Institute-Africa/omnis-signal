import re
from typing import List
from bs4 import BeautifulSoup
from app.scraping.extractors.base import BaseExtractor
from app.db.models.extracted_record import ExtractedRecord
from app.scraping.normalization_loader import load_banking_normalization


BANKING_SERVICE_NORMALIZATION = [
    {
        'pattern': r'\b(cash withdrawal|atm withdrawal|atm cash|cashout|cash out|teller cash|branch cash)\b',
        'subcategory': 'cash_withdrawal',
        'title': 'Cash Withdrawal Fee',
        'item_name': 'Cash Withdrawal'
    },
    {
        'pattern': r'\b(account maintenance|maintenance fee|account service fee|service fee|monthly account fee|account administration|account upkeep|monthly fee|annual account fee)\b',
        'subcategory': 'account_maintenance',
        'title': 'Account Maintenance Fee',
        'item_name': 'Account Maintenance'
    },
    {
        'pattern': r'\b(pos payment|merchant payment|bill payment|utility payment|merchant pos|merchant pgs|merchant fees|vendor payment|merchant settlement|merchant charge)\b',
        'subcategory': 'bill_payment',
        'title': 'Bill Payment / Merchant Fee',
        'item_name': 'Bill Payment'
    },
    {
        'pattern': r'\b(rtgs|internal transfer|interbank transfer|bank transfer|telegraphic transfer|eft|zimswitch|all-pay|real time gross settlement|swift|swift transfer|telegraphic transfer|wire transfer)\b',
        'subcategory': 'bank_transfer',
        'title': 'Bank Transfer Fee',
        'item_name': 'Transfer'
    },
    {
        'pattern': r'\b(internet banking|online banking|e-banking|i-banking|online transfer|internet banking fee)\b',
        'subcategory': 'internet_banking',
        'title': 'Internet Banking Fee',
        'item_name': 'Internet Banking'
    },
    {
        'pattern': r'\b(mobile banking|mobile transfer|m-banking|sms banking|mobile money|mobile wallet|airtime transfer)\b',
        'subcategory': 'mobile_banking',
        'title': 'Mobile Banking Fee',
        'item_name': 'Mobile Banking'
    },
    {
        'pattern': r'\b(credit card|mastercard|visa card|visa prepaid|visa debit|debit card|prepaid card|card replacement|card fee|annual card fee|card issuance|card maintenance)\b',
        'subcategory': 'card_service',
        'title': 'Card Service / Card Fee',
        'item_name': 'Card'
    },
    {
        'pattern': r'\b(loans|loan application|loan processing|loan origination|overdraft|overdraft facility|loan arrangement|loan processing fee|application fee|early repayment|late payment|loan interest)\b',
        'subcategory': 'loan',
        'title': 'Loan Service / Charges',
        'item_name': 'Loan'
    },
    {
        'pattern': r'\b(savings account|deposit account|fixed deposit|term deposit|savings account|deposit fee|withdrawal limit|interest rate|aer|apr)\b',
        'subcategory': 'savings_account',
        'title': 'Savings Account',
        'item_name': 'Savings Account'
    },
    {
        'pattern': r'\b(current account|transaction account|cheque account|corporate account|business account|cheque book|cheque processing|account opening fee|account closure|closing fee|statement fee|mini statement|atm balance inquiry|pin change)\b',
        'subcategory': 'current_account',
        'title': 'Current Account / Transactional Charges',
        'item_name': 'Current Account'
    }
]

def _build_banking_normalization_rules():
    """Combine default and spreadsheet-driven banking normalization rules."""
    rules = list(BANKING_SERVICE_NORMALIZATION)
    try:
        external = load_banking_normalization()
        if external:
            rules = external + rules
    except Exception:
        external = []

    # Compile regexes for speed and fall back to escaped literal patterns.
    for r in rules:
        try:
            r['regex'] = re.compile(r['pattern'], re.I)
        except Exception:
            r['regex'] = re.compile(re.escape(r.get('pattern', '')), re.I)

    # Sort by pattern length to prefer more specific matches.
    rules.sort(key=lambda r: -len(r.get('pattern', '')))
    return rules

BANKING_SERVICE_NORMALIZATION = _build_banking_normalization_rules()


class BankingExtractor(BaseExtractor):
    """Extractor for banking websites (accounts, loans, cards, etc.)."""

    def get_entity_name(self) -> str:
        return self._detect_entity_name()


    def get_category(self) -> str:
        return 'banking'

    def extract(self) -> List[ExtractedRecord]:
        """Extract banking products from HTML content."""
        records = []

        if self.snapshot.content_type.lower() != 'html':
            return records

        soup = BeautifulSoup(self.snapshot.content, 'html.parser')

        # Remove script and style elements that might contain irrelevant text
        for script in soup(["script", "style"]):
            script.decompose()

        # Look for common patterns in banking sites with improved selectors
        # Current accounts
        current_accounts = self._extract_current_accounts(soup)
        records.extend(current_accounts)

        # Savings accounts
        savings_accounts = self._extract_savings_accounts(soup)
        records.extend(savings_accounts)

        # Credit cards - improved
        credit_cards = self._extract_credit_cards_improved(soup)
        records.extend(credit_cards)

        # Loans
        loans = self._extract_loans(soup)
        records.extend(loans)

        # Banking service fees and normalized service entries
        service_fees = self._extract_service_fee_records(soup)
        records.extend(service_fees)

        # If no specific products found, try to extract general banking info
        if not records:
            general_banking = self._extract_general_banking_info(soup)
            records.extend(general_banking)

        # Normalize any matched banking service names across the extracted records
        records = [self._normalize_banking_service(record) for record in records]
        return records

    def _extract_current_accounts(self, soup) -> List[ExtractedRecord]:
        """Extract current account products."""
        records = []

        account_selectors = [
            '.current-account', '.account', '.banking-account',
            '[class*="current"]', '[class*="account"]'
        ]

        for selector in account_selectors:
            accounts = soup.select(selector)
            for account in accounts:
                record = self._parse_current_account(account)
                if record:
                    records.append(record)

        return records


    def _parse_current_account(self, element) -> ExtractedRecord:
        """Parse a single current account element."""
        title = self._extract_text(element, ['h1', 'h2', 'h3', '.title', '.name'])
        description = self._extract_text(element, ['.description', '.details', 'p'])
        link = self._extract_link(element)

        # Look for interest rate
        interest_match = re.search(r'(\d+(?:\.\d{2})?)%', str(element))
        interest_rate = float(interest_match.group(1)) if interest_match else None

        # Look for fees
        price_info = self._find_nearby_price(element)
        fee_value, fee_currency = price_info['value'], price_info['currency']

        # Skip if price is 0 and title is suspicious (noise)
        if fee_value == 0 and any(noise in title.lower() for noise in ['personalise', 'join', 'login', 'search']):
            return None

        return self._create_record(
            subcategory='current_account',
            title=title or 'Current Account',
            description=description,
            unit_value=interest_rate,
            unit_type='APR' if interest_rate else None,
            price_value=fee_value,  # Monthly fee
            price_currency=fee_currency,
            billing_period='month' if fee_value else None,
            source_url=link,
            confidence_score=0.8
        )

    def _extract_savings_accounts(self, soup) -> List[ExtractedRecord]:
        """Extract savings account products."""
        records = []

        savings_selectors = [
            '.savings', '.deposit', '.isa',
            '[class*="saving"]', '[class*="deposit"]'
        ]

        for selector in savings_selectors:
            accounts = soup.select(selector)
            for account in accounts:
                record = self._parse_savings_account(account)
                if record:
                    records.append(record)

        return records

    def _parse_savings_account(self, element) -> ExtractedRecord:

        """Parse a single savings account element."""
        title = self._extract_text(element, ['h1', 'h2', 'h3', '.title', '.name'])
        description = self._extract_text(element, ['.description', '.details', 'p'])
        link = self._extract_link(element)

        # Look for interest rate
        interest_match = re.search(r'(\d+(?:\.\d{2})?)%', str(element))
        interest_rate = float(interest_match.group(1)) if interest_match else None

        # Look for minimum deposit
        price_info = self._find_nearby_price(element)
        min_deposit, currency = price_info['value'], price_info['currency']

        if not title or any(noise in title.lower() for noise in ['personalise', 'join', 'login']):
            return None

        return self._create_record(
            subcategory='savings_account',
            title=title or 'Savings Account',
            description=description,
            unit_value=interest_rate,
            unit_type='AER' if interest_rate else None,
            eligibility=f'Minimum deposit: {currency}{min_deposit}' if min_deposit else None,
            source_url=link,
            confidence_score=0.8
        )

    def _extract_credit_cards_improved(self, soup) -> List[ExtractedRecord]:
        """Extract credit card products with improved selectors."""
        records = []

        # More comprehensive selectors for credit cards
        card_selectors = [
            '.credit-card', '.card', '.creditcard',
            '[class*="credit"]', '[class*="card"]',
            '[data-product-type*="credit"]', '[data-type*="card"]',
            '.product-card', '.financial-product',
            'article[class*="card"]', 'div[class*="card"]'
        ]

        # Also look for text content containing credit card keywords
        page_text = soup.get_text().lower()
        if any(kw in page_text for kw in ['credit card', 'creditcard', 'mastercard', 'visa card']):
            # Extract from headings and paragraphs
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                heading_text = heading.get_text().strip()
                if any(keyword in heading_text.lower() for keyword in ['credit card', 'creditcard', 'card', 'visa', 'mastercard']):
                    if any(noise in heading_text.lower() for noise in ['login', 'about', 'help', 'contact', 'personalise']):
                        continue
                        
                    # Look for pricing in nearby elements
                    price_info = self._find_nearby_price(heading)

                    record = self._create_record(
                        subcategory='credit_card',
                        title=heading_text,
                        description=self._extract_description_from_heading(heading),
                        price_value=price_info.get('value'),
                        price_currency=price_info.get('currency'),
                        source_url=self._extract_link(heading),
                        confidence_score=0.7
                    )
                    if record:
                        records.append(record)

        return records

    def _extract_loans(self, soup) -> List[ExtractedRecord]:
        """Extract loan products."""
        records = []

        loan_selectors = [
            '.loan', '.credit', '.borrowing',
            '[class*="loan"]', '[class*="credit"]'
        ]

        for selector in loan_selectors:
            loans = soup.select(selector)
            for loan in loans:
                record = self._parse_loan(loan)
                if record:
                    records.append(record)

        return records

    def _extract_description_from_heading(self, heading) -> str:
        """Extract description text from around a heading."""
        description = ""

        # Look at next few siblings for description
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

    def _extract_general_banking_info(self, soup) -> List[ExtractedRecord]:

        """Extract general banking information when specific products aren't found."""
        records = []

        # Look for main headings that might indicate banking products
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip()

            # Skip navigation/irrelevant headings
            skip_keywords = ['login', 'contact', 'about', 'help', 'search', 'menu', 'navigation', 'personalise', 'join', 'sign in']
            if any(skip in heading_text.lower() for skip in skip_keywords):
                continue

            # Look for banking-related content
            banking_keywords = ['account', 'saving', 'loan', 'credit', 'mortgage', 'debit', 'rate', 'fee']
            if any(keyword in heading_text.lower() for keyword in banking_keywords):
                # Get description from nearby paragraphs
                description = ""
                for sibling in heading.find_next_siblings(['p', 'div', 'span']):
                    text = sibling.get_text().strip()
                    if text and len(text) > 20 and len(description) < 300:
                        description += text + " "
                    if len(description) > 200:
                        break

                # Look for pricing information
                price_info = self._find_nearby_price(heading)

                if price_info.get('value') is not None:
                    record = self._create_record(
                        subcategory='general_banking',
                        title=heading_text,
                        description=description.strip(),
                        price_value=price_info.get('value'),
                        price_currency=price_info.get('currency'),
                        confidence_score=0.5
                    )
                    if record:
                        records.append(record)

        return records

    def _extract_service_fee_records(self, soup) -> List[ExtractedRecord]:
        """Extract normalized banking service fee records from page text."""
        records = []

        for element in soup.find_all(['tr', 'li', 'p', 'div']):
            text = element.get_text(separator=' ', strip=True)
            if not text or len(text) < 20:
                continue

            normalized = self._match_banking_service_text(text)
            if not normalized:
                continue

            price_info = self._find_nearby_price(element)
            if price_info.get('value') is None:
                continue

            title = normalized['title']
            description = text
            record = self._create_record(
                subcategory=normalized['subcategory'],
                title=title,
                item_name=normalized.get('item_name'),
                description=description,
                price_value=price_info['value'],
                price_currency=price_info['currency'],
                source_url=self._extract_link(element),
                confidence_score=0.6
            )
            if record:
                records.append(record)

        return records

    def _match_banking_service_text(self, text: str) -> dict:
        """Match raw text to a normalized banking service definition."""
        if not text:
            return {}

        normalized_text = text.lower()
        for rule in BANKING_SERVICE_NORMALIZATION:
            regex = rule.get('regex')
            if regex and regex.search(text):
                return rule
        return {}

    def _normalize_banking_service(self, record: ExtractedRecord) -> ExtractedRecord:
        """Apply service normalization based on title/description content."""
        if not record:
            return record

        text = ' '.join(
            filter(None, [record.title, record.description, record.item_name])
        )
        normalized = self._match_banking_service_text(text)
        if not normalized:
            return record

        record.subcategory = normalized['subcategory']
        record.title = normalized['title']
        if not record.item_name:
            record.item_name = normalized.get('item_name')
        if not record.description:
            record.description = normalized['title']

        return record

    def _parse_loan(self, element) -> ExtractedRecord:
        """Parse a single loan element."""
        title = self._extract_text(element, ['h1', 'h2', 'h3', '.title', '.name'])
        description = self._extract_text(element, ['.description', '.details', 'p'])

        # Look for APR
        apr_match = re.search(r'(\d+(?:\.\d{2})?)%', str(element))
        apr = float(apr_match.group(1)) if apr_match else None

        # Look for loan amount range
        price_info = self._find_nearby_price(element)
        amount = price_info['value']
        currency = price_info['currency']

        if not title or any(noise in title.lower() for noise in ['personalise', 'join', 'login']):
            return None

        return self._create_record(
            subcategory='loan',
            title=title or 'Loan',
            description=description,
            unit_value=apr,
            unit_type='APR' if apr else None,
            price_value=amount,
            price_currency=currency,
            confidence_score=0.8
        )


    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from element using multiple selectors, filtering out noise."""
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                text = found.get_text(strip=True)
                # Skip if it's just a number or too short
                if text and len(text) > 3 and not re.match(r'^\d+$', text):
                    return text
        
        # Fallback to direct text but filter common noisy headings
        raw_text = element.get_text(strip=True)
        if any(noise in raw_text.lower() for noise in ['looking for help', 'digital reset', 'back to my accounts', 'join today']):
            return ''
            
        return raw_text if len(raw_text) > 3 else ''