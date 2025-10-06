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
    final_json = {'meta_data': {'id': state['id'],'url': state.get("url", "")}}

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

    


    return {"result": final_json}
