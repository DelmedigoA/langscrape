# Langscrape: Simple LLM-Powered HTML Extraction

Langscrape is a minimal agent-style pipeline for extracting structured data from raw HTML using an LLM and helper tools.  
It is designed as a starting point for building more advanced agentic pipelines that combine **web fetching**, **LLM reasoning**, and **post-processing**.

---

## 📦 Project Overview

The flow of the system can be visualized as:

![Pipeline Graph](assets/graph.png)

1. **`html_fetcher`**  
   Retrieves raw HTML from a given URL using a headless browser or HTTP client.  
   This ensures the LLM receives the full DOM, including dynamically rendered content.

2. **`llm`**  
   The central reasoning component. The LLM analyzes the HTML and decides how to extract the required information.  
   It can:
   - Call **tools** (e.g. XPath extractors, cleaning utilities).
   - Pass structured results forward.

3. **`tools`**  
   Helper functions the LLM may invoke for specialized tasks, such as:
   - Cleaning noisy HTML.
   - Extracting DOM elements with XPath.
   - Parsing tables or metadata.

4. **`output_formatter`**  
   Normalizes the LLM output into a clean structured format (e.g., JSON or dict).  
   This ensures consistency even when LLM generations vary.

---

## 🚀 Quickstart

Clone the repository:

```bash
git clone https://github.com/DelmedigoA/langscrape.git
cd langscrape

## 🖥️ Interactive UI

An experimental local UI is available for quickly testing batches of URLs and
watching the extraction pipeline populate the desired fields in real time.

1. Install the project dependencies and export the required LLM credentials
   (e.g. `OPENAI_API_KEY` or `DS_API_KEY`).
2. Launch the development server:

   ```bash
   python run_ui.py
   ```

3. Open <http://localhost:8000> in your browser, paste one URL per line into
   the form, and press **Start Extraction**. The table begins with the URLs and
   empty columns for the expected fields, then updates row-by-row as each
   extraction finishes.
