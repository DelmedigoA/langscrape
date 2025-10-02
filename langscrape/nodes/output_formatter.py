from ..agent.state import AgentState
from ..utils import load_config
from ..html.xpath_extractor import extract_by_xpath_map_from_html

config = load_config()

def output_formatter(state: AgentState) -> AgentState:
    state['result'] = extract_by_xpath_map_from_html(state['cleaned_html_content'], state['global_state'])
    return state
