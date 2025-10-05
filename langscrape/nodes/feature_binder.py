from ..agent.state import AgentState
from ..html.xpath_extractor import extract_by_xpath_map_from_html


def feature_binder(state: AgentState) -> AgentState:
    return {
        "extracted_fields": extract_by_xpath_map_from_html(
            state["cleaned_html_content"],
            state["global_state"],
        )
    }
