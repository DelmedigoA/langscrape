from langscrape.agent.graph import get_graph
from langscrape.agent.tools import make_store_xpath, make_store_value
from langscrape.utils import load_config, initialize_global_state, get_extractor, get_summarizer
from dotenv import load_dotenv
import os
import pandas as pd
import json


def test_llm_extraction(url: str, id: str):
    """
    Run full extraction pipeline for a single URL.
    """
    config = load_config()
    load_dotenv(config["api_keys"])

    # Initialize shared state and tools
    global_state = initialize_global_state(config)
    store_xpath = make_store_xpath(global_state)
    store_field_value = make_store_value(global_state)
    tools = [store_xpath, store_field_value]

    # Build LangGraph
    graph = get_graph(tools=tools)

    # LLMs
    extractor = get_extractor(config)
    extractor_with_tools = extractor.bind_tools(
        tools,
        parallel_tool_calls=config["extractor"]["allow_parallel_tool_calls"],
    )
    summarizer = get_summarizer(config)

    # Initial state
    initial_state = {
        "messages": [],
        "url": url,
        "global_state": global_state,
        "extractor": extractor_with_tools,
        "summarizer": summarizer,
        "iterations": 0,
        "id": id,
    }

    # Run
    response = graph.invoke(initial_state)
    return response


if __name__ == "__main__":
    csv_path = "/Users/delmedigo/Dev/langtest/langscrape/data/links.csv"
    df = pd.read_csv(csv_path)

    # 🔹 Filter only PDF URLs (case-insensitive)
    pdf_df = df[df["url"].str.lower().str.endswith(".pdf")]

    # 🔹 Optionally sample if you want only a few
    pdf_df = pdf_df.sample(3) if len(pdf_df) > 3 else pdf_df

    urls = pdf_df.url.tolist()
    ids = pdf_df.ID.tolist()

    results = {}

    for idx, (url, id) in enumerate(zip(urls, ids)):
        print(f"\n[{idx+1} / {len(urls)}] Processing {url}")
        try:
            state = test_llm_extraction(url, id)
            results[id] = {
                "url": url,
                "result": "success",
                "error": None,
            }

        except Exception as e:
            print(f"❌ Failed with {url}: {e}")
            results[id] = {
                "url": url,
                "result": "failure",
                "error": str(e),
            }

    # 🔹 Save global log
    with open("log.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n✅ Finished processing PDF URLs only.")
