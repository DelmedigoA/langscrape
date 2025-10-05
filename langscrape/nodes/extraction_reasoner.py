from langchain_core.messages import SystemMessage
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..agent.state import AgentState
from ..utils import (
    get_system_prompt,
    get_formatted_extracts,
    coerce_model_content_to_str,
)

def extraction_reasoner(state: AgentState) -> AgentState:
    state["iterations"] += 1
    current_extracts = extract_by_xpath_map_from_html(state['cleaned_html_content'], state['global_state'])
    formatted_extracts = get_formatted_extracts(current_extracts)
    system_prompt = get_system_prompt(state, formatted_extracts)
    print(f"\n=== 🧠 SYSTEM PROMPT (ITERATION: {state["iterations"]}) ===\n")
    print(system_prompt.content)
    print("\n=== END OF PROMPT ===\n")
    response = state['extractor'].invoke([system_prompt] + state["messages"])

    reasoning_raw = getattr(response, "additional_kwargs", {}).get("reasoning_content")
    reasoning_text = coerce_model_content_to_str(reasoning_raw)

    content_text = coerce_model_content_to_str(response.content)
    if content_text != response.content:
        response = response.model_copy(update={"content": content_text})

    if reasoning_text:
        print("=== 🤔 MODEL REASONING ===\n")
        print(reasoning_text)
        print("\n=== END OF REASONING ===\n")

    print("=== 🗣️ MODEL RESPONSE ===\n")
    print(content_text)
    print("\n=== END OF RESPONSE ===\n")

    print("DEBUG tool_calls:", getattr(response, "tool_calls", None))
    return {"messages": [response]}
