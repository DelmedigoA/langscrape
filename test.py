import asyncio
from langscrape import fetch_html_patchright, final_print
from langscrape.agent.graph import get_graph
from langscrape.html.utils import clean_html_for_extraction3
from langscrape.agent.tools import make_store_xpath
from langscrape.utils import load_config, get_llm

config = load_config()

global_state = {"article_body": None, "title": None, "author": None, "datetime": None}
expected_fields = list(global_state.keys())

store_xpath = make_store_xpath(global_state)
tools = [store_xpath]
graph = get_graph(tools=tools)

llm = get_llm(config)
llm_with_tools = llm.bind_tools(tools)

initial_state = {
    "messages": [],
    "url": "https://www.gov.il/en/pages/spoke-start080924",
    "global_state": global_state,  
    "llm_with_tools": llm_with_tools,
}

final_state = graph.invoke(initial_state)

final_print(global_state, final_state['cleaned_html_content'])