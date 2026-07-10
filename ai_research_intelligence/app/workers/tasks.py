import logging
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Any
from sqlalchemy import and_, or_, func
from app.workers.celery_app import app
from app.db import SessionLocal
from app.models import (
    ResearchItem, ItemEnrichment, AlertLog, Trend, User, UserSubscription,
    ResearchSource, AlertPriority, EmailLog, ScheduledReport, Startup,
    AIModel, Patent, Grant, RegulationPolicy, GPUMarketIndex, ContentType
)
from app.crawlers.base import (
    ArxivCrawler, OpenReviewCrawler, PapersWithCodeCrawler, HuggingFaceCrawler,
    CorporateResearchCrawler, NewsCrawler, CommunityCrawler, PatentGrantCrawler,
    PolicyRegulationCrawler, GPUMarketCrawler
)
from app.services.agents import ResearcherAgent, EnricherAgent, ValuationAgent
from app.services.deduplication import DeduplicationService
from app.email_service.sender import EmailService

logger = logging.getLogger(__name__)

# ============================================================================
# CRAWLING TASKS
# ============================================================================

async def _crawl_source(crawler_class, source_name: str, source_type: str, authority_score: float) -> int:
    """Helper to run a crawler and ingest items via ResearcherAgent."""
    db = SessionLocal()
    researcher = ResearcherAgent()
    try:
        # Get or create source
        source = db.query(ResearchSource).filter_by(name=source_name).first()
        if not source:
            source = ResearchSource(
                name=source_name,
                source_type=source_type,
                url=crawler_class().source_url,
                authority_score=authority_score
            )
            db.add(source)
            db.commit()
            
        # Update last checked
        source.last_checked = datetime.utcnow()
        db.commit()

        crawler = crawler_class()
        async with crawler:
            items = await crawler.fetch_items()
            
        added = 0
        for item_data in items:
            item_data['source_id'] = source.id
            res = await researcher.ingest_item(db, item_data)
            if res:
                added += 1
                
        logger.info(f"Source {source_name}: crawled {len(items)} items, ingested {added} unique items.")
        return added
    except Exception as e:
        logger.error(f"Error crawling source {source_name}: {e}")
        return 0
    finally:
        db.close()


@app.task(bind=True, max_retries=3)
def crawl_arxiv(self):
    """Crawl arXiv AI categories."""
    try:
        return asyncio.run(_crawl_source(ArxivCrawler, "arXiv", "arxiv", 0.95))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_openreview(self):
    """Crawl OpenReview submissions."""
    try:
        return asyncio.run(_crawl_source(OpenReviewCrawler, "OpenReview", "openreview", 0.90))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_papers_with_code(self):
    """Crawl Papers With Code."""
    try:
        return asyncio.run(_crawl_source(PapersWithCodeCrawler, "Papers With Code", "papers_with_code", 0.90))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_huggingface(self):
    """Crawl Hugging Face papers."""
    try:
        return asyncio.run(_crawl_source(HuggingFaceCrawler, "Hugging Face", "huggingface", 0.85))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_corporate_research(self):
    """Crawl Corporate AI Research Blogs (OpenAI, DeepMind, Anthropic, etc.)."""
    try:
        return asyncio.run(_crawl_source(CorporateResearchCrawler, "Corporate AI Labs", "corporate", 0.95))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_techcrunch(self):
    """Crawl TechCrunch AI."""
    try:
        return asyncio.run(_crawl_source(NewsCrawler, "AI Industry News", "news", 0.85))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_github(self):
    """Crawl GitHub trending repos."""
    try:
        return asyncio.run(_crawl_source(CommunityCrawler, "Community Trends", "community", 0.80))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_patents_and_grants(self):
    """Crawl patents and research grants."""
    try:
        return asyncio.run(_crawl_source(PatentGrantCrawler, "Patents & Grants Monitor", "patent_grant", 0.90))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_policy_and_regulations(self):
    """Crawl global AI policies and regulation boards."""
    try:
        return asyncio.run(_crawl_source(PolicyRegulationCrawler, "AI Policy Monitor", "policy", 0.90))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_gpu_market(self):
    """Crawl cloud GPU price indices."""
    try:
        return asyncio.run(_crawl_source(GPUMarketCrawler, "GPU Market Tracker", "gpu_market", 0.90))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


@app.task
def crawl_all_sources():
    """Triggers all crawlers concurrently."""
    logger.info("Triggering all crawlers in parallel...")
    crawl_arxiv.delay()
    crawl_openreview.delay()
    crawl_papers_with_code.delay()
    crawl_huggingface.delay()
    crawl_corporate_research.delay()
    crawl_techcrunch.delay()
    crawl_github.delay()
    crawl_patents_and_grants.delay()
    crawl_policy_and_regulations.delay()
    crawl_gpu_market.delay()
    return "All crawls queued."

# ============================================================================
# PROCESSING & ENRICHMENT TASKS
# ============================================================================

@app.task
def process_new_items():
    """Runs Multi-Agent pipeline: enrich, parse specialized data, alert."""
    db = SessionLocal()
    enricher = EnricherAgent()
    valuator = ValuationAgent()
    email_service = EmailService()
    
    async def _process():
        # Get items that haven't been enriched yet, exclude duplicates
        items = db.query(ResearchItem).filter(
            ResearchItem.enrichment == None,
            ResearchItem.duplicate_of == None
        ).order_by(ResearchItem.created_at.desc()).limit(30).all()
        
        logger.info(f"Processing {len(items)} new items for enrichment...")
        processed = 0
        
        for item in items:
            try:
                # Enrich item via LLM agent
                enrichment = await enricher.enrich(db, item)
                if not enrichment:
                    continue
                
                # Extract specialized records based on content type
                # 1. Startups & Funding Round valuations
                if item.content_type in [ContentType.STARTUP_ANNOUNCEMENT, ContentType.FUNDING_ROUND]:
                    # Estimate funding details
                    funding_amount = 5000000.0  # Default $5M
                    stage = "Seed"
                    if item.extra_metadata and "amount" in item.extra_metadata:
                        funding_amount = float(item.extra_metadata["amount"])
                    if item.extra_metadata and "stage" in item.extra_metadata:
                        stage = item.extra_metadata["stage"]
                        
                    # Extract startup name from title or payload
                    name_words = item.title.split(" ")
                    startup_name = name_words[0] if name_words else "AIStartup"
                    
                    await valuator.track_startup(
                        db_session=db,
                        name=startup_name,
                        round_amount=funding_amount,
                        stage=stage,
                        focus_areas=item.categories or ["LLMs"],
                        details=enrichment.executive_summary
                    )
                
                # 2. AI Model benchmarks
                elif item.content_type in [ContentType.BENCHMARK_RESULT, ContentType.MODEL_RELEASE]:
                    name_words = item.title.split(" ")
                    model_name = name_words[0] if name_words else "AIModel"
                    
                    model = db.query(AIModel).filter_by(name=model_name).first()
                    if not model:
                        model = AIModel(
                            name=model_name,
                            organization="Community",
                            model_type="LLM",
                            benchmark_dataset="MMLU",
                            benchmark_score=85.0,
                            vs_gpt4_performance=95.0,
                            parameter_count=70, # Billion
                            context_length=128000,
                            is_open_source=True,
                            release_date=datetime.utcnow(),
                            paper_id=item.id
                        )
                        db.add(model)
                        db.commit()
                
                # 3. Patents
                elif item.extra_metadata and "patent_number" in item.extra_metadata:
                    pat_num = item.extra_metadata["patent_number"]
                    patent = db.query(Patent).filter_by(patent_number=pat_num).first()
                    if not patent:
                        patent = Patent(
                            patent_number=pat_num,
                            title=item.title,
                            organization=item.extra_metadata.get("org", "Unknown"),
                            abstract=item.abstract,
                            filing_date=datetime.utcnow() - timedelta(days=90),
                            grant_date=datetime.utcnow(),
                            technology_area=item.categories[0] if item.categories else "AI"
                        )
                        db.add(patent)
                        db.commit()
                
                # 4. Grants
                elif item.content_type == ContentType.GRANT_ANNOUNCEMENT:
                    grant = db.query(Grant).filter_by(title=item.title).first()
                    if not grant:
                        amt = 500000.0
                        agency = "NSF"
                        if item.extra_metadata:
                            amt = item.extra_metadata.get("amount", amt)
                            agency = item.extra_metadata.get("agency", agency)
                        grant = Grant(
                            title=item.title,
                            agency=agency,
                            amount=amt,
                            award_date=datetime.utcnow(),
                            recipient_organization="Research Institute",
                            abstract=item.abstract,
                            url=item.url,
                            focus_areas=item.categories
                        )
                        db.add(grant)
                        db.commit()
                
                # 5. Policy Regulations
                elif item.content_type == ContentType.REGULATORY_POLICY:
                    gov = "AI Commission"
                    juris = "Global"
                    status = "Proposed"
                    impact = "medium"
                    if item.extra_metadata:
                        gov = item.extra_metadata.get("governing_body", gov)
                        juris = item.extra_metadata.get("jurisdiction", juris)
                        status = item.extra_metadata.get("status", status)
                        impact = item.extra_metadata.get("impact_level", impact)
                    policy = db.query(RegulationPolicy).filter_by(title=item.title).first()
                    if not policy:
                        policy = RegulationPolicy(
                            title=item.title,
                            governing_body=gov,
                            jurisdiction=juris,
                            status=status,
                            announcement_date=datetime.utcnow(),
                            summary=item.abstract,
                            impact_level=impact,
                            url=item.url
                        )
                        db.add(policy)
                        db.commit()
                
                # 6. GPU market updates
                elif item.content_type == ContentType.GPU_MARKET_INDEX:
                    gpu = "H100"
                    prov = "AWS"
                    price = 2.50
                    stat = "available"
                    if item.extra_metadata:
                        gpu = item.extra_metadata.get("gpu_model", gpu)
                        prov = item.extra_metadata.get("provider", prov)
                        price = item.extra_metadata.get("price_per_hour", price)
                        stat = item.extra_metadata.get("status", stat)
                    valuator.update_gpu_market_index(db, gpu, prov, price, stat)

                # Real-time alerts trigger (Intelligence Score > 85)
                if enrichment.intelligence_score > 85:
                    logger.info(f"HIGH PRIORITY alert triggered (Score: {enrichment.intelligence_score:.1f}). Sending emails...")
                    
                    # Fetch active users
                    users = db.query(User).filter(User.is_active == True).all()
                    for user in users:
                        await email_service.send_alert_email(user.email, item, enrichment, db)
                        
                        alert = AlertLog(
                            user_id=user.id,
                            item_id=item.id,
                            priority=AlertPriority.HIGH,
                            importance_score=enrichment.importance_score,
                            email_sent=True
                        )
                        db.add(alert)
                        db.commit()
                
                processed += 1
            except Exception as e:
                logger.error(f"Failed processing item {item.id}: {e}")
                
        return processed
        
    try:
        res = asyncio.run(_process())
        return res
    except Exception as e:
        logger.error(f"Error in process_new_items: {e}")
        return 0
    finally:
        db.close()


@app.task
def deduplicate_items():
    """Mark duplicates using DeduplicationService."""
    db = SessionLocal()
    dedup = DeduplicationService()
    try:
        async def _dedup():
            # Check items from last 12 hours that aren't duplicates yet
            cutoff = datetime.utcnow() - timedelta(hours=12)
            items = db.query(ResearchItem).filter(
                ResearchItem.duplicate_of == None,
                ResearchItem.created_at > cutoff
            ).all()
            
            marked = 0
            for item in items:
                res = await dedup.detect_and_mark_duplicates(item, db)
                if res:
                    marked += 1
            return marked
        return asyncio.run(_dedup())
    except Exception as e:
        logger.error(f"Error in deduplicate task: {e}")
        return 0
    finally:
        db.close()


@app.task
def detect_trends():
    """Detect emerging trends and calculate surge metrics."""
    db = SessionLocal()
    try:
        logger.info("Detecting trends...")
        # Simple count aggregation
        cutoff = datetime.utcnow() - timedelta(hours=24)
        counts = db.query(
            ResearchItem.primary_category,
            func.count(ResearchItem.id)
        ).filter(
            ResearchItem.created_at > cutoff,
            ResearchItem.duplicate_of == None
        ).group_by(ResearchItem.primary_category).all()
        
        trends = 0
        for category, count in counts:
            if not category:
                continue
            # Previous count (24h to 48h)
            prev_count = db.query(ResearchItem).filter(
                ResearchItem.primary_category == category,
                ResearchItem.created_at > cutoff - timedelta(hours=24),
                ResearchItem.created_at <= cutoff,
                ResearchItem.duplicate_of == None
            ).count()
            
            growth = ((count - prev_count) / max(prev_count, 1)) * 100
            if growth > 30:  # 30% growth threshold
                trend = db.query(Trend).filter_by(name=f"{category.value} Surge").first()
                if not trend:
                    trend = Trend(
                        name=f"{category.value} Surge",
                        category=category,
                        description=f"Surging activity in {category.value} over the last 24 hours.",
                        mention_count=count,
                        growth_rate=growth,
                        trend_score=min(100.0, float(count * 2 + growth)),
                        is_emerging=True,
                        emergence_date=datetime.utcnow()
                    )
                    db.add(trend)
                else:
                    trend.mention_count = count
                    trend.growth_rate = growth
                    trend.trend_score = min(100.0, float(count * 2 + growth))
                    trend.is_emerging = True
                trends += 1
        db.commit()
        return trends
    except Exception as e:
        logger.error(f"Error detecting trends: {e}")
        return 0
    finally:
        db.close()


@app.task
def send_digest_reports():
    """Generates the 4-hour digest report, converts to PDF, and emails to users."""
    db = SessionLocal()
    email_service = EmailService()
    try:
        async def _run_digest():
            users = db.query(User).filter(User.is_active == True).all()
            if not users:
                return 0
                
            # Fetch top articles from last 4 hours
            cutoff = datetime.utcnow() - timedelta(hours=4)
            items = db.query(ResearchItem).join(ItemEnrichment).filter(
                ResearchItem.created_at > cutoff,
                ResearchItem.duplicate_of == None
            ).order_by(ItemEnrichment.importance_score.desc()).limit(20).all()
            
            if not items:
                logger.info("No items to send in 4-hour digest")
                return 0
                
            enrichments = {item.id: item.enrichment for item in items if item.enrichment}
            
            # Aggregate trends for report
            trending = db.query(Trend).filter(Trend.is_emerging == True).limit(5).all()
            trends_list = [t.name for t in trending]
            
            report_data = {
                "trending_topics_count": len(trends_list),
                "trending_topics": trends_list,
                "next_digest_time": "in 4 hours"
            }
            
            sent = 0
            for user in users:
                success = await email_service.send_digest_email(
                    recipient=user.email,
                    items=items,
                    enrichments=enrichments,
                    report_data=report_data,
                    db_session=db
                )
                if success:
                    sent += 1
                    # Log ScheduledReport
                    report = ScheduledReport(
                        report_type='digest',
                        user_id=user.id,
                        scheduled_time=datetime.utcnow(),
                        generated_at=datetime.utcnow(),
                        sent_at=datetime.utcnow(),
                        status='sent',
                        top_papers=[i.id for i in items[:5]]
                    )
                    db.add(report)
            db.commit()
            return sent
            
        return asyncio.run(_run_digest())
    except Exception as e:
        logger.error(f"Error in digest reports: {e}")
        return 0
    finally:
        db.close()


@app.task
def update_source_health():
    """Updates health status of crawlers."""
    db = SessionLocal()
    try:
        sources = db.query(ResearchSource).all()
        for source in sources:
            # Check items ingested in last 24h
            cutoff = datetime.utcnow() - timedelta(hours=24)
            cnt = db.query(ResearchItem).filter(
                ResearchItem.source_id == source.id,
                ResearchItem.created_at > cutoff
            ).count()
            
            if cnt > 0:
                source.status = "active"
                source.consecutive_failures = 0
            else:
                source.status = "degraded"
            source.last_checked = datetime.utcnow()
        db.commit()
        return "Source health updated."
    except Exception as e:
        logger.error(f"Error updating health: {e}")
        return "Error"
    finally:
        db.close()
