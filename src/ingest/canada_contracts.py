"""Extract federal contracts to McKinsey / BCG / Bain from Canada's proactive-disclosure contracts dataset.

Streams the 600+ MB CSV from open.canada.ca and keeps only matching vendor rows; the raw file is never stored.
Source: https://open.canada.ca/data/en/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b (contracts over $10,000).
Usage: python -m src.ingest.canada_contracts [local_csv]
Output: data/raw/canada_contracts_firms.csv
"""
import io
import re
from pathlib import Path
import pandas as pd
import requests

from src.common import firm_of

CKAN = "https://open.canada.ca/data/api/3/action/package_show?id=d8f85d91-7dec-4fd1-8055-483b77225d8b"
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "canada_contracts_firms.csv"


def scan(text, keep):
    for chunk in pd.read_csv(text, chunksize=100_000, dtype=str, on_bad_lines="skip"):
        chunk["firm"] = chunk["vendor_name"].map(firm_of)
        hit = chunk.dropna(subset=["firm"])
        if len(hit):
            keep.append(hit)


def main(local_csv=None):
    """Stream the CSV from open.canada.ca, or filter a copy already downloaded to local_csv (resumable with curl -C -)."""
    keep = []
    if local_csv:
        with open(local_csv, encoding="utf-8-sig", errors="replace") as text:
            scan(text, keep)
    else:
        pkg = requests.get(CKAN, timeout=60).json()["result"]
        url = next(r["url"] for r in pkg["resources"] if r["name"] == "Contracts over $10,000")
        print("streaming", url)
        with requests.get(url, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            resp.raw.decode_content = True
            scan(io.TextIOWrapper(resp.raw, encoding="utf-8-sig", errors="replace"), keep)
    df = pd.concat(keep, ignore_index=True)
    cols = ["firm", "vendor_name", "reference_number", "contract_date", "contract_period_start", "delivery_date",
            "contract_value", "original_value", "amendment_value", "owner_org", "owner_org_title",
            "description_en", "commodity_type", "commodity_code", "solicitation_procedure"]
    df = df[[c for c in cols if c in df.columns]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} contracts written to {OUT}")
    print(df.groupby("firm").size())


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
