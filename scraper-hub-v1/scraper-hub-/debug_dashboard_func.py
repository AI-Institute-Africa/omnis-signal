import os
import sys
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from app.web.router import dashboard
from app.db.session import SessionLocal

async def test_dashboard_func():
    db = SessionLocal()
    request = MagicMock()
    # Mocking jinja context
    request.app.state.templates = MagicMock()
    
    try:
        print("Calling dashboard function...")
        response = await dashboard(request, db)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_dashboard_func())
