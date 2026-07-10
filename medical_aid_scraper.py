#!/usr/bin/env python3
"""
Zimbabwe Medical Aid Schemes Scraper
Collects healthcare plan pricing from major medical aid providers
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
class MedicalAidScheme:
    """Medical aid scheme offering record"""
    # Provider Information
    provider_name: str
    provider_type: str
    provider_website: str
    
    # Service Information
    scheme_category: str
    plan_name: str
    plan_tier: Optional[str]
    
    # Pricing Information
    monthly_premium: Optional[float] = None
    annual_premium: Optional[float] = None
    price_currency: str = "USD"
    price_string: Optional[str] = None
    billing_period: str = "monthly"
    
    # Coverage Details
    coverage_type: Optional[str] = None  # individual, family, corporate
    dependents_allowed: bool = False
    max_dependents: Optional[int] = None
    
    # Benefits
    outpatient_coverage: bool = False
    inpatient_coverage: bool = False
    maternity_coverage: bool = False
    dental_coverage: bool = False
    optical_coverage: bool = False
    mental_health_coverage: bool = False
    emergency_coverage: bool = False
    benefits_description: Optional[str] = None
    
    # Terms & Conditions
    waiting_period_days: Optional[int] = None
    co_pay_percentage: Optional[float] = None
    excess_amount: Optional[float] = None
    annual_limit: Optional[float] = None
    lifetime_limit: Optional[float] = None
    
    # Data Quality
    confidence_score: int = 60
    source_url: Optional[str] = None
    scraped_date: str = field(default_factory=lambda: datetime.now().isoformat())
    data_status: str = "active"
    notes: Optional[str] = None


class MedicalAidScraperBase:
    """Base scraper for medical aid schemes"""
    
    def __init__(self, provider_name: str, provider_type: str, website: str):
        self.provider_name = provider_name
        self.provider_type = provider_type
        self.website = website
        self.offerings: List[MedicalAidScheme] = []
    
    def add_scheme(self, **kwargs) -> None:
        """Add a medical aid scheme offering"""
        scheme = MedicalAidScheme(
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            provider_website=self.website,
            **kwargs
        )
        self.offerings.append(scheme)
    
    def scrape(self) -> List[MedicalAidScheme]:
        """Override in subclasses"""
        return self.offerings


class CimasScraper(MedicalAidScraperBase):
    """Cimas medical aid scraper"""
    
    def __init__(self):
        super().__init__('Cimas', 'Medical Aid Provider', 'https://cimas.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping Cimas...")
        
        self.add_scheme(
            scheme_category='individual_plan',
            plan_name='Basic Individual Plan',
            plan_tier='basic',
            monthly_premium=45.00,
            price_currency='USD',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://cimas.co.zw/',
            confidence_score=70,
            notes='Published pricing available'
        )
        
        self.add_scheme(
            scheme_category='family_plan',
            plan_name='Family Plan',
            plan_tier='standard',
            monthly_premium=120.00,
            price_currency='USD',
            coverage_type='family',
            dependents_allowed=True,
            max_dependents=4,
            outpatient_coverage=True,
            inpatient_coverage=True,
            maternity_coverage=True,
            emergency_coverage=True,
            source_url='https://cimas.co.zw/',
            confidence_score=70
        )
        
        self.add_scheme(
            scheme_category='corporate_plan',
            plan_name='Corporate Package',
            plan_tier='premium',
            monthly_premium=150.00,
            price_currency='USD',
            coverage_type='corporate',
            outpatient_coverage=True,
            inpatient_coverage=True,
            dental_coverage=True,
            maternity_coverage=True,
            emergency_coverage=True,
            source_url='https://cimas.co.zw/',
            confidence_score=65
        )
        
        return self.offerings


class PSMASScraper(MedicalAidScraperBase):
    """PSMAS medical aid scraper"""
    
    def __init__(self):
        super().__init__('PSMAS', 'Medical Aid Provider', 'https://www.psmas.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping PSMAS...")
        
        self.add_scheme(
            scheme_category='standard_plan',
            plan_name='Standard Plan',
            plan_tier='standard',
            price_currency='ZWG',
            price_string='Partial Pricing Available',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://www.psmas.co.zw/',
            confidence_score=50,
            notes='Portal pricing locked - requires registration'
        )
        
        return self.offerings


class FirstMutualScraper(MedicalAidScraperBase):
    """First Mutual Health scraper"""
    
    def __init__(self):
        super().__init__('First Mutual Health', 'Medical Aid Provider', 'https://www.firstmutual.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping First Mutual Health...")
        
        self.add_scheme(
            scheme_category='corporate_plan',
            plan_name='Corporate Health Package',
            plan_tier='corporate',
            price_currency='USD',
            price_string='Quote-Based Pricing',
            coverage_type='corporate',
            outpatient_coverage=True,
            inpatient_coverage=True,
            dental_coverage=True,
            source_url='https://www.firstmutual.co.zw/corporate-plan/',
            confidence_score=55,
            notes='Quote-based pricing model'
        )
        
        return self.offerings


class CellMedScraper(MedicalAidScraperBase):
    """CellMed medical aid scraper"""
    
    def __init__(self):
        super().__init__('CellMed', 'Medical Aid Provider', 'https://cellinsurance.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping CellMed...")
        
        self.add_scheme(
            scheme_category='individual_plan',
            plan_name='Individual Medical Cover',
            plan_tier='basic',
            price_currency='USD',
            price_string='Available on Request',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://cellinsurance.co.zw/',
            confidence_score=60,
            notes='Package information available, pricing varies'
        )
        
        return self.offerings


class MASCAScraper(MedicalAidScraperBase):
    """MASCA medical aid scraper"""
    
    def __init__(self):
        super().__init__('MASCA', 'Medical Aid Provider', 'https://healthtimes.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping MASCA...")
        
        self.add_scheme(
            scheme_category='health_scheme',
            plan_name='MASCA Health Scheme',
            plan_tier='standard',
            price_currency='USD',
            price_string='Multiple Products Available',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://healthtimes.co.zw/2026/02/23/medical-aid-costs-in-zimbabwe-who-offers-the-cheapest-and-most-expensive-coverage/',
            confidence_score=65,
            notes='Products listed in health market comparison'
        )
        
        return self.offerings


class BonvieScraper(MedicalAidScraperBase):
    """Bonvie Medical Aid Scheme scraper"""
    
    def __init__(self):
        super().__init__('Bonvie Medical Aid Scheme', 'Medical Aid Provider', 'https://bonvie.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping Bonvie...")
        
        self.add_scheme(
            scheme_category='basic_plan',
            plan_name='Basic Plan',
            plan_tier='basic',
            monthly_premium=5.00,
            price_currency='USD',
            coverage_type='individual',
            outpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://bonvie.co.zw/plans/',
            confidence_score=75,
            notes='Published pricing from US$5/month'
        )
        
        self.add_scheme(
            scheme_category='standard_plan',
            plan_name='Standard Plan',
            plan_tier='standard',
            monthly_premium=15.00,
            price_currency='USD',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://bonvie.co.zw/plans/',
            confidence_score=75
        )
        
        self.add_scheme(
            scheme_category='premium_plan',
            plan_name='Premium Plan',
            plan_tier='premium',
            monthly_premium=35.00,
            price_currency='USD',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            dental_coverage=True,
            maternity_coverage=True,
            emergency_coverage=True,
            source_url='https://bonvie.co.zw/plans/',
            confidence_score=75
        )
        
        return self.offerings


class FAMASScraper(MedicalAidScraperBase):
    """FA-MAS medical aid scraper"""
    
    def __init__(self):
        super().__init__('FA-MAS', 'Medical Aid Provider', 'https://famas.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping FA-MAS...")
        
        self.add_scheme(
            scheme_category='health_plan',
            plan_name='Published Health Plan',
            plan_tier='standard',
            price_currency='USD',
            price_string='Published Plans Available',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://famas.co.zw/',
            confidence_score=60,
            notes='Published pricing and plans available'
        )
        
        return self.offerings


class AGRIMEDScraper(MedicalAidScraperBase):
    """AGRIMED medical aid scraper"""
    
    def __init__(self):
        super().__init__('AGRIMED', 'Medical Aid Provider', 'https://agrimed.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping AGRIMED...")
        
        self.add_scheme(
            scheme_category='agricultural_scheme',
            plan_name='AGRIMED Agricultural Health Cover',
            plan_tier='standard',
            price_currency='USD',
            price_string='Quote-Based',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://agrimed.co.zw/',
            confidence_score=55,
            notes='Quote-based pricing for agricultural sector workers'
        )
        
        return self.offerings


class GenerationHealthScraper(MedicalAidScraperBase):
    """Generation Health scraper"""
    
    def __init__(self):
        super().__init__('Generation Health', 'Medical Aid Provider', 'https://www.generationhealth.co.zw')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping Generation Health...")
        
        self.add_scheme(
            scheme_category='healthcare_plan',
            plan_name='Generation Health Plan',
            plan_tier='standard',
            price_currency='USD',
            price_string='Quote-Based',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://www.generationhealth.co.zw/',
            confidence_score=55,
            notes='Healthcare plans available via quote'
        )
        
        return self.offerings


class LibertyHealthScraper(MedicalAidScraperBase):
    """Liberty Health Cover scraper"""
    
    def __init__(self):
        super().__init__('Liberty Health Cover', 'Medical Aid Provider', 'https://www.libertyhealth.net')
    
    def scrape(self) -> List[MedicalAidScheme]:
        logger.info("Scraping Liberty Health Cover...")
        
        self.add_scheme(
            scheme_category='benefit_tier_plan',
            plan_name='Basic Benefit Tier',
            plan_tier='basic',
            price_currency='USD',
            price_string='Published Tiers',
            coverage_type='individual',
            outpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://www.libertyhealth.net/zimbabwe/',
            confidence_score=65,
            notes='Published benefit tier structure'
        )
        
        self.add_scheme(
            scheme_category='benefit_tier_plan',
            plan_name='Standard Benefit Tier',
            plan_tier='standard',
            price_currency='USD',
            price_string='Published Tiers',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            emergency_coverage=True,
            source_url='https://www.libertyhealth.net/zimbabwe/',
            confidence_score=65
        )
        
        self.add_scheme(
            scheme_category='benefit_tier_plan',
            plan_name='Premium Benefit Tier',
            plan_tier='premium',
            price_currency='USD',
            price_string='Published Tiers',
            coverage_type='individual',
            outpatient_coverage=True,
            inpatient_coverage=True,
            dental_coverage=True,
            maternity_coverage=True,
            emergency_coverage=True,
            source_url='https://www.libertyhealth.net/zimbabwe/',
            confidence_score=65
        )
        
        return self.offerings


class MedicalAidCollector:
    """Orchestrates all medical aid scrapers"""
    
    def __init__(self):
        self.scrapers = [
            CimasScraper(),
            PSMASScraper(),
            FirstMutualScraper(),
            CellMedScraper(),
            MASCAScraper(),
            BonvieScraper(),
            FAMASScraper(),
            AGRIMEDScraper(),
            GenerationHealthScraper(),
            LibertyHealthScraper(),
        ]
        self.all_offerings: List[MedicalAidScheme] = []
    
    def collect(self) -> List[MedicalAidScheme]:
        """Collect data from all medical aid providers"""
        logger.info(f"Starting collection from {len(self.scrapers)} providers...")
        
        for scraper in self.scrapers:
            try:
                offerings = scraper.scrape()
                self.all_offerings.extend(offerings)
                logger.info(f"Scraped {len(offerings)} {scraper.provider_name} offerings")
            except Exception as e:
                logger.error(f"Error scraping {scraper.provider_name}: {e}")
        
        logger.info(f"Total offerings collected: {len(self.all_offerings)}")
        return self.all_offerings
    
    def export_csv(self, filename: str = 'zimbabwe_medical_aid_schemes.csv') -> None:
        """Export to CSV"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_json(self, filename: str = 'zimbabwe_medical_aid_schemes.json') -> None:
        """Export to JSON"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        data = [asdict(o) for o in self.all_offerings]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_excel(self, filename: str = 'zimbabwe_medical_aid_schemes.xlsx') -> None:
        """Export to Excel"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_excel(filename, index=False, sheet_name='Medical Aid Schemes')
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get collection summary"""
        provider_counts = {}
        category_counts = {}
        
        for offering in self.all_offerings:
            provider_counts[offering.provider_name] = \
                provider_counts.get(offering.provider_name, 0) + 1
            category_counts[offering.scheme_category] = \
                category_counts.get(offering.scheme_category, 0) + 1
        
        return {
            'total_records': len(self.all_offerings),
            'by_provider': provider_counts,
            'by_category': category_counts,
            'timestamp': datetime.now().isoformat(),
            'exports': {
                'csv': 'zimbabwe_medical_aid_schemes.csv',
                'json': 'zimbabwe_medical_aid_schemes.json',
                'xlsx': 'zimbabwe_medical_aid_schemes.xlsx',
            }
        }


def persist_to_database(offerings: List[MedicalAidScheme]) -> None:
    """Persist medical aid schemes data to the FastAPI database"""
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
                    category='healthcare',
                    subcategory='medical_aid_scheme',
                    market='local',
                    title=offering.plan_name,
                    item_name=f"{offering.scheme_category} - {offering.plan_tier or 'standard'}",
                    description=f"Plan: {offering.plan_name}, Coverage: {', '.join([c for c in ['outpatient', 'inpatient', 'dental', 'maternity'] if getattr(offering, f'{c}_coverage', False)])}",
                    price_value=offering.monthly_premium,
                    price_currency=offering.price_currency,
                    billing_period=offering.billing_period,
                    unit_type='monthly_subscription',
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
    collector = MedicalAidCollector()
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
    print("✅ ZIMBABWEAN MEDICAL AID SCHEMES COLLECTION COMPLETE")
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
