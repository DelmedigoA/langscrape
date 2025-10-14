# tools/store_xpath.py
from typing import Any, Dict, List

from langchain_core.tools import tool

def _normalize_state_entry(state_dict: Dict[str, Any], key: str) -> Dict[str, Any]:
    entry = state_dict.setdefault(key, {})
    if not isinstance(entry, dict):
        entry = {"strategy": "xpath_extractor", "xpath": entry}
    entry.setdefault("strategy", "xpath_extractor")
    state_dict[key] = entry
    return entry

def make_store_xpath(state_dict: dict):
    @tool
    def store_xpath(key: str, xpath: str):
        """Store a new XPath under a given key in the injected state_dict."""

        entry = _normalize_state_entry(state_dict, key)
        entry["strategy"] = entry.get("strategy", "xpath_extractor")
        if entry["strategy"] != "xpath_extractor":
            return (
                f"Field '{key}' is configured for '{entry['strategy']}', so XPaths are ignored."
            )

        entry["xpath"] = xpath
        entry.pop("value", None)
        state_dict[key] = entry
        return f"Stored XPath for '{key}': {xpath}"
    return store_xpath

def make_store_value(state_dict: dict):
    @tool
    def store_field_value(key: str, value: Any):
        """Store a natural-language value for a field managed by the LLM."""

        entry = _normalize_state_entry(state_dict, key)
        strategy = entry.get("strategy", "xpath_extractor")
        if strategy != "lm_capabilities":
            return (
                f"Field '{key}' is configured for '{strategy}', so `store_field_value` is disabled. "
                "Update the configuration if you want to handle this field with LM capabilities."
            )

        if isinstance(value, str):
            values: List[str] = [value]
        elif isinstance(value, list):
            values = [str(v) for v in value if str(v).strip()]
        else:
            values = [str(value)]

        entry["value"] = values
        entry.pop("xpath", None)
        state_dict[key] = entry
        return f"Stored value for '{key}': {values}"
    return store_field_value
