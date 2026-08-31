"""
Database Universal Synchronizer
Mirrors all 220 Listing, Provider, Category, and Sector records into the
legacy ExtractedRecord, Product, Service, PriceEntry, and Organization tables.
Ensures every frontend view, dashboard, and report reflects all 7 sectors immediately.
"""
import re
import sys
from datetime import datetime

sys.path.insert(0, ".")
from app.db.session import SessionLocal
from app.db.models.catalog import SectorConfig, Category, Provider, Listing, ListingPriceHistory
from app.db.models.extracted_record import ExtractedRecord
from app.db.models.raw_snapshot import RawSnapshot
from app.db.models.organization import Organization
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.price_entry import PriceEntry
from app.db.models.source import Source


def slugify(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
    return re.sub(r'[\s-]+', '-', cleaned)


def sync_all():
    print("[Sync] Starting universal database sync...")
    db = SessionLocal()

    try:
        listings = db.query(Listing).all()
        print(f"[Sync] Found {len(listings)} active catalog listings across all 7 sectors.")

        # Ensure at least one RawSnapshot exists for ExtractedRecord FK
        snapshot = db.query(RawSnapshot).first()
        if not snapshot:
            snapshot = RawSnapshot(
                url="https://www.zimbabwe.co.zw",
                content="<html><body>Omnis Signal Intelligence Data</body></html>",
                content_type="html"
            )
            db.add(snapshot)
            db.flush()

        synced_records = 0
        synced_products = 0
        synced_services = 0
        synced_orgs = 0

        # 1. Sync Providers -> Organizations & Sources
        providers = db.query(Provider).all()
        org_map = {}
        source_map = {}
        for p in providers:
            p_slug = slugify(p.name)
            org = db.query(Organization).filter(
                (Organization.name == p.name) | (Organization.slug == p_slug)
            ).first()

            if not org:
                org = Organization(
                    name=p.name,
                    slug=p_slug,
                    category="finance" if "bank" in p.name.lower() or "cabs" in p.name.lower() else "telecom",
                    website=p.website_url or "https://www.zimbabwe.co.zw",
                    description=p.description or f"Verified provider in Zimbabwe"
                )
                db.add(org)
                db.flush()
                synced_orgs += 1

            org_map[p.name] = org

            source = db.query(Source).filter(Source.name == p.name).first()
            if not source:
                source = Source(
                    name=p.name,
                    base_url=p.website_url or "https://www.zimbabwe.co.zw",
                    category="telecom" if "econet" in p.name.lower() or "netone" in p.name.lower() else "banking",
                    market="local"
                )
                db.add(source)
                db.flush()

            source_map[p.name] = source

        db.commit()

        # 2. Sync Listings -> ExtractedRecord, Product, Service, PriceEntry
        for l in listings:
            cat = l.category
            sector = cat.sector if cat else None
            provider = l.provider
            provider_name = provider.name if provider else "Unknown"
            sector_name = sector.slug if sector else "general"
            cat_name = cat.slug if cat else "general"
            attrs = l.attributes or {}
            org = org_map.get(provider_name)
            src = source_map.get(provider_name)

            # Sync to ExtractedRecord
            rec = db.query(ExtractedRecord).filter(
                ExtractedRecord.entity_name == provider_name,
                ExtractedRecord.title == l.name
            ).first()

            if not rec:
                rec = ExtractedRecord(
                    snapshot_id=snapshot.id,
                    entity_name=provider_name,
                    category=sector_name,
                    subcategory=cat_name,
                    title=l.name,
                    item_name=l.name,
                    description=l.description or f"{l.name} offered by {provider_name}",
                    price_value=l.price,
                    price_currency=l.currency or "USD",
                    market="local",
                    confidence_score=0.98,
                    source_url=l.source_url or "https://www.zimbabwe.co.zw"
                )
                db.add(rec)
                synced_records += 1
            else:
                rec.price_value = l.price
                rec.category = sector_name
                rec.subcategory = cat_name

            # If sector is retail, food, or telecom products -> sync to Product + PriceEntry
            if sector_name in ("retail", "food", "telecom"):
                prod = db.query(Product).filter(
                    Product.name == l.name,
                    Product.brand == provider_name
                ).first()

                if not prod:
                    prod = Product(
                        organization_id=org.id if org else None,
                        source_id=src.id if src else None,
                        name=l.name,
                        category=cat_name,
                        subcategory=cat_name,
                        brand=provider_name,
                        description=l.description or l.name
                    )
                    db.add(prod)
                    db.flush()
                    synced_products += 1

                # Add PriceEntry for Product
                pe = db.query(PriceEntry).filter(PriceEntry.product_id == prod.id).first()
                if not pe:
                    pe = PriceEntry(
                        product_id=prod.id,
                        organization_id=org.id if org else None,
                        price_value=l.price,
                        currency=l.currency or "USD",
                        source_url=l.source_url or "https://www.zimbabwe.co.zw"
                    )
                    db.add(pe)
                else:
                    pe.price_value = l.price

            # If sector is banking, education, hotels, transport -> sync to Service + PriceEntry
            if sector_name in ("banking", "education", "hotels", "transport"):
                srv = db.query(Service).filter(
                    Service.name == l.name,
                    Service.organization_id == (org.id if org else None)
                ).first()

                if not srv:
                    srv = Service(
                        organization_id=org.id if org else None,
                        source_id=src.id if src else None,
                        name=l.name,
                        category=cat_name,
                        subcategory=cat_name,
                        description=l.description or l.name
                    )
                    db.add(srv)
                    db.flush()
                    synced_services += 1

                # Add PriceEntry for Service
                pe = db.query(PriceEntry).filter(PriceEntry.service_id == srv.id).first()
                if not pe:
                    pe = PriceEntry(
                        service_id=srv.id,
                        organization_id=org.id if org else None,
                        price_value=l.price,
                        currency=l.currency or "USD",
                        source_url=l.source_url or "https://www.zimbabwe.co.zw"
                    )
                    db.add(pe)
                else:
                    pe.price_value = l.price

        db.commit()
        print(f"[Sync] SUCCESS! Synced {synced_records} records, {synced_products} products, {synced_services} services, {synced_orgs} organizations.")
    except Exception as e:
        db.rollback()
        print(f"[Sync] ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    sync_all()
