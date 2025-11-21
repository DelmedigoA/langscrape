from typing import Tuple
import pandas as pd
import math
import datetime


XLSX_PATH = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/summaries/data.xlsx"
SHEET_NAME = "MASTER Production"
OUTPUT_DIR = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/summaries"
SAMPLES = 100
SEED = 88

MAPPING = {
    "Title": "summary.title",
    "Description*": "summary.summary",
    "published Date": "summary.publication_date",
    "Event date from": "summary.event_start_date",
    "Event date to": "summary.event_end_date",
    "Platform": "summary.platform",
    "Author": "summary.author",
    "Source": "summary.source",
    "Reference": "summary.reference",
    "Language": "summary.language",
    "Location": "summary.location_tags",
    "Locations (tag)": "summary.location_tags",
    "Type": "summary.type",
    "Media": "summary.media",
    "Theme (tag)": "summary.theme_tags",
    "Places & Organizations (tag)": "summary.countries_and_organizations_tags",
    "Figures (tag)": "summary.figures_tags",
}

def get_key_1_2(key) -> Tuple[str, str]:
    return key.split(".")[0], key.split(".")[-1]

def dfid_to_json(id):
    row = df[df.Number == id].squeeze()
    data = {"summary": {}}
    for key in MAPPING.keys():
        k1, k2 = get_key_1_2(MAPPING[key])
        value = row[key]
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, float):
            value = None if math.isnan(value) else value
        data[k1][k2] = value
    return data

df = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME)
df = df.sample(n=SAMPLES, random_state=SEED)

lines = []
for row in range(len(df)):
    data = {"summary": {}}
    for key in MAPPING.keys():
        k1, k2 = get_key_1_2(MAPPING[key])
        value = df.iloc[row][key]
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, float):
            value = None if math.isnan(value) else value
        data[k1][k2] = value
    lines.append(data)

print(lines[0])