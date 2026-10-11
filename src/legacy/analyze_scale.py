"""Domain 1: Scale & hiring footprint, from H-1B LCA filings."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(ROOT / "data" / "clean" / "lca_firms.csv", parse_dates=["received_date", "decision_date"])

ANNUAL = {"Year": 1, "Hour": 2080, "Week": 52, "Month": 12, "Bi-Weekly": 26}
df["wage_annual"] = df["wage_rate_of_pay_from"] * df["wage_unit_of_pay"].map(ANNUAL)
df.loc[~df["wage_annual"].between(30_000, 1_000_000), "wage_annual"] = pd.NA
df["soc_title"] = df["soc_title"].str.title()
df["job_title"] = df["job_title"].str.title()
df["certified"] =df["case_status"].str.upper().str.startswith("CERTIFIED")
df["positions"] = df["total_worker_positions"].fillna(1)
c = df[df["certified"]]
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}
out = {}

out["overview"] = df.groupby("firm").agg(rows=("case_number", "size"), certified=("certified", "sum"),
    positions=("positions", "sum"), first_fy=("fiscal_year", "min"), last_fy=("fiscal_year", "max"))
out["overview"]["cert_rate"] = out["overview"]["certified"] / out["overview"]["rows"]

yr = c.pivot_table(index="fiscal_year", columns="firm", values="case_number", aggfunc="count").fillna(0)
pos = c.pivot_table(index="fiscal_year", columns="firm", values="positions", aggfunc="sum").fillna(0)
out["filings_by_year"], out["positions_by_year"] = yr, pos

def cagr(s, a, b):
    s = s.loc[a:b]
    return (s.iloc[-1] / s.iloc[0]) ** (1 / (len(s) - 1)) - 1 if s.iloc[0] > 0 else float("nan")
out["cagr_2016_2024"] = pd.Series({f: cagr(yr[f], 2016, 2024) for f in yr.columns})

out["states"] = c.groupby("firm")["worksite_state"].nunique()
out["cities"] = c.groupby("firm")["worksite_city"].nunique()
top_states = c.pivot_table(index="worksite_state", columns="firm", values="positions", aggfunc="sum").fillna(0)
share = top_states / top_states.sum()
out["top_states_share"] = share.assign(total=top_states.sum(axis=1)).sort_values("total", ascending=False).head(8).drop(columns="total")
out["hhi_state"] = (share ** 2).sum()
out["wage_median"] = c.groupby("firm")["wage_annual"].median()
out["wage_by_year"] = c.pivot_table(index="fiscal_year", columns="firm", values="wage_annual", aggfunc="median")
out["wage_level"] = pd.crosstab(c["firm"], c["pw_wage_level"], normalize="index")
out["top_soc"] = c.groupby(["firm", "soc_title"]).size().groupby(level=0, group_keys=False).nlargest(5)
out["top_titles"] = c.groupby(["firm", "job_title"]).size().groupby(level=0, group_keys=False).nlargest(4)

# charts
for name, data, title in [("filings_by_year", yr, "Certified H-1B LCA filings per fiscal year"),
                          ("wage_by_year", out["wage_by_year"], "Median offered annual wage (USD)")]:
    ax = data.plot(figsize=(8, 4.5), color=[COL[f] for f in data.columns], marker="o")
    ax.set_title(title); ax.set_xlabel("Fiscal year"); ax.grid(alpha=.3); plt.tight_layout()
    plt.savefig(FIG / f"{name}.png", dpi=150); plt.close()
ax = out["top_states_share"].plot.bar(figsize=(8, 4.5), color=[COL[f] for f in out["top_states_share"].columns])
ax.set_title("Share of certified positions by worksite state (top 8)"); ax.set_ylabel("Share"); plt.tight_layout()
plt.savefig(FIG / "state_share.png", dpi=150); plt.close()

pd.set_option("display.width", 200, "display.float_format", "{:,.3f}".format)
for k, v in out.items():
    print(f"\n=== {k} ===\n{v}")
