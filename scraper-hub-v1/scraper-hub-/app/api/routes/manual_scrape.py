from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.db.models.raw_snapshot import RawSnapshot
from app.services.fetcher import PlaywrightFetcher
from app.services.extractor import ExtractorService


class ManualScrapeRequest(BaseModel):
    url: str
    category: str
    extractor_type: str = "auto"
    store_result: bool = True
    content: Optional[str] = None


router = APIRouter()


@router.post("/")
async def manual_scrape(
    request: Request,
    url: str = Form(...),
    category: str = Form(...),
    extractor_type: str = Form("auto"),
    store_result: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    from app.logging import logger
    logger.info(f"Manual scrape request received for URL: {url} (Category: {category}, Extractor: {extractor_type})")
    
    # Handle checkbox logic correctly for HTMX form data.
    should_store = (store_result == "on")
    
    # If raw content is provided, skip fetching and extract directly from it.
    if content:
        if not url:
            url = "https://raw-content.local"
        content_value = content
        content_type = "html" if '<' in content_value and '>' in content_value else "text"
    else:
        fetcher = PlaywrightFetcher()
        content_value = ""
        try:
            content_value = await fetcher.fetch_page_content(url)
            if not content_value:
                raise Exception("Fetched content is empty. The site might be blocking the scraper or is currently unreachable.")
            content_type = "html"
        except Exception as e:
            import traceback
            err_msg = str(e)
            tb_msg = traceback.format_exc()
            logger.error(f"Manual scrape fetch failed: {err_msg}")
            logger.error(f"Traceback: {tb_msg}")
            full_error = f"{err_msg}\n\nTraceback:\n{tb_msg}" if tb_msg else err_msg
            if request.headers.get("HX-Request"):
                return HTMLResponse(
                    status_code=200, # Still 200 so HTMX swaps it
                    content=f"""
                    <div class="alert alert-danger">
                        <h4>❌ Fetch Failed</h4>
                        <p>{full_error}</p>
                        <p>Try again or check if the URL is accessible in a normal browser.</p>
                    </div>
                    """
                )
            raise HTTPException(status_code=500, detail=f"Failed to fetch page: {full_error}")
    
    snapshot = None
    extracted_records = []

    try:
        if should_store:
            snapshot = RawSnapshot(
                source_page_id=None,
                url=url,
                content=content_value,
                content_type=content_type
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)

            # Run extraction with hints
            extractor_service = ExtractorService(db)
            extracted_records = extractor_service.extract_from_snapshot(
                snapshot, 
                category_hint=category, 
                extractor_type=extractor_type,
                persist=True,
                run_ai_enrichment=False,
                real_prices_only=True
            )
        else:
            # Create a temporary snapshot object without saving to DB if storage is disabled
            temp_snapshot = RawSnapshot(url=url, content=content_value, content_type=content_type)
            extractor_service = ExtractorService(db)
            # BaseExtractor uses snapshot.id in _create_record, so set a safe temporary value.
            temp_snapshot.id = 0 
            extracted_records = extractor_service.extract_from_snapshot(
                temp_snapshot, 
                category_hint=category, 
                extractor_type=extractor_type,
                persist=False,
                run_ai_enrichment=False,
                real_prices_only=True
            )
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        if request.headers.get("HX-Request"):
            return HTMLResponse(
                content=f"""
                <div class="alert alert-warning">
                    <h4>⚠️ Extraction Issue</h4>
                    <p>The page was fetched ({len(content_value):,} bytes), but data extraction encountered an error: {str(e)}</p>
                    <p>The raw content has been captured. You can try again later.</p>
                </div>
                """
            )
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Check if this is an HTMX request (from web interface)
    if request.headers.get("HX-Request"):
        # Return HTML for HTMX
        html_response = f"""
        <div class="alert alert-success">
            <h4>✅ Scrape Successful!</h4>
            <div class="row small mb-2">
                <div class="col-sm-6"><strong>URL:</strong> {url}</div>
                <div class="col-sm-3"><strong>Size:</strong> {len(content_value):,} bytes</div>
                <div class="col-sm-3"><strong>Category:</strong> {category}</div>
            </div>
            <p class="mb-0"><strong>Records Extracted:</strong> {len(extracted_records)}</p>
        </div>
        """
        
        if extracted_records:
            html_response += """
            <div class="card mt-3 shadow-sm">
                <div class="card-header bg-transparent">
                    <h5 class="mb-0">Extracted Intelligence</h5>
                </div>
                <div class="card-body p-0">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Entity</th>
                                <th>Product/Service</th>
                                <th>Price</th>
                                <th>Category</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for record in extracted_records[:15]:
                price_val = record.get("price_value")
                price_curr = record.get("price_currency", "USD")
                price_str = f"{price_curr} {price_val:,.2f}" if price_val is not None else "-"
                html_response += f"""
                            <tr>
                                <td class="fw-bold">{record.get('entity_name', 'Unknown')}</td>
                                <td>{record.get('title', 'Unknown')}</td>
                                <td class="text-primary fw-bold">{price_str}</td>
                                <td><span class="badge bg-info text-dark">{record.get('category', 'Unknown')}</span></td>
                            </tr>
                """
            html_response += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
        else:
            html_response += """
            <div class="alert alert-warning mt-3">
                <h5>⚠️ No Priced Records Found</h5>
                <p>The extractor processed the page but did not find any price-bearing records. Try a different extractor type or verify that the page contains visible pricing information.</p>
            </div>
            """

        html_response += """
        <div class="mt-4 d-flex gap-2">
            <a href="/records" class="btn btn-primary">📊 View Intelligence Feed</a>
            <button class="btn btn-outline-secondary" onclick="location.reload()">🔄 New Scrape</button>
        </div>
        """

        return HTMLResponse(content=html_response)

    # Return JSON for API calls
    response = {
        "status": "success",
        "url": url,
        "content_length": len(content_value),
        "extracted_records_count": len(extracted_records),
        "extracted_records": extracted_records
    }

    if snapshot:
        response["snapshot_id"] = snapshot.id

    return response
