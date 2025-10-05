import json
import os
import re

from ..agent.state import AgentState
from ..utils import load_config

config = load_config()

def extract_json_block(text):
    match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return {}

def output_formatter(state: AgentState) -> AgentState:
    base_result = state.get("extracted_fields") or state.get("extracted_fields") or {}
    result = dict(base_result)

    summary_message = state.get("summary")
    summary_raw = getattr(summary_message, "content", "")
    try:
        summary_json = extract_json_block(summary_raw)
    except json.JSONDecodeError:
        summary_json = {}

    if isinstance(summary_json, dict):
        result.update(summary_json)

    result.setdefault("url", state.get("url", ""))

    output_dir = config.get("output_dir", "data")
    os.makedirs(output_dir, exist_ok=True)
    filename = state.get("url", "output").rstrip("/").split("/")[-1] or "output"
    output_path = os.path.join(output_dir, f"{filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return {"result": result}
