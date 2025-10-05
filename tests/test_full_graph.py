import asyncio
from langscrape import fetch_html_patchright, final_print
from langscrape.agent.graph import get_graph
from langscrape.html.utils import clean_html_for_extraction3
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
import json
from dotenv import load_dotenv


import os

def beep():
    os.system('afplay /System/Library/Sounds/Funk.aiff')  # or "Glass.aiff", "Submarine.aiff", etc.

def test_llm_extraction():
    load_dotenv("api_keys.env")
    config = load_config()

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
        "url": "https://www.middleeasteye.net/news/israel-soldier-boasted-running-over-dead-palestinian-man-tank",
        "global_state": global_state,  
        "extractor": extractor_with_tools,
        "summarizer": summarizer,
        "iterations": 0
    }

    graph.invoke(initial_state)
if __name__ == "__main__":
    beep()  
    test_llm_extraction()
    beep()
