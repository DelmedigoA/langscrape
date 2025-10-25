import warnings
from ..agent.state import AgentState
from ..html.xpath_extractor import extract_by_xpath_map_from_html
from ..warnings import TooShortArticleBody
from ..utils import load_config
import newspaper
import nltk

# newspaper3k requires 'punkt' (not 'punkt_tab')
nltk.download('punkt')

def apply_articlebody_logic(article_body: str, min_len: int = None) -> bool:
    """Check article body length and emit a warning if too short."""
    if min_len is None:
        min_len = load_config()['warnings']['min_article_body']

    ab_len = len(article_body)
    if ab_len < min_len:
        warnings.warn(TooShortArticleBody(ab_len))
        return False
    return True

def get_article_traditional(url):
    try:
        return newspaper.article(url)
    except:
        return None
    
def _is_empty(c):
    return c == ["(Empty Result)"] or c == "(Empty Result)"

def feature_binder(state: AgentState) -> AgentState:
    """Extract features from cleaned HTML and validate article body length."""
    extracted_fields = extract_by_xpath_map_from_html(
        state["cleaned_content"],
        state["global_state"],
    )
    traditional_flag_updates = []
    article_body = " ".join(extracted_fields.get("article_body", "")) or ""
    articlebody_len_ok = apply_articlebody_logic(article_body)
    article = get_article_traditional(state["url"])

    if not articlebody_len_ok and article:
        try:
            traditional_flag_updates.append("article_body")
            article_body = article.text
            extracted_fields["article_body"] = article_body
            apply_articlebody_logic(article_body)
        except:
            pass

    empty_checks = {k: _is_empty(v) for k, v in extracted_fields.items()}
    if article:
        for k, empty in empty_checks.items():
            try:
                if empty and k == "title":
                    traditional_flag_updates.append("title")
                    extracted_fields["title"] = article.title
                elif empty and k == "author":
                    traditional_flag_updates.append("author")
                    extracted_fields["author"] = article.authors
                elif empty and k == "datetime":
                    traditional_flag_updates.append("datetime")
                    extracted_fields["datetime"] = article.publish_date
            except:
                pass
    return {"extracted_fields": extracted_fields, "traditional_flag": traditional_flag_updates}