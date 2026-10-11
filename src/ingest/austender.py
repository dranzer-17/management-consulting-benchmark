"""Extract Australian federal contracts awarded to McKinsey / BCG / Bain from the AusTender OCDS API.

Source: https://api.tenders.gov.au (Open Contracting Data Standard). The API has no supplier filter, so every
contract notice published 2015-2025 is paged through (weekly windows, 6 workers) and filtered locally.
Resumable: finished windows are recorded in data/raw/austender_done.txt (gitignored).
Output: data/raw/austender_contracts_firms.csv
"""
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS, firm_of

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
DONE = RAW / "austender_done.txt"
PART = RAW / "austender_rows.jsonl"
OUT = RAW / "austender_contracts_firms.csv"
HEADERS = COMMON_HEADERS
BASE = "https://api.tenders.gov.au/ocds/findByDates/contractPublished/{a}T00:00:00Z/{b}T23:59:59Z"
START, END = date(2015, 1, 1), date(2025, 12, 31)


def fetch(url):
    for attempt in range(6):
        try:
            r = requests.get(url, headers=HEADERS, timeout=120)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def window(a, b):
    url, rows, seen = BASE.format(a=a, b=b), [], 0
    while url:
        j = fetch(url)
        for rel in j.get("releases", []):
            seen += 1
            sup = {p["id"]: p["name"] for p in rel.get("parties", []) if "supplier" in p.get("roles", [])}
            hit = {i: n for i, n in sup.items() if firm_of(n)}
            if not hit:
                continue
            buyer = next((p["name"] for p in rel.get("parties", []) if "procuringEntity" in p.get("roles", [])), None)
            for c in rel.get("contracts", []):
                rows.append({"firm": firm_of(next(iter(hit.values()))), "supplier": next(iter(hit.values())), "buyer": buyer,
                             "contract_id": c.get("id"), "date_signed": c.get("dateSigned"), "title": c.get("title"),
                             "description": c.get("description"), "value": (c.get("value") or {}).get("amount"),
                             "currency": (c.get("value") or {}).get("currency"),
                             "unspsc": next((it["classification"]["id"] for it in c.get("items", []) if it.get("classification")), None),
                             "start": (c.get("period") or {}).get("startDate"), "end": (c.get("period") or {}).get("endDate"),
                             "method": (rel.get("tender") or {}).get("procurementMethodDetails")})
        url = j.get("links", {}).get("next")
    return a, rows, seen


def main():
    done = set(DONE.read_text().split()) if DONE.exists() else set()
    wins, d = [], START
    while d <= END:
        e = min(d + timedelta(days=6), END)
        if d.isoformat() not in done:
            wins.append((d.isoformat(), e.isoformat()))
        d = e + timedelta(days=1)
    print(f"{len(wins)} windows to fetch", flush=True)
    total = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(window, a, b) for a, b in wins]
        for n, f in enumerate(as_completed(futs), 1):
            a, rows, seen = f.result()
            total += seen
            with PART.open("a") as fh:
                for r in rows:
                    fh.write(pd.Series(r).to_json() + "\n")
            with DONE.open("a") as fh:
                fh.write(a + "\n")
            if n % 10 == 0:
                print(f"{n}/{len(wins)} windows, {total:,} releases scanned", flush=True)
    df = pd.read_json(PART, lines=True, dtype=False).drop_duplicates(subset=["firm", "contract_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} contracts written to {OUT}")
    print(df.groupby("firm").size())


if __name__ == "__main__":
    main()
