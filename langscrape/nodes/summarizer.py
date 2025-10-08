import json

from langchain_core.messages import HumanMessage, SystemMessage

from ..agent.state import AgentState
from ..json import JSON_SCHEME
from ..tags import COUNTRIES_AND_ORGANIZATIONS, FIGURES, LOCATIONS, THEME_TAGS
from ..utils import update_token_usage

def get_summarizer_system_prompt(state: AgentState) -> str:
    prompt_template = f"""Your task is to analyze the provided contens.

    Instructions:
    1. For dates:
    - Publication date: When the content was published
    - Event date: When the described events occurred
    - Use YYYY-MM-DD format
    - For date ranges use: YYYY-MM-DD to YYYY-MM-DD
    - If only month/year available, use first day: YYYY-MM-01
    - If no date is available, return an empty string

    2. For content type, classify as:
    - Official Report: Research papers, formal investigations, detailed reports
    - Official Statement: Press releases, announcements, declarations
    - Opinion: Editorial content, opinion pieces, commentary
    - Testimony: First-hand accounts, witness statements
    - Journalistic Report: News articles, investigative journalism
    - Analysis: Analysis, commentary
    - Open letter: Letters to the editor, letters to the government, letters to the media
    - News: Breaking news, time-sensitive reporting
    - Post: Social media posts, short updates

    3. For media type, classify as:
    - Video: Video content, broadcasts
    - Photo: Photo galleries, image-focused content
    - Audio: Audio content, podcasts
    - Text: Text content, articles, reports

    4. For tags:
    - IMPORTANT: You must ONLY use tags from the following list. DO NOT use tags that are not listed below.
    --*ALLOWED TAGS*--
    --THEME_TAGS--
    {THEME_TAGS}
    --COUNTRIES_AND_ORGANIZATIONS--
    {COUNTRIES_AND_ORGANIZATIONS}
    --LOCATIONS--
    {LOCATIONS}
    --FIGURES--
    {FIGURES}

    - Select ONLY the most relevant tags from this list that are reflected in the content
    - Format as an array of strings
    - If no tags from the list apply, return an empty array

    Return a JSON object with these exact fields:

    {JSON_SCHEME}
    
    - All string values (including "summary" and "tags") **must be in English**.
    
    Important
    - Even if the content is in non-english language (e.g: Hebrew, French etc...) your output should be in *English*.
    - Extract information only from the provided content
    - Leave field empty ("") if information is not explicitly present
    - For platform, extract from the URL or content source
    - For language, specify if clearly identifiable
    - Tags should ONLY be from the provided list, do not create new ones
    - Search for publication date in the content's metadata
    - If no publication date is found, use the creation date of the content
    - Always return content processed in English
    """
    return prompt_template


def get_html_summarizer_user_prompt(state: AgentState) -> str:
    extracted_data = state["extracted_fields"]
    title = extracted_data.get("title", "")
    content = extracted_data.get("article_body", "")
    author = extracted_data.get("author", "")
    datetime = extracted_data.get("datetime", "")
    prompt = f"""
    URL: {state["url"]}
    Title: {title}
    Author: {author}
    Publication Date: {datetime}
    Content: 
    '''
    {content}
    '''
    
    Please analyze carefully and return the JSON according to the system instructions.
    - Return your final answer **only** inside a fenced code block using the `json` language 
    """
    return prompt

def get_pdf_summarizer_user_prompt(state: AgentState) -> str:
    prompt = f"""
    URL: {state["url"]}
    Content: 
    '''
    {state['cleaned_content']}
    '''
    
    Please analyze carefully and return the JSON according to the system instructions.
    """
    return prompt

def summarizer(state: AgentState) -> AgentState:
    """Invoke the summarizer model with system + user prompts."""
    get_user_prompt = (
        get_pdf_summarizer_user_prompt if state.get("url_is_pdf", False)
        else get_html_summarizer_user_prompt
    )
    messages = [
        SystemMessage(content=get_summarizer_system_prompt(state)),
        HumanMessage(content=get_user_prompt(state)),
    ]
    response = state["summarizer"].invoke(messages)
    token_usage = update_token_usage(state, "summarizer", response)
    return {"summary": response, "token_usage": token_usage}
