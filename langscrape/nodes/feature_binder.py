import warnings
from ..agent.state import AgentState
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..warnings import TooShortArticleBody
from ..utils import load_config

def apply_articlebody_logic(article_body: str, min_len: int = None) -> None:
    """Check article body length and emit a warning if too short."""
    if min_len is None:
        min_len = load_config()['warnings']['min_article_body']

    ab_len = len(article_body)
    if ab_len < min_len:
        warnings.warn(TooShortArticleBody(ab_len))

def feature_binder(state: AgentState) -> AgentState:
    """Extract features from cleaned HTML and validate article body length."""
    extracted_fields = extract_by_xpath_map_from_html(
        state["cleaned_content"],
        state["global_state"],
    )

    article_body = " ".join(extracted_fields.get("article_body", "")) or ""
    apply_articlebody_logic(article_body)

    # ✅ Return for LangGraph node (merges automatically)
    return {"extracted_fields": extracted_fields}