"""Extract scholarly works with a McKinsey / BCG / Bain affiliation from OpenAlex.

Source: OpenAlex API (https://openalex.org), open and keyless. One row per work per firm,
with publication year, type, citation count and the primary topic/field/domain (a subject-emphasis proxy).
Output: data/clean/openalex_works_firms.csv
"""
import re
import time
from pathlib import Path
import pandas as pd
import requests
from src.common import CONTACT, HEADERS

API = "https://api.openalex.org"
MAIL = {"mailto": CONTACT} if "@" in CONTACT else {}
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "openalex_works_firms.csv"
FIRMS = {"McKinsey": ("McKinsey", r"mckinsey"),
         "BCG": ("Boston Consulting Group", r"boston consulting"),
         "Bain": ("Bain & Company", r"^bain (&|and) co")}


def institutions(search, pattern):
    out = []
    for page in (1, 2):
        r = requests.get(f"{API}/institutions", headers=HEADERS, params={**MAIL, "search": search, "per-page": 50, "page": page}, timeout=60).json()
        out += [i for i in r["results"] if re.search(pattern, i["display_name"], re.I)]
    return {i["id"].rsplit("/", 1)[-1]: i["display_name"] for i in out}


def works(inst_ids):
    flt = "institutions.id:" + "|".join(inst_ids) + ",publication_year:2010-2025"
    cursor, rows = "*", []
    while cursor:
        r = requests.get(f"{API}/works", headers=HEADERS, params={**MAIL, "filter": flt, "per-page": 200, "cursor": cursor,
                         "select": "id,doi,title,publication_year,type,cited_by_count,primary_topic"}, timeout=90).json()
        for w in r["results"]:
            t = w.get("primary_topic") or {}
            rows.append({"work_id": w["id"], "title": w.get("title"), "year": w["publication_year"], "type": w.get("type"),
                         "cited_by_count": w.get("cited_by_count"), "topic": t.get("display_name"),
                         "subfield": (t.get("subfield") or {}).get("display_name"),
                         "field": (t.get("field") or {}).get("display_name"),
                         "domain": (t.get("domain") or {}).get("display_name")})
        cursor = r["meta"].get("next_cursor")
        time.sleep(0.2)
    return rows


def main():
    frames = []
    for firm, (search, pat) in FIRMS.items():
        inst = institutions(search, pat)
        print(firm, "institutions:", inst)
        if not inst:
            continue
        df = pd.DataFrame(works(list(inst)))
        df.insert(0, "firm", firm)
        frames.append(df)
        print(firm, len(df), "works")
    out = pd.concat(frames, ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"{len(out):,} rows written to {OUT}")

if __name__ == "__main__":
    main()
