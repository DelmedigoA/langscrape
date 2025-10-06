import json
import os
import re

from ..agent.state import AgentState
from ..utils import load_config

config = load_config()

def extract_json_block(text: str) -> dict:
    """
    Extract a JSON object from text.
    Supports fenced ```json blocks and bare {…} JSON.
    Returns {} if nothing valid found.
    """
    if not text or not isinstance(text, str):
        return {}

    text = text.strip()

    # 1. fenced ```json blocks (case-insensitive)
    match = re.search(r"```json\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # try fallback

    # 2. bare JSON object anywhere in the string
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group(0).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # still malformed, fallback

    # 3. final attempt: parse entire text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
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
