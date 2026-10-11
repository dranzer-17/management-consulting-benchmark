"""Extract SEC EDGAR filings that mention McKinsey / BCG / Bain, with the filer's industry (SIC code).

Source: SEC EDGAR full-text search (efts.sec.gov), 2015-2025. One row per filing (accession number) per firm.
A mention is NOT proof of a client relationship: names also appear in cited studies, director biographies, etc.
Output: data/clean/sec_mentions.csv
"""
import time
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS

URL = "https://efts.sec.gov/LATEST/search-index"
HEADERS = COMMON_HEADERS
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "sec_mentions.csv"
PHRASES = {"McKinsey": '"McKinsey & Company"', "BCG": '"Boston Consulting Group"', "Bain": '"Bain & Company"'}
START, END = date(2015, 1, 1), date(2025, 12, 31)
PAGE = 100


def get(params):
    for attempt in range(5):
        r = requests.get(URL, params=params, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            return r.json()
        time.sleep(2 * (attempt + 1))
    r.raise_for_status()


def window_rows(firm, q, start, end):
    """All hits in [start, end]; splits the window if the result set exceeds the 10,000 paging cap."""
    base = {"q": q, "dateRange": "custom", "startdt": start.isoformat(), "enddt": end.isoformat()}
    first = get(base)
    total = first["hits"]["total"]["value"]
    if total > 9000 and (end - start).days > 0:
        mid = start + (end - start) // 2
        return window_rows(firm, q, start, mid) + window_rows(firm, q, mid + timedelta(days=1), end)
    hits = first["hits"]["hits"]
    for offset in range(PAGE, total, PAGE):
        time.sleep(0.15)
        hits += get({**base, "from": offset})["hits"]["hits"]
    rows = []
    for h in hits:
        s = h["_source"]
        rows.append({"firm": firm, "adsh": s["adsh"], "file_date": s["file_date"], "form": s.get("root_forms", [s.get("form")])[0],
                     "company": (s["display_names"] or [""])[0], "cik": (s["ciks"] or [""])[0],
                     "sic": (s.get("sics") or [""])[0], "biz_state": (s.get("biz_states") or [""])[0],
                     "file_type": s.get("file_type")})
    time.sleep(0.15)
    return rows


def main():
    rows = []
    for firm, q in PHRASES.items():
        for year in range(START.year, END.year + 1):
            for m in range(1, 13):
                s = date(year, m, 1)
                e = (date(year + (m == 12), m % 12 + 1, 1)) - timedelta(days=1)
                got = window_rows(firm, q, s, e)
                rows += got
            print(firm, year, len(rows), flush=True)
    df = pd.DataFrame(rows).drop_duplicates(subset=["firm", "adsh"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} filings written to {OUT}")
    print(df.groupby("firm").size())

if __name__ == "__main__":
    main()
