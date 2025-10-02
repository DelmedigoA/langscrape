import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
import os
from langchain_core.messages import SystemMessage

def load_config(path: str = "config/default_config.yaml") -> dict:
    """
    Load YAML config into a Python dict.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def get_llm(config=None):
    if config is None:
        config = load_config()

    if config["llm"]["provider"] == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    elif config["llm"]["provider"] == "deepseek":
        api_key = os.getenv("DS_API_KEY")
        return ChatDeepSeek(
            model=config["llm"]["name"],
            temperature=config["llm"]["temperature"],
            top_p=config["llm"]["top_p"],
            api_key=api_key
        )
    else:
        raise NameError(f"{config['llm']['type']} is not supported. try")

def get_system_prompt(state, formatted_extracts):
    return SystemMessage(
        content=f"""You are a ReAct-style HTML extraction agent.

GOAL:
Ensure each field has the correct extracted TEXT from the HTML.
XPath is just a tool; the objective is accurate content.

Reasoning Rules:
- **author** → should look like a human name.
- **article_body** → should be a long coherent article.
- **title** → should be a real article title.
- **datetime** → should look like a publication date or time.

ACTION POLICY:
For every field:
- If the extracted text is empty, irrelevant, too short, or violates the rules → call the tool:
    store_xpath(key, new_xpath)
  to propose a **better XPath**.
- If the extraction looks plausible and correct → do nothing.
Stop when **all fields pass** these checks.

When proposing XPath, follow these strict rules:
- Always use real tag names (div, section, span, time, h1, p, etc.)
- Never use class names as tag names.
- Use `contains(@class, '...')` to target classes.
- Always start with '//' or '/html' and separate each tag with '/'.

Example:
✅ //section[contains(@class, 'article-body')]//p/text()
❌ /html/body/main/article/section/article-details-body-container/article-body

CURRENT XPATH MAP:
{state['global_state']}

CURRENT EXTRACTIONS SUMMARY:
{formatted_extracts}

HTML:
{state['html_content']}
"""
    )