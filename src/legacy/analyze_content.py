"""Set 7: Published content footprint (sitemaps, OpenAlex) as a research-emphasis proxy.

Counts of dated public pages and works, classified with the shared taxonomy (taxonomy.py).
This measures what each firm PUBLISHES, not what it earns. McKinsey's site is not covered (it does not respond to
automated requests from this environment); OpenAlex has no Bain institution record.
"""
import re
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taxonomy import topic_of

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
COL = {"McKinsey": "#1f3a5f", "BCG": "#2e8b57", "Bain": "#c0392b"}
s = pd.read_csv(ROOT / "data" / "clean" / "site_content_firms.csv")

# --- BCG dated publications (URL contains /publications/YYYY/slug)
b = s[(s.firm == "BCG") & (s.top == "publications") & s.year_in_path.between(2013, 2025)].copy()
b["slug"] = b["path"].str.split("/").str[-1]
b["topic"] = b["slug"].map(topic_of)
print("BCG dated publications 2013-2025:", len(b))
by_year = b.groupby("year_in_path").size(); print(by_year.to_dict())
tm = pd.crosstab(b["year_in_path"], b["topic"]); print("\nBCG topic counts by year:\n", tm)
print("\nBCG topic share overall (%):\n", (b.topic.value_counts(normalize=True) * 100).round(1))
def share(df, lo, hi): return (df[df.year_in_path.between(lo, hi)].topic.value_counts(normalize=True) * 100).round(1)
print("\nBCG topic share 2013-17 vs 2021-25:\n", pd.concat({"2013-17": share(b, 2013, 2017), "2021-25": share(b, 2021, 2025)}, axis=1).fillna(0))
tech = b[b.slug.str.contains(r"(^|-)(ai|genai|gen-ai|generative|artificial-intelligence|agentic)(-|$)")]
print("\nBCG publications with AI in the slug by year:", tech.groupby("year_in_path").size().to_dict())

# --- Bain dated press releases (path .../press-releases/<region>/<year>/slug)
p = s[(s.firm == "Bain") & s.path.str.contains("press-releases")].copy()
parts = p["path"].str.split("/")
p["region"] = parts.str[3]; p["year"] = parts.str[4]
p = p[p.year.str.fullmatch(r"20\d{2}", na=False)].assign(year=lambda x: x.year.astype(int))
print("\nBain press releases:", len(p), p.groupby("year").size().to_dict())
print("Regions:", p.region.value_counts().head(15).to_dict())
p["topic"] = p["path"].str.split("/").str[-1].map(topic_of)
print("Press-release topics:", p.topic.value_counts().head(8).to_dict())

# --- inventory pages for industries / capabilities / offices
inv = s.assign(group=lambda d: d.top.where(d.top.isin(["industries", "industry-expertise", "capabilities", "consulting-services", "offices", "press", "client-results", "our-team"])))
print("\nInventory pages by group:\n", inv.dropna(subset=["group"]).pivot_table(index="group", columns="firm", values="url", aggfunc="count").fillna(0).astype(int))
# office cities
bo = s[(s.firm == "Bain") & (s.top == "offices")].path.str.split("/").str[1].value_counts()
bc = s[(s.firm == "BCG") & (s.top == "offices")].path.str.split("/").str[1].value_counts()
print("\nBain office slugs:", len(bo), " BCG office slugs:", len(bc))
print("Bain offices sample:", sorted(bo.index.tolist())[:40])

# --- industry sections of BCG and Bain
bi = s[(s.firm == "BCG") & (s.top == "industries")].path.str.split("/").str[1].value_counts().head(25)
print("\nBCG industries sections:", bi.to_dict())
ai = s[(s.firm == "Bain") & (s.top == "industry-expertise")].path.str.split("/").str[1].str.lower().value_counts()
print("Bain industry-expertise sections:", ai.to_dict())

# --- OpenAlex works
w = pd.read_csv(ROOT / "data" / "clean" / "openalex_works_firms.csv")
print("\nOpenAlex works:", w.groupby("firm").size().to_dict(), " years:", w.year.min(), w.year.max())
print("Works by year:\n", w.pivot_table(index="year", columns="firm", values="work_id", aggfunc="count").fillna(0).astype(int).tail(12))
print("Top fields:\n", w.groupby("firm")["field"].apply(lambda x: (x.value_counts(normalize=True).head(5) * 100).round(1).to_dict()))
print("Median citations:", w.groupby("firm")["cited_by_count"].median().to_dict(), " mean:", w.groupby("firm")["cited_by_count"].mean().round(1).to_dict())

ax = by_year.plot.bar(figsize=(8, 4.2), color=COL["BCG"]); ax.set_title("BCG dated publication pages per year (from sitemap URLs)"); ax.set_xlabel("Year")
plt.tight_layout(); plt.savefig(FIG / "bcg_publications_by_year.png", dpi=150); plt.close()
ax = p.groupby("year").size().plot.bar(figsize=(8, 4.2), color=COL["Bain"]); ax.set_title("Bain press-release pages per year (from sitemap URLs)"); ax.set_xlabel("Year")
plt.tight_layout(); plt.savefig(FIG / "bain_press_by_year.png", dpi=150); plt.close()
b.to_csv(ROOT / "data" / "clean" / "bcg_publications.csv", index=False)
p.to_csv(ROOT / "data" / "clean" / "bain_press_releases.csv", index=False)
