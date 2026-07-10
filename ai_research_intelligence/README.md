# AI Research Intelligence Platform

A production-grade, enterprise-level AI research monitoring and analysis system that continuously discovers, analyzes, and distributes the latest AI research papers, news, model releases, and industry developments in real-time.

## 🎯 Overview

The AI Research Intelligence Platform is a hedge-fund-grade system designed to:

- **Monitor** AI research from 15+ sources in real-time
- **Analyze** new content with AI-powered enrichment (summaries, scoring)
- **Rank** items by importance using multi-factor scoring (0-100)
- **Detect** emerging trends and viral content
- **Alert** users immediately for high-priority items
- **Report** 4-hour digest summaries
- **Archive** all historical data for trend analysis
- **Predict** impact, virality, and startup valuations
- **Track** AI company metrics and funding activity

## ✨ Key Features

### Real-Time Monitoring
- **11 Research Sources**: arXiv, Papers with Code, OpenReview, Hugging Face, Google Research, DeepMind, Anthropic, OpenAI, Microsoft Research, Meta, NVIDIA
- **8 News Sources**: TechCrunch, VentureBeat, MIT Technology Review, The Verge, Reuters, AI News, Analytics India, Towards Data Science
- **Community Sources**: Reddit, Hacker News, X/Twitter, LinkedIn, GitHub

### AI Enrichment Pipeline
Each discovered item receives:
- **Executive Summary** (business-friendly)
- **Technical Summary** (deep technical details)
- **Business Impact Analysis**
- **Key Insights & Applications**
- **Research Gaps Identification**

### Advanced Scoring System
- **Innovation Score** (0-100)
- **Market Impact Score** (0-100)
- **Research Significance Score** (0-100)
- **Citation Velocity Prediction**
- **Social Engagement Score**
- **Technical Novelty Score**
- **Importance Score** (0-100, composite)
- **Intelligence Score** (0-100, hedge-fund grade)
- **Virality Prediction** (0-1)
- **Impact Prediction** (0-1)

### Email Alerts & Digests
- **Immediate Alerts**: For items with importance score > 85
- **4-Hour Digests**: Aggregated reports with top papers, news, releases, trends
- **Professional HTML Templates**: Enterprise-quality, responsive design
- **Email Tracking**: Open rates, click tracking, delivery confirmation

### Trend Detection
- Fast-rising topics identification
- Emerging models tracking
- New benchmarks detection
- Startup announcements
- Funding activity monitoring
- Patent tracking

### Deduplication Engine
- URL-based deduplication
- Title/abstract similarity matching
- Content-based embedding similarity
- Prevents duplicate alerts

### Monitoring & Observability
- Real-time dashboard metrics
- Source health monitoring
- Email delivery success rates
- Processing latency tracking
- Trending topics visualization

## 🏗️ Architecture

### Tech Stack
- **Language**: Python 3.13
- **API**: FastAPI with uvicorn
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Broker**: Redis
- **Task Queue**: Celery
- **Scheduler**: APScheduler
- **Vector DB**: Qdrant (for embeddings)
- **Web Scraping**: Playwright, BeautifulSoup, feedparser
- **LLMs**: OpenAI GPT-4, Anthropic Claude-3, LiteLLM
- **Containerization**: Docker & Docker Compose

### System Architecture

```
┌─────────────────────────────────────────────────┐
│          CRAWLERS (15+ Sources)                 │
│  arXiv, TechCrunch, GitHub, Papers w/ Code...  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      INGESTION PIPELINE                         │
│  - URL Hashing  - Deduplication                │
│  - Metadata Extraction                          │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      AI ENRICHMENT PIPELINE                     │
│  - Summaries (GPT-4/Claude-3)                  │
│  - Scoring (0-100)                            │
│  - Classification                              │
│  - Embeddings (Vector DB)                     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      ALERT ENGINE                               │
│  - Real-time (score > 85)                      │
│  - 4-Hour Digests                              │
│  - Email Delivery                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      STORAGE & ANALYSIS                         │
│  - PostgreSQL (Relational)                     │
│  - Redis (Cache)                               │
│  - Qdrant (Vectors)                            │
│  - Trend Detection                             │
│  - Historical Archives                         │
└─────────────────────────────────────────────────┘
```

### Component Structure

```
ai_research_intelligence/
├── app/
│   ├── api/                  # FastAPI endpoints
│   │   └── research.py       # Research data endpoints
│   ├── models/               # SQLAlchemy ORM models
│   │   └── __init__.py       # All database models
│   ├── services/             # Business logic
│   │   ├── enrichment.py     # AI enrichment service
│   │   └── deduplication.py  # Duplicate detection
│   ├── crawlers/             # Data crawlers
│   │   └── base.py           # Base + specific crawlers
│   ├── workers/              # Celery tasks & scheduling
│   │   ├── celery_app.py     # Celery configuration
│   │   └── tasks.py          # Task definitions
│   ├── email_service/        # Email handling
│   │   └── sender.py         # Email service
│   ├── utils/                # Helper utilities
│   ├── config.py             # Configuration management
│   ├── db.py                 # Database connection
│   └── main.py               # FastAPI application
├── tests/                    # Test suite
├── migrations/               # Database migrations
├── templates/                # Email templates
├── docs/                     # Documentation
├── docker-compose.yml        # Docker Compose orchestration
├── Dockerfile                # API container
├── Dockerfile.worker         # Worker container
├── Dockerfile.beat          # Scheduler container
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.13 (for local development)
- PostgreSQL 16+ (optional, Docker handles it)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   cd ai_research_intelligence
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the platform**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Monitoring: http://localhost:5555 (Flower)

### Local Development

1. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**
   ```bash
   # PostgreSQL should be running
   export DATABASE_URL="postgresql://user:password@localhost:5432/ai_research_intelligence"
   ```

4. **Initialize database**
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

5. **Run API server**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Run Celery worker** (in separate terminal)
   ```bash
   celery -A app.workers.celery_app worker -l info
   ```

7. **Run Celery beat** (in separate terminal)
   ```bash
   celery -A app.workers.celery_app beat -l info
   ```

## 📊 API Endpoints

### Research Items
- `GET /api/v1/items` - List items with filtering
- `GET /api/v1/items/{id}` - Get specific item
- `GET /api/v1/items/trending/today` - Today's trending items
- `GET /api/v1/items/high-priority` - Items with score > 85
- `GET /api/v1/items/by-category/{category}` - Items by category

### Trends
- `GET /api/v1/trends` - All detected trends
- `GET /api/v1/trends/emerging` - Emerging trends (>50% growth)

### Search & Intelligence
- `GET /api/v1/search?q=query` - Full-text search
- `GET /api/v1/intelligence/summary` - AI intelligence summary
- `GET /api/v1/intelligence/key-findings` - Key research findings

### Dashboard & Monitoring
- `GET /api/v1/dashboard/metrics` - System metrics
- `GET /api/v1/dashboard/sources-health` - Source health status
- `GET /api/v1/dashboard/summary-stats` - Summary statistics

### Health
- `GET /health` - Health check
- `GET /ready` - Readiness check

## ⚙️ Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_research_intelligence
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379/0

# APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_LLM_PROVIDER=openai  # openai | anthropic | litellm

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=ai-research@yourdomain.com
EMAIL_ENABLED=true

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=ai_research

# Scheduling
DIGEST_SCHEDULE_HOURS=4
CRAWLER_SCHEDULE_MINUTES=15
DEDUPLICATION_SCHEDULE_MINUTES=30
TREND_ANALYSIS_SCHEDULE_MINUTES=60

# Alerts
HIGH_PRIORITY_SCORE_THRESHOLD=85
MEDIUM_PRIORITY_SCORE_THRESHOLD=65

# Environment
ENVIRONMENT=production  # development | staging | production
DEBUG=false
```

## 🔄 Scheduling & Automation

### Scheduled Tasks
- **Every 15 minutes**: Crawl arXiv, TechCrunch, GitHub
- **Every 5 minutes**: Process new items (enrich, alert)
- **Every 30 minutes**: Deduplication
- **Every 60 minutes**: Trend detection
- **Every 4 hours**: Send digest reports
- **Every 30 minutes**: Update source health

All tasks are managed by Celery Beat and can be monitored via Flower UI at http://localhost:5555

## 📧 Email Alerts

### Alert Trigger
- **Score > 85**: Immediate email alert
- **Score 65-85**: Included in 4-hour digest
- **Score < 65**: Archive only

### Email Types
1. **Real-Time Alerts** - Single high-priority item
2. **Digest Reports** - 4-hour aggregated summary
3. **Trend Reports** - Weekly trend analysis (optional)

## 🤖 AI Scoring System

### Importance Score Calculation
```
Importance = (
    Innovation * 0.25 +
    Market_Impact * 0.20 +
    Significance * 0.20 +
    Citation_Velocity * 0.15 +
    Social_Engagement * 0.10 +
    Technical_Novelty * 0.10
) * Authority_Boost
```

### Intelligence Score (Hedge-Fund Grade)
```
Intelligence = (
    Importance * 0.30 +
    Impact_Prediction * 0.30 +
    Market_Impact * 0.25 +
    Virality_Prediction * 0.10 +
    Significance * 0.05
)
```

Higher intelligence score = higher institutional investment potential

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=app tests/
```

### Sample Test
```python
def test_enrichment_service():
    service = AIEnrichmentService()
    # Test implementation
    assert service is not None
```

## 📈 Monitoring

### Available Metrics
- Total items collected
- Items by category
- High-priority alerts sent
- Email delivery success rate
- Source availability
- Processing latency
- Trending topics

### Access Monitoring
- **Flower Dashboard**: http://localhost:5555
- **API Metrics**: GET `/api/v1/dashboard/metrics`
- **Logs**: Docker container logs

## 🔐 Security

### Implemented
- SQL injection prevention (SQLAlchemy)
- Input validation (Pydantic)
- Rate limiting (configurable)
- Secrets management (environment variables)
- HTTPS ready
- CORS configuration
- API key authentication (planned)

### Best Practices
- Store sensitive data in environment variables
- Use `.env` file (never commit)
- Rotate API keys regularly
- Enable email verification
- Use HTTPS in production
- Implement rate limiting
- Monitor access logs

## 🚢 Production Deployment

### Kubernetes Ready
The system is containerized and ready for Kubernetes deployment:

```bash
# Build images
docker build -t air-api:latest -f Dockerfile .
docker build -t air-worker:latest -f Dockerfile.worker .
docker build -t air-beat:latest -f Dockerfile.beat .

# Push to registry
docker push your-registry/air-api:latest
docker push your-registry/air-worker:latest
docker push your-registry/air-beat:latest
```

### AWS Deployment
- Use RDS for PostgreSQL
- Use ElastiCache for Redis
- Use ECR for Docker images
- Use ECS for container orchestration
- Use SES for email
- Use CloudWatch for monitoring

### GCP Deployment
- Use Cloud SQL for PostgreSQL
- Use Memorystore for Redis
- Use Artifact Registry for Docker
- Use Cloud Run or GKE
- Use Cloud Tasks for scheduling
- Use Cloud Logging

## 📚 Documentation

### Additional Docs
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Database Schema](docs/SCHEMA.md)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📜 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@airesearchintel.com
- **Docs**: https://docs.airesearchintel.com

## 🎉 Acknowledgments

- Built with FastAPI, SQLAlchemy, and Celery
- AI enrichment powered by OpenAI and Anthropic
- Vector embeddings via Qdrant
- Community resources from arXiv, GitHub, HuggingFace

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
