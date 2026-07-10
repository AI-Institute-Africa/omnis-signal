#!/usr/bin/env powershell
<#
.SYNOPSIS
    Scraper Hub Startup Script
    
.DESCRIPTION
    This script starts all components of the Scraper Hub system:
    - API server (FastAPI on port 8000)
    - Background worker (RQ)
    - Scheduler (APScheduler)
    
.PARAMETER Mode
    'full' - Run all components
    'api' - API only
    'worker' - Worker only
    'scheduler' - Scheduler only
    'test' - Run tests
    
.PARAMETER Port
    API port (default: 8000)
#>

param(
    [ValidateSet('full', 'api', 'worker', 'scheduler', 'test', 'finalize')]
    [string]$Mode = 'full',
    [int]$Port = 8000,
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Definition -Detailed
    exit 0
}

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Color output
function Write-Status {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] ✅ $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] ⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] ❌ $Message" -ForegroundColor Red
}

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║           SCRAPER HUB - SYSTEM STARTUP                     ║
║     Extract Real-Time Price and Product Data               ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Status "Python found: $pythonVersion"
}
catch {
    Write-Error-Custom "Python not found. Please install Python 3.9+"
    exit 1
}

# Check if in project directory
if (-not (Test-Path "app\main.py")) {
    Write-Error-Custom "Not in project directory. Please run from scraper-hub root."
    exit 1
}

# Ensure .env exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Warning-Custom ".env not found, creating from .env.example"
        Copy-Item ".env.example" ".env"
    }
    else {
        Write-Error-Custom ".env not found and .env.example not available"
        exit 1
    }
}

# Install dependencies if needed
Write-Status "Checking dependencies..."
python -m pip install -q -r requirements.txt --disable-pip-version-check

# Initialize database
Write-Status "Initializing database..."
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

# Run finalization
Write-Status "Running system finalization..."
python finalize_system.py --status

Write-Host ""

# Run based on mode
switch ($Mode) {
    'full' {
        Write-Status "Starting FULL system (API + Worker + Scheduler)..."
        Write-Host ""
        Write-Host "Note: Press Ctrl+C to stop all services" -ForegroundColor Yellow
        Write-Host ""
        
        # Start API in current process
        Write-Status "Starting API on http://localhost:$Port"
        python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
    }
    
    'api' {
        Write-Status "Starting API only on http://localhost:$Port"
        Write-Host "Note: Worker and scheduler not running. Use separate terminals for those." -ForegroundColor Yellow
        Write-Host ""
        python -m uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
    }
    
    'worker' {
        Write-Status "Starting RQ Worker..."
        Write-Host "Note: Make sure Redis is running (redis://localhost:6379)" -ForegroundColor Yellow
        Write-Host ""
        python -m rq worker -u redis://localhost:6379
    }
    
    'scheduler' {
        Write-Status "Starting APScheduler..."
        python -c "from app.scheduler import start_scheduler; start_scheduler()"
    }
    
    'test' {
        Write-Status "Running tests..."
        python -m pytest tests/ -v
    }
    
    'finalize' {
        Write-Status "Running full system finalization..."
        python finalize_system.py --full-finalize
    }
}
