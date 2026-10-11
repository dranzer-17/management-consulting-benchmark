"""Run every query in sql/queries against data/benchmark.db and print the results."""
import sqlite3
from pathlib import Path
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "data" / "benchmark.db")
con.create_function("POWER", 2, lambda x, y: math.pow(x, y))
pd.set_option("display.width", 200, "display.max_rows", 200)
for q in sorted((ROOT / "sql" / "queries").glob("*.sql")):
    print(f"\n### {q.name}\n{q.read_text().splitlines()[0]}")
    print(pd.read_sql(q.read_text(), con).to_string(index=False))
