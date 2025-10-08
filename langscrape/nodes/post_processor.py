from ..agent.state import AgentState
from ..json import SchemeValidator, JSON_SCHEME
import json
import os
from langscrape.utils import load_config
from ..tags import LOCATIONS, FIGURES, COUNTRIES_AND_ORGANIZATIONS, THEME_TAGS
from typing import List

from typing import List



def clean_tags(summary: dict, TAGS: List[str] = LOCATIONS + FIGURES + COUNTRIES_AND_ORGANIZATIONS + THEME_TAGS) -> dict:
    """
    Clean each tag list in summary by keeping only tags that appear in TAGS.

    Args:
        summary (dict): A dictionary with keys like 'locational_tags', 'figures_tags', etc.
        TAGS (List[str]): Allowed tags.

    Returns:
        dict: Updated summary with cleaned tag lists.
    """
    tag_keys = [
        "locational_tags",
        "figures_tags",
        "countries_and_organizations_tags",
        "theme_tags",
    ]

    for key in tag_keys:
        tags = summary.get(key, [])
        if isinstance(tags, list):
            summary[key] = [tag for tag in tags if tag in TAGS]
        else:
            summary[key] = []  # ensure consistent type

    return summary



def post_processor(state: AgentState) -> AgentState:
    """
    Validate the extracted summary against JSON_SCHEME and
    attach validation metadata to state['result']['meta_data'].
    """ 
    config = load_config()

    summary = (
        state.get("result", {})
             .get("summary", {})
             if isinstance(state.get("result", {}).get("summary", {}), dict)
             else {}
    )
    cleaned_summary = clean_tags(summary)
    scheme_validator = SchemeValidator(
        scheme=JSON_SCHEME,
        data=summary,
    )

    validation_report = scheme_validator.generate_report()

    is_valid = (
        validation_report["all_data_keys_in_scheme"]
        and validation_report["all_scheme_keys_in_data"]
    )
    state['result']['meta_data']["is_valid_scheme"] = is_valid
    output_dir = config.get("output_dir", "data")
    os.makedirs(output_dir, exist_ok=True)
    filename = state.get("url", "output").rstrip("/").split("/")[-1] or "output"
    output_path = os.path.join(output_dir, f"{filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(state['result'], f, ensure_ascii=False, indent=2)
    return {
        "result": {
            "meta_data": {
                "is_valid_scheme": is_valid,
                "validation_report": validation_report,
            },
            'summary': cleaned_summary
        }
    }