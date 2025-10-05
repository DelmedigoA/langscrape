from langchain_core.messages import SystemMessage

from ..agent.state import AgentState
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..logging import get_logger
from ..utils import get_system_prompt, get_formatted_extracts


logger = get_logger(__name__)

def extraction_reasoner(state: AgentState) -> AgentState:
    state["iterations"] += 1
    current_extracts = extract_by_xpath_map_from_html(state['cleaned_html_content'], state['global_state'])
    formatted_extracts = get_formatted_extracts(current_extracts)
    system_prompt = get_system_prompt(state, formatted_extracts)
    logger.info("\n=== 🧠 SYSTEM PROMPT (ITERATION: %s) ===\n", state["iterations"])
    logger.info(system_prompt.content)
    logger.info("\n=== END OF PROMPT ===\n")
    response = state['extractor'].invoke([system_prompt] + state["messages"])
    logger.debug("DEBUG tool_calls: %s", getattr(response, "tool_calls", None))
    return {"messages": [response]}

