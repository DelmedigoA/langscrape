from .html.xpath_extractor import extract_by_xpath_map_from_html

def final_print(global_state, html_content):

    # 🎨 ANSI color codes
    BLUE = "\033[94m"  
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{BLUE}=== FINAL XPATH STATE ==={RESET}")
    for k, v in global_state.items():
        if isinstance(v, dict):
            strategy = v.get("strategy", "xpath_extractor")
            if strategy == "lm_capabilities":
                detail = v.get("value")
            else:
                detail = v.get("xpath")
            print(f"{BLUE}{k}{RESET} ({strategy}): {detail}")
        else:
            print(f"{BLUE}{k}{RESET}: {v}")

    print(f"\n{BOLD}{GREEN}=== FINAL EXTRACTED CONTENT ==={RESET}")
    results = extract_by_xpath_map_from_html(html_content, field_state=global_state)
    for k, v in results.items():
        joined = " | ".join(v)
        print(f"{GREEN}{k}{RESET}: {joined}")
    
    return None
