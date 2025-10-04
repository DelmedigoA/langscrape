from ..agent.state import AgentState
import asyncio
from ..browser.chrome import fetch_html_patchright
from ..html.utils import clean_html_for_extraction3
from ..utils import load_config

config = load_config()

async def fetch_url(url):
    result = await fetch_html_patchright(url)
    return result

def url_handler(state: AgentState) -> AgentState:
    url = state['url']
    html_content = asyncio.run(fetch_url(url))
    print("len before cleaning:", len(html_content))
    state['cleaned_html_content'] = clean_html_for_extraction3(html_content)
    print("len cleaned:", len(state['cleaned_html_content']))
    return state
