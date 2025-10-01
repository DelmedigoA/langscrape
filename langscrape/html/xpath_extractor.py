from lxml import html as lxml_html

def extract_by_xpath_map_from_html(html_content: str, xpath_map: dict[str, str]) -> dict[str, list[str]]:
    """
    Extracts content from HTML using a dict of XPath expressions.
    Skips missing or invalid XPaths and returns trimmed text values.
    """
    tree = lxml_html.fromstring(html_content)
    result = {}

    for key, xp in xpath_map.items():
        if not xp or not isinstance(xp, str) or xp.strip() == "":
            result[key] = ["Skipped: No XPath"]
            continue

        try:
            values = tree.xpath(xp)
            clean_values = [
                v.text_content().strip() if isinstance(v, lxml_html.HtmlElement) else str(v).strip()
                for v in values
            ]
            result[key] = clean_values or ["(Empty Result)"]
        except Exception as e:
            result[key] = [f"Error: {e}"]

    return result
