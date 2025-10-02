from collections.abc import Mapping, Sequence
from typing import Any, Dict, List, Optional

from lxml import html as lxml_html


FieldState = Dict[str, Any]


def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        value = list(value)
    else:
        value = [value]

    cleaned: List[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def _get_strategy(entry: Any) -> str:
    if isinstance(entry, Mapping):
        return str(entry.get("strategy", "xpath_extractor"))
    return "xpath_extractor"


def _get_xpath(entry: Any) -> Optional[str]:
    if isinstance(entry, Mapping):
        xpath = entry.get("xpath")
    else:
        xpath = entry
    if isinstance(xpath, str):
        xpath = xpath.strip()
        return xpath or None
    return None


def extract_by_xpath_map_from_html(html_content: str, field_state: Dict[str, FieldState]) -> Dict[str, List[str]]:
    """Extract structured content using field definitions.

    Each field may either rely on an XPath expression (``xpath_extractor``)
    or on previously stored natural-language values (``lm_capabilities``).
    The helper gracefully handles both strategies, returning a map of
    ``field -> list[str]`` for downstream formatting.
    """

    result: Dict[str, List[str]] = {}
    tree = None

    for key, entry in field_state.items():
        strategy = _get_strategy(entry)

        if strategy == "lm_capabilities":
            values = []
            if isinstance(entry, Mapping):
                values = _ensure_list(entry.get("value"))
            result[key] = values or ["(No stored value)"]
            continue

        xpath = _get_xpath(entry)
        if not xpath:
            result[key] = ["Skipped: No XPath"]
            continue

        if tree is None:
            tree = lxml_html.fromstring(html_content)

        try:
            values = tree.xpath(xpath)
            clean_values = [
                v.text_content().strip() if isinstance(v, lxml_html.HtmlElement) else str(v).strip()
                for v in values
            ]
            result[key] = clean_values or ["(Empty Result)"]
        except Exception as e:
            result[key] = [f"Error: {e}"]

    return result
