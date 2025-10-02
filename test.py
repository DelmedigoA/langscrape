import asyncio
from langscrape import fetch_html_patchright, final_print
from langscrape.agent.graph import get_graph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langscrape.html.utils import clean_html_for_extraction3
from langscrape.agent.tools import make_store_xpath
from langscrape.utils import load_config, get_llm

config = load_config()

async def fetch_url(url):
    result = await fetch_html_patchright(url)
    return result

some_url = "https://www.gov.il/en/pages/spoke-start080924"

html_content = asyncio.run(fetch_url(some_url))
cleaned_html_content = clean_html_for_extraction3(html_content)
print("len cleaned:", len(html_content))

global_state = {"article_body": None, "title": None, "author": None, "datetime": None}
expected_fields = list(global_state.keys())

store_xpath = make_store_xpath(global_state)
tools = [store_xpath]
graph = get_graph(tools=tools)

llm = get_llm(config)
llm_with_tools = llm.bind_tools(tools)

initial_state = {
    "messages": [HumanMessage(content=f"Please extract the fields: {expected_fields}")],
    "html_content": cleaned_html_content,
    "global_state": global_state,  
    "llm_with_tools": llm_with_tools,
}

final_state = graph.invoke(initial_state)

final_print(global_state, html_content)
