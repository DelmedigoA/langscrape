from .html.xpath_extractor import extract_by_xpath_map_from_html
from .logging import get_logger


logger = get_logger(__name__)


def final_print(global_state, html_content):

    # 🎨 ANSI color codes
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    logger.info("\n%s%s=== FINAL XPATH STATE ===%s", BOLD, BLUE, RESET)
    for k, v in global_state.items():
        if isinstance(v, dict):
            strategy = v.get("strategy", "xpath_extractor")
            if strategy == "lm_capabilities":
                detail = v.get("value")
            else:
                detail = v.get("xpath")
            logger.info("%s%s%s (%s): %s", BLUE, k, RESET, strategy, detail)
        else:
            logger.info("%s%s%s: %s", BLUE, k, RESET, v)

    logger.info("\n%s%s=== FINAL EXTRACTED CONTENT ===%s", BOLD, GREEN, RESET)
    results = extract_by_xpath_map_from_html(html_content, field_state=global_state)
    for k, v in results.items():
        joined = " | ".join(v)
        logger.info("%s%s%s: %s", GREEN, k, RESET, joined)

    return None
