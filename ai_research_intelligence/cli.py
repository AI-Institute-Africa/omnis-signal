#!/usr/bin/env python3
"""CLI utility for AI Research Intelligence Platform."""

import click
import logging
from datetime import datetime
from app.db import SessionLocal, init_db, verify_db_connection
from app.models import ResearchItem, ResearchSource, User, ItemEnrichment, Trend
from sqlalchemy import func, and_

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """AI Research Intelligence Platform CLI."""
    pass


# ============================================================================
# DATABASE COMMANDS
# ============================================================================

@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
def init():
    """Initialize database."""
    click.echo("Initializing database...")
    try:
        init_db()
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@db.command()
def verify():
    """Verify database connection."""
    click.echo("Verifying database connection...")
    if verify_db_connection():
        click.echo("✅ Database connection verified")
    else:
        click.echo("❌ Database connection failed")


@db.command()
def stats():
    """Show database statistics."""
    db_session = SessionLocal()
    try:
        total_items = db_session.query(ResearchItem).count()
        total_sources = db_session.query(ResearchSource).count()
        total_users = db_session.query(User).count()
        enriched_items = db_session.query(ItemEnrichment).count()
        high_priority = db_session.query(ItemEnrichment).filter(
            ItemEnrichment.importance_score > 85
        ).count()
        
        click.echo("\n📊 Database Statistics")
        click.echo("=" * 50)
        click.echo(f"Total Items:         {total_items:,}")
        click.echo(f"Enriched Items:      {enriched_items:,}")
        click.echo(f"High Priority Items: {high_priority:,}")
        click.echo(f"Total Sources:       {total_sources:,}")
        click.echo(f"Total Users:         {total_users:,}")
        click.echo("=" * 50)
        
    finally:
        db_session.close()


# ============================================================================
# ANALYSIS COMMANDS
# ============================================================================

@cli.group()
def analyze():
    """Data analysis commands."""
    pass


@analyze.command()
@click.option('--hours', default=24, help='Hours to analyze')
@click.option('--limit', default=10, help='Number of items to show')
def top_items(hours, limit):
    """Show top items by importance score."""
    from datetime import timedelta
    
    db_session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        items = db_session.query(ResearchItem).join(ItemEnrichment).filter(
            ResearchItem.created_at > cutoff
        ).order_by(ItemEnrichment.importance_score.desc()).limit(limit).all()
        
        click.echo(f"\n🔥 Top {limit} Items (Last {hours} hours)")
        click.echo("=" * 80)
        
        for i, item in enumerate(items, 1):
            click.echo(f"\n{i}. {item.title[:70]}")
            if item.enrichment:
                click.echo(f"   Score: {item.enrichment.importance_score:.1f}/100")
                click.echo(f"   Innovation: {item.enrichment.innovation_score:.1f}")
                click.echo(f"   Impact: {item.enrichment.market_impact_score:.1f}")
            click.echo(f"   URL: {item.url}")
        
        click.echo("\n" + "=" * 80)
        
    finally:
        db_session.close()


@analyze.command()
def trends():
    """Show emerging trends."""
    db_session = SessionLocal()
    try:
        trends_list = db_session.query(Trend).filter(
            Trend.is_emerging == True
        ).order_by(Trend.growth_rate.desc()).limit(10).all()
        
        if not trends_list:
            click.echo("No emerging trends detected yet.")
            return
        
        click.echo("\n📈 Emerging Trends")
        click.echo("=" * 80)
        
        for trend in trends_list:
            click.echo(f"\n🔝 {trend.name}")
            click.echo(f"   Growth Rate: {trend.growth_rate:.1f}%")
            click.echo(f"   Mentions: {trend.mention_count}")
            click.echo(f"   Trend Score: {trend.trend_score:.1f}")
        
        click.echo("\n" + "=" * 80)
        
    finally:
        db_session.close()


@analyze.command()
def categories():
    """Show items by category."""
    db_session = SessionLocal()
    try:
        categories = db_session.query(
            ResearchItem.primary_category,
            func.count(ResearchItem.id)
        ).group_by(ResearchItem.primary_category).all()
        
        click.echo("\n📂 Items by Category")
        click.echo("=" * 50)
        
        for category, count in sorted(categories, key=lambda x: x[1], reverse=True):
            cat_name = category.value if category else "Unknown"
            click.echo(f"{cat_name:30s} {count:>10,}")
        
        click.echo("=" * 50)
        
    finally:
        db_session.close()


# ============================================================================
# SOURCE COMMANDS
# ============================================================================

@cli.group()
def sources():
    """Source management commands."""
    pass


@sources.command()
def list():
    """List all sources."""
    db_session = SessionLocal()
    try:
        sources_list = db_session.query(ResearchSource).all()
        
        click.echo("\n📡 Research Sources")
        click.echo("=" * 100)
        click.echo(f"{'Name':<30} {'Type':<15} {'Authority':<12} {'Status':<10} {'Items':<10}")
        click.echo("-" * 100)
        
        for source in sources_list:
            items_count = db_session.query(ResearchItem).filter_by(
                source_id=source.id
            ).count()
            
            status = "✅ Active" if source.is_active else "❌ Inactive"
            click.echo(
                f"{source.name:<30} {source.source_type:<15} "
                f"{source.authority_score:>11.2f} {status:<10} {items_count:>10,}"
            )
        
        click.echo("=" * 100)
        
    finally:
        db_session.close()


@sources.command()
@click.argument('source_name')
def health(source_name):
    """Check source health."""
    db_session = SessionLocal()
    try:
        source = db_session.query(ResearchSource).filter_by(name=source_name).first()
        
        if not source:
            click.echo(f"❌ Source '{source_name}' not found")
            return
        
        # Get recent items
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        items_24h = db_session.query(ResearchItem).filter(
            and_(
                ResearchItem.source_id == source.id,
                ResearchItem.created_at > cutoff
            )
        ).count()
        
        click.echo(f"\n📊 Source Health: {source_name}")
        click.echo("=" * 50)
        click.echo(f"Status: {source.status.value}")
        click.echo(f"Authority Score: {source.authority_score:.2f}")
        click.echo(f"Items (24h): {items_24h}")
        click.echo(f"Last Checked: {source.last_checked}")
        click.echo(f"Consecutive Failures: {source.consecutive_failures}")
        click.echo("=" * 50)
        
    finally:
        db_session.close()


# ============================================================================
# USER COMMANDS
# ============================================================================

@cli.group()
def users():
    """User management commands."""
    pass


@users.command()
def list():
    """List all users."""
    db_session = SessionLocal()
    try:
        users_list = db_session.query(User).all()
        
        click.echo("\n👥 Users")
        click.echo("=" * 80)
        click.echo(f"{'Email':<35} {'Status':<15} {'Created':<20}")
        click.echo("-" * 80)
        
        for user in users_list:
            status = "✅ Active" if user.is_active else "❌ Inactive"
            created = user.created_at.strftime("%Y-%m-%d %H:%M")
            click.echo(f"{user.email:<35} {status:<15} {created:<20}")
        
        click.echo("=" * 80)
        
    finally:
        db_session.close()


@users.command()
@click.option('--email', prompt='Email', help='User email')
@click.option('--username', prompt='Username', help='Username')
@click.option('--password', prompt=True, hide_input=True, help='Password')
def create(email, username, password):
    """Create new user."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db_session = SessionLocal()
    try:
        # Check if user exists
        existing = db_session.query(User).filter_by(email=email).first()
        if existing:
            click.echo(f"❌ User with email '{email}' already exists")
            return
        
        # Create user
        user = User(
            email=email,
            username=username,
            hashed_password=pwd_context.hash(password)
        )
        db_session.add(user)
        db_session.commit()
        
        click.echo(f"✅ User '{email}' created successfully")
        click.echo(f"   ID: {user.id}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        db_session.rollback()
    finally:
        db_session.close()


# ============================================================================
# CLEANUP COMMANDS
# ============================================================================

@cli.group()
def cleanup():
    """Data cleanup commands."""
    pass


@cleanup.command()
@click.option('--days', default=90, help='Delete items older than N days')
@click.confirmation_option(prompt='Are you sure you want to delete old items?')
def old_items(days):
    """Delete old items."""
    from datetime import timedelta
    
    db_session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        count = db_session.query(ResearchItem).filter(
            ResearchItem.created_at < cutoff
        ).delete()
        
        db_session.commit()
        click.echo(f"✅ Deleted {count} items older than {days} days")
        
    finally:
        db_session.close()


@cleanup.command()
@click.confirmation_option(prompt='Are you sure you want to delete duplicate items?')
def duplicates():
    """Delete duplicate items."""
    db_session = SessionLocal()
    try:
        count = db_session.query(ResearchItem).filter(
            ResearchItem.duplicate_of.isnot(None)
        ).delete()
        
        db_session.commit()
        click.echo(f"✅ Deleted {count} duplicate items")
        
    finally:
        db_session.close()


# ============================================================================
# AGENT & CRAWLER INTERACTIVE COMMANDS
# ============================================================================

@cli.group()
def agent():
    """AI Research Analyst Agent commands."""
    pass


@agent.command('query')
@click.argument('question')
def agent_query(question):
    """Query the RAG AI Research Analyst Agent."""
    import asyncio
    from app.services.agents import RAGAnalystAgent
    
    click.echo(f"Analyst Agent thinking about: '{question}'...")
    agent_inst = RAGAnalystAgent()
    
    async def _query():
        return await agent_inst.answer_question(question)
        
    result = asyncio.run(_query())
    
    click.echo("\n🤖 ANALYST ANSWER:")
    click.echo("=" * 80)
    click.echo(result["answer"])
    click.echo("=" * 80)
    
    if result["citations"]:
        click.echo("\n📚 CITATIONS:")
        for idx, cite in enumerate(result["citations"], 1):
            click.echo(f"{idx}. [{cite['source']}] {cite['title']} - {cite['url']}")
        click.echo("=" * 80)


@cli.group()
def crawl():
    """Crawler commands."""
    pass


@crawl.command('run-all')
def crawl_run_all():
    """Run all crawlers and process new items synchronously."""
    from app.workers.tasks import (
        crawl_arxiv, crawl_openreview, crawl_papers_with_code, crawl_huggingface,
        crawl_corporate_research, crawl_techcrunch, crawl_github, crawl_patents_and_grants,
        crawl_policy_and_regulations, crawl_gpu_market, process_new_items, deduplicate_items, detect_trends
    )
    
    click.echo("Running all crawlers synchronously for testing...")
    
    crawl_arxiv()
    crawl_openreview()
    crawl_papers_with_code()
    crawl_huggingface()
    crawl_corporate_research()
    crawl_techcrunch()
    crawl_github()
    crawl_patents_and_grants()
    crawl_policy_and_regulations()
    crawl_gpu_market()
    
    click.echo("Running deduplication...")
    deduplicate_items()
    
    click.echo("Processing and enriching new items...")
    processed = process_new_items()
    click.echo(f"Processed and enriched {processed} items.")
    
    click.echo("Running trend detection...")
    detect_trends()
    
    click.echo("[SUCCESS] Crawling and processing run complete.")


if __name__ == '__main__':
    cli()

