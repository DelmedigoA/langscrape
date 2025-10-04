import asyncio
from langscrape import fetch_html_patchright, final_print
from langscrape.agent.graph import get_graph
from langscrape.html.utils import clean_html_for_extraction3
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, get_llm, initialize_global_state
import json
from dotenv import load_dotenv

def test_llm_extraction():
    load_dotenv("api_keys.env")

    config = load_config()

    global_state = initialize_global_state(config)
    expected_fields = list(global_state.keys())

    store_xpath = make_store_xpath(global_state)
    store_field_value = make_store_value(global_state)
    tools = [store_xpath, store_field_value]
    graph = get_graph(tools=tools)

    llm = get_llm(config)
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=True)

    initial_state = {
        "messages": [],
        "url": "https://www.gov.il/en/pages/spoke-start080924",
        "global_state": global_state,  
        "llm_with_tools": llm_with_tools,
    }

    final_state = graph.invoke(initial_state)
    print(final_state["summary"])
    
    import re
    import json

    def extract_json_block(text):
        match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return {}

    summary_raw = final_state["summary"].content
    summary_json = extract_json_block(summary_raw)

    with open("summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    test_llm_extraction()
