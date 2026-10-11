"""Set 6: US workforce size and talent profile from PERM (green-card) labor certifications."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
d = pd.read_csv(ROOT / "data" / "clean" / "perm_firms.csv")
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}
print("Rows:", d.groupby("firm").size().to_dict(), " FY range:", d.fiscal_year.min(), d.fiscal_year.max())

# 1. employer-reported US headcount on the form
# The yearly MAXIMUM is used: individual filings sometimes report a smaller entity/office count, so the largest value
# reported in a year best approximates the firm-wide US headcount. FY2015 BCG (503) is an outlier and is excluded.
emp = d[d.fiscal_year.between(2016, 2024)].pivot_table(index="fiscal_year", columns="firm", values="employer_num_employees", aggfunc="max")
emp_n = d[d.fiscal_year.between(2015, 2024)].pivot_table(index="fiscal_year", columns="firm", values="employer_num_employees", aggfunc="count")
print("\nMax employer-reported US employees by FY (FY2016-24):\n", emp, "\nN with a value:\n", emp_n)
print("Distinct reported values by firm (FY2016-24):")
for f in COL:
    print(" ", f, sorted(d[(d.firm == f) & d.fiscal_year.between(2016, 2024)].employer_num_employees.dropna().unique())[:25])
# 2. filings per year and outcome
yr = d.pivot_table(index="fiscal_year", columns="firm", values="case_number", aggfunc="count").fillna(0).astype(int)
print("\nPERM filings by FY:\n", yr)
print("\nOutcome mix:\n", pd.crosstab(d.firm, d.case_status.str.replace("-EXPIRED", ""), normalize="index").round(3))
# 3. talent origin
cit = d.groupby("firm")["country_of_citizenship"].apply(lambda s: (s.str.title().value_counts(normalize=True).head(6) * 100).round(1).to_dict())
print("\nTop citizenship (%):\n", cit)
print("\nDistinct citizenships:", d.groupby("firm")["country_of_citizenship"].nunique().to_dict())
# 4. education
print("\nMinimum education required (%):\n", (pd.crosstab(d.firm, d.minimum_education, normalize="index") * 100).round(1))
print("\nTop majors:\n", d.groupby("firm")["major_field_of_study"].apply(lambda s: s.str.title().value_counts().head(4).to_dict()))
d["major_l"] = d["major_field_of_study"].str.lower().fillna("")
for label, pat in [("business", "business"), ("computer science", "computer"), ("quantitative/engineering", "engineering|quantitative|stat|math|operations|analytics")]:
    print("Share of filings naming", label, "as a major:", d.assign(h=d.major_l.str.contains(pat)).groupby("firm").h.mean().round(3).to_dict())
# 5. consistency check vs LCA data
lca = pd.read_csv(ROOT / "data" / "clean" / "lca_firms.csv")
print("\nLCA vs PERM filings (FY2016-2024) per firm:", lca[lca.fiscal_year.between(2016, 2024)].groupby("firm").size().to_dict(), d[d.fiscal_year.between(2016, 2024)].groupby("firm").size().to_dict())

ax = emp.loc[2016:2024].plot(figsize=(8, 4.5), color=[COL[c] for c in emp.columns], marker="o")
ax.set_title("Employer-reported US employees on PERM filings (yearly maximum)"); ax.set_xlabel("Fiscal year"); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(FIG / "perm_us_employees.png", dpi=150)
