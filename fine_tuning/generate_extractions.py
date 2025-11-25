from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
from dotenv import load_dotenv
import os
import pandas as pd
import json
from datetime import datetime
import time

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
        "id": id,
        "summarizer_data_perepation_for_fine_tune": True
    }
    response = graph.invoke(initial_state)
    return response

import os
import json
def get_id_list(dir="/Users/delmedigo/Dev/langtest/langscrape/data/jsons"):
    paths = [os.path.join(dir, p) for p in os.listdir(dir)]
    ids = []
    for p in paths:
        try:
            ids.append(json.load(open(p, "r")).get("meta_data", {}).get("id", None))
        except:
            pass
    ids = [str(e) for e in ids if e]
    return ids

if __name__ == "__main__":
    SHEET_NAME = "For_Fine_Tune"
    SAMPLES = 30
    global_start = time.perf_counter()
    config = load_config()
    config["output_dir"] = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/extractions"
    df = pd.read_excel("/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/summaries/data_24-11.xlsx", sheet_name=SHEET_NAME)
    df.rename(columns={"Number": "ID", "Link": "url"}, inplace=True)
    df = df.sample(SAMPLES)
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
    global_end = time.perf_counter()
    print(f"Running took {global_end-global_start:.3} seconds")