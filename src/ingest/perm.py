"""Extract McKinsey / BCG / Bain PERM (green card labor certification) filings from the public DOL mirror.

Same remote-query approach as extract_lca.py. Output: data/clean/perm_firms.csv
Note: some DOL name fields lost the ampersand ("MCKINSEY  COMPANY"), so matching is on the leading name only.
"""
from pathlib import Path
import time

import duckdb

URL = "https://huggingface.co/datasets/Nason/dol-visas-database/resolve/main/dol_visas.duckdb"
OUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "perm_firms.csv"
FIRM_CASE = """
CASE
  WHEN regexp_matches(lower(employer_name), '^mckinsey\\s*(&(amp;)?|and)?\\s*company') THEN 'McKinsey'
  WHEN employer_name ILIKE '%boston consulting group%' THEN 'BCG'
  WHEN regexp_matches(lower(employer_name), '^bain\\s+(&(amp;)?\\s*|and\\s+)?(company|co\\b)') THEN 'Bain'
END
"""
QUERY = f"""
SELECT {FIRM_CASE} AS firm, employer_name, fiscal_year, case_number, case_status,
       employer_num_employees, employer_year_established, employer_state,
       job_title, soc_code, soc_title, naics_code, worksite_state, worksite_city,
       country_of_citizenship, foreign_worker_birth_country, minimum_education, major_field_of_study,
       wage_offer_from, wage_offer_unit_of_pay, pw_level, received_date, decision_date
FROM v.perm WHERE is_latest AND ({FIRM_CASE}) IS NOT NULL
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
    con.sql(f"ATTACH '{URL}' AS v (READ_ONLY)")
    df = query_with_retry(con, QUERY)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"{len(df):,} rows written to {OUT}")
    print(df.groupby("firm").size())

if __name__ == "__main__":
    main()
