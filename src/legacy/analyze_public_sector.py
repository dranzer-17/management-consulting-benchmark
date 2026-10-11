"""Domain 2: Public-sector exposure, from USAspending federal contract awards."""
import ast
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(ROOT / "data" / "clean" / "awards_firms.csv")
parse = lambda s, k: ast.literal_eval(s).get(k) if isinstance(s, str) else None
df["naics_desc"] = df["NAICS"].map(lambda s: parse(s, "description"))
df["psc_desc"] = df["PSC"].map(lambda s: parse(s, "description"))
df = df[df["fiscal_year"].between(2015, 2024)]  # decade window; FY2025 is incomplete
df = df[df["Award Amount"] > 0]
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}
out = {}

out["overview"] = df.groupby("firm")["Award Amount"].agg(awards="count", total_usd="sum", median_usd="median", max_usd="max")
yr_n = df.pivot_table(index="fiscal_year", columns="firm", values="Award ID", aggfunc="count").fillna(0)
yr_usd = df.pivot_table(index="fiscal_year", columns="firm", values="Award Amount", aggfunc="sum").fillna(0) / 1e6
out["awards_by_year"], out["usd_m_by_year"] = yr_n, yr_usd

df["agency_group"] = df["Awarding Agency"].where(df["Awarding Agency"].isin(df["Awarding Agency"].value_counts().head(5).index), "Other")
ag = df.pivot_table(index="agency_group", columns="firm", values="Award Amount", aggfunc="sum").fillna(0)
out["agency_share"] = (ag / ag.sum()).sort_values("McKinsey", ascending=False)
out["defense_share"] = df.assign(d=df["Awarding Agency"].eq("Department of Defense")).groupby("firm").apply(
    lambda g: g.loc[g.d, "Award Amount"].sum() / g["Award Amount"].sum())
out["distinct_agencies"] = df.groupby("firm")["Awarding Agency"].nunique()
top5 = lambda col: df.groupby(["firm", col])["Award Amount"].sum().groupby(level=0, group_keys=False).nlargest(4)
out["top_psc_by_usd"], out["top_naics_by_usd"] = top5("psc_desc"), top5("naics_desc")
out["top_agency_by_usd"] = top5("Awarding Agency")

ax = yr_usd.plot.bar(figsize=(9, 4.5), color=[COL[f] for f in yr_usd.columns])
ax.set_title("Federal contract value by award start year (USD millions)"); ax.set_xlabel("Fiscal year"); plt.tight_layout()
plt.savefig(FIG / "awards_usd_by_year.png", dpi=150); plt.close()
ag_p = out["agency_share"]
ax = ag_p.plot.bar(figsize=(9, 4.8), color=[COL[f] for f in ag_p.columns])
ax.set_title("Share of federal contract value by awarding agency"); ax.set_xlabel(""); plt.xticks(rotation=30, ha="right"); plt.tight_layout()
plt.savefig(FIG / "awards_agency_share.png", dpi=150); plt.close()

pd.set_option("display.width", 220, "display.float_format", "{:,.2f}".format, "display.max_colwidth", 70)
for k, v in out.items():
    print(f"\n=== {k} ===\n{v}")
