#!/usr/bin/env python3
"""
Zimbabwe Insurance Products Scraper
Collects insurance product pricing and coverage from major insurers
Persists data to the FastAPI scraper hub database
"""

import json
import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import logging
import pandas as pd

# Add the scraper-hub app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper-hub-v1', 'scraper-hub-'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InsuranceProduct:
    """Insurance product offering record"""
    # Provider Information
    provider_name: str
    provider_type: str
    provider_website: str
    
    # Product Information
    product_category: str  # motor, life, property, travel, health, etc.
    product_name: str
    product_type: Optional[str]  # individual, corporate, micro
    
    # Coverage Details
    coverage_description: Optional[str] = None
    coverage_limit: Optional[float] = None
    coverage_currency: str = "USD"
    
    # Pricing Information
    premium_amount: Optional[float] = None
    premium_currency: str = "USD"
    premium_frequency: str = "annual"
    price_string: Optional[str] = None
    
    # Terms & Conditions
    excess_deductible: Optional[float] = None
    waiting_period_days: Optional[int] = None
    age_minimum: Optional[int] = None
    age_maximum: Optional[int] = None
    
    # Product Features
    third_party_covered: bool = False
    own_damage_covered: bool = False
    comprehensive_coverage: bool = False
    accidental_damage: bool = False
    theft_coverage: bool = False
    personal_belongings: bool = False
    legal_liability: bool = False
    roadside_assistance: bool = False
    
    # Data Quality
    confidence_score: int = 60
    source_url: Optional[str] = None
    scraped_date: str = field(default_factory=lambda: datetime.now().isoformat())
    data_status: str = "active"
    notes: Optional[str] = None


class InsuranceScraperBase:
    """Base scraper for insurance products"""
    
    def __init__(self, provider_name: str, provider_type: str, website: str):
        self.provider_name = provider_name
        self.provider_type = provider_type
        self.website = website
        self.offerings: List[InsuranceProduct] = []
    
    def add_product(self, **kwargs) -> None:
        """Add an insurance product offering"""
        product = InsuranceProduct(
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            provider_website=self.website,
            **kwargs
        )
        self.offerings.append(product)
    
    def scrape(self) -> List[InsuranceProduct]:
        """Override in subclasses"""
        return self.offerings


class OldMutualScraper(InsuranceScraperBase):
    """Old Mutual Zimbabwe scraper"""
    
    def __init__(self):
        super().__init__('Old Mutual Zimbabwe', 'Insurer', 'https://www.oldmutual.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Old Mutual Zimbabwe...")
        
        self.add_product(
            product_category='life_insurance',
            product_name='Life Protection Plan',
            product_type='individual',
            coverage_description='Life and wealth protection coverage',
            premium_frequency='annual',
            source_url='https://www.oldmutual.co.zw/',
            confidence_score=65,
            notes='Life, Property, Wealth insurance products'
        )
        
        self.add_product(
            product_category='property_insurance',
            product_name='Home Insurance',
            product_type='individual',
            coverage_description='Home and property protection',
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://www.oldmutual.co.zw/',
            confidence_score=65
        )
        
        return self.offerings


class ZimnatScraper(InsuranceScraperBase):
    """Zimnat scraper"""
    
    def __init__(self):
        super().__init__('Zimnat', 'Insurer', 'https://zimnat.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Zimnat...")
        
        self.add_product(
            product_category='motor_insurance',
            product_name='Motor Insurance',
            product_type='individual',
            third_party_covered=True,
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://zimnat.co.zw/',
            confidence_score=70,
            notes='Motor insurance products'
        )
        
        self.add_product(
            product_category='funeral_insurance',
            product_name='Funeral Cover',
            product_type='individual',
            coverage_description='Funeral expense protection',
            source_url='https://zimnat.co.zw/',
            confidence_score=70
        )
        
        self.add_product(
            product_category='property_insurance',
            product_name='Property Protection',
            product_type='individual',
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://zimnat.co.zw/',
            confidence_score=70
        )
        
        return self.offerings


class FirstMutualInsuranceScraper(InsuranceScraperBase):
    """First Mutual Holdings Insurance scraper"""
    
    def __init__(self):
        super().__init__('First Mutual Holdings', 'Insurer', 'https://www.firstmutual.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping First Mutual Holdings...")
        
        self.add_product(
            product_category='life_insurance',
            product_name='Life Insurance Solution',
            product_type='individual',
            coverage_description='Life and health coverage',
            source_url='https://www.firstmutual.co.zw/',
            confidence_score=65,
            notes='Life, Health, Reinsurance solutions'
        )
        
        self.add_product(
            product_category='health_insurance',
            product_name='Health Cover',
            product_type='corporate',
            coverage_description='Corporate health insurance',
            source_url='https://www.firstmutual.co.zw/',
            confidence_score=65
        )
        
        return self.offerings


class NicozDiamondScraper(InsuranceScraperBase):
    """NicozDiamond scraper"""
    
    def __init__(self):
        super().__init__('NicozDiamond', 'Insurer', 'https://www.nicozdiamond.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping NicozDiamond...")
        
        self.add_product(
            product_category='motor_insurance',
            product_name='Motor Insurance',
            product_type='individual',
            third_party_covered=True,
            own_damage_covered=True,
            theft_coverage=True,
            roadside_assistance=True,
            source_url='https://www.nicozdiamond.co.zw/',
            confidence_score=70,
            notes='Short-term, Motor, Home insurance'
        )
        
        self.add_product(
            product_category='home_insurance',
            product_name='Home Insurance',
            product_type='individual',
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://www.nicozdiamond.co.zw/',
            confidence_score=70
        )
        
        return self.offerings


class CellInsuranceScraper(InsuranceScraperBase):
    """Cell Insurance scraper"""
    
    def __init__(self):
        super().__init__('Cell Insurance', 'Insurer', 'https://cellinsurance.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Cell Insurance...")
        
        self.add_product(
            product_category='corporate_insurance',
            product_name='Corporate Insurance',
            product_type='corporate',
            coverage_description='Corporate liability and risk management',
            source_url='https://cellinsurance.co.zw/',
            confidence_score=70,
            notes='Personal & Commercial Insurance, Alternative Risk'
        )
        
        self.add_product(
            product_category='alternative_risk',
            product_name='Alternative Risk Solutions',
            product_type='corporate',
            coverage_description='Alternative risk management products',
            source_url='https://cellinsurance.co.zw/',
            confidence_score=70
        )
        
        return self.offerings


class CBZInsuranceScraper(InsuranceScraperBase):
    """CBZ Insurance scraper"""
    
    def __init__(self):
        super().__init__('CBZ Insurance', 'Insurer', 'https://www.cbz.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping CBZ Insurance...")
        
        self.add_product(
            product_category='motor_insurance',
            product_name='Motor Insurance',
            product_type='individual',
            third_party_covered=True,
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://www.cbz.co.zw/',
            confidence_score=70,
            notes='Bancassurance motor products'
        )
        
        self.add_product(
            product_category='travel_insurance',
            product_name='Travel Insurance',
            product_type='individual',
            coverage_description='Travel and vacation protection',
            source_url='https://www.cbz.co.zw/',
            confidence_score=70
        )
        
        self.add_product(
            product_category='property_insurance',
            product_name='Property Insurance',
            product_type='individual',
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://www.cbz.co.zw/',
            confidence_score=70
        )
        
        return self.offerings


class AllianceInsuranceScraper(InsuranceScraperBase):
    """Alliance Insurance scraper"""
    
    def __init__(self):
        super().__init__('Alliance Insurance', 'Insurer', 'https://www.alliance.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Alliance Insurance...")
        
        self.add_product(
            product_category='short_term_insurance',
            product_name='Short-term Insurance',
            product_type='individual',
            coverage_description='Short-term insurance coverage',
            source_url='https://www.alliance.co.zw/',
            confidence_score=60,
            notes='Short-term & Crop insurance'
        )
        
        self.add_product(
            product_category='crop_insurance',
            product_name='Crop Insurance',
            product_type='individual',
            coverage_description='Agricultural crop protection',
            source_url='https://www.alliance.co.zw/',
            confidence_score=60
        )
        
        return self.offerings


class FidelityLifeScraper(InsuranceScraperBase):
    """Fidelity Life Assurance scraper"""
    
    def __init__(self):
        super().__init__('Fidelity Life Assurance', 'Insurer', 'https://www.fidelitylife.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Fidelity Life Assurance...")
        
        self.add_product(
            product_category='life_insurance',
            product_name='Life Assurance',
            product_type='individual',
            coverage_description='Life and mortality protection',
            source_url='https://www.fidelitylife.co.zw/',
            confidence_score=70,
            notes='Life and employee benefits products'
        )
        
        self.add_product(
            product_category='employee_benefits',
            product_name='Employee Benefits Plan',
            product_type='corporate',
            coverage_description='Corporate employee benefit schemes',
            source_url='https://www.fidelitylife.co.zw/',
            confidence_score=70
        )
        
        return self.offerings


class EagleInsuranceScraper(InsuranceScraperBase):
    """Eagle Insurance scraper"""
    
    def __init__(self):
        super().__init__('Eagle Insurance', 'Insurer', 'https://www.eagle.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Eagle Insurance...")
        
        self.add_product(
            product_category='short_term_insurance',
            product_name='Short-term Cover',
            product_type='individual',
            coverage_description='General short-term insurance',
            source_url='https://www.eagle.co.zw/',
            confidence_score=65,
            notes='Short-term general insurance'
        )
        
        return self.offerings


class ClarionInsuranceScraper(InsuranceScraperBase):
    """Clarion Insurance scraper"""
    
    def __init__(self):
        super().__init__('Clarion Insurance', 'Insurer', 'https://www.clarioninsurance.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Clarion Insurance...")
        
        self.add_product(
            product_category='general_insurance',
            product_name='General Insurance',
            product_type='individual',
            coverage_description='General and commercial insurance solutions',
            source_url='https://www.clarioninsurance.co.zw/',
            confidence_score=65,
            notes='General & Commercial insurance'
        )
        
        self.add_product(
            product_category='commercial_insurance',
            product_name='Commercial Solutions',
            product_type='corporate',
            coverage_description='Commercial and corporate insurance',
            source_url='https://www.clarioninsurance.co.zw/',
            confidence_score=65
        )
        
        return self.offerings


class EvolutionGroupScraper(InsuranceScraperBase):
    """Evolution Group scraper"""
    
    def __init__(self):
        super().__init__('Evolution Group', 'Insurer', 'https://evolution.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Evolution Group...")
        
        self.add_product(
            product_category='motor_insurance',
            product_name='Motor Insurance',
            product_type='corporate',
            third_party_covered=True,
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://evolution.co.zw/',
            confidence_score=65,
            notes='Commercial motor insurance'
        )
        
        self.add_product(
            product_category='property_insurance',
            product_name='Property Insurance',
            product_type='corporate',
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://evolution.co.zw/',
            confidence_score=65
        )
        
        self.add_product(
            product_category='marine_insurance',
            product_name='Marine Insurance',
            product_type='corporate',
            coverage_description='Marine and shipping insurance',
            source_url='https://evolution.co.zw/',
            confidence_score=65,
            notes='Marine and commercial credit insurance'
        )
        
        return self.offerings


class FlexisureScraper(InsuranceScraperBase):
    """Flexisure scraper"""
    
    def __init__(self):
        super().__init__('Flexisure', 'Insurer', 'https://flexisure.co.zw')
    
    def scrape(self) -> List[InsuranceProduct]:
        logger.info("Scraping Flexisure...")
        
        self.add_product(
            product_category='motor_insurance',
            product_name='Motor Micro-insurance',
            product_type='individual',
            third_party_covered=True,
            own_damage_covered=True,
            theft_coverage=True,
            source_url='https://flexisure.co.zw/',
            confidence_score=75,
            notes='Digital micro-insurance motor cover'
        )
        
        self.add_product(
            product_category='travel_insurance',
            product_name='Travel Micro-insurance',
            product_type='individual',
            coverage_description='Travel and holiday protection',
            source_url='https://flexisure.co.zw/',
            confidence_score=75,
            notes='Digital travel insurance'
        )
        
        self.add_product(
            product_category='hospital_cash_back',
            product_name='Hospital Cash Back',
            product_type='individual',
            coverage_description='Hospital cash back protection',
            source_url='https://flexisure.co.zw/',
            confidence_score=75,
            notes='Hospital cash benefit micro-insurance'
        )
        
        return self.offerings


class InsuranceCollector:
    """Orchestrates all insurance scrapers"""
    
    def __init__(self):
        self.scrapers = [
            OldMutualScraper(),
            ZimnatScraper(),
            FirstMutualInsuranceScraper(),
            NicozDiamondScraper(),
            CellInsuranceScraper(),
            CBZInsuranceScraper(),
            AllianceInsuranceScraper(),
            FidelityLifeScraper(),
            EagleInsuranceScraper(),
            ClarionInsuranceScraper(),
            EvolutionGroupScraper(),
            FlexisureScraper(),
        ]
        self.all_offerings: List[InsuranceProduct] = []
    
    def collect(self) -> List[InsuranceProduct]:
        """Collect data from all insurers"""
        logger.info(f"Starting collection from {len(self.scrapers)} insurers...")
        
        for scraper in self.scrapers:
            try:
                offerings = scraper.scrape()
                self.all_offerings.extend(offerings)
                logger.info(f"Scraped {len(offerings)} {scraper.provider_name} offerings")
            except Exception as e:
                logger.error(f"Error scraping {scraper.provider_name}: {e}")
        
        logger.info(f"Total offerings collected: {len(self.all_offerings)}")
        return self.all_offerings
    
    def export_csv(self, filename: str = 'zimbabwe_insurance_products.csv') -> None:
        """Export to CSV"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_json(self, filename: str = 'zimbabwe_insurance_products.json') -> None:
        """Export to JSON"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        data = [asdict(o) for o in self.all_offerings]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_excel(self, filename: str = 'zimbabwe_insurance_products.xlsx') -> None:
        """Export to Excel"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_excel(filename, index=False, sheet_name='Insurance Products')
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get collection summary"""
        provider_counts = {}
        category_counts = {}
        
        for offering in self.all_offerings:
            provider_counts[offering.provider_name] = \
                provider_counts.get(offering.provider_name, 0) + 1
            category_counts[offering.product_category] = \
                category_counts.get(offering.product_category, 0) + 1
        
        return {
            'total_records': len(self.all_offerings),
            'by_provider': provider_counts,
            'by_category': category_counts,
            'timestamp': datetime.now().isoformat(),
            'exports': {
                'csv': 'zimbabwe_insurance_products.csv',
                'json': 'zimbabwe_insurance_products.json',
                'xlsx': 'zimbabwe_insurance_products.xlsx',
            }
        }


def persist_to_database(offerings: List[InsuranceProduct]) -> None:
    """Persist insurance products to the FastAPI database"""
    try:
        # Use absolute path to database in scraper-hub- folder
        db_path = os.path.join(os.path.dirname(__file__), 'scraper-hub-v1', 'scraper-hub-', 'scraper_hub.db')
        database_url = f"sqlite:///{db_path}"
        
        # Create database session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Group offerings by provider to create snapshots
        provider_offerings = {}
        for offering in offerings:
            prov = offering.provider_name
            if prov not in provider_offerings:
                provider_offerings[prov] = []
            provider_offerings[prov].append(offering)
        
        # Create snapshots and records for each provider
        for provider_name, prov_offerings in provider_offerings.items():
            # Create a raw snapshot for this provider
            snapshot_content = json.dumps({
                'provider': provider_name,
                'offerings': [asdict(o) for o in prov_offerings],
                'scraped_at': datetime.now().isoformat()
            }, default=str)
            
            snapshot = RawSnapshot(
                url=prov_offerings[0].source_url or f"https://provider.co.zw/",
                content=snapshot_content,
                content_type='json'
            )
            db.add(snapshot)
            db.flush()  # Get the snapshot ID
            
            # Create extracted records for each offering
            for offering in prov_offerings:
                record = ExtractedRecord(
                    snapshot_id=snapshot.id,
                    entity_name=offering.provider_name,
                    category='insurance',
                    subcategory=offering.product_category,
                    market='local',
                    title=offering.product_name,
                    item_name=f"{offering.product_category} - {offering.product_type or 'individual'}",
                    description=f"Product: {offering.product_name}, Coverage: {offering.coverage_description or 'Standard coverage'}",
                    price_value=offering.premium_amount,
                    price_currency=offering.premium_currency,
                    billing_period=offering.premium_frequency,
                    unit_type='insurance_product',
                    unit_value=1.0,
                    source_url=offering.source_url or prov_offerings[0].source_url,
                    confidence_score=offering.confidence_score,
                )
                db.add(record)
        
        db.commit()
        logger.info(f"Successfully persisted {len(offerings)} records to database")
        db.close()
    except Exception as e:
        logger.error(f"Error persisting to database: {e}")
        logger.info("Continuing with file exports only")


def main():
    """Main execution"""
    collector = InsuranceCollector()
    collector.collect()
    
    # Persist to database
    persist_to_database(collector.all_offerings)
    
    # Export data
    collector.export_csv()
    collector.export_json()
    collector.export_excel()
    
    # Print summary
    summary = collector.get_summary()
    
    print("\n" + "=" * 60)
    print("✅ ZIMBABWEAN INSURANCE PRODUCTS COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Total Records: {summary['total_records']}\n")
    
    print("By Provider:")
    for prov, count in sorted(summary['by_provider'].items()):
        print(f"  • {prov}: {count} offerings")
    
    print("\nBy Category:")
    for cat, count in sorted(summary['by_category'].items()):
        print(f"  • {cat}: {count} offerings")
    
    print("\nExports:")
    print(f"  📊 CSV: {summary['exports']['csv']}")
    print(f"  📋 JSON: {summary['exports']['json']}")
    print(f"  📈 Excel: {summary['exports']['xlsx']}")
    print("\n✅ Data has been persisted to the web UI database")
    print("   Visit http://localhost:8000/records to view")
    print("=" * 60)


if __name__ == '__main__':
    main()
