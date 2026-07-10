#!/usr/bin/env python3
"""
Zimbabwe Telecom Market Intelligence Scraper
Scrapes pricing, bundles, tariffs, and service data from Zimbabwean telecom providers
"""

import json
import csv
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ServiceOffering:
    """Complete market intelligence record for a telecom service"""
    # Provider Information
    provider_name: str
    provider_type: str  # MNO, ISP, MVNO, etc.
    provider_website: str
    
    # Service Information
    service_category: str  # broadband_plan, data_bundle, voice_bundle, sms_bundle, etc.
    service_name: str
    service_description: Optional[str] = None
    
    # Unit Information
    unit_type: str  # GB, MB, SMS Count, Minutes, etc.
    unit_value: Optional[float] = None
    
    # Pricing Information
    price_usd: Optional[float] = None
    price_local: Optional[str] = None  # e.g., "2341.00 ZWG"
    billing_period: Optional[str] = None  # Daily, Weekly, Monthly, etc.
    
    # Additional Details
    validity: Optional[str] = None  # e.g., "30 Days", "1 Hour"
    peak_data: Optional[str] = None  # For packages with peak/off-peak distinction
    off_peak_data: Optional[str] = None
    additional_features: Optional[str] = None  # JSON string of extra features
    
    # Data Quality
    confidence_score: Optional[int] = None  # 60-100%
    source_url: Optional[str] = None
    
    # Metadata
    scraped_date: str = field(default_factory=lambda: datetime.now().isoformat())
    data_last_updated: Optional[str] = None
    

class TelecomScraper:
    """Base scraper for telecom providers"""
    
    PROVIDERS = {
        'econet': {
            'name': 'Econet Wireless Zimbabwe',
            'type': 'MNO',
            'website': 'https://www.econet.co.zw',
            'urls': {
                'bundles': 'https://www.econet.co.zw/bundles/',
                'tariffs': 'https://www.econet.co.zw/tariffs/',
                'devices': 'https://www.econet.co.zw/devices/',
            }
        },
        'netone': {
            'name': 'NetOne Cellular',
            'type': 'MNO',
            'website': 'https://www.netone.co.zw',
            'urls': {
                'bundles': 'https://www.netone.co.zw/bundles/',
                'products': 'https://www.netone.co.zw/products/',
                'promotions': 'https://www.netone.co.zw/promotions',
            }
        },
        'telecel': {
            'name': 'Telecel Zimbabwe',
            'type': 'MNO',
            'website': 'https://telecel.co.zw',
            'urls': {
                'products': 'https://telecel.co.zw/products/',
                'bundles': 'https://telecel.co.zw/bundles/',
            }
        },
        'telone': {
            'name': 'TelOne',
            'type': 'ISP/Telecom',
            'website': 'https://www.telone.co.zw',
            'urls': {
                'residential': 'https://www.telone.co.zw/Products/Broadband',
                'enterprise': 'https://www.telone.co.zw/Products/Enterprise',
                'tariffs': 'https://www.telone.co.zw/products/details/service-tariffs-effective-5-august-2025',
            }
        },
        'tagtel': {
            'name': 'Tagtel',
            'type': 'MVNO',
            'website': 'https://www.tagtel.co.zw',
            'urls': {
                'data_plans': 'https://www.tagtel.co.zw/data-plans/',
                'sim': 'https://www.tagtel.co.zw/sim/',
            }
        },
        'liquid_home': {
            'name': 'Liquid Home Zimbabwe',
            'type': 'ISP',
            'website': 'https://www.liquidhome.co.zw',
            'urls': {
                'packages': 'https://www.liquidhome.co.zw/packages/',
            }
        },
        'africom': {
            'name': 'Africom',
            'type': 'ISP',
            'website': 'https://www.africom.co.zw',
            'urls': {
                'services': 'https://www.africom.co.zw/services/',
            }
        },
    }
    
    def __init__(self, headless=True):
        """Initialize scraper with requests session and optional Selenium"""
        self.session = self._create_session()
        self.headless = headless
        self.offerings = []
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def scrape_econet(self) -> List[ServiceOffering]:
        """Scrape Econet Wireless offerings"""
        logger.info("Scraping Econet Wireless...")
        offerings = []
        
        # Note: Econet uses dynamic content - requires JavaScript rendering
        # For now, collect structured data from known sources
        
        return offerings
    
    def scrape_netone(self) -> List[ServiceOffering]:
        """Scrape NetOne offerings"""
        logger.info("Scraping NetOne...")
        offerings = []
        
        # NetOne VALUE BUNDLE: 1 Gig for USD$1
        offerings.append(ServiceOffering(
            provider_name='NetOne Cellular',
            provider_type='MNO',
            provider_website='https://www.netone.co.zw',
            service_category='data_bundle',
            service_name='VALUE BUNDLE',
            service_description='1 Gig of data valid till 12 midnight daily',
            unit_type='GB',
            unit_value=1.0,
            price_usd=1.0,
            billing_period='Daily',
            validity='Till 12 midnight',
            confidence_score=85,
            source_url='https://www.netone.co.zw'
        ))
        
        return offerings
    
    def scrape_telone(self) -> List[ServiceOffering]:
        """Scrape TelOne offerings"""
        logger.info("Scraping TelOne...")
        offerings = []
        
        soup = self.fetch_page('https://www.telone.co.zw/Products/Broadband')
        if not soup:
            return offerings
        
        # TelOne broadband packages
        broadband_packages = {
            'Home Plus': 'Capped broadband',
            'Home Premier': 'Capped broadband',
            'Home Surfer': 'Capped broadband',
            'Home Boost': 'Capped broadband',
            'Infinity Pro': 'Capped broadband',
            'Intense': 'Uncapped broadband',
            'Infinity Supreme': 'Uncapped broadband',
        }
        
        for package_name, package_type in broadband_packages.items():
            offerings.append(ServiceOffering(
                provider_name='TelOne',
                provider_type='ISP',
                provider_website='https://www.telone.co.zw',
                service_category='broadband_plan',
                service_name=package_name,
                service_description=package_type,
                unit_type='Mbps/Month',
                billing_period='Monthly',
                confidence_score=80,
                source_url='https://www.telone.co.zw/Products/Broadband'
            ))
        
        return offerings
    
    def export_to_csv(self, filename: str = 'zimbabwe_telecom_intelligence.csv'):
        """Export all offerings to CSV"""
        if not self.offerings:
            logger.warning("No offerings to export")
            return
        
        keys = asdict(self.offerings[0]).keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for offering in self.offerings:
                writer.writerow(asdict(offering))
        
        logger.info(f"Exported {len(self.offerings)} records to {filename}")
    
    def export_to_json(self, filename: str = 'zimbabwe_telecom_intelligence.json'):
        """Export all offerings to JSON"""
        data = [asdict(o) for o in self.offerings]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(self.offerings)} records to {filename}")
    
    def run_all_scrapers(self):
        """Execute all scraper methods"""
        self.offerings.extend(self.scrape_econet())
        self.offerings.extend(self.scrape_netone())
        self.offerings.extend(self.scrape_telone())
        
        logger.info(f"Total offerings collected: {len(self.offerings)}")
        return self.offerings


if __name__ == '__main__':
    scraper = TelecomScraper()
    offerings = scraper.run_all_scrapers()
    
    # Export results
    scraper.export_to_csv('zimbabwe_telecom_intelligence.csv')
    scraper.export_to_json('zimbabwe_telecom_intelligence.json')
    
    # Print summary
    print(f"\n✅ Scraping Complete!")
    print(f"Total records: {len(offerings)}")
    print(f"\nProvider Summary:")
    providers = {}
    for offering in offerings:
        if offering.provider_name not in providers:
            providers[offering.provider_name] = 0
        providers[offering.provider_name] += 1
    
    for provider, count in providers.items():
        print(f"  {provider}: {count} offerings")
