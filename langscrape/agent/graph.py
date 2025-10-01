from .state import AgentState
from ..nodes.call_model import call_model
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from .tools import store_xpath

tools = [store_xpath]

graph = StateGraph(AgentState)

graph.add_node("llm", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", tools_condition)
graph.add_edge("tools", "llm")

graph = graph.compile()
