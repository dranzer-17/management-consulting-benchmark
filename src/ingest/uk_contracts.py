"""Extract UK central/local government contract awards to McKinsey / BCG / Bain from Contracts Finder.

Source: Contracts Finder search API (gov.uk). Quoted-phrase keyword search, windowed by publication year because the
API has no pagination. Results are filtered to awards whose awardedSupplier matches the firm's name.
Output: data/clean/uk_contracts_firms.csv
"""
import re
import time
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS, firm_of

URL = "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/json"
HEADERS = {**COMMON_HEADERS, "Content-Type": "application/json"}
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "uk_contracts_firms.csv"
QUERIES = {"McKinsey": '"McKinsey & Company"', "BCG": '"Boston Consulting Group"', "Bain": '"Bain & Company"'}
FIELDS = ["noticeIdentifier", "title", "organisationName", "awardedSupplier", "awardedValue", "awardedDate", "publishedDate",
          "cpvDescription", "cpvCodes", "start", "end", "region"]


def search(kw, year):
    body = {"searchCriteria": {"keyword": kw, "types": ["Contract"], "statuses": ["Awarded"],
                               "publishedFrom": f"{year}-01-01", "publishedTo": f"{year}-12-31"}, "size": 100}
    for attempt in range(5):
        r = requests.post(URL, json=body, headers=HEADERS, timeout=90)
        if r.status_code == 200:
            j = r.json()
            if j["hitCount"] > 100:
                print("  WARNING: >100 hits, results truncated for", kw, year, j["hitCount"])
            return [n["item"] for n in j["noticeList"]]
        time.sleep(3 * (attempt + 1))
    r.raise_for_status()


def main():
    rows = []
    for firm, kw in QUERIES.items():
        for year in range(2015, 2026):
            for it in search(kw, year):
                if firm_of(it.get("awardedSupplier")) == firm:
                    rows.append({"firm": firm, **{f: it.get(f) for f in FIELDS}})
            time.sleep(0.3)
    df = pd.DataFrame(rows).drop_duplicates(subset=["firm", "noticeIdentifier"])
    df["awardedValue"] = pd.to_numeric(df["awardedValue"], errors="coerce")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} awards written to {OUT}")
    print(df.groupby("firm")["awardedValue"].agg(["count", "sum", "median"]))


if __name__ == "__main__":
    main()
