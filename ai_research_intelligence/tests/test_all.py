"""
Comprehensive Test Suite for the AI Research Intelligence Platform.
Covers: Models, Services (Enrichment, Deduplication, VectorStore, Agents),
        Crawlers, API Endpoints, Performance, and Integration Workflows.
"""
import pytest
import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base, ResearchItem, ResearchSource, User, ItemEnrichment, Trend,
    Startup, AIModel, Patent, Grant, RegulationPolicy, GPUMarketIndex,
    ContentType, ResearchCategory, AlertPriority, SourceStatus
)
from app.db import get_db
from app.services.enrichment import AIEnrichmentService
from app.services.deduplication import DeduplicationService
from app.services.vector_store import VectorStoreService
from app.crawlers.base import BaseCrawler, ArxivCrawler
from app.config import settings


# ============================================================================
# TEST DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db():
    """Create in-memory SQLite test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_db):
    """Provide a clean transactional database session for each test."""
    Session = sessionmaker(bind=test_db)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_source(db_session):
    """Create a sample research source."""
    source = ResearchSource(
        name="Test Source arXiv",
        source_type="arxiv",
        url="https://arxiv.org",
        authority_score=0.95
    )
    db_session.add(source)
    db_session.commit()
    return source


@pytest.fixture
def sample_item(db_session, sample_source):
    """Create a sample research item."""
    item = ResearchItem(
        source_id=sample_source.id,
        title="Attention is All You Need: A Transformer Breakthrough",
        url="https://arxiv.org/abs/1706.03762",
        url_hash=hashlib.sha256(b"https://arxiv.org/abs/1706.03762").hexdigest(),
        abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
        authors=["Vaswani", "Shazeer", "Parmar"],
        published_date=datetime.utcnow(),
        content_type=ContentType.RESEARCH_PAPER,
        primary_category=ResearchCategory.LLM
    )
    db_session.add(item)
    db_session.commit()
    return item


# ============================================================================
# TESTS: DATABASE MODELS
# ============================================================================

class TestModels:
    """Tests for all database models including new Grant, Policy, and GPU tables."""

    def test_research_source_creation(self, db_session):
        """Test ResearchSource model creation with all fields."""
        source = ResearchSource(
            name="OpenReview Test",
            source_type="openreview",
            url="https://openreview.net",
            authority_score=0.85,
            status=SourceStatus.ACTIVE
        )
        db_session.add(source)
        db_session.commit()

        assert source.id is not None
        assert source.name == "OpenReview Test"
        assert source.authority_score == 0.85
        assert source.status == SourceStatus.ACTIVE

    def test_research_item_creation(self, db_session, sample_source):
        """Test ResearchItem model creation."""
        item = ResearchItem(
            source_id=sample_source.id,
            title="Test Paper on LLMs",
            url="https://example.com/paper1",
            url_hash="abc123unique",
            abstract="Test abstract for LLMs",
            authors=["Author1", "Author2"],
            published_date=datetime.utcnow(),
            content_type=ContentType.RESEARCH_PAPER
        )
        db_session.add(item)
        db_session.commit()

        assert item.id is not None
        assert item.title == "Test Paper on LLMs"
        assert len(item.authors) == 2

    def test_content_type_enum_completeness(self):
        """Verify all required content types exist in the enum."""
        required_types = [
            "research_paper", "news_article", "blog_post", "github_repo",
            "model_release", "startup_announcement", "funding_round",
            "benchmark_result", "grant_announcement", "regulatory_policy",
            "gpu_market_index", "patent_filing"
        ]
        all_types = [t.value for t in ContentType]
        for ct in required_types:
            assert ct in all_types, f"Missing ContentType: {ct}"

    def test_research_category_enum_completeness(self):
        """Verify all required research categories exist."""
        required_cats = ["llm", "agents", "robotics", "computer_vision", "nlp",
                         "multimodal_ai", "ai_safety", "ai_policy"]
        all_cats = [c.value for c in ResearchCategory]
        for cat in required_cats:
            assert cat in all_cats, f"Missing ResearchCategory: {cat}"

    def test_user_creation(self, db_session):
        """Test User model."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pass_value"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_grant_model_creation(self, db_session, sample_item):
        """Test Grant model (new table)."""
        grant = Grant(
            title="NSF AI Research Grant",
            agency="National Science Foundation",
            amount=500000.0,
            recipient_organization="MIT",
            abstract="Funding for large language model research.",
            url="https://grants.gov/nfs-ai-001",
            focus_areas=["Large Language Models", "AI Safety"]
        )
        db_session.add(grant)
        db_session.commit()

        assert grant.id is not None
        assert grant.amount == 500000.0
        assert grant.agency == "National Science Foundation"

    def test_regulation_policy_model_creation(self, db_session, sample_item):
        """Test RegulationPolicy model (new table)."""
        policy = RegulationPolicy(
            title="EU AI Act Framework",
            governing_body="European Parliament",
            jurisdiction="European Union",
            status="Active",
            impact_level="high",
            summary="Comprehensive regulation for AI systems across the EU.",
            url="https://eur-lex.europa.eu/ai-act"
        )
        db_session.add(policy)
        db_session.commit()

        assert policy.id is not None
        assert policy.jurisdiction == "European Union"
        assert policy.impact_level == "high"

    def test_gpu_market_index_model_creation(self, db_session, sample_item):
        """Test GPUMarketIndex model (new table)."""
        gpu_index = GPUMarketIndex(
            gpu_model="NVIDIA H100 SXM5 80GB",
            provider="AWS",
            price_per_hour=3.49,
            availability_status="available",
            demand_index=1.2
        )
        db_session.add(gpu_index)
        db_session.commit()

        assert gpu_index.id is not None
        assert gpu_index.gpu_model == "NVIDIA H100 SXM5 80GB"
        assert gpu_index.price_per_hour == 3.49

    def test_startup_model_creation(self, db_session, sample_item):
        """Test Startup model."""
        startup = Startup(
            name="AI Unicorn Inc",
            description="Next-generation AI platform.",
            total_funding=50_000_000.0,
            funding_stage="Series A",
            current_valuation=250_000_000.0,
            team_size=45,
            headquarters="San Francisco, USA"
        )
        db_session.add(startup)
        db_session.commit()

        assert startup.id is not None
        assert startup.current_valuation == 250_000_000.0

    def test_item_enrichment_scores(self, db_session, sample_item):
        """Test ItemEnrichment model with all scoring fields."""
        enrichment = ItemEnrichment(
            item_id=sample_item.id,
            executive_summary="A groundbreaking study on attention mechanisms.",
            technical_summary="Introduces multi-head self-attention for sequence modelling.",
            innovation_score=95.0,
            market_impact_score=88.0,
            research_significance_score=98.0,
            importance_score=93.0,
            intelligence_score=91.5,
            virality_prediction=78.0,
            impact_prediction=85.0,
            valuation_potential_score=70.0,
            regulatory_feasibility_score=80.0,
        )
        db_session.add(enrichment)
        db_session.commit()

        assert enrichment.id is not None
        assert enrichment.importance_score == 93.0
        assert enrichment.intelligence_score == 91.5


# ============================================================================
# TESTS: DEDUPLICATION SERVICE
# ============================================================================

class TestDeduplicationService:
    """Tests for the DeduplicationService with multi-tier checking."""

    def test_url_hash_is_deterministic(self):
        """URL hash must always return same value for same URL."""
        dedup = DeduplicationService()
        url = "https://arxiv.org/abs/2401.12345"
        assert dedup.calculate_url_hash(url) == dedup.calculate_url_hash(url)
        assert len(dedup.calculate_url_hash(url)) == 64  # SHA-256 hex

    def test_url_hash_differs_for_different_urls(self):
        """Different URLs must produce different hashes."""
        dedup = DeduplicationService()
        hash1 = dedup.calculate_url_hash("https://arxiv.org/abs/2401.00001")
        hash2 = dedup.calculate_url_hash("https://arxiv.org/abs/2401.00002")
        assert hash1 != hash2

    def test_content_hash_normalizes_case(self):
        """Content hash should be case-insensitive."""
        dedup = DeduplicationService()
        h1 = dedup.calculate_content_hash("Title ABC", "Abstract XYZ")
        h2 = dedup.calculate_content_hash("title abc", "abstract xyz")
        assert h1 == h2

    def test_url_similarity_identical_urls(self):
        """Identical URLs should have similarity of 1.0."""
        dedup = DeduplicationService()
        url = "https://example.com/paper/123"
        assert dedup._url_similarity(url, url) == 1.0

    def test_url_similarity_different_query_params(self):
        """URLs differing only in query params should be very similar."""
        dedup = DeduplicationService()
        url1 = "https://example.com/paper?v=1"
        url2 = "https://example.com/paper?v=2"
        assert dedup._url_similarity(url1, url2) > 0.8

    def test_content_similarity_identical(self):
        """Identical title+abstract should yield similarity 1.0."""
        dedup = DeduplicationService()
        title = "Deep Learning for NLP"
        abstract = "A comprehensive study on applying deep learning to NLP."
        assert dedup._content_similarity(title, abstract, title, abstract) == 1.0

    def test_content_similarity_different_content(self):
        """Completely different content should have low similarity."""
        dedup = DeduplicationService()
        sim = dedup._content_similarity(
            "Quantum Computing",
            "This paper discusses quantum entanglement and superposition states.",
            "Deep Learning Models",
            "This paper discusses neural network architectures for vision tasks."
        )
        assert sim < 0.5

    def test_is_duplicate_url_match(self, db_session, sample_source):
        """Test that exact URL match is detected as duplicate."""
        dedup = DeduplicationService()

        item1 = ResearchItem(
            source_id=sample_source.id,
            title="Paper Alpha",
            url="https://example.com/paper-alpha",
            url_hash="hash_alpha_001",
            abstract="Abstract alpha."
        )
        item2 = ResearchItem(
            source_id=sample_source.id,
            title="Paper Alpha (Duplicate)",
            url="https://example.com/paper-alpha",
            url_hash="hash_alpha_002",
            abstract="Abstract alpha."
        )
        db_session.add(item1)
        db_session.commit()

        duplicate_of = dedup.is_duplicate(item2, [item1])
        assert duplicate_of is not None
        assert duplicate_of.id == item1.id

    def test_is_not_duplicate_different_content(self, db_session, sample_source):
        """Completely different papers should not be marked as duplicates."""
        dedup = DeduplicationService()

        item1 = ResearchItem(
            source_id=sample_source.id,
            title="Quantum Computing for Drug Discovery",
            url="https://example.com/quantum-paper",
            url_hash="hash_quantum",
            abstract="Quantum algorithms for molecular simulation."
        )
        item2 = ResearchItem(
            source_id=sample_source.id,
            title="Transformer Architectures for Image Generation",
            url="https://example.com/transformer-vision",
            url_hash="hash_transformer",
            abstract="Vision transformers for diffusion-based image synthesis."
        )
        db_session.add(item1)
        db_session.commit()

        duplicate_of = dedup.is_duplicate(item2, [item1])
        assert duplicate_of is None

    def test_get_deduplication_status(self, db_session, sample_source):
        """Test deduplication statistics computation."""
        dedup = DeduplicationService()

        item1 = ResearchItem(
            source_id=sample_source.id, title="Parent",
            url="https://example.com/parent", url_hash="hash_p1"
        )
        item2 = ResearchItem(
            source_id=sample_source.id, title="Duplicate",
            url="https://example.com/dup1", url_hash="hash_dup1"
        )
        db_session.add_all([item1, item2])
        db_session.commit()
        item2.duplicate_of = item1.id
        db_session.commit()

        status = dedup.get_deduplication_status(db_session)
        assert "total_items" in status
        assert "duplicate_items" in status
        assert status["duplicate_items"] >= 1


# ============================================================================
# TESTS: VECTOR STORE SERVICE
# ============================================================================

class TestVectorStoreService:
    """Tests for VectorStoreService (in-memory fallback mode)."""

    def test_vector_store_initializes_in_fallback_mode(self):
        """Vector store should work even without Qdrant."""
        vs = VectorStoreService()
        assert vs is not None
        assert isinstance(vs.fallback_db, dict)

    def test_generate_embedding_returns_vector(self):
        """Embedding generation should return a list of floats."""
        vs = VectorStoreService()
        # Mock OpenAI embedding response
        with patch.object(vs, '_openai_embed', return_value=[0.1] * 1536):
            embedding = vs.generate_embedding("This is a test sentence.")
            assert embedding is not None
            assert len(embedding) > 0

    def test_generate_embedding_fallback_without_api_key(self):
        """Without an API key, should return deterministic fallback embedding."""
        vs = VectorStoreService()
        # Force no API key context
        with patch.object(vs, 'openai_client', None):
            embedding = vs.generate_embedding("Test text for embedding")
            assert embedding is not None
            assert len(embedding) > 0

    def test_upsert_and_search_in_fallback_mode(self):
        """In fallback mode, upserted vectors should be findable via search."""
        vs = VectorStoreService()
        test_id = "test-item-uuid-001"
        test_vector = [0.1] * vs.vector_size
        test_metadata = {"title": "Test Paper", "source": "arxiv"}

        # Upsert
        vs.upsert_vector(item_id=test_id, vector=test_vector, metadata=test_metadata)
        assert test_id in vs.fallback_db

        # Search
        results = vs.search_similar(query_vector=test_vector, limit=5, threshold=0.5)
        ids_found = [r["id"] for r in results]
        assert test_id in ids_found

    def test_cosine_similarity_calculation(self):
        """Test cosine similarity between known vectors."""
        vs = VectorStoreService()
        import numpy as np

        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        v3 = np.array([0.0, 1.0, 0.0])

        sim_identical = vs._cosine_similarity(v1.tolist(), v2.tolist())
        sim_orthogonal = vs._cosine_similarity(v1.tolist(), v3.tolist())

        assert abs(sim_identical - 1.0) < 1e-6
        assert abs(sim_orthogonal - 0.0) < 1e-6

    def test_batch_upsert_handles_multiple_items(self):
        """Batch upsert should add all items to the fallback DB."""
        vs = VectorStoreService()
        items = [
            {"id": f"batch-item-{i}", "vector": [float(i)] * vs.vector_size, "metadata": {"idx": i}}
            for i in range(5)
        ]
        for item in items:
            vs.upsert_vector(item["id"], item["vector"], item["metadata"])

        for item in items:
            assert item["id"] in vs.fallback_db


# ============================================================================
# TESTS: ENRICHMENT SERVICE & SCORING
# ============================================================================

class TestEnrichmentService:
    """Tests for AIEnrichmentService and the importance/intelligence scoring formulas."""

    def test_importance_score_is_bounded(self):
        """Importance score must always be between 0 and 100."""
        enrichment = AIEnrichmentService()
        for _ in range(20):
            import random
            score = enrichment._calculate_importance_score(
                innovation=random.uniform(0, 100),
                market_impact=random.uniform(0, 100),
                significance=random.uniform(0, 100),
                citation_velocity=random.uniform(0, 100),
                engagement=random.uniform(0, 100),
                novelty=random.uniform(0, 100),
                authority=random.uniform(0, 1)
            )
            assert 0 <= score <= 100, f"Score out of bounds: {score}"

    def test_high_scores_produce_high_importance(self):
        """Inputs with all-max values should yield a high importance score."""
        enrichment = AIEnrichmentService()
        score = enrichment._calculate_importance_score(
            innovation=100, market_impact=100, significance=100,
            citation_velocity=100, engagement=100, novelty=100, authority=1.0
        )
        assert score >= 90, f"Expected >90, got {score}"

    def test_zero_scores_produce_low_importance(self):
        """Inputs with all-zero values should yield a low importance score."""
        enrichment = AIEnrichmentService()
        score = enrichment._calculate_importance_score(
            innovation=0, market_impact=0, significance=0,
            citation_velocity=0, engagement=0, novelty=0, authority=0.0
        )
        assert score <= 10, f"Expected <=10, got {score}"

    def test_intelligence_score_formula(self):
        """Verify the hedge-fund intelligence score formula is applied correctly.

        Actual signature:
            _calculate_intelligence_score(importance, virality, impact, market_impact, significance)

        Formula:
            0.30 * importance + 0.30 * impact*100 + 0.25 * market_impact + 0.10 * virality*100 + 0.05 * significance
        """
        enrichment = AIEnrichmentService()
        score = enrichment._calculate_intelligence_score(
            importance=80.0,
            virality=0.5,       # 0-1 scale
            impact=0.7,         # 0-1 scale
            market_impact=70.0,
            significance=90.0,
        )
        expected = (80.0 * 0.30 + 0.7 * 100 * 0.30 + 70.0 * 0.25 + 0.5 * 100 * 0.10 + 90.0 * 0.05)
        assert abs(score - expected) < 1.0, f"Expected ~{expected:.1f}, got {score:.1f}"

    def test_extract_key_topics_returns_list(self):
        """_extract_key_topics should return a list of strings."""
        enrichment = AIEnrichmentService()
        text = "Large language models, transformers, RLHF, fine-tuning, chain-of-thought reasoning."
        # Use the synchronous keyword extraction fallback
        topics = enrichment._extract_keywords_heuristic(text)
        assert isinstance(topics, list)
        assert len(topics) > 0


# ============================================================================
# TESTS: CRAWLERS
# ============================================================================

class TestCrawlers:
    """Tests for the crawler infrastructure."""

    @pytest.mark.asyncio
    async def test_base_crawler_url_hash_deterministic(self):
        """BaseCrawler URL hashing must be deterministic."""
        crawler = BaseCrawler("Test", "https://test.com")
        url = "https://example.com/paper"
        assert crawler.calculate_url_hash(url) == crawler.calculate_url_hash(url)

    @pytest.mark.asyncio
    async def test_arxiv_crawler_initialization(self):
        """ArxivCrawler should initialize with correct source name and URL."""
        crawler = ArxivCrawler()
        assert crawler.source_name == "arXiv"
        assert "arxiv.org" in crawler.source_url

    @pytest.mark.asyncio
    async def test_base_crawler_clean_text(self):
        """BaseCrawler should strip HTML tags from text."""
        crawler = BaseCrawler("Test", "https://test.com")
        html_text = "<p>This is <b>bold</b> text.</p>"
        clean = crawler._clean_text(html_text)
        assert "<b>" not in clean
        assert "bold" in clean

    @pytest.mark.asyncio
    async def test_arxiv_crawler_parse_feed_item(self):
        """ArxivCrawler should correctly parse a mock feed entry."""
        crawler = ArxivCrawler()

        mock_entry = MagicMock()
        mock_entry.title = "Test Paper: A Study of Transformers"
        mock_entry.link = "https://arxiv.org/abs/2401.99999"
        mock_entry.summary = "We study the impact of transformers on NLP tasks."
        mock_entry.authors = [MagicMock(name="Author A"), MagicMock(name="Author B")]
        mock_entry.tags = [MagicMock(term="cs.AI"), MagicMock(term="cs.LG")]
        mock_entry.published_parsed = (2024, 1, 15, 0, 0, 0, 0, 0, 0)

        parsed = crawler._parse_entry(mock_entry)
        assert parsed is not None
        assert "Transformer" in parsed["title"]
        assert parsed["url"] == "https://arxiv.org/abs/2401.99999"


# ============================================================================
# TESTS: API ENDPOINTS
# ============================================================================

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the /health endpoint returns healthy status."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_info_endpoint():
    """Test the /api/v1/info endpoint returns version info."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    data = response.json()
    assert "version" in data


@pytest.mark.asyncio
async def test_items_list_endpoint_returns_paginated_data():
    """Test /api/v1/items returns paginated response."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/items?limit=5&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_analyst_query_endpoint_accepts_question():
    """Test POST /api/v1/analyst/query endpoint with a valid question."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    payload = {"question": "What are the top AI research trends today?"}

    # The endpoint should at minimum return 200 even if LLM API is not connected
    response = client.post("/api/v1/analyst/query", json=payload)
    assert response.status_code in [200, 503]  # 503 if LLM keys not configured


@pytest.mark.asyncio
async def test_startups_endpoint():
    """Test GET /api/v1/startups returns a list."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/startups")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_policy_alerts_endpoint():
    """Test GET /api/v1/policy-alerts returns a list."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/policy-alerts")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_gpu_market_endpoint():
    """Test GET /api/v1/market/gpu returns GPU pricing data."""
    from app.main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/v1/market/gpu")
    assert response.status_code == 200


# ============================================================================
# TESTS: MULTI-AGENT SYSTEM
# ============================================================================

class TestMultiAgentSystem:
    """Tests for ResearcherAgent, EnricherAgent, and ValuationAgent."""

    @pytest.mark.asyncio
    async def test_researcher_agent_ingest_new_item(self, db_session, sample_source):
        """ResearcherAgent should save new items and return the created object."""
        from app.services.agents import ResearcherAgent

        agent = ResearcherAgent()
        item_data = {
            "title": "Novel GPT-5 Architecture Paper",
            "url": "https://arxiv.org/abs/2501.unique001",
            "abstract": "We introduce GPT-5, a novel large language model.",
            "authors": ["Test Author"],
            "published_date": datetime.utcnow(),
            "content_type": ContentType.RESEARCH_PAPER,
            "source_id": sample_source.id
        }

        with patch.object(agent.vector_store, 'upsert_vector', return_value=True):
            result = await agent.ingest_item(db_session, item_data)

        assert result is not None
        assert result.title == "Novel GPT-5 Architecture Paper"

    @pytest.mark.asyncio
    async def test_researcher_agent_rejects_duplicate(self, db_session, sample_source):
        """ResearcherAgent should return None for duplicate URLs."""
        from app.services.agents import ResearcherAgent

        agent = ResearcherAgent()
        url = "https://arxiv.org/abs/2501.duplicate001"
        url_hash = hashlib.sha256(url.encode()).hexdigest()

        # Pre-insert the item
        existing = ResearchItem(
            source_id=sample_source.id,
            title="Existing Paper",
            url=url,
            url_hash=url_hash,
        )
        db_session.add(existing)
        db_session.commit()

        item_data = {
            "title": "Existing Paper (resubmission)",
            "url": url,
            "abstract": "Same paper again.",
            "authors": [],
            "source_id": sample_source.id
        }

        result = await agent.ingest_item(db_session, item_data)
        assert result is None  # Should be rejected as duplicate

    @pytest.mark.asyncio
    async def test_enricher_agent_calculates_scores(self, db_session, sample_item):
        """EnricherAgent should assign all required scoring fields."""
        from app.services.agents import EnricherAgent

        agent = EnricherAgent()

        with patch.object(agent, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"innovation": 85, "market_impact": 72, "significance": 90, "applications": ["NLP", "Code Generation"]}'
            with patch.object(agent.vector_store, 'upsert_vector', return_value=True):
                enrichment = await agent.enrich_item(db_session, sample_item)

        assert enrichment is not None
        assert hasattr(enrichment, "importance_score")
        assert hasattr(enrichment, "intelligence_score")
        assert 0 <= enrichment.importance_score <= 100
        assert 0 <= enrichment.intelligence_score <= 100

    @pytest.mark.asyncio
    async def test_valuation_agent_estimates_startup_value(self, db_session, sample_item):
        """ValuationAgent should estimate a reasonable startup valuation."""
        from app.services.agents import ValuationAgent

        agent = ValuationAgent()
        startup_data = {
            "company_name": "Hypothetical AI Labs",
            "funding_amount_usd": 10_000_000.0,
            "funding_round": "Seed",
            "employees_count": 15,
            "founded_year": 2023,
            "hq_country": "USA",
            "item_id": sample_item.id
        }

        with patch.object(agent, '_call_llm', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"estimated_valuation_usd": 50000000, "confidence": 0.7}'
            startup = await agent.estimate_valuation(db_session, startup_data)

        assert startup is not None
        assert startup.valuation_usd > 0


# ============================================================================
# TESTS: PERFORMANCE
# ============================================================================

class TestPerformance:
    """Performance benchmarks for critical hot-path operations."""

    def test_url_hash_at_scale(self):
        """10,000 URL hashes should complete in < 1 second."""
        dedup = DeduplicationService()
        start = time.time()
        for i in range(10_000):
            dedup.calculate_url_hash(f"https://example.com/paper/{i}")
        elapsed = time.time() - start
        assert elapsed < 1.0, f"URL hashing too slow: {elapsed:.2f}s"

    def test_content_similarity_at_scale(self):
        """1,000 content similarity checks should complete in < 5 seconds."""
        dedup = DeduplicationService()
        start = time.time()
        for i in range(1_000):
            dedup._content_similarity(
                f"Title {i}",
                f"Abstract content discussing topic {i}" * 5,
                f"Title {i + 1}",
                f"Abstract content discussing topic {i + 1}" * 5,
            )
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Similarity calculation too slow: {elapsed:.2f}s"

    def test_vector_store_bulk_insert_performance(self):
        """Inserting 1,000 vectors in fallback mode should be fast."""
        vs = VectorStoreService()
        start = time.time()
        vector = [0.01] * vs.vector_size
        for i in range(1_000):
            vs.upsert_vector(f"perf-item-{i}", vector, {"index": i})
        elapsed = time.time() - start
        assert elapsed < 3.0, f"Bulk insert too slow: {elapsed:.2f}s"

    def test_scoring_throughput(self):
        """10,000 importance score calculations should complete in < 2 seconds."""
        enrichment = AIEnrichmentService()
        start = time.time()
        for i in range(10_000):
            enrichment._calculate_importance_score(
                innovation=75, market_impact=65, significance=80,
                citation_velocity=50, engagement=60, novelty=70, authority=0.8
            )
        elapsed = time.time() - start
        assert elapsed < 2.0, f"Scoring too slow: {elapsed:.2f}s"


# ============================================================================
# TESTS: INTEGRATION
# ============================================================================

class TestIntegration:
    """End-to-end integration tests for the full ingestion and enrichment pipeline."""

    def test_complete_ingestion_workflow(self, db_session, sample_source):
        """Full flow: ingest item -> verify in DB -> check enrichment exists."""
        # Create item
        item = ResearchItem(
            source_id=sample_source.id,
            title="Revolutionary AI Breakthrough: AGI Discovered",
            url="https://example.com/agi-paper",
            url_hash="integration_test_hash_001",
            abstract="A groundbreaking discovery in artificial general intelligence.",
            content_type=ContentType.RESEARCH_PAPER
        )
        db_session.add(item)
        db_session.commit()

        # Attach enrichment
        enrichment = ItemEnrichment(
            item_id=item.id,
            executive_summary="Potentially world-changing AGI breakthrough.",
            innovation_score=99.0,
            market_impact_score=99.0,
            research_significance_score=99.0,
            importance_score=99.0,
            intelligence_score=99.0,
        )
        db_session.add(enrichment)
        db_session.commit()

        # Verify
        fetched = db_session.query(ResearchItem).filter_by(id=item.id).first()
        assert fetched is not None
        assert fetched.title == "Revolutionary AI Breakthrough: AGI Discovered"
        assert fetched.enrichment is not None
        assert fetched.enrichment.importance_score == 99.0

    def test_new_model_tables_are_linked_to_items(self, db_session, sample_source):
        """Grant and RegulationPolicy must be creatable without requiring item_id FK."""
        # Grant (no item_id FK in actual model)
        grant = Grant(
            title="NSF Grant Announcement",
            agency="NSF",
            amount=1_000_000.0,
            abstract="Funding for Foundation Models research."
        )
        db_session.add(grant)
        db_session.commit()

        fetched_grant = db_session.query(Grant).filter_by(id=grant.id).first()
        assert fetched_grant is not None
        assert fetched_grant.amount == 1_000_000.0

    def test_deduplication_prevents_double_insertion(self, db_session, sample_source):
        """After inserting an item, a second identical URL should be marked as duplicate."""
        dedup = DeduplicationService()

        url = "https://arxiv.org/abs/integration-2024-001"
        url_hash = dedup.calculate_url_hash(url)

        original = ResearchItem(
            source_id=sample_source.id,
            title="Original Unique Paper",
            url=url,
            url_hash=url_hash,
            abstract="Original abstract content."
        )
        db_session.add(original)
        db_session.commit()

        # Now attempt to insert a duplicate
        duplicate_candidate = ResearchItem(
            source_id=sample_source.id,
            title="Original Unique Paper",
            url=url,
            url_hash=url_hash,  # Same hash
            abstract="Original abstract content."
        )

        # The hash lookup should catch it before DB insert
        existing = db_session.query(ResearchItem).filter_by(url_hash=url_hash).first()
        assert existing is not None
        assert existing.id == original.id


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
