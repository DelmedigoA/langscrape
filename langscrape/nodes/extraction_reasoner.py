from langchain_core.messages import SystemMessage
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..agent.state import AgentState
from ..utils import get_system_prompt, get_formatted_extracts

def extraction_reasoner(state: AgentState) -> AgentState:
    iters = state["iterations"]
    iters += 1
    current_extracts = extract_by_xpath_map_from_html(state['cleaned_html_content'], state['global_state'])
    formatted_extracts = get_formatted_extracts(current_extracts)
    system_prompt = get_system_prompt(state, formatted_extracts)
    print(f"\n=== 🧠 SYSTEM PROMPT (ITERATION: {state["iterations"] + 1}) ===\n")
    print(system_prompt.content)
    print("\n=== END OF PROMPT ===\n")
    response = state['extractor'].invoke([system_prompt] + state["messages"])
    print("DEBUG tool_calls:", getattr(response, "tool_calls", None))
    return {"messages": [response], "iterations": iters}