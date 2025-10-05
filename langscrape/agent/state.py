from typing import TypedDict, Annotated, Sequence, Union, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from datetime import datetime

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    extractor: Union[ChatOpenAI, ChatDeepSeek]
    summarizer: Union[ChatOpenAI, ChatDeepSeek]
    invoke_time: datetime
    finish_time: datetime
    id: str
    url: str
    cleaned_html_content: str
    iterations: int
    global_state: Dict[str, Dict[str, Any]]
    extracted_fields: Dict[str, Any]
    summary: BaseMessage
    result: Dict[str, Any]
