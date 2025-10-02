from langchain_core.messages import SystemMessage
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..agent.state import AgentState
from ..utils import get_system_prompt, get_formatted_extracts

def call_model(state: AgentState) -> AgentState:
    global global_state, expected_fields, html_content
    current_extracts = extract_by_xpath_map_from_html(state['cleaned_html_content'], state['global_state'])
    formatted_extracts = get_formatted_extracts(current_extracts)
    system_prompt = get_system_prompt(state, formatted_extracts)
    print("\n=== 🧠 SYSTEM PROMPT (ITERATION) ===\n")
    print(system_prompt.content)
    print("\n=== END OF PROMPT ===\n")
    response = state['llm_with_tools'].invoke([system_prompt] + state["messages"])
    print("DEBUG tool_calls:", getattr(response, "tool_calls", None))
    return {"messages": [response]}