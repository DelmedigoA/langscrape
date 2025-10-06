import json
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from .html.xpath_extractor import extract_by_xpath_map_from_html

def load_config(path: str = "config/default_config.yaml") -> dict:
    """
    Load YAML config into a Python dict.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def get_extractor(config=None):
    if config is None:
        config = load_config()

    if config["extractor"]["provider"] == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config["extractor"]["name"],
            temperature=config["extractor"]["temperature"],
            top_p=config["extractor"]["top_p"],
            api_key=api_key
        )
    elif config["extractor"]["provider"] == "deepseek":
        api_key = os.getenv("DS_API_KEY")
        return ChatDeepSeek(
            model=config["extractor"]["name"],
            temperature=config["extractor"]["temperature"],
            top_p=config["extractor"]["top_p"],
            api_key=api_key
        )
    else:
        raise NameError(f"{config['extractor']['type']} is not supported.")

def get_summarizer(config=None):
    if config is None:
        config = load_config()

    if config["summarizer"]["provider"] == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config["summarizer"]["name"],
            temperature=config["summarizer"]["temperature"],
            top_p=config["summarizer"]["top_p"],
            api_key=api_key
        )
    elif config["summarizer"]["provider"] == "deepseek":
        api_key = os.getenv("DS_API_KEY")
        return ChatDeepSeek(
            model=config["summarizer"]["name"],
            temperature=config["summarizer"]["temperature"],
            top_p=config["summarizer"]["top_p"],
            api_key=api_key
        )
    else:
        raise NameError(f"{config['summarizer']['type']} is not supported.")

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


def get_system_prompt(state, formatted_extracts, iters):
    if iters == 1:
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
    {state['cleaned_content']}
    """
        )
    else:
        return SystemMessage(content=f"""                  
    Reasoning Rules Reminder:
                             
    - **author** → should look like a human name, max 3-4 words.
    - **article_body** → should be a long coherent article.
    - **title** → should be a the article title.
    - **datetime** → should look like a publication date or time.
                             
    CURRENT XPATH MAP:
    {_format_xpath_snapshot(state['global_state'])}

    FIELD STRATEGIES:
    {_format_field_strategies(state['global_state'])}

    CURRENT EXTRACTIONS SUMMARY:
    {formatted_extracts}

    HTML:
    USE THE PROVIDED HTML ABOVE.""")


def get_formatted_extracts(current_extracts):
    lines = []
    for key, vals in current_extracts.items():
        vals = vals or []
        clean_vals = [str(v).strip() for v in vals if str(v).strip()]
        if not all(
            c in {"'Skipped: No XPath'", "(Empty Result)", "(No stored value)"}
            for c in clean_vals
        ):
            joined = " ".join(clean_vals)
            preview = joined[:200]
            info = f"len={len(joined)}; preview={preview}"
        else:
            info = "XPATH not found or empty; Try a different one."
        lines.append(f"{key}: {info}")
    return "\n".join(lines)


def final_print(global_state, html_content):

    # 🎨 ANSI color codes
    BLUE = "\033[94m"  
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{BLUE}=== FINAL XPATH STATE ==={RESET}")
    for k, v in global_state.items():
        if isinstance(v, dict):
            strategy = v.get("strategy", "xpath_extractor")
            if strategy == "lm_capabilities":
                detail = v.get("value")
            else:
                detail = v.get("xpath")
            print(f"{BLUE}{k}{RESET} ({strategy}): {detail}")
        else:
            print(f"{BLUE}{k}{RESET}: {v}")

    print(f"\n{BOLD}{GREEN}=== FINAL EXTRACTED CONTENT ==={RESET}")
    results = extract_by_xpath_map_from_html(html_content, field_state=global_state)
    for k, v in results.items():
        joined = " | ".join(v)
        print(f"{GREEN}{k}{RESET}: {joined}")
    
    return None
