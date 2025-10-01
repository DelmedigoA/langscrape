import asyncio
from langscrape import fetch_html_patchright
from langscrape.agent.graph import get_graph
from IPython.display import Image
from langchain_openai import ChatOpenAI
from langscrape.html.xpath_extractor import extract_by_xpath_map_from_html
from langchain_core.messages import HumanMessage
from langscrape.html.utils import clean_html_for_extraction3
from langscrape.agent.tools import make_store_xpath

async def fetch_url(url):
    result = await fetch_html_patchright(url)
    return result

some_url = "https://www.gov.il/en/pages/spoke-start080924"

html_content = asyncio.run(fetch_url(some_url))
html_content = clean_html_for_extraction3(html_content)
print("len cleaned:", len(html_content))
global_state = {"article_body": None, "title": None, "author": None, "datetime": None}
expected_fields = list(global_state.keys())

LLM_NAME = "gpt-4o-mini"
OPENAI_API_KEY=""

store_xpath = make_store_xpath(global_state)
tools = [store_xpath]
graph = get_graph(tools=tools)
llm = ChatOpenAI(model=LLM_NAME, api_key=OPENAI_API_KEY, temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 4) pass the SAME dict reference into the graph state
initial_state = {
    "messages": [HumanMessage(content=f"Please inspect the HTML and set correct XPath for all expected fields: {expected_fields}")],
    "html_content": html_content,
    "global_state": global_state,  
    "llm_with_tools": llm_with_tools,
}

llm = ChatOpenAI(model=LLM_NAME, api_key=OPENAI_API_KEY, temperature=0, top_p=1)
llm_with_tools = llm.bind_tools(tools)


final_state = graph.invoke(initial_state)

# 🎨 ANSI color codes
BLUE = "\033[94m"     # light blue
GREEN = "\033[92m"    # green
BOLD = "\033[1m"
RESET = "\033[0m"

print(f"\n{BOLD}{BLUE}=== FINAL XPATH STATE ==={RESET}")
for k, v in global_state.items():
    print(f"{BLUE}{k}{RESET}: {v}")

print(f"\n{BOLD}{GREEN}=== FINAL EXTRACTED CONTENT ==={RESET}")
results = extract_by_xpath_map_from_html(html_content, xpath_map=global_state)
for k, v in results.items():
    joined = " | ".join(v)
    print(f"{GREEN}{k}{RESET}: {joined}")
