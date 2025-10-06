from .state import AgentState
from ..nodes.extraction_reasoner import extraction_reasoner
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from ..nodes.url_handler import url_handler
from ..nodes.feature_binder import feature_binder
from ..nodes.summarizer_prompt_builder import summarizer
from ..nodes.data_collator import data_collator
from ..nodes.post_processor import post_processor


def is_pdf_condition(state: AgentState) -> str:
    """
    Determine routing after url_handler based on whether the URL is a PDF.
    """
    return "pdf" if state.get("url_is_pdf", False) else "html"

def get_graph(tools):
    graph = StateGraph(AgentState)

    # 🔹 Nodes
    graph.add_node("url_handler", url_handler)
    graph.add_node("extraction_reasoner", extraction_reasoner)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("feature_binder", feature_binder)
    graph.add_node("summarizer", summarizer)
    graph.add_node("data_collator", data_collator)
    graph.add_node("post_processor", post_processor)

    # 🔹 Flow
    graph.add_edge(START, "url_handler")

    # ✅ Conditional branching happens *after* url_handler
    graph.add_conditional_edges(
        "url_handler",
        is_pdf_condition,
        {
            "pdf": "summarizer",        # skip extraction branch
            "html": "extraction_reasoner",  # go through normal flow
        },
    )

    # 🧠 HTML branch: reasoner + tools + binder
    graph.add_conditional_edges(
        "extraction_reasoner",
        tools_condition,
        {"tools": "tools", "__end__": "feature_binder"},
    )
    graph.add_edge("tools", "extraction_reasoner")
    graph.add_edge("feature_binder", "summarizer")

    # 🔄 Common downstream path
    graph.add_edge("summarizer", "data_collator")
    graph.add_edge("data_collator", "post_processor")
    graph.add_edge("post_processor", END)

    # ✅ Compile
    return graph.compile()
