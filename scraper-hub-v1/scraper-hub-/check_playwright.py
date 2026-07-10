import asyncio
from playwright.async_api import async_playwright

async def check_browsers():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            print("Chromium browser available")
            await browser.close()
        except Exception as e:
            print(f"Chromium not available: {e}")

asyncio.run(check_browsers())