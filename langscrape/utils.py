import json
import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

DEFAULT_REASONER_TEMPLATE = """You are a ReAct-style HTML extraction agent.

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
{{xpath_snapshot}}

FIELD STRATEGIES:
{{field_strategies}}

CURRENT EXTRACTIONS SUMMARY:
{{formatted_extracts}}

HTML:
{{html_content}}
"""

DEFAULT_SUMMARIZER_TEMPLATE = """Analyze this content and extract specific metadata.

URL: {{url}}
Title: {{title}}
Author: {{author}}
Date: {{datetime}}
Content: {{content}}

Instructions:
1. For dates:
- Publication date: When the content was published
- Event date: When the described events occurred
- Use YYYY-MM-DD format
- For date ranges use: YYYY-MM-DD to YYYY-MM-DD
- If only month/year available, use first day: YYYY-MM-01
- If no date is available, return an empty string

2. For content type, classify as:
- Official Report: Research papers, formal investigations, detailed reports
- Official Statement: Press releases, announcements, declarations
- Opinion: Editorial content, opinion pieces, commentary
- Testimony: First-hand accounts, witness statements
- Journalistic Report: News articles, investigative journalism
- Analysis: Analysis, commentary
- Open letter: Letters to the editor, letters to the government, letters to the media
- News: Breaking news, time-sensitive reporting
- Post: Social media posts, short updates

3. For media type, classify as:
- Video: Video content, broadcasts
- Photo: Photo galleries, image-focused content
- Audio: Audio content, podcasts
- Text: Text content, articles, reports

4. For tags:
- IMPORTANT: You must ONLY use tags from the following list. DO NOT create any new tags:
{{allowed_tags}}
- Select ONLY the most relevant tags from this list that are reflected in the content
- Format as an array of strings
- If no tags from the list apply, return an empty array

Return a JSON object with these exact fields:

{
    "summary": "One clear, informative sentence summarizing the main content",
    "date_published": "YYYY-MM-DD",
    "event_date": "YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD",
    "type": "One of the content types listed above",
    "media": "One of the media types listed above",
    "language": "The primary language of the content",
    "platform": "The website or platform where content is published",
    "author": "The content author or organization",
    "tags": ["relevant", "topic", "tags"]
}
- All string values (including "summary" and "tags") **must be in English**.

Important
- Even if the content is in non-english language (e.g: Hebrew, French etc...) your output should be in *English*.
- Extract information only from the provided content
- Leave field empty ("") if information is not explicitly present
- For platform, extract from the URL or content source
- For language, specify if clearly identifiable
- Tags should ONLY be from the provided list, do not create new ones
- Search for publication date in the content's metadata
- If no publication date is found, use the creation date of the content
- Always return content processed in English
"""

_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def load_config(path: str = "config/default_config.yaml") -> dict:
    """Load YAML config into a Python dict."""
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_prompt_template(template: str, context: Dict[str, Any]) -> str:
    """Replace ``{{placeholder}}`` tokens with values from ``context``."""

    def _replacement(match: re.Match) -> str:
        key = match.group(1).strip()
        value = context.get(key, "")
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)

    return _PLACEHOLDER_PATTERN.sub(_replacement, template)


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
    config = state.get("config") if isinstance(state, dict) else None
    if config is None:
        config = load_config()

    prompts_config = (config.get("prompts") or {})
    reasoner_config = prompts_config.get("reasoner", {})
    template = reasoner_config.get("template", DEFAULT_REASONER_TEMPLATE)

    extra_context = reasoner_config.get("context", {})
    content = render_prompt_template(
        template,
        {
            "formatted_extracts": formatted_extracts,
            "xpath_snapshot": _format_xpath_snapshot(state["global_state"]),
            "field_strategies": _format_field_strategies(state["global_state"]),
            "html_content": state["cleaned_html_content"],
            **extra_context,
        },
    )

    return SystemMessage(content=content)


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
