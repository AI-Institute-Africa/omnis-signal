#!/bin/bash
# AI Research Intelligence Platform - Startup Script (Linux/macOS)

echo ""
echo "============================================================"
echo "  AI Research Intelligence Platform - Startup"
echo "============================================================"
echo ""

# Check if Docker is running
echo "[1/5] Checking Docker status..."
if ! docker ps > /dev/null 2>&1; then
    echo ""
    echo "ERROR: Docker daemon is not running!"
    echo ""
    echo "Please start Docker by running:"
    echo "  sudo systemctl start docker"
    echo ""
    exit 1
fi
echo "[✓] Docker is running"

# Navigate to project directory
echo "[2/5] Navigating to project directory..."
cd "$(dirname "$0")"
echo "[✓] In project directory"

# Check environment
echo "[3/5] Checking environment configuration..."
if [ ! -f .env ]; then
    echo "[✓] Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env to add your API keys:"
    echo "  - OPENAI_API_KEY"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - SMTP credentials (if email enabled)"
    echo ""
    echo "Opening .env..."
    ${EDITOR:-nano} .env
fi
echo "[✓] .env configured"

# Start services
echo "[4/5] Starting services with Docker Compose..."
echo ""
docker-compose up -d

# Verify
echo ""
echo "[5/5] Verifying services..."
sleep 5
docker-compose ps

# Display info
echo ""
echo "============================================================"
echo "  System Started Successfully!"
echo "============================================================"
echo ""
echo "Access Points:"
echo "  API Documentation:  http://localhost:8000/docs"
echo "  API (Redoc):        http://localhost:8000/redoc"
echo "  Health Check:       http://localhost:8000/health"
echo "  Monitoring (Flower): http://localhost:5555"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the system:"
echo "  docker-compose down"
echo ""
echo "============================================================"
echo ""
