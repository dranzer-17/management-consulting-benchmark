"""Export stage: writes everything the website shows into web/data/ (JSON) and web/public/data/ (downloadable CSVs).

The site (Next.js, web/) is static and reads only these files, so no research number is typed into the frontend.
Outputs:
  web/data/tables.json     every outputs/tables/*.csv (except metrics) keyed by file name
  web/data/metrics.json    metrics.csv with definition, numerator, denominator, filters, missing-data rule, source IDs
  web/data/claims.json     claims.csv (each claim is tested against metrics by tests/test_pipeline.py)
  web/data/sources.json    sources.csv
  web/data/summary.json    counts and coverage derived from the files above
  web/public/data/*.csv    selected cleaned datasets offered for download
Run: python -m src.export_web
"""
import json
import os
import shutil
from datetime import datetime

import pandas as pd

from src import validate
from src.common import CLEAN, ROOT, TABLES

WEB = ROOT / "web"
DATA = WEB / "data"
DOWNLOADS = WEB / "public" / "data"
REPO = "https://github.com/dranzer-17/management-consulting-benchmark"

# clean file -> source ID(s). Derived tables are excluded from the record count (they restate other tables).
CLEAN_SOURCES = {
    "lca.csv": "S1", "perm.csv": "S1", "awards.csv": "S2", "subawards.csv": "S2", "firm_scale_points.csv": "S3",
    "site_inventory.csv": "S4", "bcg_publications.csv": "S4", "bain_press_releases.csv": "S4", "office_pages.csv": "S4",
    "sec_mentions.csv": "S5", "uk_contracts.csv": "S6", "canada_contracts.csv": "S7", "austender_contracts.csv": "S8",
    "openalex_works.csv": "S9", "attention_monthly.csv": "S10", "wikidata_facts.csv": "S11",
}
DERIVED = {"sec_mentions_operating.csv": "subset of sec_mentions.csv", "industry_taxonomy.csv": "derived from site_inventory.csv",
           "capability_taxonomy.csv": "derived from site_inventory.csv"}
DOWNLOAD_FILES = ["lca.csv", "perm.csv", "awards.csv", "uk_contracts.csv", "canada_contracts.csv", "austender_contracts.csv", "firm_scale_points.csv"]


def frame(path, **kw):
    return json.loads(pd.read_csv(path, keep_default_na=False, **kw).to_json(orient="records"))


def write(name, obj):
    (DATA / name).write_text(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    tables = {p.stem: frame(p) for p in sorted(TABLES.glob("*.csv")) if p.stem != "metrics"}
    metrics = frame(TABLES / "metrics.csv")
    claims = frame(ROOT / "claims.csv", usecols=["claim_id", "claim", "metric", "source_ids", "method", "limitation", "status"])
    sources = frame(ROOT / "sources.csv")
    write("tables.json", tables); write("metrics.json", metrics); write("claims.json", claims); write("sources.json", sources)

    datasets = []
    for f, sid in CLEAN_SOURCES.items():
        datasets.append({"file": f, "source_id": sid, "rows": int(len(pd.read_csv(CLEAN / f)))})
    validate.FAILURES.clear(); validate.PASSED.clear()
    failures = validate.run()
    period = next(m["period"] for m in metrics if m["metric_id"] == "HIRE-001")   # e.g. "FY2015-2025": the analysis window
    fy_range = [int(x) for x in period.replace("FY", "").split("-")]
    summary = {
        # "Last updated" shown on the site: the local run date, or LAST_UPDATED=YYYY-MM-DD to set it explicitly
        "generated_at": os.environ.get("LAST_UPDATED") or datetime.now().strftime("%Y-%m-%d"),
        "repo": REPO,
        "firms": 3,
        "sources": len(sources),
        "source_records": sum(d["rows"] for d in datasets),
        "source_records_note": "rows across the clean source tables; derived tables (" + ", ".join(DERIVED) + ") are excluded",
        "datasets": datasets,
        "derived_tables": DERIVED,
        "metric_definitions": len({m["metric_id"] for m in metrics}),
        "metric_values": len(metrics),
        "claims": len(claims),
        "claims_verified": sum(c["status"] == "verified" for c in claims),
        "validation_checks_passed": len(validate.PASSED),
        "validation_failures": len(failures),
        "us_filings_fiscal_years": fy_range,
        "analysis_dimensions": 8,
        "downloads": DOWNLOAD_FILES + ["metrics.csv", "claims.csv", "sources.csv"],
    }
    write("summary.json", summary)

    for f in DOWNLOAD_FILES:
        shutil.copy(CLEAN / f, DOWNLOADS / f)
    shutil.copy(TABLES / "metrics.csv", DOWNLOADS / "metrics.csv")
    shutil.copy(ROOT / "claims.csv", DOWNLOADS / "claims.csv")
    shutil.copy(ROOT / "sources.csv", DOWNLOADS / "sources.csv")
    print(f"web/data written: {len(tables)} tables, {len(metrics)} metric rows, {len(claims)} claims, "
          f"{summary['source_records']:,} source records, {summary['validation_checks_passed']} checks passed")


if __name__ == "__main__":
    main()
