from .state import AgentState
from ..nodes.extraction_reasoner import extraction_reasoner
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from ..nodes.url_handler import url_handler
from ..nodes.feature_binder import feature_binder
from ..nodes.summarizer import summarizer
from ..nodes.data_collator import data_collator
from ..nodes.post_processor import post_processor
from typing import Literal
from ..utils import load_config

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
    return tools_condition(state, messages_key) if state["iterations"] <=  config['extractor']['max_iters'] else "__end__"


def get_graph(tools):
    graph = StateGraph(AgentState)

    graph.add_node("url_handler", url_handler)
    graph.add_node("extraction_reasoner", extraction_reasoner)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("feature_binder", feature_binder)
    graph.add_node("summarizer", summarizer)
    graph.add_node("data_collator", data_collator)
    graph.add_node("post_processor", post_processor)

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

