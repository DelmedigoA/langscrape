from .state import AgentState
from ..nodes.call_model import call_model
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from ..nodes.html_fetcher import html_fetcher
from ..nodes.output_formatter import output_formatter

def get_graph(tools):
    graph = StateGraph(AgentState)

    graph.add_node("html_fetcher", html_fetcher)
    graph.add_node("llm", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("output_formatter", output_formatter)

    graph.add_edge(START, "html_fetcher")
    graph.add_edge('html_fetcher', 'llm')
    graph.add_conditional_edges(
        "llm",
        tools_condition,
        {"tools": "tools", "__end__": "output_formatter"}
        )
    graph.add_edge("tools", "llm")
    graph.add_edge("llm", 'output_formatter')
    graph.add_edge('output_formatter', END)
    
    graph = graph.compile()
    
    return graph
