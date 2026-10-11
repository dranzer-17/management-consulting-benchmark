"""Export stage: bundles every table the website shows into web/data.js (window.DATA = {...}).

The site is static and reads only this file, so every number on it comes from outputs/tables/, claims.csv and sources.csv.
Run: python -m src.export_web
"""
import json

import pandas as pd

from src.common import ROOT, TABLES

WEB = ROOT / "web"


def frame(path, **kw):
    return json.loads(pd.read_csv(path, keep_default_na=False, **kw).to_json(orient="records"))


def main():
    WEB.mkdir(exist_ok=True)
    data = {"tables": {p.stem: frame(p) for p in sorted(TABLES.glob("*.csv")) if p.stem != "metrics"},
            "metrics": frame(TABLES / "metrics.csv"),
            "claims": frame(ROOT / "claims.csv", usecols=["claim_id", "claim", "metric", "source_ids", "method", "limitation", "status"]),
            "sources": frame(ROOT / "sources.csv")}
    (WEB / "data.js").write_text("window.DATA = " + json.dumps(data, separators=(",", ":")) + ";\n")
    print(f"web/data.js written: {len(data['tables'])} tables, {len(data['metrics'])} metric rows, {len(data['claims'])} claims")


if __name__ == "__main__":
    main()
