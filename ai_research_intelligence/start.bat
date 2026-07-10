@echo off
REM AI Research Intelligence Platform - Startup Script

echo.
echo ============================================================
echo   AI Research Intelligence Platform - Startup
echo ============================================================
echo.

REM Check if Docker is running
echo [1/5] Checking Docker status...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Docker daemon is not running!
    echo.
    echo Please start Docker Desktop by:
    echo   1. Press Windows Key + S
    echo   2. Search for "Docker Desktop"
    echo   3. Click to launch
    echo   4. Wait for it to fully start (2-3 minutes)
    echo   5. Then run this script again
    echo.
    pause
    exit /b 1
)

echo [✓] Docker is running

REM Change to project directory
echo [2/5] Navigating to project directory...
cd /d "%~dp0"
echo [✓] In project directory

REM Check if .env exists
echo [3/5] Checking environment configuration...
if not exist .env (
    echo [✓] Creating .env from template...
    copy .env.example .env >nul
    echo [!] IMPORTANT: Edit .env to add your API keys:
    echo    - OPENAI_API_KEY
    echo    - ANTHROPIC_API_KEY
    echo    - SMTP credentials (if email enabled^)
    echo.
    echo Opening .env in notepad...
    start notepad .env
    pause
)
echo [✓] .env configured

REM Start Docker Compose
echo [4/5] Starting services with Docker Compose...
echo.
docker-compose up -d

REM Check status
echo.
echo [5/5] Verifying services...
timeout /t 5 >nul
docker-compose ps

REM Display information
echo.
echo ============================================================
echo   System Started Successfully!
echo ============================================================
echo.
echo Access Points:
echo   API Documentation:  http://localhost:8000/docs
echo   API (Redoc):        http://localhost:8000/redoc
echo   Health Check:       http://localhost:8000/health
echo   Monitoring (Flower): http://localhost:5555
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop the system:
echo   docker-compose down
echo.
echo ============================================================
echo.
pause
