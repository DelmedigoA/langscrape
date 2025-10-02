"""Utility helpers for running Langscrape extractions from the UI."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath
from langscrape.utils import get_llm, load_config

DEFAULT_FIELDS: List[str] = [
    "title",
    "author",
    "datetime",
    "article_body",
]


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, str)):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "\n\n".join(parts)
    return str(value)


def run_extraction(url: str, config: Optional[Dict[str, object]] = None, llm=None) -> Dict[str, str]:
    """Execute the Langscrape pipeline for a single URL."""

    if config is None:
        config = load_config()

    base_llm = llm or get_llm(config)

    global_state = {field: None for field in DEFAULT_FIELDS}
    store_xpath = make_store_xpath(global_state)
    tools = [store_xpath]
    graph = get_graph(tools=tools)

    llm_with_tools = base_llm.bind_tools(tools)

    initial_state = {
        "messages": [],
        "url": url,
        "global_state": global_state,
        "llm_with_tools": llm_with_tools,
    }

    final_state = graph.invoke(initial_state)
    raw_result = final_state.get("result", {})

    formatted: Dict[str, str] = {}
    for field in DEFAULT_FIELDS:
        formatted[field] = _stringify(raw_result.get(field))
    return formatted


__all__ = ["DEFAULT_FIELDS", "run_extraction"]
