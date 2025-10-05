class TooShortArticleBody(Warning):
    def __init__(self, article_length: int = 0,
                 message: str = "Article Body is too short. Possibly due to main content being video."):
        self.article_length = article_length
        self.message = message
        super().__init__(f"{message} Got: {article_length} chars")