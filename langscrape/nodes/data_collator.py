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

def data_collator(state: AgentState) -> AgentState:
    final_json = {'meta_data': {'url': state.get("url", "")}}

    base_result = state.get("extracted_fields") or state.get("extracted_fields") or {}
    final_json['extraction'] = dict(base_result)

    summary_message = state.get("summary")
    summary_raw = getattr(summary_message, "content", "")
    try:
        summary_json = extract_json_block(summary_raw)
    except json.JSONDecodeError:
        summary_json = {}

    if isinstance(summary_json, dict):
        final_json['summary'] = summary_json

    

    output_dir = config.get("output_dir", "data")
    os.makedirs(output_dir, exist_ok=True)
    filename = state.get("url", "output").rstrip("/").split("/")[-1] or "output"
    output_path = os.path.join(output_dir, f"{filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    return {"result": final_json}
