"""Extract federal SUBAWARDS where McKinsey / BCG / Bain is the subcontractor, from USAspending.gov.

Complements extract_awards.py (prime contracts). Output: data/clean/subawards_firms.csv
"""
import re
from pathlib import Path
import pandas as pd
import requests

from src.common import firm_of

URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "subawards_firms.csv"
SEARCHES = ["McKinsey", "Boston Consulting", "Bain & Company", "Bain and Company"]
FIELDS = ["Sub-Award ID", "Sub-Awardee Name", "Sub-Award Amount", "Sub-Award Date", "Sub-Award Type",
          "Prime Recipient Name", "Prime Award ID", "Awarding Agency", "Awarding Sub Agency", "Sub-Award Description"]


def pull(text):
    rows, page = [], 1
    while True:
        body = {"filters": {"recipient_search_text": [text], "award_type_codes": ["A", "B", "C", "D"],
                            "time_period": [{"start_date": "2007-10-01", "end_date": "2025-09-30"}]},
                "fields": FIELDS, "subawards": True, "page": page, "limit": 100, "sort": "Sub-Award Amount", "order": "desc"}
        r = requests.post(URL, json=body, timeout=90)
        r.raise_for_status()
        d = r.json()
        rows += d.get("results", [])
        if not d.get("page_metadata", {}).get("hasNext"):
            return rows
        page += 1


def main():
    df = pd.DataFrame([r for s in SEARCHES for r in pull(s)]).drop(columns=["internal_id", "generated_internal_id", "prime_award_generated_internal_id"], errors="ignore")
    df["firm"] = df["Sub-Awardee Name"].map(firm_of)
    df = df.dropna(subset=["firm"]).drop_duplicates(subset=["firm", "Sub-Award ID", "Prime Award ID", "Sub-Award Amount", "Sub-Award Date"])
    d = pd.to_datetime(df["Sub-Award Date"], errors="coerce")
    df["fiscal_year"] = d.dt.year + (d.dt.month >= 10)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} subawards written to {OUT}")
    print(df.groupby("firm")["Sub-Award Amount"].agg(["count", "sum"]))


if __name__ == "__main__":
    main()
