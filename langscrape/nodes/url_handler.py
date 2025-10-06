from ..agent.state import AgentState
import asyncio
from ..browser.chrome import fetch_html_patchright
from ..html.utils import clean_html_for_extraction3
from ..exceptions import TooShortHtml, InvalidUrl
from ..utils import load_config
from urllib.parse import urlparse
from ..browser.request import simple_url_to_html

async def fetch_url(url: str) -> str:
    return await fetch_html_patchright(url)

def apply_html_logic(html, min_len = load_config()['exceptions']['min_html_length']) -> None:
    html_len = len(html)
    if html_len < min_len:
        raise TooShortHtml(html_len)

def validate_url(url: str) -> None:
    """Raise InvalidUrl if URL is missing scheme or netloc."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise InvalidUrl(url)

def url_handler(state: AgentState) -> AgentState:
    url = state["url"]
    validate_url(url)
    html_content = asyncio.run(fetch_url(url))
    cleaned_html = clean_html_for_extraction3(html_content)
    try:
        apply_html_logic(cleaned_html)
    except TooShortHtml:
        html_content = simple_url_to_html(url)
        cleaned_html = clean_html_for_extraction3(html_content)
        apply_html_logic(cleaned_html)
    cleaned_html = clean_html_for_extraction3(html_content)
    return {"cleaned_html_content": cleaned_html}
