from langchain_core.messages import HumanMessage
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..agent.state import AgentState

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
    system_prompt = HumanMessage(
        content=f"""You are a ReAct-style HTML extraction agent.

GOAL:
Ensure each field has the correct extracted TEXT from the HTML.
XPath is just a tool; the objective is accurate content.

Reasoning Rules:
- **author** → should look like a human name.
- **article_body** → should be a long coherent article.
- **title** → should be a real article title.
- **datetime** → should look like a publication date or time.

ACTION POLICY:
For every field:
- If the extracted text is empty, irrelevant, too short, or violates the rules → call the tool:
    store_xpath(key, new_xpath)
  to propose a **better XPath**.
- If the extraction looks plausible and correct → do nothing.
Stop when **all fields pass** these checks.

When proposing XPath, follow these strict rules:
- Always use real tag names (div, section, span, time, h1, p, etc.)
- Never use class names as tag names.
- Use `contains(@class, '...')` to target classes.
- Always start with '//' or '/html' and separate each tag with '/'.

Example:
✅ //section[contains(@class, 'article-body')]//p/text()
❌ /html/body/main/article/section/article-details-body-container/article-body

CURRENT XPATH MAP:
{state['global_state']}

CURRENT EXTRACTIONS SUMMARY:
{formatted_extracts}

HTML:
{state['html_content']}
"""
    )

    # print the entire system prompt for debugging
    print("\n=== 🧠 SYSTEM PROMPT (ITERATION) ===\n")
    print(system_prompt.content)
    print("\n=== END OF PROMPT ===\n")

    # Invoke LLM (it will call tools or stop if all valid)
    response = state['llm_with_tools'].invoke([system_prompt] + state["messages"])
    print("DEBUG tool_calls:", getattr(response, "tool_calls", None))

    return {"messages": [response]}