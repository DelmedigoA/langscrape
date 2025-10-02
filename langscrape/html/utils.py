import re
from lxml import html as lxml_html, etree
from bs4 import BeautifulSoup
from feilian.soup_tools import clean_html as feilian_clean_html, extract_html_structure

def clean_html_for_extraction3(html_content: str) -> str:
    """
    Hybrid HTML cleaner combining lxml + FeiLian (BeautifulSoup).
    """

    parser = lxml_html.HTMLParser(remove_comments=True)
    tree = lxml_html.fromstring(html_content, parser=parser)

    # Remove junk tags entirely
    remove_tags = ["script", "style", "noscript", "iframe", "form", "svg"]
    etree.strip_elements(tree, *remove_tags, with_tail=False)

    # Remove elements with ad/tracker keywords in class/id
    bad_keywords = [
        "advert", "promo", "banner", "cookie", "footer", "nav", "subscribe", "tracking"
    ]
    for el in tree.xpath("//*"):
        classes = " ".join(el.get("class", "").lower().split())
        ids = " ".join(el.get("id", "").lower().split())
        if any(word in classes or word in ids for word in bad_keywords):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

    # Remove empty elements
    for el in tree.xpath("//*[not(normalize-space()) and not(.//img)]"):
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)

    # Convert to string (pre-cleaned HTML)
    precleaned_html = etree.tostring(tree, encoding="unicode", pretty_print=False)

    soup = BeautifulSoup(precleaned_html, "html5lib")
    soup = feilian_clean_html(soup)

    # Convert back to string
    cleaned_html = str(soup)

    cleaned_html = re.sub(r"\s+", " ", cleaned_html)
    return cleaned_html.strip()
