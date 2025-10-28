from ..agent.state import AgentState
from ..json import SchemeValidator, JSON_SCHEME
import json
import os
from langscrape.utils import load_config, get_default_token_usage
from ..tags import TAGS_DICT, df
from typing import List

from typing import Dict, List

# Build once from your DataFrame
keys = df.columns.tolist()
TAGS_DICT = {key: df[key].dropna().tolist() for key in keys}

def _normalizer(allowed: List[str]) -> Dict[str, str]:
    """lowercased -> canonical string mapping"""
    return {str(a).strip().casefold(): str(a).strip() for a in allowed}

# Canon maps for ALL lists you provided
CANON = {
    "THEMES": _normalizer(TAGS_DICT.get("THEMES", [])),
    "COUNTRIES_AND_ORGANIZATIONS": _normalizer(TAGS_DICT.get("COUNTRIES_AND_ORGANIZATIONS", [])),
    "LOCATIONS": _normalizer(TAGS_DICT.get("LOCATIONS", [])),
    "FIGURES": _normalizer(TAGS_DICT.get("FIGURES", [])),
    "TYPES": _normalizer(TAGS_DICT.get("TYPES", [])),
    "MEDIAS": _normalizer(TAGS_DICT.get("MEDIAS", [])),
    "LANGUAGES": _normalizer(TAGS_DICT.get("LANGUAGES", [])),
    "PLATFORMS": _normalizer(TAGS_DICT.get("PLATFORMS", [])),
}

def _clean_list(values: List[str], canon_map: Dict[str, str]) -> List[str]:
    out = []
    for v in values or []:
        if not isinstance(v, str):
            continue
        k = v.strip().casefold()
        if k in canon_map:               # keep only allowed, canonicalized
            out.append(canon_map[k])
    return out

def _canon_or_keep(value: str, canon_map: Dict[str, str]) -> str:
    """Canonicalize single value if known; else keep original (do NOT discard)."""
    if not isinstance(value, str):
        return value
    k = value.strip().casefold()
    return canon_map.get(k, value.strip())

def clean_tags(summary: dict) -> dict:
    """
    - Filters *_tags lists to their allowed sets.
    - Canonicalizes scalar fields (type, media, language, platform) if known; never discards.
    - Example: 'HAMAS' in figures_tags is dropped unless present in FIGURES list.
               'YouTube' in platform is kept; if it's known, it’s canonicalized to the sheet spelling.
    """
    s = dict(summary)  # shallow copy

    # 1) Clean tag lists
    tag_fields = {
        "theme_tags": CANON["THEMES"],
        "countries_and_organizations_tags": CANON["COUNTRIES_AND_ORGANIZATIONS"],
        "location_tags": CANON["LOCATIONS"],
        "figures_tags": CANON["FIGURES"],
    }
    for field, cmap in tag_fields.items():
        current = s.get(field, [])
        s[field] = _clean_list(current if isinstance(current, list) else [], cmap)

    # 2) Canonicalize single-value fields (no dropping)
    scalar_fields = {
        "type": CANON["TYPES"],
        "media": CANON["MEDIAS"],
        "language": CANON["LANGUAGES"],
        "platform": CANON["PLATFORMS"],
    }
    for field, cmap in scalar_fields.items():
        if field in s and isinstance(s[field], str):
            s[field] = _canon_or_keep(s[field], cmap)

    return s

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