import asyncio
from patchright.async_api import async_playwright

USER_DATA_DIR = "/tmp/patchright-profile"

async def fetch_html_patchright(url: str) -> str:
    """
    Fetch full HTML using Patchright (stealth Playwright fork).
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            no_viewport=True,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-gpu",
            ]
        )

        page = await browser.new_page()
        print(f"Navigating to {url} ...")
        try:
            await page.goto(url)
            await page.wait_for_timeout(3000)
            html = await page.content()
            print(f"HTML fetched ({len(html)} chars)")
        except Exception as e:
            print(f"Failed to fetch: {e}")
            html = ""
        finally:
            await browser.close()

        return html