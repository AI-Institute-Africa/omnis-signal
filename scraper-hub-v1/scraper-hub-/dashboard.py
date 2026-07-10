#!/usr/bin/env python3
"""
Scraper Hub Dashboard and Monitoring Script

Provides real-time monitoring and statistics for the data extraction system.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.ERROR)

from app.db.session import SessionLocal
from app.db.models import Source, SourcePage, ExtractedRecord, RawSnapshot
from sqlalchemy import func, and_


class ScraperDashboard:
    def __init__(self):
        self.db = SessionLocal()
    
    def close(self):
        self.db.close()
    
    def get_basic_stats(self):
        """Get basic system statistics."""
        return {
            'total_sources': self.db.query(Source).count(),
            'total_pages': self.db.query(SourcePage).count(),
            'enabled_pages': self.db.query(SourcePage).filter(SourcePage.enabled == True).count(),
            'total_snapshots': self.db.query(RawSnapshot).count(),
            'total_records': self.db.query(ExtractedRecord).count(),
            'records_with_prices': self.db.query(ExtractedRecord).filter(
                ExtractedRecord.price_value.isnot(None)
            ).count(),
        }
    
    def get_recent_activity(self, hours=24):
        """Get recent scraping activity."""
        since = datetime.now() - timedelta(hours=hours)
        
        recent_snapshots = self.db.query(RawSnapshot).filter(
            RawSnapshot.captured_at >= since
        ).count()
        
        recent_records = self.db.query(ExtractedRecord).filter(
            ExtractedRecord.captured_at >= since
        ).count()
        
        return {
            'recent_snapshots': recent_snapshots,
            'recent_records': recent_records,
            'hours': hours
        }
    
    def get_category_breakdown(self):
        """Get records by category."""
        results = self.db.query(
            ExtractedRecord.category,
            func.count(ExtractedRecord.id).label('total'),
            func.count(func.nullif(ExtractedRecord.price_value, None)).label('with_price'),
            func.avg(ExtractedRecord.price_value).label('avg_price'),
            func.min(ExtractedRecord.price_value).label('min_price'),
            func.max(ExtractedRecord.price_value).label('max_price'),
        ).group_by(ExtractedRecord.category).order_by(
            func.count(ExtractedRecord.id).desc()
        ).all()
        
        return [
            {
                'category': r[0],
                'total': r[1],
                'with_price': r[2],
                'avg_price': float(r[3]) if r[3] else None,
                'min_price': float(r[4]) if r[4] else None,
                'max_price': float(r[5]) if r[5] else None,
            }
            for r in results
        ]
    
    def get_top_entities(self, limit=10):
        """Get top entities by record count."""
        results = self.db.query(
            ExtractedRecord.entity_name,
            func.count(ExtractedRecord.id).label('count'),
            func.count(func.nullif(ExtractedRecord.price_value, None)).label('with_price'),
            func.avg(ExtractedRecord.price_value).label('avg_price'),
        ).filter(ExtractedRecord.entity_name.isnot(None)).group_by(
            ExtractedRecord.entity_name
        ).order_by(
            func.count(ExtractedRecord.id).desc()
        ).limit(limit).all()
        
        return [
            {
                'entity': r[0],
                'records': r[1],
                'with_price': r[2],
                'avg_price': float(r[3]) if r[3] else None,
            }
            for r in results
        ]
    
    def get_quality_metrics(self):
        """Get data quality metrics."""
        total = self.db.query(ExtractedRecord).count()
        
        with_price = self.db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).count()
        
        with_description = self.db.query(ExtractedRecord).filter(
            ExtractedRecord.description.isnot(None)
        ).count()
        
        good_quality = self.db.query(ExtractedRecord).filter(
            and_(
                ExtractedRecord.price_value.isnot(None),
                ExtractedRecord.confidence_score >= 0.75
            )
        ).count()
        
        return {
            'total_records': total,
            'completeness': {
                'with_price': round(100 * with_price / max(1, total), 1),
                'with_description': round(100 * with_description / max(1, total), 1),
            },
            'quality': {
                'good_quality': good_quality,
                'good_quality_percent': round(100 * good_quality / max(1, total), 1),
            }
        }
    
    def get_source_status(self, limit=10):
        """Get source scraping status."""
        results = self.db.query(
            Source.name,
            Source.category,
            func.count(SourcePage.id).label('pages'),
            func.sum(func.case((SourcePage.enabled == True, 1), else_=0)).label('enabled_pages'),
            func.count(RawSnapshot.id).label('snapshots'),
            func.count(ExtractedRecord.id).label('records'),
        ).outerjoin(SourcePage).outerjoin(RawSnapshot).outerjoin(ExtractedRecord).group_by(
            Source.id
        ).order_by(
            func.count(ExtractedRecord.id).desc()
        ).limit(limit).all()
        
        return [
            {
                'source': r[0],
                'category': r[1],
                'pages': r[2] or 0,
                'enabled': r[3] or 0,
                'snapshots': r[4] or 0,
                'records': r[5] or 0,
            }
            for r in results
        ]


def print_dashboard():
    """Print an interactive dashboard."""
    dashboard = ScraperDashboard()
    
    try:
        stats = dashboard.get_basic_stats()
        activity = dashboard.get_recent_activity()
        quality = dashboard.get_quality_metrics()
        categories = dashboard.get_category_breakdown()
        entities = dashboard.get_top_entities(10)
        sources = dashboard.get_source_status(10)
        
        # Header
        print("\n" + "="*80)
        print("SCRAPER HUB - REAL-TIME DASHBOARD")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Overall Stats
        print("📊 OVERALL STATISTICS")
        print("-" * 80)
        print(f"  Sources:              {stats['total_sources']:,}")
        print(f"  Pages:                {stats['total_pages']:,} (enabled: {stats['enabled_pages']:,})")
        print(f"  Snapshots:            {stats['total_snapshots']:,}")
        print(f"  Extracted Records:    {stats['total_records']:,}")
        print(f"  Records w/ Price:     {stats['records_with_prices']:,} ({100*stats['records_with_prices']/max(1,stats['total_records']):.1f}%)")
        
        # Recent Activity
        print(f"\n📈 RECENT ACTIVITY (Last {activity['hours']} hours)")
        print("-" * 80)
        print(f"  New Snapshots:        {activity['recent_snapshots']:,}")
        print(f"  New Records:          {activity['recent_records']:,}")
        
        # Quality Metrics
        print(f"\n✅ DATA QUALITY METRICS")
        print("-" * 80)
        print(f"  Completeness:")
        print(f"    - With Price:       {quality['completeness']['with_price']:.1f}%")
        print(f"    - With Description: {quality['completeness']['with_description']:.1f}%")
        print(f"  Quality (High Confidence):")
        print(f"    - Good Quality:     {quality['quality']['good_quality']:,} ({quality['quality']['good_quality_percent']:.1f}%)")
        
        # By Category
        print(f"\n🏷️  RECORDS BY CATEGORY")
        print("-" * 80)
        print(f"  {'Category':<20} {'Total':>10} {'w/Price':>10} {'Avg Price':>12} {'Range':>20}")
        print("-" * 80)
        for cat in categories[:10]:
            price_pct = 100 * cat['with_price'] / max(1, cat['total'])
            range_str = f"${cat['min_price']:.2f}-${cat['max_price']:.2f}" if cat['min_price'] else "N/A"
            price_str = f"${cat['avg_price']:.2f}" if cat['avg_price'] else "N/A"
            print(f"  {cat['category']:<20} {cat['total']:>10,} {cat['with_price']:>9,}% {price_str:>12} {range_str:>20}")
        
        # Top Entities
        print(f"\n🏢 TOP ENTITIES (by records)")
        print("-" * 80)
        print(f"  {'Entity':<35} {'Records':>12} {'w/Price':>10} {'Avg Price':>12}")
        print("-" * 80)
        for ent in entities[:10]:
            price_pct = 100 * ent['with_price'] / max(1, ent['records'])
            price_str = f"${ent['avg_price']:.2f}" if ent['avg_price'] else "N/A"
            print(f"  {ent['entity']:<35} {ent['records']:>12,} {ent['with_price']:>9,}% {price_str:>12}")
        
        # Top Sources
        print(f"\n🌐 TOP SOURCES (by records)")
        print("-" * 80)
        print(f"  {'Source':<30} {'Category':<15} {'Snapshots':>10} {'Records':>10}")
        print("-" * 80)
        for src in sources[:10]:
            print(f"  {src['source']:<30} {src['category']:<15} {src['snapshots']:>10,} {src['records']:>10,}")
        
        print("\n" + "="*80 + "\n")
        
        # Tips
        print("💡 NEXT STEPS:")
        print("  • Run: python finalize_system.py --scrape-batch to scrape more sources")
        print("  • Run: python finalize_system.py --export-csv to export data to CSV")
        print("  • Run: python finalize_system.py --export-json to export data to JSON")
        print("  • Visit: http://localhost:8000 for the web dashboard")
        print()
        
    finally:
        dashboard.close()


if __name__ == '__main__':
    print_dashboard()
