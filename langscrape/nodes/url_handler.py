from ..agent.state import AgentState
import asyncio
from ..browser.chrome import fetch_html_patchright
from ..html.utils import clean_html_for_extraction3
from ..errors import TooShortHtml
from ..utils import load_config

async def fetch_url(url: str) -> str:
    return await fetch_html_patchright(url)

def apply_html_logic(html, min_len = load_config()['exceptions']['min_html_length']) -> None:
    html_len = len(html)
    if html_len < min_len:
        raise TooShortHtml(html_len)

def url_handler(state: AgentState) -> AgentState:
    url = state["url"]
    html_content = asyncio.run(fetch_url(url))
    cleaned_html = clean_html_for_extraction3(html_content)
    apply_html_logic(cleaned_html)
    return {"cleaned_html_content": cleaned_html}
