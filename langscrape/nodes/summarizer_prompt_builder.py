from importlib import import_module
from typing import Any, Dict

from ..agent.state import AgentState
from ..utils import (
    DEFAULT_SUMMARIZER_TEMPLATE,
    get_llm,
    load_config,
    render_prompt_template,
)


def _load_allowed_tags(summarizer_config: Dict[str, Any]) -> Any:
    if "allowed_tags" in summarizer_config:
        return summarizer_config.get("allowed_tags") or []

    module_path = summarizer_config.get("allowed_tags_module")
    if module_path:
        module_name, _, attr = module_path.partition(":")
        try:
            module = import_module(module_name)
            attr_name = attr or "ALLOWED_TAGS"
            return getattr(module, attr_name)
        except (ModuleNotFoundError, AttributeError) as exc:
            raise ValueError(
                f"Unable to load allowed tags from '{module_path}'."
            ) from exc

    try:
        module = import_module("config.allowed_tags")
        return getattr(module, "ALLOWED_TAGS")
    except ModuleNotFoundError:
        return []


def _resolve_field_mapping(
    extracted_data: Dict[str, Any],
    mapping: Dict[str, str],
) -> Dict[str, Any]:
    resolved = {}
    for placeholder, field_name in mapping.items():
        resolved[placeholder] = extracted_data.get(field_name, "")
    return resolved


def get_prompt(state: AgentState, config: Dict[str, Any] | None = None) -> str:
    if config is None:
        config = load_config()
    prompts_config = config.get("prompts") or {}
    summarizer_config = prompts_config.get("summarizer", {})

    template = summarizer_config.get("template", DEFAULT_SUMMARIZER_TEMPLATE)

    default_mapping = {
        "title": "title",
        "content": "article_body",
        "author": "author",
        "datetime": "datetime",
    }
    field_mapping = summarizer_config.get("field_mapping", default_mapping)

    extracted_data = state.get("result", {})
    dynamic_fields = _resolve_field_mapping(extracted_data, field_mapping)

    context = {
        "url": state.get("url", ""),
        **dynamic_fields,
        "allowed_tags": _load_allowed_tags(summarizer_config),
    }

    context.update(summarizer_config.get("context", {}))

    return render_prompt_template(template, context)


def summarizer(state: AgentState) -> AgentState:
    config = load_config()
    state["summarizer"] = get_llm(config)
    prompt = get_prompt(state, config)
    state["summary"] = state["summarizer"].invoke(prompt)
    return state
