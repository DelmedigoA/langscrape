from typing import Tuple
import pandas as pd
import math
import datetime
import os
import json

XLSX_PATH = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/summaries/data_24-11.xlsx"
SHEET_NAME = "For_Fine_Tune"
OUTPUT_DIR = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/summaries"

MAPPING = {
    "Title": "summary.title_in_english",
    "Title (Hebrew)": "summary.title_in_hebrew",
    "Description": "summary.summary_in_english",
    "Description (Hebrew)": "summary.summary_in_hebrew",
    "published Date": "summary.publication_date",
    "Event date from": "summary.event_start_date",
    "Event date to": "summary.event_end_date",
    "Platform": "summary.platform",
    "Author": "summary.author_in_english",
    "Author (Hebrew)": "summary.author_in_hebrew",
    "Source": "summary.source",
    "Reference": "summary.reference",
    "Language": "summary.language",
    "Location": "summary.free_location_tags_in_english",
    "Location (Hebrew)": "summary.free_location_tags_in_hebrew",
    "Locations (tag)": "summary.location_tags",
    "Type": "summary.type",
    "Media": "summary.media",
    "Theme (tag)": "summary.theme_tags",
    "Places & Organizations (tag)": "summary.countries_and_organizations_tags",
    "Figures (tag)": "summary.figures_tags",
}

def get_key_1_2(key) -> Tuple[str, str]:
    return key.split(".")[0], key.split(".")[-1]

def dfid_to_json(id, df):
    row = df[df.Number.astype(str) == str(id)].squeeze()
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



# lines = []
# for row in range(len(df)):
#     data = {"summary": {}}
#     for key in MAPPING.keys():
#         k1, k2 = get_key_1_2(MAPPING[key])
#         value = df.iloc[row][key]
#         if isinstance(value, datetime.datetime):
#             value = value.strftime("%Y-%m-%d")
#         elif isinstance(value, float):
#             value = None if math.isnan(value) else value
#         data[k1][k2] = value
#     lines.append(data)

root = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/extractions"
unique_ids = list(set([p.split("_")[0] for p in os.listdir(root)]))
df = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME)
lines = []
for id in unique_ids:
    system = open(os.path.join(root, id + "_system.txt")).read()
    user = open(os.path.join(root, id + "_user.txt")).read()
    assistant = dfid_to_json(id, df)
    line = {"messages":[{"role":"system","content":system},{"role":"user","content":user},{"role":"assistant","content":assistant}]}
    lines.append(line)

final_path = "/Users/delmedigo/Dev/langtest/langscrape/fine_tuning/finetuning_ready_data/data.jsonl"
errors = 0
with open(final_path, "w") as f:
    for l in lines:
        try:
            json_line = json.dumps(l, ensure_ascii=False)
            f.write(json_line + "\n")
        except Exception as e:
            print(e)
            errors+=1
            #print(l)
import json

rows = []
with open(final_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))

# print(rows[0]["messages"][0])
print(f"total errors:", errors)