from typing import TypedDict, Annotated, Sequence, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    url: str
    cleaned_html_content: str
    global_state: dict
    summarizer: Union[ChatOpenAI, ChatDeepSeek]
    llm_with_tools: Union[ChatOpenAI, ChatDeepSeek]
    summary: str
    result: dict