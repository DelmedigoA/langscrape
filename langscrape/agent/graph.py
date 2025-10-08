from copy import deepcopy
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Dict, Literal, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .state import AgentState
from ..nodes.data_collator import data_collator
from ..nodes.extraction_reasoner import extraction_reasoner
from ..nodes.feature_binder import feature_binder
from ..nodes.post_processor import post_processor
from ..nodes.summarizer import summarizer
from ..nodes.url_handler import url_handler
from ..utils import load_config


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Safely parse an ISO-8601 datetime string into a datetime object."""

    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _instrument_node(
    node_callable: Callable[[AgentState], AgentState],
    node_name: str,
    timeout_seconds: Optional[float],
):
    """Wrap a node callable to record timing metadata and enforce timeouts."""

    def wrapper(state: AgentState) -> AgentState:
        prior_measurements = state.get("time_measurements") or {}
        pipeline_snapshot = prior_measurements.get("__pipeline__", {})

        now = datetime.now(timezone.utc)
        if timeout_seconds is not None:
            pipeline_start = _parse_iso_datetime(pipeline_snapshot.get("start_time"))
            if pipeline_start is not None:
                elapsed_before = (now - pipeline_start).total_seconds()
                if elapsed_before > timeout_seconds:
                    raise TimeoutError(
                        (
                            f"Graph execution exceeded timeout of {timeout_seconds} seconds "
                            f"before running '{node_name}'. Elapsed: {elapsed_before:.3f}s"
                        )
                    )

        start_dt = now
        start_perf = perf_counter()
        result = node_callable(state)
        end_perf = perf_counter()
        end_dt = datetime.now(timezone.utc)

        node_duration = end_perf - start_perf

        measurements: Dict[str, Dict[str, Any]] = deepcopy(prior_measurements)
        measurements[node_name] = {
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_seconds": round(node_duration, 6),
        }

        pipeline_entry = deepcopy(measurements.get("__pipeline__", {}))
        pipeline_start_dt = _parse_iso_datetime(pipeline_entry.get("start_time")) or start_dt
        pipeline_end_dt = _parse_iso_datetime(pipeline_entry.get("end_time")) or end_dt

        if start_dt < pipeline_start_dt:
            pipeline_start_dt = start_dt
        if end_dt > pipeline_end_dt:
            pipeline_end_dt = end_dt

        total_duration = (pipeline_end_dt - pipeline_start_dt).total_seconds()
        pipeline_entry.update(
            {
                "start_time": pipeline_start_dt.isoformat(),
                "end_time": pipeline_end_dt.isoformat(),
                "total_duration_seconds": round(total_duration, 6),
            }
        )
        measurements["__pipeline__"] = pipeline_entry

        if timeout_seconds is not None and total_duration > timeout_seconds:
            raise TimeoutError(
                (
                    f"Graph execution exceeded timeout of {timeout_seconds} seconds "
                    f"after running '{node_name}'. Elapsed: {total_duration:.3f}s"
                )
            )

        if result is None:
            updates: Dict[str, Any] = {}
        elif isinstance(result, dict):
            updates = dict(result)
        else:
            raise TypeError(
                f"Node '{node_name}' returned unsupported type {type(result).__name__}; expected dict."
            )

        updates["time_measurements"] = measurements
        return updates

    return wrapper

def is_pdf_condition(state: AgentState) -> str:
    """
    Determine routing after url_handler based on whether the URL is a PDF.
    """
    return "pdf" if state.get("url_is_pdf", False) else "html"

def tools_condition_with_iter_limit(
    state,
    messages_key: str = "messages",
) -> Literal["tools", "__end__"]:
    config = load_config()
    return (
        tools_condition(state, messages_key)
        if state["iterations"] <= config["extractor"]["max_iters"]
        else "__end__"
    )


def get_graph(tools):
    config = load_config()
    timeout_cfg = (config.get("graph") or {}).get("timeout_seconds")
    timeout_seconds: Optional[float]
    try:
        timeout_seconds = float(timeout_cfg) if timeout_cfg is not None else None
    except (TypeError, ValueError):
        timeout_seconds = None
    if timeout_seconds is not None and timeout_seconds <= 0:
        timeout_seconds = None

    graph = StateGraph(AgentState)

    graph.add_node("url_handler", _instrument_node(url_handler, "url_handler", timeout_seconds))
    graph.add_node(
        "extraction_reasoner",
        _instrument_node(extraction_reasoner, "extraction_reasoner", timeout_seconds),
    )
    graph.add_node("tools", _instrument_node(ToolNode(tools), "tools", timeout_seconds))
    graph.add_node("feature_binder", _instrument_node(feature_binder, "feature_binder", timeout_seconds))
    graph.add_node("summarizer", _instrument_node(summarizer, "summarizer", timeout_seconds))
    graph.add_node("data_collator", _instrument_node(data_collator, "data_collator", timeout_seconds))
    graph.add_node("post_processor", _instrument_node(post_processor, "post_processor", timeout_seconds))

    graph.add_edge(START, "url_handler")

    graph.add_conditional_edges(
        "url_handler",
        is_pdf_condition,
        {
            "pdf": "summarizer",
            "html": "extraction_reasoner",
        },
    )

    graph.add_conditional_edges(
        "extraction_reasoner",
        tools_condition_with_iter_limit,
        {"tools": "tools", "__end__": "feature_binder"},
    )
    graph.add_edge("tools", "extraction_reasoner")
    graph.add_edge("feature_binder", "summarizer")

    graph.add_edge("summarizer", "data_collator")
    graph.add_edge("data_collator", "post_processor")
    graph.add_edge("post_processor", END)

    return graph.compile()
