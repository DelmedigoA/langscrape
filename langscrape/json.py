class SchemeValidator:
    def __init__(self, scheme: dict, data: dict):
        """
        Initialize with scheme (dict) and data (dict).
        """
        self.scheme = scheme if isinstance(scheme, dict) else {}
        self.data = data if isinstance(data, dict) else {}

    def get_data_keys(self) -> set:
        """
        Safely extract keys from data if it exists and is a dict.
        """
        return set(self.data.keys())

    def get_scheme_keys(self) -> set:
        """
        Safely extract keys from scheme if it exists and is a dict.
        """
        return set(self.scheme.keys())

    def all_data_keys_in_scheme(self) -> bool:
        """
        True if all keys in data are present in scheme
        """
        return self.get_data_keys().issubset(self.get_scheme_keys())

    def all_scheme_keys_in_data(self) -> bool:
        """
        True if all keys in scheme are present in data
        """
        return self.get_scheme_keys().issubset(self.get_data_keys())

    def get_keys_to_remove(self) -> list:
        """
        Return keys in data that are NOT in scheme
        """
        return sorted(list(self.get_data_keys() - self.get_scheme_keys()))

    def get_missed_keys(self) -> list:
        """
        Return keys in scheme that are missing in data
        """
        return sorted(list(self.get_scheme_keys() - self.get_data_keys()))

    def generate_report(self) -> dict:
        """
        Generate a comprehensive validation report.
        """
        return {
            "all_data_keys_in_scheme": self.all_data_keys_in_scheme(),
            "all_scheme_keys_in_data": self.all_scheme_keys_in_data(),
            "keys_to_remove": self.get_keys_to_remove(),
            "keys_missing": self.get_missed_keys(),
            "data_keys": sorted(list(self.get_data_keys())),
            "scheme_keys": sorted(list(self.get_scheme_keys())),
        }
    
JSON_SCHEME = {
    "title_in_english": "The title of the content in english",
    "title_in_hebrew": "The title of the content in hebrew",
    "author_in_english": "The content's author name (string, empty if unknown) in english",
    "author_in_hebrew": "The content's author name (string, empty if unknown) in hebrew",
    "publication_date": "YYYY-MM-DD",
    "language": "The primary language of the content",
    "type": "One of the content types listed above",
    "media": "One of the media types listed above",
    "platform": "The website or platform where the content is published",
    "source": "The original issuer of the information (e.g., UN, IDF, MoH). If the publisher is the original issuer, match platform",
    "reference": "Canonical link to the primary document or official source cited (string, empty if none)",
    "summary_in_enlgish": "One clear, informative sentence summarizing the main content, in english",
    "summary_in_hebrew": "One clear, informative sentence summarizing the main content, in hebrew",
    "event_start_date": "YYYY-MM-DD",
    "event_end_date": "YYYY-MM-DD",
    "theme_tags": ["relevant", "theme", "tags"],
    "countries_and_organizations_tags": ["relevant", "countries_and_organizations", "tags"],
    "location_tags": ["relevant", "location", "tags"],
    "figures_tags": ["relevant", "figures", "tags"]
}
