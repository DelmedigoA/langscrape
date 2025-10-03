import re
import requests
import pymupdf
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


def collapse_dots(text: str) -> str:
    return re.sub(r"\.{2,}", ".", text)


def text_normalizer(text: str) -> str:
    text = collapse_dots(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_joined_text(pdf) -> str:
    texts = [p.get_text() for p in pdf]
    return " ".join(texts)


def pdfurl_to_text(url: str, normalize: bool = True) -> str:
    """
    Download PDF from URL (in-memory), extract, normalize, and return text.
    """
    headers = _get_headers(url)
    r = requests.get(url, headers=headers)

    # open directly from bytes
    pdf = pymupdf.open(stream=r.content, filetype="pdf")

    text = get_joined_text(pdf)
    if normalize:
        return text_normalizer(text)
    return text
