import re
import requests
import pymupdf
from urllib.parse import urlparse
from ..browser.request import simple_url_to_html

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

    content = simple_url_to_html(url)
    # open directly from bytes
    pdf = pymupdf.open(stream=content, filetype="pdf")

    text = get_joined_text(pdf)
    if normalize:
        return text_normalizer(text)
    return text
