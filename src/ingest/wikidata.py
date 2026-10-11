"""Extract dated revenue / employee-count statements (with their references) for the three firms from Wikidata.

Source: Wikidata entity JSON (CC0). Output: data/clean/wikidata_facts.csv
Properties: P2139 total revenue, P1128 employees, P571 inception, P159 headquarters. Qualifier P585 = point in time.
"""
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS

HEADERS = COMMON_HEADERS
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "wikidata_facts.csv"
ENTITIES = {"McKinsey": "Q310207", "BCG": "Q135635", "Bain": "Q764850"}
PROPS = {"P2139": "revenue", "P1128": "headcount", "P2137": "total_assets", "P3362": "operating_income"}


def main():
    rows = []
    for firm, qid in ENTITIES.items():
        ent = requests.get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json", headers=HEADERS, timeout=60).json()["entities"][qid]
        for pid, metric in PROPS.items():
            for c in ent["claims"].get(pid, []):
                snak = c["mainsnak"].get("datavalue", {}).get("value", {})
                amount = snak.get("amount") if isinstance(snak, dict) else None
                when = (c.get("qualifiers", {}).get("P585") or [{}])[0].get("datavalue", {}).get("value", {}).get("time")
                refs = [r["snaks"].get("P854", [{}])[0].get("datavalue", {}).get("value") for r in c.get("references", [])]
                unit = snak.get("unit", "").rsplit("/", 1)[-1] if isinstance(snak, dict) else None
                rows.append({"firm": firm, "qid": qid, "metric": metric, "value": amount, "unit": unit, "point_in_time": when,
                             "reference_url": next((r for r in refs if r), None), "rank": c.get("rank")})
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} statements written to {OUT}")
    print(df.to_string(index=False) if len(df) else "none")

if __name__ == "__main__":
    main()
