import logging
import sys
import asyncio
from playwright.async_api import async_playwright
from app.config import settings

# Ensure ProactorEventLoop on Windows for subprocess support
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    def __init__(self):
        self.headless = settings.PLAYWRIGHT_HEADLESS
        self.timeout = settings.PLAYWRIGHT_TIMEOUT_MS

    async def fetch_page_content(self, url: str) -> str:
        """Fetch the HTML content of a web page using Playwright."""
        import random
        print(f"[FETCHER] Starting fetch for {url}, headless={self.headless}, timeout={self.timeout}")
        
        try:
            # Try direct async first
            return await self._fetch_async(url, random)
        except NotImplementedError as e:
            # Fall back to thread executor on Windows when async subprocess creation fails
            print(f"[FETCHER] Async subprocess failed, trying thread pool...")
            import concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(pool, self._fetch_sync, url, random)
    
    async def _fetch_async(self, url: str, random_module) -> str:
        """Async fetch using Playwright."""
        try:
            async with async_playwright() as p:
                # Use randomized user agents
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                ]
                
                browser = await p.chromium.launch(headless=self.headless)
                print(f"[FETCHER] Browser launched successfully")
                try:
                    context = await browser.new_context(
                        user_agent=random_module.choice(user_agents),
                        viewport={'width': 1920, 'height': 1080},
                        extra_http_headers={
                            "Accept-Language": "en-US,en;q=0.9",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                            "Referer": "https://www.google.com/"
                        },
                        ignore_https_errors=True
                    )
                    page = await context.new_page()
                    
                    # Add randomized delay before navigating - reduced
                    await page.wait_for_timeout(random_module.randint(500, 1500))
                    
                    # Try with longer timeout and different wait conditions
                    print(f"[FETCHER] Navigating to {url}")
                    try:
                        await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                        print(f"[FETCHER] Page navigated successfully")
                    except:
                        # Fallback
                        print(f"[FETCHER] First goto failed, trying fallback...")
                        await page.goto(url, timeout=self.timeout, wait_until="load")
                        print(f"[FETCHER] Fallback goto succeeded")
                    
                    # Extra wait for dynamic content - reduced
                    await page.wait_for_timeout(2000)
                    
                    # Scroll a bit to trigger lazy loading
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                    await page.wait_for_timeout(1000)
                    
                    content = await page.content()
                    
                    # Basic check for blocked content
                    if len(content) < 1000 and ("blocked" in content.lower() or "challenge" in content.lower() or "cloudflare" in content.lower()):
                        logger.warning(f"Likely block detected for {url}. Content length: {len(content)}")
                    
                    return content
                finally:
                    await browser.close()
        except NotImplementedError as nie:
            # This is the Windows asyncio subprocess issue - re-raise to trigger fallback
            print(f"[FETCHER] NotImplementedError in async: {nie}")
            raise
        except Exception as e:
            import traceback
            error_type = type(e).__name__
            error_msg = str(e)
            tb_msg = traceback.format_exc()
            print(f"[FETCHER] Exception caught in async: {error_type}")
            print(f"[FETCHER] Error message: '{error_msg}'")
            print(f"[FETCHER] Traceback: {tb_msg}")
            logger.error(f"Error fetching {url}: {error_type}: {error_msg}")
            logger.error(f"Traceback: {tb_msg}")
            raise
    
    def _fetch_sync(self, url: str, random_module) -> str:
        """Synchronous fetch using Playwright (for thread pool executor fallback)."""
        import random
        from playwright.sync_api import sync_playwright
        
        print(f"[FETCHER-SYNC] Starting sync fetch for {url}")
        
        with sync_playwright() as p:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
            
            browser = p.chromium.launch(headless=self.headless)
            print(f"[FETCHER-SYNC] Browser launched")
            try:
                context = browser.new_context(
                    user_agent=random.choice(user_agents),
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "Referer": "https://www.google.com/"
                    },
                    ignore_https_errors=True
                )
                page = context.new_page()
                
                # Add delay
                import time
                time.sleep(random.uniform(0.5, 1.5))
                
                # Navigate
                print(f"[FETCHER-SYNC] Navigating to {url}")
                try:
                    page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                    print(f"[FETCHER-SYNC] Page navigated successfully")
                except:
                    print(f"[FETCHER-SYNC] First goto failed, trying fallback...")
                    page.goto(url, timeout=self.timeout, wait_until="load")
                    print(f"[FETCHER-SYNC] Fallback goto succeeded")
                
                # Wait and scroll
                time.sleep(2)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                time.sleep(1)
                
                content = page.content()
                print(f"[FETCHER-SYNC] Content retrieved: {len(content)} bytes")
                return content
            except Exception as e:
                import traceback
                error_type = type(e).__name__
                error_msg = str(e)
                tb_msg = traceback.format_exc()
                print(f"[FETCHER-SYNC] Exception: {error_type}: {error_msg}")
                print(f"[FETCHER-SYNC] Traceback: {tb_msg}")
                logger.error(f"Sync fetch error for {url}: {error_type}: {error_msg}")
                logger.error(f"Traceback: {tb_msg}")
                raise
            finally:
                browser.close()


