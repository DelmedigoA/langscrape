from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
from dotenv import load_dotenv
import os
import pandas as pd
import json
from datetime import datetime

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
def extract(url: str, id: str):
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
        "iterations": 1,
        "id": id
    }
    response = graph.invoke(initial_state)
    return response

if __name__ == "__main__":

    config = load_config()
    df = pd.read_excel("/Users/delmedigo/Dev/langtest/langscrape/data/production_21_10_2025/real_links_21_10_25.xlsx").sample(5)
    urls = df.url.tolist()
    ids = df.ID.tolist()
    log_path = "log.json"

    # initialize log file if not exists
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    for idx, (url, id) in enumerate(zip(urls, ids)):
        start = datetime.now()
        print(f"[{idx+1} / {len(urls)}]")
        print(f"working on {url.split('/')[-1]} from {url} ...")
        try:
            extraction = extract(url, id)
            end = datetime.now()
            entry = {
                "url": url,
                "result": "success",
                "error": None,
                "token_usage": extraction.get("token_usage", {}),
                "traditional_flag": extraction.get("traditional_flag", []),
                "time": (end-start).seconds,
                "config": config
            }
            data = extraction.get("result", {})
        except Exception as e:
            print(f"failed with {url}: {e}")
            entry = {
                "url": url,
                "result": "failure",
                "error": str(e),
                "token_usage": None,
                "time": None,
                "config": config
            }

        # 🔹 Live logging per ID
        with open(log_path, "r", encoding="utf-8") as f:
            existing_results = json.load(f)

        existing_results[str(id)] = entry

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(existing_results, f, ensure_ascii=False, indent=2)