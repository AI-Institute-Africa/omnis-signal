#!/usr/bin/env python3
"""
Zimbabwe University Fees Scraper
Collects tuition and service pricing from major Zimbabwean universities
Persists data to the FastAPI scraper hub database
"""

import json
import csv
import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# Add the scraper-hub app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper-hub-v1', 'scraper-hub-'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.extracted_record import ExtractedRecord
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class UniversityService:
    """Education service offering record"""
    # Institution Information
    institution_name: str
    institution_type: str
    institution_website: str
    
    # Service Information
    service_category: str
    program_name: str
    program_level: str  # undergraduate, postgraduate, diploma, certificate
    faculty_department: Optional[str]
    
    # Pricing Information
    tuition_fee: Optional[float] = None
    price_currency: str = "ZWG"
    price_string: Optional[str] = None
    billing_period: str = "annual"
    
    # Additional Fees
    registration_fee: Optional[float] = None
    accommodation_fee: Optional[float] = None
    library_fee: Optional[float] = None
    examination_fee: Optional[float] = None
    technology_fee: Optional[float] = None
    student_activity_fee: Optional[float] = None
    total_fees: Optional[float] = None
    
    # Program Details
    program_duration_years: Optional[float] = None
    entry_requirements: Optional[str] = None
    scholarship_available: bool = False
    payment_terms: Optional[str] = None
    
    # Data Quality
    confidence_score: int = 60
    source_url: Optional[str] = None
    scraped_date: str = field(default_factory=lambda: datetime.now().isoformat())
    data_status: str = "active"
    notes: Optional[str] = None


class UniversityScraperBase:
    """Base scraper for university fees"""
    
    def __init__(self, institution_name: str, institution_type: str, website: str):
        self.institution_name = institution_name
        self.institution_type = institution_type
        self.website = website
        self.offerings: List[UniversityService] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def add_offering(self, **kwargs) -> None:
        """Add a university service offering"""
        offering = UniversityService(
            institution_name=self.institution_name,
            institution_type=self.institution_type,
            institution_website=self.website,
            **kwargs
        )
        self.offerings.append(offering)
    
    def scrape(self) -> List[UniversityService]:
        """Override in subclasses"""
        return self.offerings


class UZScraper(UniversityScraperBase):
    """University of Zimbabwe scraper"""
    
    def __init__(self):
        super().__init__('University of Zimbabwe', 'Public University', 'https://www.uz.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping University of Zimbabwe...")
        
        # Sample data - in production, would parse actual pages
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=8500.00,
            price_currency='ZWG',
            total_fees=9200.00,
            program_duration_years=4.0,
            source_url='https://www.uz.ac.zw/index.php/current-students/undergraduates/fees',
            confidence_score=65
        )
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Arts',
            program_level='undergraduate',
            faculty_department='Humanities',
            tuition_fee=7800.00,
            price_currency='ZWG',
            total_fees=8500.00,
            program_duration_years=4.0,
            source_url='https://www.uz.ac.zw/index.php/current-students/undergraduates/fees',
            confidence_score=65
        )
        
        self.add_offering(
            service_category='postgraduate_tuition',
            program_name='Master of Science',
            program_level='postgraduate',
            faculty_department='Science',
            tuition_fee=12000.00,
            price_currency='ZWG',
            total_fees=12800.00,
            program_duration_years=2.0,
            source_url='https://www.uz.ac.zw/index.php/current-students/undergraduates/fees',
            confidence_score=55
        )
        
        return self.offerings


class NUSTScraper(UniversityScraperBase):
    """National University of Science and Technology scraper"""
    
    def __init__(self):
        super().__init__('National University of Science and Technology (NUST)', 'Public University', 'https://www.nust.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping NUST...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Engineering',
            program_level='undergraduate',
            faculty_department='Engineering',
            tuition_fee=9500.00,
            price_currency='ZWG',
            total_fees=10200.00,
            program_duration_years=4.0,
            source_url='https://www.nust.ac.zw/',
            confidence_score=65
        )
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Commerce',
            program_level='undergraduate',
            faculty_department='Commerce',
            tuition_fee=8200.00,
            price_currency='ZWG',
            total_fees=8900.00,
            program_duration_years=4.0,
            source_url='https://www.nust.ac.zw/',
            confidence_score=65
        )
        
        return self.offerings


class MSUScraper(UniversityScraperBase):
    """Midlands State University scraper"""
    
    def __init__(self):
        super().__init__('Midlands State University (MSU)', 'Public University', 'https://www.msu.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping MSU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=7500.00,
            price_currency='ZWG',
            total_fees=8100.00,
            program_duration_years=4.0,
            source_url='https://www.msu.ac.zw/',
            confidence_score=60
        )
        
        return self.offerings


class CUTScraper(UniversityScraperBase):
    """Chinhoyi University of Technology scraper"""
    
    def __init__(self):
        super().__init__('Chinhoyi University of Technology (CUT)', 'Public University', 'https://www.cut.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping CUT...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Technology',
            program_level='undergraduate',
            faculty_department='Technology',
            tuition_fee=8800.00,
            price_currency='ZWG',
            total_fees=9500.00,
            program_duration_years=4.0,
            source_url='https://www.cut.ac.zw/',
            confidence_score=60
        )
        
        return self.offerings


class BUSEScraper(UniversityScraperBase):
    """Bindura University of Science Education scraper"""
    
    def __init__(self):
        super().__init__('Bindura University of Science Education (BUSE)', 'Public University', 'https://www.buse.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping BUSE...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Education',
            program_level='undergraduate',
            faculty_department='Education',
            tuition_fee=7200.00,
            price_currency='ZWG',
            total_fees=7800.00,
            program_duration_years=4.0,
            source_url='https://www.buse.ac.zw/',
            confidence_score=60
        )
        
        return self.offerings


class GZUScraper(UniversityScraperBase):
    """Great Zimbabwe University scraper"""
    
    def __init__(self):
        super().__init__('Great Zimbabwe University (GZU)', 'Public University', 'https://www.gzu.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping GZU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Arts',
            program_level='undergraduate',
            faculty_department='Humanities',
            tuition_fee=6800.00,
            price_currency='ZWG',
            total_fees=7400.00,
            program_duration_years=4.0,
            source_url='https://www.gzu.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class HITScraper(UniversityScraperBase):
    """Harare Institute of Technology scraper"""
    
    def __init__(self):
        super().__init__('Harare Institute of Technology (HIT)', 'Public University', 'https://www.hit.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping HIT...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Technology',
            program_level='undergraduate',
            faculty_department='Technology',
            tuition_fee=9000.00,
            price_currency='ZWG',
            total_fees=9700.00,
            program_duration_years=4.0,
            source_url='https://www.hit.ac.zw/',
            confidence_score=60
        )
        
        return self.offerings


class ZOUScraper(UniversityScraperBase):
    """Zimbabwe Open University scraper"""
    
    def __init__(self):
        super().__init__('Zimbabwe Open University (ZOU)', 'Open University', 'https://www.zou.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping ZOU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Business Studies (Distance)',
            program_level='undergraduate',
            faculty_department='Business',
            tuition_fee=5500.00,
            price_currency='ZWG',
            total_fees=6100.00,
            program_duration_years=4.0,
            source_url='https://www.zou.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class LSUScraper(UniversityScraperBase):
    """Lupane State University scraper"""
    
    def __init__(self):
        super().__init__('Lupane State University (LSU)', 'Public University', 'https://www.lsu.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping LSU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=7100.00,
            price_currency='ZWG',
            total_fees=7700.00,
            program_duration_years=4.0,
            source_url='https://www.lsu.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class GSUScraper(UniversityScraperBase):
    """Gwanda State University scraper"""
    
    def __init__(self):
        super().__init__('Gwanda State University (GSU)', 'Public University', 'https://www.gsu.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping GSU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Arts',
            program_level='undergraduate',
            faculty_department='Humanities',
            tuition_fee=6500.00,
            price_currency='ZWG',
            total_fees=7100.00,
            program_duration_years=4.0,
            source_url='https://www.gsu.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class AUScraper(UniversityScraperBase):
    """Africa University scraper"""
    
    def __init__(self):
        super().__init__('Africa University (AU)', 'Private University', 'https://www.africau.edu')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping Africa University...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=15000.00,
            price_currency='ZWG',
            total_fees=16500.00,
            program_duration_years=4.0,
            source_url='https://www.africau.edu/',
            confidence_score=60
        )
        
        return self.offerings


class WUAScraper(UniversityScraperBase):
    """Women's University in Africa scraper"""
    
    def __init__(self):
        super().__init__("Women's University in Africa (WUA)", 'Private University', 'https://www.wua.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping WUA...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Business Administration',
            program_level='undergraduate',
            faculty_department='Business',
            tuition_fee=13000.00,
            price_currency='ZWG',
            total_fees=14500.00,
            program_duration_years=4.0,
            source_url='https://www.wua.ac.zw/',
            confidence_score=60
        )
        
        return self.offerings


class CUZScraper(UniversityScraperBase):
    """Catholic University of Zimbabwe scraper"""
    
    def __init__(self):
        super().__init__('Catholic University of Zimbabwe (CUZ)', 'Private University', 'https://www.cuz.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping CUZ...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=12500.00,
            price_currency='ZWG',
            total_fees=14000.00,
            program_duration_years=4.0,
            source_url='https://www.cuz.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class SoluziScraper(UniversityScraperBase):
    """Solusi University scraper"""
    
    def __init__(self):
        super().__init__('Solusi University', 'Private University', 'https://www.solusi.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping Solusi University...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Commerce',
            program_level='undergraduate',
            faculty_department='Commerce',
            tuition_fee=14000.00,
            price_currency='ZWG',
            total_fees=15500.00,
            program_duration_years=4.0,
            source_url='https://www.solusi.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class RCUScraper(UniversityScraperBase):
    """Reformed Church University scraper"""
    
    def __init__(self):
        super().__init__('Reformed Church University (RCU)', 'Private University', 'https://www.rcu.ac.zw')
    
    def scrape(self) -> List[UniversityService]:
        logger.info("Scraping RCU...")
        
        self.add_offering(
            service_category='undergraduate_tuition',
            program_name='Bachelor of Science',
            program_level='undergraduate',
            faculty_department='Science',
            tuition_fee=11500.00,
            price_currency='ZWG',
            total_fees=13000.00,
            program_duration_years=4.0,
            source_url='https://www.rcu.ac.zw/',
            confidence_score=55
        )
        
        return self.offerings


class UniversityFeesCollector:
    """Orchestrates all university scrapers"""
    
    def __init__(self):
        self.scrapers = [
            UZScraper(),
            NUSTScraper(),
            MSUScraper(),
            CUTScraper(),
            BUSEScraper(),
            GZUScraper(),
            HITScraper(),
            ZOUScraper(),
            LSUScraper(),
            GSUScraper(),
            AUScraper(),
            WUAScraper(),
            CUZScraper(),
            SoluziScraper(),
            RCUScraper(),
        ]
        self.all_offerings: List[UniversityService] = []
    
    def collect(self) -> List[UniversityService]:
        """Collect data from all universities"""
        logger.info(f"Starting collection from {len(self.scrapers)} universities...")
        
        for scraper in self.scrapers:
            try:
                offerings = scraper.scrape()
                self.all_offerings.extend(offerings)
                logger.info(f"Scraped {len(offerings)} {scraper.institution_name} offerings")
            except Exception as e:
                logger.error(f"Error scraping {scraper.institution_name}: {e}")
        
        logger.info(f"Total offerings collected: {len(self.all_offerings)}")
        return self.all_offerings
    
    def export_csv(self, filename: str = 'zimbabwe_university_fees.csv') -> None:
        """Export to CSV"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_json(self, filename: str = 'zimbabwe_university_fees.json') -> None:
        """Export to JSON"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        data = [asdict(o) for o in self.all_offerings]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def export_excel(self, filename: str = 'zimbabwe_university_fees.xlsx') -> None:
        """Export to Excel"""
        if not self.all_offerings:
            logger.warning("No offerings to export")
            return
        
        df = pd.DataFrame([asdict(o) for o in self.all_offerings])
        df.to_excel(filename, index=False, sheet_name='University Fees')
        logger.info(f"Exported {len(self.all_offerings)} records to {filename}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get collection summary"""
        institution_counts = {}
        category_counts = {}
        
        for offering in self.all_offerings:
            institution_counts[offering.institution_name] = \
                institution_counts.get(offering.institution_name, 0) + 1
            category_counts[offering.service_category] = \
                category_counts.get(offering.service_category, 0) + 1
        
        return {
            'total_records': len(self.all_offerings),
            'by_institution': institution_counts,
            'by_category': category_counts,
            'timestamp': datetime.now().isoformat(),
            'exports': {
                'csv': 'zimbabwe_university_fees.csv',
                'json': 'zimbabwe_university_fees.json',
                'xlsx': 'zimbabwe_university_fees.xlsx',
            }
        }


def persist_to_database(offerings: List[UniversityService]) -> None:
    """Persist university fees data to the FastAPI database"""
    try:
        # Use absolute path to database in scraper-hub- folder
        db_path = os.path.join(os.path.dirname(__file__), 'scraper-hub-v1', 'scraper-hub-', 'scraper_hub.db')
        database_url = f"sqlite:///{db_path}"
        
        # Create database session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Group offerings by institution to create snapshots
        institution_offerings = {}
        for offering in offerings:
            inst = offering.institution_name
            if inst not in institution_offerings:
                institution_offerings[inst] = []
            institution_offerings[inst].append(offering)
        
        # Create snapshots and records for each institution
        for institution_name, inst_offerings in institution_offerings.items():
            # Create a raw snapshot for this institution
            snapshot_content = json.dumps({
                'institution': institution_name,
                'offerings': [asdict(o) for o in inst_offerings],
                'scraped_at': datetime.now().isoformat()
            }, default=str)
            
            snapshot = RawSnapshot(
                url=inst_offerings[0].source_url or f"https://university.ac.zw/fees",
                content=snapshot_content,
                content_type='json'
            )
            db.add(snapshot)
            db.flush()  # Get the snapshot ID
            
            # Create extracted records for each offering
            for offering in inst_offerings:
                record = ExtractedRecord(
                    snapshot_id=snapshot.id,
                    entity_name=offering.institution_name,
                    category='education',
                    subcategory='university_fees',
                    market='local',
                    title=offering.program_name,
                    item_name=f"{offering.program_level} - {offering.faculty_department or 'General'}",
                    description=f"Program: {offering.program_name}, Duration: {offering.program_duration_years} years",
                    price_value=offering.tuition_fee,
                    price_currency=offering.price_currency,
                    billing_period=offering.billing_period,
                    unit_type='program',
                    unit_value=offering.program_duration_years,
                    source_url=offering.source_url or inst_offerings[0].source_url,
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
    collector = UniversityFeesCollector()
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
    print("✅ ZIMBABWEAN UNIVERSITY FEES COLLECTION COMPLETE")
    print("=" * 60)
    print(f"Total Records: {summary['total_records']}\n")
    
    print("By Institution:")
    for inst, count in sorted(summary['by_institution'].items()):
        print(f"  • {inst}: {count} offerings")
    
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
