"""Build the SQLite benchmarking database from the standardized tables in data/clean/. Output: data/benchmark.db
Run: python -m src.build_database   then   python -m src.run_queries
"""
import sqlite3

import pandas as pd

from src.common import CLEAN, FIRMS, ROOT

DB = ROOT / "data" / "benchmark.db"


def load(con, table, file, cols, firms):
    d = pd.read_csv(CLEAN / file)
    d["firm_id"] = d["firm"].map(firms)
    d["certified"] = d["certified"].astype(int) if "certified" in d else None
    if "is_technical" in d:
        d["is_technical"] = d["is_technical"].astype(int)
    d[cols].to_sql(table, con, if_exists="append", index=False)


def main():
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "sql" / "schema.sql").read_text())
    firms = {f: i for i, f in enumerate(FIRMS, 1)}
    con.executemany("INSERT INTO dim_firm VALUES (?, ?)", [(i, n) for n, i in firms.items()])
    load(con, "fact_lca", "lca.csv", ["case_number", "firm_id", "fiscal_year", "case_status", "certified", "job_title", "soc_code",
                                      "soc_title", "is_technical", "worksite_state", "worksite_city", "positions", "wage_annual"], firms)
    load(con, "fact_award", "awards.csv", ["award_id", "firm_id", "fiscal_year", "agency", "sub_agency", "award_usd", "naics_desc", "psc_desc"], firms)
    load(con, "fact_firm_scale", "firm_scale_points.csv", ["firm_id", "year", "metric", "value", "unit", "type", "confidence", "source_url", "note"], firms)
    con.commit()
    for t in ["dim_firm", "fact_lca", "fact_award", "fact_firm_scale"]:
        print(t, con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
    con.close()


if __name__ == "__main__":
    main()
