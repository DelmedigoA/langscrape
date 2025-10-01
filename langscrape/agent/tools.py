# tools/store_xpath.py
from langchain_core.tools import tool

def make_store_xpath(state_dict: dict):
    @tool
    def store_xpath(key: str, xpath: str):
        """
        Store a new XPath under a given key in the injected state_dict.
        """
        state_dict[key] = xpath
        return f"Stored XPath for '{key}': {xpath}"

    return store_xpath
