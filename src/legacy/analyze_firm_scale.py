"""Domain 3: Firm-level scale (revenue, headcount, reach) from sourced public data points.

Input is a hand-compiled, source-linked table (data/clean/firm_scale_points.csv).
Derived figures are only computed where both end points exist for the same firm.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
d = pd.read_csv(ROOT / "data" / "clean" / "firm_scale_points.csv")
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}

print("Data points by firm and type:\n", d.groupby(["firm", "type"]).size().unstack(fill_value=0))
p = d.pivot_table(index=["firm", "year"], columns="metric", values="value")
print("\nAll points:\n", p)

def cagr(first, last, years):
    return (last / first) ** (1 / years) - 1

def val(firm, year, metric):
    return p.loc[(firm, year), metric]

print("\nBCG revenue CAGR 2018-2025: {:.1%}".format(cagr(val("BCG", 2018, "revenue"), val("BCG", 2025, "revenue"), 7)))
print("BCG headcount CAGR 2018-2025: {:.1%}".format(cagr(val("BCG", 2018, "headcount"), val("BCG", 2025, "headcount"), 7)))
print("Headcount CAGR 2018-2023: BCG {:.1%}, McKinsey {:.1%}".format(
    cagr(val("BCG", 2018, "headcount"), val("BCG", 2023, "headcount"), 5),
    cagr(val("McKinsey", 2018, "headcount"), val("McKinsey", 2023, "headcount"), 5)))
print("\nRevenue per employee, 2023 (USD thousand):")
for f in ["BCG", "McKinsey", "Bain"]:
    print(f"  {f}: {val(f, 2023, 'revenue') * 1e9 / val(f, 2023, 'headcount') / 1e3:,.0f}")
print("BCG revenue per employee (USD thousand): 2018 {:,.0f}, 2025 {:,.0f}".format(
    val("BCG", 2018, "revenue") * 1e9 / val("BCG", 2018, "headcount") / 1e3,
    val("BCG", 2025, "revenue") * 1e9 / val("BCG", 2025, "headcount") / 1e3))

# chart: all revenue points, marker style by type
fig, ax = plt.subplots(figsize=(8, 4.5))
for f, g in d[d.metric == "revenue"].groupby("firm"):
    g = g.sort_values("year")
    for _, r in g.iterrows():
        ax.scatter(r.year, r.value, color=COL[f], marker="o" if r.type == "reported" else "^", s=55, label=None)
ax.set_title("Revenue data points (USD billion): circles reported, triangles estimated")
ax.set_xlabel("Year"); ax.grid(alpha=.3)
ax.legend(handles=[plt.Line2D([], [], color=c, label=f) for f, c in COL.items()], loc="upper left")
plt.tight_layout(); plt.savefig(FIG / "revenue_points.png", dpi=150)
