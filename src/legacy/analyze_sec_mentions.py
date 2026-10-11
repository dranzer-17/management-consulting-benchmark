"""Set 5: Which industries' public-company filings name each firm? (SEC EDGAR full-text mentions)

Keeps operating-company filing types only; excludes funds/ETFs (forms 497, 485BPOS, N-*), proxy statements
(director biographies), and blank-check shells. Industry is the filer's SIC code mapped via taxonomy.py.
A mention is a visibility signal, NOT evidence of a paid engagement.
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taxonomy import sic_to_industry

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
d = pd.read_csv(ROOT / "data" / "clean" / "sec_mentions.csv", dtype={"sic": str})
d["year"] = d["file_date"].str[:4].astype(int)
d["industry"] = d["sic"].map(sic_to_industry)
OPERATING = {"10-K", "8-K", "S-1", "20-F", "S-4", "DRS", "10-Q", "S-1/A", "424B4", "424B1", "40-F"}
print("All filings with a mention:", d.groupby("firm").size().to_dict())
o = d[d["form"].isin(OPERATING) & ~d["industry"].isin(["Blank-check / SPAC", "Investment vehicles and PE"]) & d["industry"].notna()].copy()
print("Operating-company filings with a mapped industry:", o.groupby("firm").size().to_dict())
print("Distinct filers:", o.groupby("firm")["cik"].nunique().to_dict())
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}

mix = pd.crosstab(o["industry"], o["firm"], normalize="columns")
print("\nIndustry mix of operating-company filings:\n", (mix * 100).round(1).sort_values("McKinsey", ascending=False))
cnt = pd.crosstab(o["industry"], o["firm"]); print("\nCounts:\n", cnt)
yr = o.pivot_table(index="year", columns="firm", values="adsh", aggfunc="count")
print("\nFilings by year:\n", yr)
early, late = o["year"].between(2015, 2019), o["year"].between(2021, 2025)
shift = pd.concat({"2015-19": pd.crosstab(o[early]["industry"], o[early]["firm"], normalize="columns"),
                   "2021-25": pd.crosstab(o[late]["industry"], o[late]["firm"], normalize="columns")}, axis=1)
print("\nShift in mix, McKinsey:\n", (shift.xs("McKinsey", axis=1, level=1) * 100).round(1))
print("Shift in mix, BCG:\n", (shift.xs("BCG", axis=1, level=1) * 100).round(1))
print("Shift in mix, Bain:\n", (shift.xs("Bain", axis=1, level=1) * 100).round(1))
# concentration
print("\nHHI of industry mix:", (mix ** 2).sum().round(3).to_dict())
# vs. all-SEC-filer baseline not available; report top filers per firm
for f in COL:
    print(f, "top filers:", o[o.firm == f]["company"].str.replace(r"\s+\(CIK.*", "", regex=True).value_counts().head(5).to_dict())

ax = (mix * 100).sort_values("McKinsey").plot.barh(figsize=(9, 5.5), color=[COL[c] for c in mix.columns])
ax.set_xlabel("% of firm's operating-company filings that mention it"); ax.set_ylabel(""); ax.set_title("Industry of filers mentioning each firm (SEC EDGAR, 2015 to 2025)")
plt.tight_layout(); plt.savefig(FIG / "sec_industry_mix.png", dpi=150); plt.close()
o.to_csv(ROOT / "data" / "clean" / "sec_mentions_operating.csv", index=False)
