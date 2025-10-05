class TooShortHtml(Exception):
    def __init__(self, html_length: int = 0, message="HTML is too short. You've likely been detected as a bot."):
        self.html_length = html_length
        self.message = message
        super().__init__(f"{message} Got: {html_length} chars")

class InvalidUrl(Exception):
    """Raised when a URL is invalid or unsupported."""
    def __init__(self, url: str, message="Invalid or unsupported URL"):
        self.url = url
        self.message = message
        super().__init__(f"{message}: {url}")