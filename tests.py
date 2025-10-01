import asyncio
from langscrape import fetch_html_patchright

async def fetch_url(url):
    result = await fetch_html_patchright(url)
    print(result[:2000])


some_url = "https://www.ynet.co.il/news/article/s1j00pj9nge"
result = asyncio.run(fetch_url(some_url))
