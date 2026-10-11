"""Extract public content inventories (URL, last-modified date, section, year, region) from firm sitemaps.

Only the sitemap files named in each site's robots.txt are fetched; no page is crawled.
McKinsey's site does not respond to automated requests from this environment, so it is not covered.
Output: data/clean/site_content_firms.csv
"""
import re
from pathlib import Path
import pandas as pd
import requests
from src.common import HEADERS as COMMON_HEADERS

HEADERS = COMMON_HEADERS
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "site_content_firms.csv"
SITEMAPS = {"BCG": ["https://www.bcg.com/google_sitemap-content.xml"],
            "Bain": ["https://www.bain.com/en/sitemap.xml"]}
URL_RE = re.compile(r"<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?")


def parse(firm, url, lastmod):
    path = re.sub(r"^https?://[^/]+/", "", url).strip("/")
    parts = path.split("/")
    year = next((int(p) for p in parts if re.fullmatch(r"(19|20)\d{2}", p)), None)
    return {"firm": firm, "url": url, "lastmod": lastmod, "section": "/".join(parts[:2]) if len(parts) > 1 else parts[0],
            "top": parts[0], "year_in_path": year, "depth": len(parts), "path": path}


def main():
    rows = []
    for firm, urls in SITEMAPS.items():
        for sm in urls:
            xml = requests.get(sm, headers=HEADERS, timeout=120).text
            rows += [parse(firm, u, lm) for u, lm in URL_RE.findall(xml)]
    df = pd.DataFrame(rows).drop_duplicates(subset=["firm", "url"])
    df["lastmod_year"] = pd.to_datetime(df["lastmod"], errors="coerce", utc=True).dt.year
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} URLs written to {OUT}")
    print(df.groupby(["firm", "top"]).size().sort_values(ascending=False).head(20))

if __name__ == "__main__":
    main()
