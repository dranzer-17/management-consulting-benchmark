"""Public-attention time series for the three firms: Wikipedia pageviews and GDELT news-volume intensity.

- Wikipedia: monthly user pageviews of each firm's English article (Wikimedia REST API), 2015-07 to 2025-12.
- GDELT: share of global news coverage mentioning the firm's name (DOC 2.0 API, 'Volume Intensity'), 2017-2025.
Both measure attention, not business performance. Output: data/clean/attention_monthly.csv
"""
import time
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS

HEADERS = COMMON_HEADERS
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "attention_monthly.csv"
WIKI = {"McKinsey": "McKinsey_%26_Company", "BCG": "Boston_Consulting_Group", "Bain": "Bain_%26_Company"}
GDELT = {"McKinsey": '"McKinsey & Company"', "BCG": '"Boston Consulting Group"', "Bain": '"Bain & Company"'}


def wiki(article):
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{article}/monthly/20150701/20251231"
    items = requests.get(url, headers=HEADERS, timeout=60).json()["items"]
    return [{"month": f"{i['timestamp'][:4]}-{i['timestamp'][4:6]}", "value": i["views"]} for i in items]


def gdelt(query):
    for attempt in range(4):
        r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", headers=HEADERS, timeout=90,
                         params={"query": query, "mode": "timelinevol", "format": "json",
                                 "startdatetime": "20170101000000", "enddatetime": "20251231000000"})
        if r.ok and r.text.startswith("{"):
            data = r.json()["timeline"][0]["data"]
            df = pd.DataFrame(data)
            df["month"] = df["date"].str[:4] + "-" + df["date"].str[4:6]
            return df.groupby("month")["value"].mean().reset_index().to_dict("records")
        time.sleep(8 * (attempt + 1))
    return []


def main():
    rows = []
    for firm in WIKI:
        rows += [{"firm": firm, "source": "wikipedia_pageviews", **r} for r in wiki(WIKI[firm])]
        time.sleep(1)
        rows += [{"firm": firm, "source": "gdelt_volume_intensity", **r} for r in gdelt(GDELT[firm])]
        time.sleep(6)
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} monthly observations written to {OUT}")
    print(df.groupby(["source", "firm"]).size())


if __name__ == "__main__":
    main()
