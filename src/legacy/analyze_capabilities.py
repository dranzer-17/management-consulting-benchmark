"""Domain 4: Capability emphasis, proxied by the share of H-1B filings in technical/analytical occupations.

Technical = SOC major group 15 (Computer and Mathematical Occupations), e.g. data scientists,
statisticians, software developers, operations research analysts.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
df = pd.read_csv(ROOT / "data" / "clean" / "lca_firms.csv")
df = df[df["case_status"].str.upper().str.startswith("CERTIFIED") & df["fiscal_year"].between(2015, 2025)].copy()
df["soc_group"] = df["soc_code"].astype(str).str.extract(r"^(\d{2})")[0]
df["soc_title"] = df["soc_title"].str.title()
df["technical"] =df["soc_group"].eq("15")
df["mgmt_analyst"] = df["soc_code"].astype(str).str.startswith("13-1111")
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}

print("Rows with SOC code missing:", df["soc_code"].isna().mean().round(3))
print("\nOverall technical share:\n", df.groupby("firm")["technical"].mean().round(3))
print("\nManagement-analyst share:\n", df.groupby("firm")["mgmt_analyst"].mean().round(3))
share = df.pivot_table(index="fiscal_year", columns="firm", values="technical", aggfunc="mean")
n = df.pivot_table(index="fiscal_year", columns="firm", values="technical", aggfunc="size")
print("\nTechnical share by year:\n", share.round(3))
print("\nTechnical filings by year (count):\n", df.pivot_table(index="fiscal_year", columns="firm", values="technical", aggfunc="sum").astype(int))

early, late = df["fiscal_year"].between(2015, 2019), df["fiscal_year"].between(2021, 2025)
print("\nTechnical share FY2015-19 vs FY2021-25:")
print(pd.DataFrame({"FY2015-19": df[early].groupby("firm")["technical"].mean(), "FY2021-25": df[late].groupby("firm")["technical"].mean()}).round(3))
tech_soc = df[df.technical].groupby(["firm", "soc_title"]).size().groupby(level=0, group_keys=False).nlargest(5)
print("\nTop technical occupations:\n", tech_soc)

ax = share.plot(figsize=(8, 4.5), color=[COL[f] for f in share.columns], marker="o")
ax.set_title("Share of certified filings in technical occupations (SOC 15)")
ax.set_xlabel("Fiscal year"); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1)); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "technical_share_by_year.png", dpi=150)
