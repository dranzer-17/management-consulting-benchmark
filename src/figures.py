"""Figures stage: draws every chart from outputs/tables/*.csv. Each chart carries its source and retrieval date.
Run: python -m src.figures
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.common import COLORS, FIGURES, FIRMS, TABLES

RETRIEVED = "retrieved Oct 2026"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25})


def t(name, **kw):
    return pd.read_csv(TABLES / f"{name}.csv", **kw)


def finish(fig, name, title, source, subtitle=None):
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold")
    if subtitle:
        fig.text(0.01, 0.9, subtitle, fontsize=9, color="#555")
    fig.text(0.01, 0.01, f"Source: {source}; {RETRIEVED}.", fontsize=7.5, color="#666")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93 if subtitle else 0.96))
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", dpi=150)
    plt.close(fig)


def lines(df, name, title, source, ylabel="", pct=False, subtitle=None, marker="o"):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for f in FIRMS:
        if f in df.columns:
            ax.plot(df.index, df[f], color=COLORS[f], marker=marker, label=f, lw=2)
    ax.set_xlabel("Fiscal year"); ax.set_ylabel(ylabel); ax.legend(frameon=False)
    if pct:
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100))
    finish(fig, name, title, source, subtitle)


def bars(df, name, title, source, xlabel="", horizontal=False, subtitle=None):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    cols = [f for f in FIRMS if f in df.columns]
    df[cols].plot.barh(ax=ax, color=[COLORS[c] for c in cols]) if horizontal else df[cols].plot.bar(ax=ax, color=[COLORS[c] for c in cols], rot=0)
    if horizontal:
        ax.set_xlabel(xlabel); ax.set_ylabel("")
    else:
        ax.set_ylabel(xlabel); ax.set_xlabel("")
    ax.legend(frameon=False)
    finish(fig, name, title, source, subtitle)


S1 = "US DOL OFLC LCA/PERM disclosure data via Hugging Face mirror (S1)"
S2 = "USAspending.gov (S2)"


def main():
    f = t("lca_filings_by_year", index_col=0)
    lines(f, "filings_by_year", "Certified H-1B filings per fiscal year", S1, "filings", subtitle="Proxy for US hiring of foreign nationals; not headcount")
    lines(t("lca_median_wage_by_year", index_col=0), "wage_by_year", "Median offered annual base wage (USD)", S1, "USD", subtitle="Offered base wage in certified filings; excludes bonuses")
    bars(t("lca_state_share_top10", index_col=0).head(8), "state_share", "Share of certified positions by worksite state (top 8)", S1, "share of positions", subtitle="FY2015-2025")
    lines(t("technical_share_by_year", index_col=0), "technical_share_by_year", "Technical share of certified filings (SOC 15)", S1, "% of certified filings", pct=True,
          subtitle="Share of sponsored filings, not of total workforce")
    bars(t("federal_value_usd_m_by_year", index_col=0), "awards_usd_by_year", "Federal prime contract value by award start year (USD millions)", S2, "USD millions",
         subtitle="Award value attributed to start year; Bain: none found")
    bars(t("federal_agency_share_pct", index_col=0), "awards_agency_share", "Share of federal contract value by awarding agency (%)", S2, "% of value")
    perm = t("perm_us_employees_max_by_year", index_col=0)
    lines(perm, "perm_us_employees", "US employees reported on PERM filings (yearly maximum)", S1, "employees", subtitle="Filer-defined, unaudited; McKinsey values are rounded")
    mix = t("sec_industry_mix_pct", index_col=0).drop(index=["Public sector"], errors="ignore")
    bars(mix.sort_values("McKinsey"), "sec_industry_mix", "Industry of filers whose SEC filings name each firm (%)", "SEC EDGAR full-text search (S5)", "% of operating-company filings", horizontal=True,
         subtitle="Visibility signal, not evidence of paid work; the mix mostly reflects the SEC filer universe")
    pts = t("scale_points_all")
    rev = pts[pts.metric == "revenue"]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for _, r in rev.iterrows():
        ax.scatter(r.year, r.value, color=COLORS[r.firm], marker="o" if r.type == "reported" else "^", s=60)
    ax.set_xlabel("Year"); ax.set_ylabel("USD billion"); ax.set_xticks(range(2018, 2026))
    ax.legend(handles=[plt.Line2D([], [], color=c, marker="s", ls="", label=k) for k, c in COLORS.items()], frameon=False, loc="upper left")
    finish(fig, "revenue_points", "Revenue data points (circles reported, triangles estimated)", "Firm releases and secondary sources (S3)", subtitle="Sparse observations; no trend line is drawn between them")
    pub = t("bcg_publications_by_year", index_col=0)
    fig, ax = plt.subplots(figsize=(8, 4.2)); ax.bar(pub.index, pub["publications"], color=COLORS["BCG"]); ax.set_xlabel("Year"); ax.set_ylabel("publication pages")
    finish(fig, "bcg_publications_by_year", "BCG dated publication pages per year", "bcg.com sitemap (S4)", subtitle="Pages with the year in the URL; a count of published pages, not of research quality or revenue")
    ai = t("bcg_ai_publications_by_year", index_col=0)
    fig, ax = plt.subplots(figsize=(8, 4.2)); ax.plot(ai.index, ai.share_pct, color=COLORS["BCG"], marker="o", lw=2); ax.set_xlabel("Year"); ax.set_ylabel("% of publication pages")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100))
    finish(fig, "bcg_ai_share", "BCG publications whose URL names AI or GenAI (%)", "bcg.com sitemap (S4)", subtitle="Keyword match on the URL slug; undercounts AI content with other titles")
    uv = t("uk_value_gbp_m_by_year", index_col=0)
    bars(uv, "uk_value_by_year", "UK public-sector contract value by award year (GBP millions)", "Contracts Finder (S6)", "GBP millions", subtitle="Excludes framework agreements of GBP 50M or more (ceiling values)")
    for name, title, src, xl in [("canada_value_cad_m_by_year", "Canadian federal contract value by year (CAD millions)", "Open Canada proactive disclosure (S7)", "CAD millions"),
                                 ("austender_value_aud_m_by_year", "Australian federal contract value by year (AUD millions)", "AusTender OCDS API (S8)", "AUD millions")]:
        if (TABLES / f"{name}.csv").exists():
            df = t(name, index_col=0)
            bars(df.loc[2015:2025], name.replace("_cad_m", "_cad").replace("_aud_m", "_aud"), title, src, xl)
    print("figures ->", FIGURES)


if __name__ == "__main__":
    main()
