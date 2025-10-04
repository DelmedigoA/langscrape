from langscrape.pdf import pdfurl_to_text
from dotenv import load_dotenv
from pathlib import Path

def test_pdf_extraction():
    load_dotenv("api_keys.env")

    url = "https://gaza-projections.org/gaza_projections_report.pdf"
    text = pdfurl_to_text(url)

    # Basic validation
    assert isinstance(text, str)
    assert len(text) > 100  # ensure some content
