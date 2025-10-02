import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
import os

def load_config(path: str = "config/default_config.yaml") -> dict:
    """
    Load YAML config into a Python dict.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def get_llm(config=None):
    if config is None:
        config = load_config()

    if config["llm"]["type"] == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    elif config["llm"]["type"] == "deepseek":
        api_key = os.getenv("DS_API_KEY")
        return ChatDeepSeek(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    else:
        raise NameError(f"{config['llm']['type']} is not supported. try")
