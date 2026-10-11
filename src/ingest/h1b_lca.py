"""Extract McKinsey / BCG / Bain H-1B LCA filings from the public DOL mirror.

Queries the DuckDB file remotely (HTTP range requests), so the 3 GB raw file is
never stored. Output: data/clean/lca_firms.csv
Original source: US DOL OFLC LCA disclosure data (mirror: Nason/dol-visas-database).
"""
from pathlib import Path
import time

import duckdb

URL = "https://huggingface.co/datasets/Nason/dol-visas-database/resolve/main/dol_visas.duckdb"
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "lca_firms.csv"

# Order matters: first matching pattern wins. 'Boston Consulting Solutions' is excluded.
FIRM_CASE = """
CASE
  WHEN regexp_matches(lower(employer_name), '^mckinsey\\s*(&(amp;)?|and)?\\s*company') THEN 'McKinsey'
  WHEN employer_name ILIKE '%boston consulting group%' THEN 'BCG'
  WHEN regexp_matches(lower(employer_name), '^bain\\s+(&(amp;)?\\s*|and\\s+)?(company|co\\b)') THEN 'Bain'
END
"""

QUERY = f"""
SELECT {FIRM_CASE} AS firm, employer_name, fiscal_year, case_number, case_status,
       visa_class, job_title, soc_code, soc_title, naics_code,
       worksite_city, worksite_state, total_worker_positions,
       wage_rate_of_pay_from, wage_unit_of_pay, prevailing_wage, pw_wage_level,
       full_time_position, h_1b_dependent, received_date, decision_date
FROM visas.lca
WHERE is_latest AND ({FIRM_CASE}) IS NOT NULL
"""

def query_with_retry(con, sql, attempts=5):
    """The Hugging Face host occasionally throttles range reads (HTTP 403/429); retry with backoff."""
    for i in range(attempts):
        try:
            return con.sql(sql).df()
        except duckdb.HTTPException as e:
            if i == attempts - 1:
                raise
            print(f"  transient HTTP error ({str(e)[:60]}...), retrying in {30 * (i + 1)}s")
            time.sleep(30 * (i + 1))


def main():
    con = duckdb.connect()
    con.sql("INSTALL httpfs; LOAD httpfs;")
    con.sql(f"ATTACH '{URL}' AS visas (READ_ONLY)")
    df = query_with_retry(con, QUERY)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} rows written to {OUT}")
    print(df.groupby("firm").size())

if __name__ == "__main__":
    main()
