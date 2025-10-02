from langchain_core.messages import SystemMessage
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..agent.state import AgentState
from ..utils import get_system_prompt

def call_model(state: AgentState) -> AgentState:
    global global_state, expected_fields, html_content

    # Recompute current extractions from the HTML
    current_extracts = extract_by_xpath_map_from_html(state['html_content'], state['global_state'])

    # Build a concise summary (length + short preview) for each field
    lines = []

    for key, vals in current_extracts.items():
        # Ensure vals is a list
        vals = vals or []

        # Clean each value
        clean_vals = [str(v).strip() for v in vals if str(v).strip()]

        if not all(c =="'Skipped: No XPath'" or c == "(Empty Result)" for c in clean_vals):
            joined = " | ".join(clean_vals)
            preview = joined[:200]  # optional truncation for readability
            info = f"len={len(joined)}; preview={preview}"
        else:
            info = "❌ XPATH not found or empty; try a different one."
        lines.append(f"{key}: {info}")
    formatted_extracts = "\n".join(lines)
    # 3️⃣ Content-centric reasoning prompt (LLM decides correctness)
    system_prompt = get_system_prompt(state, formatted_extracts)

    # print the entire system prompt for debugging
    print("\n=== 🧠 SYSTEM PROMPT (ITERATION) ===\n")
    print(system_prompt.content)
    print("\n=== END OF PROMPT ===\n")

    # Invoke LLM (it will call tools or stop if all valid)
    response = state['llm_with_tools'].invoke([system_prompt] + state["messages"])
    print("DEBUG tool_calls:", getattr(response, "tool_calls", None))

    return {"messages": [response]}