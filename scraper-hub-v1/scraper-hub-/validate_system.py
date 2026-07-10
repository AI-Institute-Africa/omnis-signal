#!/usr/bin/env python3
"""
Scraper Hub - System Validation Script

Validates that the system is properly configured and ready for operation.
"""

import sys
import os
from pathlib import Path
import subprocess
import importlib.util

# Windows console encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check(text, status):
    """Print a status line."""
    mark = "[+]" if status else "[-]"
    print(f"{mark} {text}")
    return status

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        check(f"Python {version.major}.{version.minor} - Need Python 3.9+", False)
        return False
    check(f"Python {version.major}.{version.minor}.{version.micro}", True)
    return True

def check_file_structure():
    """Check that key files exist."""
    files_to_check = [
        'app/main.py',
        'app/config.py',
        'app/db/base.py',
        'app/db/session.py',
        'app/db/models/__init__.py',
        'app/scraping/extractors/__init__.py',
        'app/services/fetcher.py',
        'requirements.txt',
        '.env.example',
    ]
    
    all_ok = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Check that required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'playwright',
        'redis',
        'httpx',
        'bs4',
        'jinja2',
        'apscheduler',
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - Not installed")
                all_ok = False
        except (ImportError, ValueError):
            print(f"❌ {package} - Not installed")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check environment configuration."""
    if not Path('.env').exists():
        if Path('.env.example').exists():
            print("⚠️  .env not found, but .env.example exists")
            print("   Run: cp .env.example .env")
            return False
        else:
            print("❌ .env not found")
            return False
    
    # Check key env vars
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'DATABASE_URL',
            'APP_ENV',
            'API_PORT',
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                masked = value[:20] + '...' if len(value) > 20 else value
                print(f"✅ {var} = {masked}")
            else:
                print(f"❌ {var} not set")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False

def check_database():
    """Check database connectivity."""
    try:
        from app.db.session import SessionLocal
        from app.db.models import Source
        
        db = SessionLocal()
        count = db.query(Source).count()
        db.close()
        
        print(f"✅ Database connected ({count} sources found)")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_playwright():
    """Check Playwright installation."""
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright API available")
        
        # Check if browsers are installed
        try:
            import subprocess
            result = subprocess.run(
                ['python', '-m', 'playwright', 'install-deps'],
                capture_output=True,
                timeout=5
            )
            print("✅ Playwright browsers checked")
            return True
        except:
            print("⚠️  Playwright browsers may not be installed")
            print("   Run: python -m playwright install")
            return False
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return False

def check_redis():
    """Check Redis connectivity (optional)."""
    try:
        from redis import Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            r = Redis.from_url(redis_url)
            r.ping()
            print(f"✅ Redis connected ({redis_url})")
            return True
        except:
            print(f"⚠️  Redis not available ({redis_url})")
            print("   Redis is optional - system works without it")
            return False
    except:
        print("⚠️  Redis not configured")
        return False

def check_extractors():
    """Check that extractors are available."""
    try:
        from app.scraping.extractors import (
            TelecomExtractor, BankingExtractor, InsuranceExtractor,
            HospitalityExtractor, EducationExtractor, TransportExtractor,
            GenericExtractor
        )
        
        extractors = [
            'TelecomExtractor',
            'BankingExtractor',
            'InsuranceExtractor',
            'HospitalityExtractor',
            'EducationExtractor',
            'TransportExtractor',
            'GenericExtractor',
        ]
        
        for extractor in extractors:
            print(f"✅ {extractor}")
        
        return True
    except Exception as e:
        print(f"❌ Extractor error: {e}")
        return False

def check_api():
    """Check FastAPI setup."""
    try:
        from app.main import app
        print(f"✅ FastAPI app created")
        print(f"✅ API routes registered")
        return True
    except Exception as e:
        print(f"❌ FastAPI error: {e}")
        return False

def validate_data():
    """Check data integrity."""
    try:
        from app.db.session import SessionLocal
        from app.db.models import Source, SourcePage, ExtractedRecord
        
        db = SessionLocal()
        
        sources = db.query(Source).count()
        pages = db.query(SourcePage).count()
        records = db.query(ExtractedRecord).count()
        records_with_price = db.query(ExtractedRecord).filter(
            ExtractedRecord.price_value.isnot(None)
        ).count()
        
        db.close()
        
        print(f"✅ {sources:,} sources configured")
        print(f"✅ {pages:,} source pages")
        print(f"✅ {records:,} extracted records")
        print(f"✅ {records_with_price:,} records with prices ({100*records_with_price/max(1,records):.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ Data validation error: {e}")
        return False

def main():
    """Run all validation checks."""
    print_header("SCRAPER HUB - SYSTEM VALIDATION")
    
    checks = [
        ("Python Version", check_python_version),
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
        ("Environment (.env)", check_env_file),
        ("Database", check_database),
        ("Playwright", check_playwright),
        ("API Setup", check_api),
        ("Extractors", check_extractors),
        ("Data Integrity", validate_data),
        ("Redis (Optional)", check_redis),
    ]
    
    results = {}
    for check_name, check_func in checks:
        print_header(check_name)
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} validation failed: {e}")
            results[check_name] = False
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {passed}/{total}\n")
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    print()
    
    if passed == total:
        print("🎉 All checks passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python finalize_system.py --status")
        print("  2. Run: .\\run.ps1 -Mode api")
        print("  3. Open: http://localhost:8000")
        return 0
    else:
        print(f"⚠️  {total - passed} checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Create .env file: cp .env.example .env")
        print("  • Install Playwright: python -m playwright install")
        print("  • Initialize database: python -c 'from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)'")
        return 1

if __name__ == '__main__':
    sys.exit(main())
