from typing import TypedDict, Annotated, Sequence, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

class AgentState(TypedDict):
    extractor: Union[ChatOpenAI, ChatDeepSeek]
    summarizer: Union[ChatOpenAI, ChatDeepSeek]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    url: str
    cleaned_html_content: str
    iterations: int
    global_state: dict
    summary: str
    result: dict