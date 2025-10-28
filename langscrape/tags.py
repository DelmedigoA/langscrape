import pandas as pd

df = pd.read_excel("/Users/delmedigo/Dev/langtest/langscrape/data/TAGS.xlsx")

TYPES = df.TYPES.dropna().tolist()

MEDIAS = df.MEDIAS.dropna().tolist()

LANGUAGES = df.LANGUAGES.dropna().tolist()

PLATFORMS = df.PLATFORMS.dropna().tolist()

THEMES = df.THEMES.dropna().tolist()

COUNTRIES_AND_ORGANIZATIONS = df.COUNTRIES_AND_ORGANIZATIONS.dropna().tolist()

LOCATIONS = df.LOCATIONS.dropna().tolist()

FIGURES = df.FIGURES.dropna().tolist()

keys = df.columns.tolist()

TAGS_DICT = {key: df[key].dropna().tolist() for key in keys}

