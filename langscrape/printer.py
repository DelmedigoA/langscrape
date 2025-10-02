from .html.xpath_extractor import extract_by_xpath_map_from_html

def final_print(global_state, html_content):

    # 🎨 ANSI color codes
    BLUE = "\033[94m"  
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{BLUE}=== FINAL XPATH STATE ==={RESET}")
    for k, v in global_state.items():
        print(f"{BLUE}{k}{RESET}: {v}")

    print(f"\n{BOLD}{GREEN}=== FINAL EXTRACTED CONTENT ==={RESET}")
    results = extract_by_xpath_map_from_html(html_content, xpath_map=global_state)
    for k, v in results.items():
        joined = " | ".join(v)
        print(f"{GREEN}{k}{RESET}: {joined}")
    
    return None
