import requests
from urllib.parse import urlparse

def _get_referer(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"

def _get_headers(url: str) -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Referer": _get_referer(url),
    }

def simple_url_to_html(url: str) -> str:
    """
    Download PDF from URL (in-memory), extract, normalize, and return text.
    """
    headers = _get_headers(url)
    r = requests.get(url, headers=headers)
    return r.content