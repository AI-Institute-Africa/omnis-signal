# Quick Reference Guide

## Getting Started

### Local Setup (5 minutes)
```bash
# 1. Clone & setup
git clone <repo>
cd ai_research_intelligence

# 2. Create environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python -c "from app.db import init_db; init_db()"

# 6. Run in terminals
# Terminal 1: API
uvicorn app.main:app --reload

# Terminal 2: Worker
celery -A app.workers.celery_app worker -l info

# Terminal 3: Scheduler
celery -A app.workers.celery_app beat -l info
```

### Docker Compose Setup (3 minutes)
```bash
# 1. Configure
cp .env.example .env
nano .env

# 2. Start
docker-compose up -d

# 3. Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Monitoring: http://localhost:5555
```

## Common Commands

### Development
```bash
make install          # Install dependencies
make dev             # Run dev server
make test            # Run tests
make lint            # Check code
make format          # Format code
```

### Database
```bash
make db-init         # Initialize DB
make db-stats        # Show statistics
python cli.py db verify  # Verify connection
```

### Docker
```bash
docker-compose up -d     # Start
docker-compose down      # Stop
docker-compose logs -f   # View logs
docker-compose ps        # Show status
```

### CLI Tools
```bash
python cli.py analyze top-items        # Top items
python cli.py analyze trends           # Trending topics
python cli.py sources list             # List sources
python cli.py sources health arxiv     # Source health
python cli.py users list               # List users
python cli.py users create             # Add user
```

## API Endpoints Cheatsheet

### Items
```
GET  /api/v1/items
GET  /api/v1/items/{id}
GET  /api/v1/items/trending/today
GET  /api/v1/items/high-priority
GET  /api/v1/items/by-category/{category}
```

### Trends
```
GET  /api/v1/trends
GET  /api/v1/trends/emerging
```

### Analysis
```
GET  /api/v1/search?q=keyword
GET  /api/v1/intelligence/summary
GET  /api/v1/intelligence/key-findings
```

### Dashboard
```
GET  /api/v1/dashboard/metrics
GET  /api/v1/dashboard/sources-health
GET  /api/v1/dashboard/summary-stats
```

### Health
```
GET  /health
GET  /ready
GET  /api/v1/info
```

## Configuration Reference

### Key Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# APIs
OPENAI_API_KEY=sk-...
DEFAULT_LLM_PROVIDER=openai

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=email@gmail.com
SMTP_PASSWORD=app-password

# Scheduling
DIGEST_SCHEDULE_HOURS=4
CRAWLER_SCHEDULE_MINUTES=15
```

## Troubleshooting

### API not responding
```bash
# Check if running
curl http://localhost:8000/health

# Check logs
docker-compose logs api

# Restart
docker-compose restart api
```

### Database connection error
```bash
# Test connection
psql postgresql://user:pass@localhost:5432/db

# Check PostgreSQL is running
docker-compose ps postgres

# Restart
docker-compose restart postgres
```

### Worker not processing tasks
```bash
# Check worker status
celery -A app.workers.celery_app inspect active

# Check queue
celery -A app.workers.celery_app inspect reserved

# Restart worker
docker-compose restart celery_worker
```

### Email not sending
```bash
# Verify credentials
# Check EMAIL_ENABLED=true in .env
# Review logs
docker-compose logs celery_worker | grep email
```

## File Structure Overview

```
ai_research_intelligence/
├── app/                 # Main application
│   ├── api/            # API endpoints
│   ├── models/         # Database models
│   ├── services/       # Business logic
│   ├── crawlers/       # Data crawlers
│   ├── workers/        # Celery tasks
│   ├── email_service/  # Email handling
│   ├── config.py       # Configuration
│   ├── db.py          # Database setup
│   └── main.py        # FastAPI app
├── tests/              # Tests
├── docs/               # Documentation
├── docker-compose.yml  # Docker orchestration
├── requirements.txt    # Dependencies
└── cli.py             # Command line tool
```

## Performance Tips

### Optimize Queries
```python
# Use select_from for better performance
db.query(ResearchItem).join(ItemEnrichment)...

# Use limit for large datasets
items = db.query(ResearchItem).limit(100).all()

# Use index fields in WHERE clause
query = db.query(ResearchItem).filter(
    ResearchItem.created_at > cutoff
)  # created_at is indexed
```

### Cache Results
```python
# Redis caching (implement in services)
from redis import Redis
redis = Redis.from_url(settings.REDIS_URL)
cached = redis.get(f"items:{category}")
```

### Batch Operations
```python
# Insert many at once (faster than individual inserts)
db.bulk_insert_mappings(ResearchItem, items_list)
```

## Monitoring

### Check System Health
```bash
# Metrics
curl http://localhost:8000/api/v1/dashboard/metrics

# Source health
curl http://localhost:8000/api/v1/dashboard/sources-health

# Summary stats
curl http://localhost:8000/api/v1/dashboard/summary-stats?days=7
```

### Watch Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery_worker

# With timestamps
docker-compose logs -f --timestamps
```

### Monitor Queue
```bash
# Via Flower (http://localhost:5555)
# Via Celery CLI
celery -A app.workers.celery_app inspect active
celery -A app.workers.celery_app inspect scheduled
celery -A app.workers.celery_app purge  # Clear queue
```

## Security Best Practices

1. **Never commit .env files**
   ```bash
   # .gitignore has this, but double-check
   echo ".env" >> .gitignore
   ```

2. **Rotate API Keys**
   ```bash
   # Update in .env and redeploy
   OPENAI_API_KEY=sk-new-key
   ```

3. **Use HTTPS in Production**
   ```bash
   # Configure in reverse proxy (Nginx, etc.)
   # Use Let's Encrypt for certificates
   ```

4. **Enable CORS properly**
   ```python
   # Don't use ["*"] in production
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

## Useful Links

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Flower Monitoring: http://localhost:5555
- GitHub: https://github.com/your-org/air
- Issues: https://github.com/your-org/air/issues

## Support & Help

```bash
# Show all CLI commands
python cli.py --help

# Get help for specific command
python cli.py analyze --help

# View logs with grep
docker-compose logs api | grep ERROR

# Clean up everything
docker-compose down -v
```

---

**Last Updated**: 2024  
**Version**: 1.0.0
