from ..agent.state import AgentState
import asyncio
from ..browser.chrome import fetch_html_patchright
from ..html.utils import clean_html_for_extraction3
from ..exceptions import TooShortHtml, InvalidUrl
from ..utils import load_config
from urllib.parse import urlparse
from ..browser.request import simple_url_to_html
from ..pdf.pdf_utils import pdfurl_to_text

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

def _is_pdf(url):
    return str(url).lower().endswith(".pdf")

def url_handler(state: AgentState) -> AgentState:
    url = state["url"]
    validate_url(url)
    url_is_pdf = _is_pdf(url)
    if url_is_pdf:
        pdf_text = pdfurl_to_text(url, normalize=True)
        return {"cleaned_content": pdf_text, "url_is_pdf": url_is_pdf}
    else:
        html_content = asyncio.run(fetch_url(url))
        cleaned_html = clean_html_for_extraction3(html_content)
        try:
            apply_html_logic(cleaned_html)
        except TooShortHtml:
            html_content = simple_url_to_html(url)
            cleaned_html = clean_html_for_extraction3(html_content)
            apply_html_logic(cleaned_html)
        cleaned_html = clean_html_for_extraction3(html_content)
        print("html len:", len(cleaned_html))
        return {"cleaned_content": cleaned_html, "url_is_pdf": url_is_pdf}
