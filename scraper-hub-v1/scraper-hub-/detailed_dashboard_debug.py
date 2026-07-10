import os
import sys
import asyncio
from unittest.mock import MagicMock
from sqlalchemy import func

# Add project root to path
sys.path.append(os.getcwd())

from app.web.router import dashboard
from app.db.session import SessionLocal
from app.db.models import Source, ExtractedRecord, RawSnapshot

async def debug_dashboard():
    db = SessionLocal()
    request = MagicMock()
    # Mocking jinja context
    request.app.state.templates = MagicMock()
    
    log_file = "dashboard_debug_log.txt"
    with open(log_file, "w") as f:
        f.write("Starting Dashboard Debug...\n")
        try:
            f.write("Fetching counts...\n")
            sources_count = db.query(Source).count()
            records_count = db.query(ExtractedRecord).count()
            f.write(f"Sources: {sources_count}, Records: {records_count}\n")
            
            f.write("Fetching markets...\n")
            market_results = db.query(
                ExtractedRecord.market, 
                func.count(ExtractedRecord.id)
            ).group_by(ExtractedRecord.market).all()
            f.write(f"Markets raw: {market_results}\n")
            
            f.write("Calling dashboard route...\n")
            # We need to mock the templates.TemplateResponse to see if it fails inside
            from app.web.router import templates
            
            # Save original
            original_render = templates.TemplateResponse
            
            def mock_render(name, context):
                f.write(f"TemplateResponse called with {name}\n")
                f.write(f"Context keys: {list(context.keys())}\n")
                # Try to actually render it to catch Jinja errors
                from jinja2 import Environment, FileSystemLoader
                env = Environment(loader=FileSystemLoader('app/templates'))
                template = env.get_template(name)
                # Remove request from context for plain jinja render as it's a mock
                clean_context = {k: v for k, v in context.items() if k != 'request'}
                template.render(**clean_context)
                f.write("Jinja rendering successful!\n")
                return MagicMock()

            import app.web.router
            app.web.router.templates.TemplateResponse = mock_render
            
            await dashboard(request, db)
            
            # Restore
            app.web.router.templates.TemplateResponse = original_render
            f.write("Dashboard route execution finished successfully!\n")
            
        except Exception as e:
            f.write(f"ERROR: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        finally:
            db.close()

if __name__ == "__main__":
    asyncio.run(debug_dashboard())
