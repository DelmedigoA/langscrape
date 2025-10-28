from ..agent.state import AgentState
from ..json import SchemeValidator, JSON_SCHEME
import json
import os
from langscrape.utils import load_config, get_default_token_usage
from ..tags import keys, LOCATIONS, LANGUAGES, FIGURES, COUNTRIES_AND_ORGANIZATIONS, THEMES, PLATFORMS, TYPES, MEDIAS
from typing import List

JSON_SCHEME = {
    "title_in_english": "The title of the content in english",
    "title_in_hebrew": "The title of the content in hebrew",
    "author_in_english": "The content's author name (string, empty if unknown) in english",
    "author_in_hebrew": "The content's author name (string, empty if unknown) in hebrew",
    "publication_date": "YYYY-MM-DD",
    "language": "The primary language of the content",
    "type": "One of the content types listed above",
    "media": "One of the media types listed above",
    "platform": "The website or platform where the content is published",
    "source": "The original issuer of the information (e.g., UN, IDF, MoH). If the publisher is the original issuer, match platform",
    "reference": "Canonical link to the primary document or official source cited (string, empty if none)",
    "summary_in_enlgish": "One clear, informative sentence summarizing the main content, in english",
    "summary_in_hebrew": "One clear, informative sentence summarizing the main content, in hebrew",
    "event_start_date": "YYYY-MM-DD",
    "event_end_date": "YYYY-MM-DD",
    "theme_tags": ["relevant", "theme", "tags"],
    "countries_and_organizations_tags": ["relevant", "countries_and_organizations", "tags"],
    "location_tags": ["relevant", "location", "tags"],
    "figures_tags": ["relevant", "figures", "tags"]
}


def clean_tags(summary: dict) -> dict:
    tags = {
            "location_tags": LOCATIONS,
            "type": TYPES,
            "platform": PLATFORMS, 
            "media": MEDIAS,
            "language": LANGUAGES,
            "figures_tags": FIGURES,
            "countries_and_organizations_tags": COUNTRIES_AND_ORGANIZATIONS,
            "theme_tags": THEMES
            }

    for key, TAGS in tags.items():
        predicted_tags = summary.get(key, [])
        if isinstance(predicted_tags, list):
            summary[key] = [predicted_tag for predicted_tag in predicted_tags if predicted_tag in TAGS]
        else:
            predicted_tags = [predicted_tags]
            summary[key] = [predicted_tag for predicted_tag in predicted_tags if predicted_tag in TAGS]
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
    token_usage = state.get("token_usage") or get_default_token_usage()
    meta_data = state['result'].setdefault('meta_data', {})
    meta_data["is_valid_scheme"] = is_valid
    meta_data["token_usage"] = token_usage
    output_dir = config.get("output_dir", "data")
    os.makedirs(output_dir, exist_ok=True)
    filename = state.get("url", "output").rstrip("/").split("/")[-1] or "output"
    output_path = os.path.join(output_dir, f"{filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(state['result'], f, ensure_ascii=False, indent=2)
    logging_path = os.path.join(output_dir, "logging.json")
    if os.path.exists(logging_path):
        try:
            with open(logging_path, "r", encoding="utf-8") as log_file:
                logging_data = json.load(log_file) or {}
        except json.JSONDecodeError:
            logging_data = {}
    else:
        logging_data = {}

    log_key = state.get("id") or state.get("url") or filename
    logging_data[str(log_key)] = {
        "id": state.get("id"),
        "url": state.get("url"),
        "traditional_flag": state.get("traditional_flag", []),
        "token_usage": token_usage,
    }

    with open(logging_path, "w", encoding="utf-8") as log_file:
        json.dump(logging_data, log_file, ensure_ascii=False, indent=2)
    return {
        "result": {
            "meta_data": {
                "is_valid_scheme": is_valid,
                "validation_report": validation_report,
            },
            'summary': cleaned_summary
        }
    }