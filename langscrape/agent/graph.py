from .state import AgentState
from ..nodes.extraction_reasoner import extraction_reasoner
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from ..nodes.html_fetcher import html_fetcher
from ..nodes.output_formatter import output_formatter
from ..nodes.summarizer_prompt_builder import summarizer


def get_graph(tools):
    graph = StateGraph(AgentState)

    graph.add_node("html_fetcher", html_fetcher)
    graph.add_node("extraction_reasoner", extraction_reasoner)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("output_formatter", output_formatter)
    graph.add_node("summarizer", summarizer)

    graph.add_edge(START, "html_fetcher")
    graph.add_edge('html_fetcher', 'extraction_reasoner')
    graph.add_conditional_edges(
        "extraction_reasoner",
        tools_condition,
        {"tools": "tools", "__end__": "output_formatter"}
        )
    graph.add_edge("tools", "extraction_reasoner")
    graph.add_edge("extraction_reasoner", 'output_formatter')
    graph.add_edge("extraction_reasoner", 'output_formatter')
    graph.add_edge('output_formatter', 'summarizer')
    graph.add_edge('summarizer', END)
    
    graph = graph.compile()
    
    return graph