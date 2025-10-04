import json
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

def load_config(path: str = "config/default_config.yaml") -> dict:
    """
    Load YAML config into a Python dict.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def get_llm(config=None):
    if config is None:
        config = load_config()

    if config["llm"]["provider"] == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    elif config["llm"]["provider"] == "deepseek":
        api_key = os.getenv("DS_API_KEY")
        return ChatDeepSeek(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    else:
        raise NameError(f"{config['llm']['type']} is not supported. try")

def initialize_global_state(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    field_definitions = config.get("fields", {}) or {}
    global_state: Dict[str, Dict[str, Any]] = {}

    for field, spec in field_definitions.items():
        spec = spec or {}
        strategy = spec.get("strategy", "xpath_extractor")
        entry: Dict[str, Any] = {"strategy": strategy}
        if strategy == "xpath_extractor":
            if "xpath" in spec:
                entry["xpath"] = spec["xpath"]
        else:
            entry["value"] = []
        global_state[field] = entry

    return global_state


def _format_field_strategies(global_state: Dict[str, Dict[str, Any]]) -> str:
    lines = []
    for field, entry in global_state.items():
        strategy = (entry or {}).get("strategy", "xpath_extractor")
        if strategy == "lm_capabilities":
            label = "LM Capabilities (use `store_field_value` to save answers)"
        else:
            label = "XPath Extractor (use `store_xpath` to refine selectors)"
        lines.append(f"- {field}: {label}")
    return "\n".join(lines) or "(none)"


def _format_xpath_snapshot(global_state: Dict[str, Dict[str, Any]]) -> str:
    snapshot = {}
    for field, entry in global_state.items():
        if isinstance(entry, dict) and entry.get("strategy") == "xpath_extractor":
            snapshot[field] = entry.get("xpath")
    return json.dumps(snapshot, ensure_ascii=False, indent=2)

def get_system_prompt(state, formatted_extracts):
    return SystemMessage(
        content=f"""You are a ReAct-style HTML extraction agent.

GOAL:
Ensure each field has the correct extracted TEXT from the HTML.
XPath is just a tool; the objective is accurate content.

Reasoning Rules:
- **author** → should look like a human name, max 3-4 words.
- **article_body** → should be a long coherent article.
- **title** → should be a the article title.
- **datetime** → should look like a publication date or time.

ACTION POLICY:
For every field:
- Follow the field strategy declared below.
- If the field uses XPath and the extracted text is empty, irrelevant, too short, or violates the rules → call the tool:
    store_xpath(key, new_xpath)
  to propose a **better XPath**.
- If the field relies on LM Capabilities, store the final answer using:
    store_field_value(key, value)
- If more than one cool tool is necessary, you should call multiple tools at a time.
- If all of the extraction looks plausible and correct → do nothing.
Stop when **all fields pass** these checks and LM fields have stored values.

When proposing XPath, follow these strict rules:
- Always use real tag names (div, section, span, time, h1, p, etc.)
- Never use class names as tag names.
- Use `contains(@class, '...')` to target classes.
- Always start with '//' or '/html' and separate each tag with '/'.

Example:
✅ //section[contains(@class, 'article-body')]//p/text()
❌ /html/body/main/article/section/article-details-body-container/article-body

CURRENT XPATH MAP:
{_format_xpath_snapshot(state['global_state'])}

FIELD STRATEGIES:
{_format_field_strategies(state['global_state'])}

CURRENT EXTRACTIONS SUMMARY:
{formatted_extracts}

HTML:
{state['cleaned_html_content']}
"""
    )

def get_formatted_extracts(current_extracts):
    lines = []
    for key, vals in current_extracts.items():
        vals = vals or []
        clean_vals = [str(v).strip() for v in vals if str(v).strip()]
        if not all(
            c in {"'Skipped: No XPath'", "(Empty Result)", "(No stored value)"}
            for c in clean_vals
        ):
            joined = " | ".join(clean_vals)
            preview = joined[:200]
            info = f"len={len(joined)}; preview={preview}"
        else:
            info = "XPATH not found or empty; Try a different one."
        lines.append(f"{key}: {info}")
    return "\n".join(lines)