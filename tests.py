import asyncio
from langscrape import fetch_html_patchright
from langscrape.agent.graph import graph, tools
from IPython.display import Image
from langchain_openai import ChatOpenAI
from langscrape.html.xpath_extractor import extract_by_xpath_map_from_html
from langchain_core.messages import HumanMessage

async def fetch_url(url):
    result = await fetch_html_patchright(url)
    print(result[:2000])

some_url = "https://www.ynet.co.il/news/article/s1j00pj9nge"
html_content = "<html><title>hello world</title>"#asyncio.run(fetch_url(some_url))

global_state = {"article_body": None, "title": None, "author": None, "datetime": None}
expected_fields = list(global_state.keys())

LLM_NAME = "gpt-4o-mini"
OPENAI_API_KEY="Your-API-Key-Here"

llm = ChatOpenAI(model=LLM_NAME, api_key=OPENAI_API_KEY, temperature=0, top_p=1)
llm_with_tools = llm.bind_tools(tools)
from html import escape

initial_state = {"messages": [HumanMessage(content=f"Please inspect the HTML and set correct XPath for all expected fields: {expected_fields}")]}
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
