"""Extract federal contract awards to McKinsey / BCG / Bain from USAspending.gov.

Uses the public USAspending API (no key needed). The recipient search is fuzzy,
so results are filtered to the firms' actual legal-entity names.
Output: data/clean/awards_firms.csv
"""
import re
from pathlib import Path
import pandas as pd
import requests

from src.common import firm_of

URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "awards_firms.csv"
SEARCHES = ["McKinsey", "Boston Consulting", "Bain & Company", "Bain and Company"]
FIELDS = ["Award ID", "Recipient Name", "Award Amount", "Start Date", "End Date",
          "Awarding Agency", "Awarding Sub Agency", "Contract Award Type", "NAICS", "PSC"]


def pull(text):
    rows, page = [], 1
    while True:
        body = {"filters": {"recipient_search_text": [text], "award_type_codes": ["A", "B", "C", "D"],
                            "time_period": [{"start_date": "2007-10-01", "end_date": "2025-09-30"}]},
                "fields": FIELDS, "page": page, "limit": 100, "sort": "Award Amount", "order": "desc"}
        resp = requests.post(URL, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        rows += data.get("results", [])
        if not data.get("page_metadata", {}).get("hasNext"):
            return rows
        page += 1


def main():
    rows = [r for s in SEARCHES for r in pull(s)]
    df = pd.DataFrame(rows).drop(columns=["internal_id", "generated_internal_id"], errors="ignore")
    df["firm"] = df["Recipient Name"].map(firm_of)
    df = df.dropna(subset=["firm"]).drop_duplicates(subset=["firm", "Award ID"])
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    # US federal fiscal year starts 1 Oct
    df["fiscal_year"] = df["Start Date"].dt.year + (df["Start Date"].dt.month >= 10)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} awards written to {OUT}")
    print(df.groupby("firm")["Award Amount"].agg(["count", "sum"]))


if __name__ == "__main__":
    main()
