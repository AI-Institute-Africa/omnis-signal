#!/bin/bash
# Scraper Hub Startup Script (Linux/Mac)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

MODE=${1:-full}
PORT=${2:-8000}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           SCRAPER HUB - SYSTEM STARTUP                     ║"
    echo "║     Extract Real-Time Price and Product Data               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

print_header

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found. Please install Python 3.9+"
    exit 1
fi

python_version=$(python3 --version)
print_status "Python found: $python_version"

# Check if in project directory
if [ ! -f "app/main.py" ]; then
    print_error "Not in project directory. Please run from scraper-hub root."
    exit 1
fi

# Ensure .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env not found, creating from .env.example"
        cp .env.example .env
    else
        print_error ".env not found and .env.example not available"
        exit 1
    fi
fi

# Install dependencies
print_status "Checking dependencies..."
pip3 install -q -r requirements.txt --disable-pip-version-check

# Initialize database
print_status "Initializing database..."
python3 -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

# Run finalization
print_status "Running system finalization..."
python3 finalize_system.py --status

echo ""

# Run based on mode
case $MODE in
    full)
        print_status "Starting FULL system (API + Worker + Scheduler)..."
        echo ""
        echo -e "${YELLOW}Note: Press Ctrl+C to stop all services${NC}"
        echo ""
        print_status "Starting API on http://localhost:$PORT"
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
        ;;
    
    api)
        print_status "Starting API only on http://localhost:$PORT"
        echo -e "${YELLOW}Note: Worker and scheduler not running. Use separate terminals for those.${NC}"
        echo ""
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
        ;;
    
    worker)
        print_status "Starting RQ Worker..."
        echo -e "${YELLOW}Note: Make sure Redis is running (redis://localhost:6379)${NC}"
        echo ""
        python3 -m rq worker -u redis://localhost:6379
        ;;
    
    scheduler)
        print_status "Starting APScheduler..."
        python3 -c "from app.scheduler import start_scheduler; start_scheduler()"
        ;;
    
    test)
        print_status "Running tests..."
        python3 -m pytest tests/ -v
        ;;
    
    finalize)
        print_status "Running full system finalization..."
        python3 finalize_system.py --full-finalize
        ;;
    
    *)
        print_error "Unknown mode: $MODE"
        echo "Usage: ./run.sh [full|api|worker|scheduler|test|finalize] [port]"
        exit 1
        ;;
esac
