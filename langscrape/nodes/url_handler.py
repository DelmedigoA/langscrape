from ..agent.state import AgentState
import asyncio
from ..browser.chrome import fetch_html_patchright
from ..html.utils import clean_html_for_extraction3


async def fetch_url(url: str) -> str:
    return await fetch_html_patchright(url)


def url_handler(state: AgentState) -> AgentState:
    url = state["url"]
    html_content = asyncio.run(fetch_url(url))
    print("len before cleaning:", len(html_content))
    cleaned_html = clean_html_for_extraction3(html_content)
    print("len cleaned:", len(cleaned_html))
    return {"cleaned_html_content": cleaned_html}
