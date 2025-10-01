from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    html_content: str
    global_state: dict
    llm_with_tools: ChatOpenAI
    results: dict