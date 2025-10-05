from .state import AgentState
from ..nodes.extraction_reasoner import extraction_reasoner
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from ..nodes.url_handler import url_handler
from ..nodes.feature_binder import feature_binder
from ..nodes.summarizer_prompt_builder import summarizer
from ..nodes.output_formatter import output_formatter


def get_graph(tools):
    graph = StateGraph(AgentState)

    graph.add_node("url_handler", url_handler)
    graph.add_node("extraction_reasoner", extraction_reasoner)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("feature_binder", feature_binder)
    graph.add_node("summarizer", summarizer)
    graph.add_node("output_formatter", output_formatter)

    graph.add_edge(START, "url_handler")
    graph.add_edge('url_handler', 'extraction_reasoner')
    graph.add_conditional_edges(
        "extraction_reasoner",
        tools_condition,
        {"tools": "tools", "__end__": "feature_binder"}
        )
    graph.add_edge("tools", "extraction_reasoner")
    graph.add_edge("extraction_reasoner", 'feature_binder')
    graph.add_edge('feature_binder', 'summarizer')
    graph.add_edge('summarizer', 'output_formatter')
    graph.add_edge('output_formatter', END)
    
    graph = graph.compile()
    
    return graph