from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
from dotenv import load_dotenv
import os
import pandas as pd
import json
from datetime import datetime
import concurrent.futures

def run_with_timeout(func, *args, timeout=60, **kwargs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout}s")

def test_llm_extraction(url: str, id: str):
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
    df = pd.read_csv("/Users/delmedigo/Dev/langtest/langscrape/data/links.csv").sample(3)
    urls = df.url.tolist()
    ids = df.ID.tolist()
    results = {}
    TIMEOUT_SECONDS = 1
    for idx, (url, id) in enumerate(zip(urls, ids)):
        start = datetime.now()
        print(f"[{idx+1} / {len(urls)}]")
        print(f"working on {url.split('/')[-1]} from {url} ...")
        try:
            state = run_with_timeout(test_llm_extraction, url, id, timeout=TIMEOUT_SECONDS)
            end = datetime.now()
            results[id] = {
                "url": url,
                "result": "success",
                "error": None,
                "token_usage": state.get("token_usage", {}),
                "time": (end-start).seconds,
                "config": config
            }
            data = state.get("result", {})
        except TimeoutError as e:
            print(f"timeout on {url}")
            results[id] = {
                "url": url,
                "result": "timeout",
                "error": str(e),
                "token_usage": None,
                "time": None,
                "config": config
            }
        except Exception as e:
            print(f"failed with {url}: {e}")
            results[id] = {
                "url": url,
                "result": "failure",
                "error": str(e),
                "token_usage": None,
                "time": None,
                "config": config
            }
    if os.path.exists("log.json"):
        with open("log.json", "r", encoding="utf-8") as f:
            existing_results = json.load(f)
        existing_results.update(results)
        with open("log.json", "w", encoding="utf-8") as f:
            json.dump(existing_results, f, ensure_ascii=False, indent=2)
    else:
        with open("log.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    print(state)
