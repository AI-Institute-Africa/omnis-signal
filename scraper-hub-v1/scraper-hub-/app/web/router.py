from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.db.session import get_db
from app.db.models import Source, ExtractedRecord, RawSnapshot, Product, Service, PriceEntry
from app.db.models.organization import Organization
from app.db.models.org_change_event import OrgChangeEvent
from app.services.market_data import MarketDataService
from app.data.zimbabwe_organizations import get_categories
from app.scraping.taxonomy import TAXONOMY
from fastapi.responses import StreamingResponse
from typing import Optional
import pandas as pd
import io

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/export/send-4h-report")
@router.get("/export/send-12h-report")
async def trigger_4h_report():
    from app.services.email_reporter import EmailReporterService
    res = EmailReporterService.send_4h_digest_email()
    return res

@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        sources_count = db.query(Source).count()
        records_count = db.query(ExtractedRecord).count()
        snapshots_count = db.query(RawSnapshot).count()
        
        # Category Distribution
        category_results = db.query(ExtractedRecord.category, func.count(ExtractedRecord.id)).group_by(ExtractedRecord.category).all()
        categories = {cat or 'Unknown': count for cat, count in category_results}
            
        # Top Entities
        entity_results = db.query(ExtractedRecord.entity_name, func.count(ExtractedRecord.id)).group_by(ExtractedRecord.entity_name).order_by(func.count(ExtractedRecord.id).desc()).limit(5).all()
        top_entities = {ent or 'Unknown': count for ent, count in entity_results}
        
        # Trends
        raw_recent = db.query(ExtractedRecord).filter(ExtractedRecord.price_value.isnot(None)).order_by(ExtractedRecord.captured_at.desc()).limit(200).all()
        seen_trends = set()
        recent_prices = []
        for r in raw_recent:
            key = (r.entity_name, r.title)
            if key not in seen_trends:
                seen_trends.add(key)
                recent_prices.append(r)
                if len(recent_prices) >= 15:
                    break
        
        price_trends = [{"label": f"{r.entity_name}: {r.title}"[:30], "price": r.price_value, "currency": r.price_currency} for r in recent_prices]
        
        # Market Distribution (Using raw SQL for robustness)
        from sqlalchemy import text
        market_query = text("SELECT market, COUNT(id) FROM extracted_records GROUP BY market")
        market_results = db.execute(market_query).all()
        markets = {m or 'unknown': count for m, count in market_results}
        
        # Real Market Data
        live_rates = MarketDataService.get_live_rates()

        return templates.TemplateResponse(
            request, 
            "dashboard.html", 
            {
                "sources_count": sources_count,
                "records_count": records_count,
                "snapshots_count": snapshots_count,
                "chart_categories": categories,
                "chart_entities": top_entities,
                "chart_markets": markets,
                "price_trends": price_trends,
                "live_rates": live_rates,
                "catalog_link": "/catalog",
                "intelligence_link": "/intelligence"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

@router.get("/sources")
async def sources(request: Request, db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return templates.TemplateResponse(request, "sources.html", {"sources": sources})

@router.get("/manual-scrape")
async def manual_scrape(request: Request):
    return templates.TemplateResponse(request, "manual_scrape.html", {})

@router.get("/data-quality")
async def data_quality(request: Request, db: Session = Depends(get_db)):
    total_count = db.query(ExtractedRecord).count()
    good_count = db.query(ExtractedRecord).filter(
        ExtractedRecord.price_value.isnot(None),
        ExtractedRecord.confidence_score.isnot(None),
        ExtractedRecord.confidence_score >= 0.75,
    ).count()
    partial_count = db.query(ExtractedRecord).filter(
        ExtractedRecord.price_value.isnot(None),
        ExtractedRecord.confidence_score.isnot(None),
        ExtractedRecord.confidence_score >= 0.5,
        ExtractedRecord.confidence_score < 0.75,
    ).count()
    poor_count = db.query(ExtractedRecord).filter(
        or_(
            ExtractedRecord.price_value.is_(None),
            ExtractedRecord.confidence_score.is_(None),
            ExtractedRecord.confidence_score < 0.5,
        )
    ).count()
    category_counts = db.query(ExtractedRecord.category, func.count(ExtractedRecord.id)).group_by(ExtractedRecord.category).all()
    source_categories = [c[0] for c in db.query(Source.category).distinct().all() if c[0]]
    present_categories = [cat for cat, _ in category_counts if cat]
    missing_categories = [cat for cat in source_categories if cat not in present_categories]
    expected_categories = sorted(TAXONOMY.keys())

    return templates.TemplateResponse(request, "data_quality.html", {
        "total_count": total_count,
        "good_count": good_count,
        "partial_count": partial_count,
        "poor_count": poor_count,
        "category_counts": category_counts,
        "missing_categories": missing_categories,
        "expected_categories": expected_categories,
    })

@router.get("/records")
async def records(request: Request, category: str = None, market: str = None, db: Session = Depends(get_db)):
    categories = ["banking", "education", "food", "hotels", "retail", "telecom", "transport", "finance", "groceries", "services", "general"]
    markets = ["local", "global"]

    query = db.query(ExtractedRecord)
    if category:
        query = query.filter(ExtractedRecord.category == category)
    if market:
        query = query.filter(ExtractedRecord.market == market)
        
    all_records = query.order_by(ExtractedRecord.captured_at.desc()).limit(100).all()
    
    seen = set()
    records = []
    for r in all_records:
        key = (r.entity_name, r.title)
        if key not in seen:
            seen.add(key)
            records.append(r)
            if len(records) >= 60:
                break
    
    return templates.TemplateResponse(request, "records.html", {
        "page_title": "Market Intelligence Matrix",
        "page_subtitle": "Structured comparison of services, pricing, and features across time periods.",
        "records": records,
        "categories": sorted(categories),
        "active_category": category,
        "markets": sorted(markets),
        "active_market": market
    })

@router.get("/zimbabwe")
async def zimbabwe_records(request: Request, db: Session = Depends(get_db)):
    query = db.query(ExtractedRecord).filter(
        ExtractedRecord.category == "telecom"
    ).order_by(ExtractedRecord.id.desc())

    all_records = query.limit(60).all()
    seen = set()
    records = []
    for r in all_records:
        key = (r.entity_name, r.title)
        if key not in seen:
            seen.add(key)
            records.append(r)
            if len(records) >= 60:
                break

    return templates.TemplateResponse(request, "records.html", {
        "page_title": "Zimbabwe Telecom Data",
        "page_subtitle": "Latest extracted records for Econet, NetOne, and Telecel Zimbabwe.",
        "records": records,
        "categories": [],
        "active_category": None,
        "markets": [],
        "active_market": None
    })

@router.get("/export/records")
async def export_records(category: str = None, market: str = None, db: Session = Depends(get_db)):
    query = db.query(ExtractedRecord)
    if category:
        query = query.filter(ExtractedRecord.category == category)
    if market:
        query = query.filter(ExtractedRecord.market == market)
        
    all_records = query.order_by(ExtractedRecord.captured_at.desc()).all()
    
    seen = set()
    records = []
    for r in all_records:
        key = (r.entity_name, r.title)
        if key not in seen:
            seen.add(key)
            records.append(r)
            
    # Format data for pandas
    data = []
    for r in records:
        data.append({
            "Entity Name": r.entity_name,
            "Market": r.market,
            "Category": r.category,
            "Subcategory": r.subcategory,
            "Product/Service Title": r.title,
            "Description": r.description,
            "Price": r.price_value,
            "Currency": r.price_currency,
            "Unit Type": r.unit_type,
            "Unit Value": r.unit_value,
            "Billing Period": r.billing_period,
            "Captured At": r.captured_at.strftime('%Y-%m-%d %H:%M:%S') if r.captured_at else None,
            "Source URL": r.source_url
        })
        
    df = pd.DataFrame(data)
    
    # Create in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Extracted Records')
        
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=market_intelligence_export.xlsx"}
    )

@router.get("/organizations")
async def org_list(
    request: Request,
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Organization)
    if category:
        q = q.filter(Organization.category == category)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Organization.name.ilike(term),
                Organization.description.ilike(term),
                Organization.keywords.ilike(term),
            )
        )

    orgs = q.order_by(Organization.category, Organization.name).limit(60).all()
    total = len(orgs)
    cat_counts = {}
    for o in orgs:
        cat_counts[o.category] = cat_counts.get(o.category, 0) + 1

    categories = get_categories()

    return templates.TemplateResponse(request, "org_list.html", {
        "orgs": orgs,
        "total": total,
        "cat_counts": cat_counts,
        "categories": categories,
        "active_category": category,
        "search": search or "",
    })

@router.get("/organizations/{slug}")
async def org_profile(request: Request, slug: str, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    changes = db.query(OrgChangeEvent).filter(
        OrgChangeEvent.organization_id == org.id
    ).order_by(OrgChangeEvent.detected_at.desc()).limit(20).all()

    # Similar orgs in same category
    similar = db.query(Organization).filter(
        Organization.category == org.category,
        Organization.id != org.id,
    ).limit(6).all()

    return templates.TemplateResponse(request, "org_profile.html", {
        "org": org,
        "changes": changes,
        "similar": similar,
    })

# â”€â”€ Market Dashboards â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/catalog")
async def product_catalog(request: Request, category: str = None, brand: str = None, db: Session = Depends(get_db)):
    query = db.query(Product).options(joinedload(Product.price_history)).order_by(Product.category)
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    products = query.limit(60).all()
    
    categories = ["cooking-oil", "mealie-meal", "bread", "sugar", "dairy", "flour", "rice", "whatsapp-data", "general-data", "fast-food", "groceries", "electronics"]
    brands = ["OK Zimbabwe", "Spar Zimbabwe", "Pick n Pay ZW", "TM Supermarkets", "Econet", "NetOne", "Chicken Inn", "Pizza Inn", "Nando's"]
    
    return templates.TemplateResponse(request, "catalog.html", {
        "products": products,
        "categories": sorted(categories),
        "active_category": category,
        "brands": brands,
        "active_brand": brand
    })

@router.get("/services-catalog")
async def services_catalog(request: Request, category: str = None, db: Session = Depends(get_db)):
    query = db.query(Service).options(joinedload(Service.price_history)).order_by(Service.category)
    if category:
        query = query.filter(Service.category == category)
    services = query.limit(60).all()
    
    categories = ["current-accounts", "savings-accounts", "cash-withdrawals", "transfers", "hotel-stays", "primary-schools", "secondary-schools", "universities", "urban-commuter", "intercity", "last-mile", "air", "contract-staff"]
    
    return templates.TemplateResponse(request, "services_catalog.html", {
        "services": services,
        "categories": sorted(categories),
        "active_category": category
    })

@router.get("/intelligence")
async def intelligence_dashboard(request: Request, db: Session = Depends(get_db)):
    # Get latest price entries across all products/services
    latest_prices = db.query(PriceEntry).options(
        joinedload(PriceEntry.product),
        joinedload(PriceEntry.service)
    ).order_by(PriceEntry.captured_at.desc()).limit(60).all()
    
    # Map to variables expected by intelligence.html
    recent_changes = latest_prices
    deals = [p for p in latest_prices if p.is_promotion]
    
    return templates.TemplateResponse(request, "intelligence.html", {
        "latest_prices": latest_prices,
        "recent_changes": recent_changes,
        "deals": deals
    })

@router.get("/apis")
async def apis_page(request: Request):
    return templates.TemplateResponse(request, "apis.html", {})

@router.get("/export/api-docs")
async def export_api_docs():
    import io
    import os
    from fastapi.responses import StreamingResponse

    # Serve the pre-written static guide (avoids Python string-escaping issues)
    guide_path = os.path.join(os.path.dirname(__file__), "..", "static", "scraper_hub_api_guide.md")
    guide_path = os.path.normpath(guide_path)

    with open(guide_path, "rb") as f:
        content = f.read()

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=scraper_hub_api_guide.md"}
    )

