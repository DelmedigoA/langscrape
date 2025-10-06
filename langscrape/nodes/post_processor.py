from ..agent.state import AgentState
from ..json import SchemeValidator, JSON_SCHEME
import json
import os
from langscrape.utils import load_config

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
            }
        }
    }