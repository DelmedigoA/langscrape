from langchain_core.tools import tool

@tool
def store_xpath(key: str, xpath: str):
    """
    Store a new XPath under a given key in global_state.
    """
    global global_state
    global_state[key] = xpath
    return f"Stored XPath for '{key}': {xpath}"

tools = [store_xpath]
