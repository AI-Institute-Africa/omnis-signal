# System Startup Guide

## Current Status

✅ **All system files created and ready**  
⏸️ **Docker daemon not running** - Needs to be started

## How to Start the System

### **Option 1: Windows (Easiest)**

#### Step 1: Start Docker Desktop
1. Press `Windows Key + S` to open Search
2. Type **"Docker Desktop"**
3. Click to launch
4. **Wait 2-3 minutes** for Docker to fully start
   - You'll see a whale icon in the system tray
   - Icon should show "Docker Desktop is running"

#### Step 2: Run the Startup Script
1. Navigate to the project folder: `ai_research_intelligence`
2. Double-click **`start.bat`**
3. The script will:
   - Verify Docker is running
   - Set up your `.env` file
   - Start all services
   - Show you access points

### **Option 2: Windows (Manual)**

```powershell
# 1. Start Docker Desktop first (see Step 1 above)

# 2. Navigate to project
cd "c:\Users\USER 2\Downloads\scraper-hub-v1 (2) - Copy\ai_research_intelligence"

# 3. Copy environment config (if not done)
copy .env.example .env

# 4. Start all services
docker-compose up -d

# 5. Check status
docker-compose ps

# 6. View logs
docker-compose logs -f
```

### **Option 3: Linux/macOS**

```bash
# 1. Ensure Docker is running
sudo systemctl start docker    # Linux
# or: Docker should auto-start on Mac

# 2. Navigate to project
cd ai_research_intelligence

# 3. Make startup script executable
chmod +x start.sh

# 4. Run startup script
./start.sh

# Or manually:
cp .env.example .env
docker-compose up -d
docker-compose ps
```

## What Gets Started

When you run the system, Docker Compose will start **8 services**:

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Primary database |
| **Redis** | 6379 | Cache & message broker |
| **Qdrant** | 6333 | Vector database |
| **API (FastAPI)** | 8000 | Main REST API |
| **Celery Worker** | — | Task processing |
| **Celery Beat** | — | Job scheduling |
| **Flower** | 5555 | Task monitoring |
| **pgAdmin** | — | Database management |

## Access the System

Once running, access these URLs:

### 🚀 **Primary Access Points**

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | API root |
| http://localhost:8000/docs | **Swagger UI (Interactive API Docs)** ⭐ |
| http://localhost:8000/redoc | ReDoc (Alternative API Docs) |
| http://localhost:8000/health | System health check |
| http://localhost:5555 | **Flower (Task Monitoring)** ⭐ |

### 💾 **Management**

| URL | Purpose |
|-----|---------|
| http://localhost:5432 | PostgreSQL (use psql client) |
| http://localhost:6379 | Redis (use redis-cli) |
| http://localhost:6333 | Qdrant dashboard |

## First Steps After Startup

### 1. Verify System Health
```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-11T...",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. Check Database
```bash
curl http://localhost:8000/api/v1/dashboard/metrics
```

### 3. View API Documentation
Open http://localhost:8000/docs in your browser
- Try **GET /health** endpoint
- Try **GET /api/v1/items** (will be empty initially)

### 4. Monitor Tasks (Flower)
Open http://localhost:5555 in your browser
- Shows active tasks
- Shows task history
- Shows worker status

### 5. View Real-Time Logs
```bash
docker-compose logs -f
# Or specific service:
docker-compose logs -f api
docker-compose logs -f celery_worker
```

## Important Configuration

### Edit Environment Variables
The system will auto-create `.env` from `.env.example`. 

**To use AI features (optional)**, add your API keys:

```bash
# Edit this file
nano .env   # or use Notepad on Windows
```

Configure these for full functionality:
```env
# For AI enrichment (required for summaries/scoring)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For email alerts (optional)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_ENABLED=true

# For custom settings
ENVIRONMENT=production
DEBUG=false
```

## Common Commands

### View System Status
```bash
docker-compose ps
```

### View All Logs
```bash
docker-compose logs -f
```

### View Specific Service Logs
```bash
docker-compose logs -f api
docker-compose logs -f celery_worker
docker-compose logs -f postgres
```

### Access Database
```bash
docker-compose exec postgres psql -U airesearch -d ai_research_intelligence
```

### Restart Services
```bash
docker-compose restart api
docker-compose restart celery_worker
```

### Stop All Services
```bash
docker-compose down
```

### Stop and Remove All Data
```bash
docker-compose down -v
```

## Troubleshooting

### Issue: "Docker daemon not running"
**Solution**: Start Docker Desktop
- Windows: Search for "Docker Desktop" and click to launch
- Wait 2-3 minutes for it to fully start
- Check system tray for whale icon

### Issue: Ports Already in Use
**Solution**: Stop conflicting services or change ports
```bash
# Find what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Or change ports in docker-compose.yml
```

### Issue: Database Connection Error
**Solution**: Give PostgreSQL time to start
```bash
docker-compose logs postgres
docker-compose restart postgres
```

### Issue: Services Keep Restarting
**Solution**: Check logs for errors
```bash
docker-compose logs --tail=50
```

### Issue: Out of Disk Space
**Solution**: Clean up Docker
```bash
docker system prune -a --volumes
```

## Next Steps

1. ✅ Start Docker Desktop
2. ✅ Run `start.bat` (or manual commands)
3. ✅ Wait for all services to be healthy (2-3 minutes)
4. ✅ Open http://localhost:8000/docs
5. ✅ Test API endpoints
6. ✅ View Flower at http://localhost:5555
7. ✅ Add API keys to `.env` for full functionality

## System Architecture Reminder

```
Crawlers (15+ sources)
        ↓
    Ingestion
        ↓
  AI Enrichment (GPT-4/Claude-3)
        ↓
  Scoring (0-100)
        ↓
  ├→ Email Alerts (score > 85)
  └→ Archive + Digest Reports
        ↓
   PostgreSQL + Redis
        ↓
  API Endpoints
        ↓
   User Dashboard
```

## Getting Help

### View CLI Commands
```bash
python cli.py --help
```

### Get command help
```bash
python cli.py analyze --help
python cli.py sources --help
```

### Check README
See `README.md` for complete documentation

### Check Architecture Docs
See `docs/ARCHITECTURE.md` for system design

---

**Status**: ✅ Ready to Start  
**Version**: 1.0.0  
**Last Updated**: 2026-06-11
