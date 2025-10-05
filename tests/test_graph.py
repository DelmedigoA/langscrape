from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
from dotenv import load_dotenv
import os

def start_sound():
    os.system('afplay /System/Library/Sounds/Blow.aiff')

def end_sound():
    os.system('afplay /System/Library/Sounds/Bottle.aiff')

def add_sound(func):
    def wrapper(*args, **kwargs):
        start_sound()
        try:
            return func(*args, **kwargs)
        finally:
            end_sound()
    return wrapper

@add_sound
def test_llm_extraction(url: str):
    config = load_config()
    load_dotenv(config["api_keys"])
    global_state = initialize_global_state(config)
    store_xpath = make_store_xpath(global_state)
    store_field_value = make_store_value(global_state)
    tools = [store_xpath, store_field_value]
    graph = get_graph(tools=tools)
    extractor = get_extractor(config)
    extractor_with_tools = extractor.bind_tools(tools, parallel_tool_calls=config["extractor"]["allow_parallel_tool_calls"])
    summarizer = get_summarizer(config)
    initial_state = {
        "messages": [],
        "url": url,
        "global_state": global_state,  
        "extractor": extractor_with_tools,
        "summarizer": summarizer,
        "iterations": 0
    }
    response = graph.invoke(initial_state)
    return response

if __name__ == "__main__":
    urls = [
       # 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)01169-3/fulltext',
        'https://www.dropsitenews.com/p/how-gaza-health-ministry-counts-dead',
        'https://theconversation.com/what-exactly-caused-the-explosion-at-a-hospital-in-gaza-without-an-independent-credible-investigation-it-will-be-hard-for-everyone-to-agree-216242'
    ]
    results = {k:None for k in urls}
    for idx, url in enumerate(urls):
        print(f"[{idx+1} / {len(urls)}]")
        print(f"working on {url.split('/')[-1]} from {url.split('/')[0]}...")
        try:
            test_llm_extraction(url)
            results[url] = "success"
        except Exception as e:
            print(f"failed with {url}: {e}")
            results[url] = e
    print(results)