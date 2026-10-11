"""Metrics stage: computes every number used in findings, charts, the website and the deck.

Reads data/clean/, writes:
  outputs/tables/metrics.csv   one row per metric value, with definition, numerator, denominator, filters, missing-data rule
  outputs/tables/<series>.csv  year-by-year and segment tables used by charts and the website
Run: python -m src.metrics
Nothing downstream types a number by hand: claims.csv refers to metric_ids produced here.
"""
import numpy as np
import pandas as pd

from src.common import CLEAN, FIRMS, MANUAL, TABLES

WINDOW = (2015, 2025)          # decade window for LCA/PERM fiscal years
GROWTH = (2016, 2024)          # growth-rate window (FY2026 is partial and excluded)
FED_WINDOW = (2015, 2024)      # federal contract awards window (FY2025 incomplete)
ROWS = []
TABLE_NAMES = []


def add(metric_id, set_, firm, period, value, unit, basis, definition, numerator, denominator, filters, missing, sources):
    ROWS.append(dict(metric_id=metric_id, set=set_, firm=firm, period=period, value=value, unit=unit, basis=basis,
                     definition=definition, numerator=numerator, denominator=denominator, filters=filters,
                     missing_data=missing, source_ids=sources))


def save(df, name, index=True):
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / f"{name}.csv", index=index)
    TABLE_NAMES.append(name)


def per_firm(metric_id, set_, series, period, unit, basis, definition, numerator, denominator, filters, missing, sources, digits=None):
    for firm in FIRMS:
        if firm in series.index and pd.notna(series[firm]):
            v = series[firm]
            add(metric_id, set_, firm, period, round(float(v), digits) if digits is not None else float(v), unit, basis,
                definition, numerator, denominator, filters, missing, sources)


def cagr(first, last, years):
    return (last / first) ** (1 / years) - 1


# --------------------------------------------------------------------------------------------- Set 1: US hiring footprint
def hiring():
    d = pd.read_csv(CLEAN / "lca.csv")
    c = d[d.certified & d.fiscal_year.between(*WINDOW)]
    src = "S1"
    flt = "certified filings, FY2015-2025"
    per_firm("HIRE-001", "1", c.groupby("firm").size(), "FY2015-2025", "filings", "proxy",
             "Certified H-1B Labor Condition Applications filed by the firm", "count of certified LCA filings", "n/a", flt,
             "none: counted as filed", src)
    yr = c.pivot_table(index="fiscal_year", columns="firm", values="case_number", aggfunc="count").reindex(columns=FIRMS).fillna(0).astype(int)
    pos = c.pivot_table(index="fiscal_year", columns="firm", values="positions", aggfunc="sum").reindex(columns=FIRMS).fillna(0).astype(int)
    save(yr, "lca_filings_by_year"); save(pos, "lca_positions_by_year")
    g0, g1 = GROWTH
    per_firm("HIRE-002", "1", pd.Series({f: cagr(yr.loc[g0, f], yr.loc[g1, f], g1 - g0) for f in FIRMS}) * 100, "FY2016-2024", "% per year", "proxy",
             "Compound annual growth rate of certified LCA filings between two endpoint years", "filings in FY2024", "filings in FY2016",
             "certified filings; endpoint years only", "FY2026 excluded as partial", src, 1)
    per_firm("HIRE-003", "1", c.groupby("firm")["worksite_state"].nunique(), "FY2015-2025", "states", "proxy",
             "Distinct US worksite states in certified filings", "distinct worksite_state", "n/a", flt, "rows without a state are ignored", src)
    per_firm("HIRE-004", "1", c.groupby("firm")["worksite_city"].nunique(), "FY2015-2025", "cities", "proxy",
             "Distinct US worksite cities in certified filings", "distinct worksite_city", "n/a", flt, "rows without a city are ignored", src)
    share = c.pivot_table(index="worksite_state", columns="firm", values="positions", aggfunc="sum").reindex(columns=FIRMS).fillna(0)
    share = share / share.sum()
    per_firm("HIRE-005", "1", (share ** 2).sum(), "FY2015-2025", "index 0-1", "proxy",
             "Herfindahl-Hirschman index of the firm's position share across worksite states (higher = more concentrated)",
             "sum of squared state shares", "total certified positions", flt, "none", src, 3)
    save(share.sort_values("McKinsey", ascending=False).head(10), "lca_state_share_top10")
    per_firm("HIRE-006", "1", d[d.fiscal_year.between(*WINDOW)].groupby("firm")["positions"].mean(), "FY2015-2025", "positions per filing", "proxy",
             "Average number of worker positions requested per filing (all filings, any status)", "sum of positions", "count of filings",
             "all statuses, FY2015-2025", "missing positions treated as 1", src, 1)
    per_firm("HIRE-007", "1", c.groupby("firm")["wage_annual"].median(), "FY2015-2025", "USD", "proxy",
             "Median offered annual base wage", "median of annualized wage_rate_of_pay_from", "n/a", flt + "; wages outside $30K-$1M dropped",
             "rows with missing or out-of-range wage ignored", src, 0)
    wy = c.pivot_table(index="fiscal_year", columns="firm", values="wage_annual", aggfunc="median").reindex(columns=FIRMS)
    save(wy.round(0), "lca_median_wage_by_year")
    per_firm("HIRE-008", "1", d[d.fiscal_year.between(*WINDOW)].groupby("firm")["certified"].mean() * 100, "FY2015-2025", "%", "proxy",
             "Share of filings certified", "certified filings", "all filings", "FY2015-2025", "none", src, 1)
    wl = pd.crosstab(c["firm"], c["pw_wage_level"], normalize="index").reindex(FIRMS) * 100
    save(wl.round(1), "lca_wage_level_mix")
    occ = c.groupby(["firm", "soc_title"]).size().rename("filings").reset_index().sort_values(["firm", "filings"], ascending=[True, False]).groupby("firm").head(8)
    save(occ, "lca_top_occupations", index=False)
    return d


# --------------------------------------------------------------------------------------------- Set 4: capability emphasis
def capability(d):
    c = d[d.certified & d.fiscal_year.between(*WINDOW)]
    src = "S1"
    per_firm("CAP-001", "4", c.groupby("firm")["is_technical"].mean() * 100, "FY2015-2025", "%", "proxy",
             "Share of certified filings in technical occupations (SOC major group 15, computer and mathematical)",
             "certified filings with SOC 15-xxxx", "certified filings", "certified, FY2015-2025", "none", src, 1)
    early, late = c.fiscal_year.between(2015, 2019), c.fiscal_year.between(2021, 2025)
    per_firm("CAP-002", "4", c[early].groupby("firm")["is_technical"].mean() * 100, "FY2015-2019", "%", "proxy",
             "Technical share of certified filings, early period", "technical certified filings", "certified filings", "certified, FY2015-2019", "none", src, 1)
    per_firm("CAP-003", "4", c[late].groupby("firm")["is_technical"].mean() * 100, "FY2021-2025", "%", "proxy",
             "Technical share of certified filings, late period (FY2020 skipped as a pandemic transition year)", "technical certified filings",
             "certified filings", "certified, FY2021-2025", "none", src, 1)
    per_firm("CAP-004", "4", c.groupby("firm").apply(lambda g: (g.soc_code.astype(str).str.startswith("13-1111")).mean()) * 100, "FY2015-2025", "%", "proxy",
             "Share of certified filings classified as Management Analysts (SOC 13-1111)", "filings with SOC 13-1111", "certified filings",
             "certified, FY2015-2025", "none", src, 1)
    ts = c.pivot_table(index="fiscal_year", columns="firm", values="is_technical", aggfunc="mean").reindex(columns=FIRMS) * 100
    tn = c.pivot_table(index="fiscal_year", columns="firm", values="is_technical", aggfunc="sum").reindex(columns=FIRMS).astype(int)
    save(ts.round(1), "technical_share_by_year"); save(tn, "technical_filings_by_year")
    top = c[c.is_technical].groupby(["firm", "soc_title"]).size().rename("filings").reset_index().sort_values(["firm", "filings"], ascending=[True, False]).groupby("firm").head(5)
    save(top, "technical_top_occupations", index=False)


# --------------------------------------------------------------------------------------------- Set 6: workforce / PERM
def workforce():
    p = pd.read_csv(CLEAN / "perm.csv")
    src = "S1"
    per_firm("WORK-001", "6", p.groupby("firm").size(), "FY2015-2026", "filings", "proxy", "PERM labor-certification filings", "count of filings",
             "n/a", "all years incl. partial FY2026", "none", src)
    emp = p[p.fiscal_year.between(2016, 2024)].pivot_table(index="fiscal_year", columns="firm", values="employer_num_employees", aggfunc="max").reindex(columns=FIRMS)
    save(emp, "perm_us_employees_max_by_year")
    per_firm("WORK-002", "6", emp.loc[2024], "FY2024", "employees", "reported-on-form",
             "Largest US employee count reported by the firm on any PERM filing in the year (filer-defined, unaudited)",
             "max(employer_num_employees)", "n/a", "FY2016-2024; FY2015 BCG (503) and FY2025+ excluded", "filings without a value ignored", src)
    per_firm("WORK-003", "6", emp.loc[2016], "FY2016", "employees", "reported-on-form", "As WORK-002 for FY2016", "max(employer_num_employees)", "n/a",
             "FY2016", "filings without a value ignored", src)
    per_firm("WORK-004", "6", pd.Series({f: cagr(emp.loc[2016, f], emp.loc[2024, f], 8) for f in FIRMS}) * 100, "FY2016-2024", "% per year", "reported-on-form",
             "Compound annual growth of WORK-002/WORK-003 endpoints", "WORK-002", "WORK-003", "endpoint years", "none", src, 1)
    per_firm("WORK-005", "6", (p.assign(c=p.outcome.eq("CERTIFIED")).groupby("firm")["c"].mean()) * 100, "FY2015-2026", "%", "proxy",
             "Share of PERM cases certified", "cases with outcome CERTIFIED", "all cases", "all years", "none", src, 1)
    per_firm("WORK-006", "6", (p.assign(c=p.outcome.eq("WITHDRAWN")).groupby("firm")["c"].mean()) * 100, "FY2015-2026", "%", "proxy",
             "Share of PERM cases withdrawn", "cases with outcome WITHDRAWN", "all cases", "all years", "none", src, 1)
    has = lambda col: p[p[col].notna() & (p[col].astype(str).str.strip() != "")]
    per_firm("WORK-007", "6", has("citizenship").assign(i=lambda x: x.citizenship.eq("India")).groupby("firm")["i"].mean() * 100, "FY2015-2026", "%", "proxy",
             "Share of sponsored workers who are citizens of India", "filings with citizenship India", "filings with a citizenship value", "all years", "filings with blank citizenship excluded from the denominator", src, 1)
    per_firm("WORK-008", "6", p.groupby("firm")["citizenship"].nunique(), "FY2015-2026", "citizenships", "proxy", "Distinct citizenships among sponsored workers",
             "distinct citizenship values", "n/a", "all years", "blank ignored", src)
    per_firm("WORK-009", "6", has("minimum_education").assign(m=lambda x: x.minimum_education.eq("Master's")).groupby("firm")["m"].mean() * 100, "FY2015-2026", "%", "proxy",
             "Share of filings stating a Master's minimum education", "filings with minimum_education Master's", "filings with a minimum_education value", "all years", "blank excluded from the denominator", src, 1)
    for mid, pat, label in [("WORK-010", "business", "business"), ("WORK-011", "engineering|quantitative|stat|math|operations|analytics", "quantitative or engineering")]:
        per_firm(mid, "6", has("major").assign(h=lambda x, pat=pat: x.major.str.contains(pat)).groupby("firm")["h"].mean() * 100, "FY2015-2026", "%", "proxy",
                 f"Share of filings naming a {label} major", f"filings whose major matches /{pat}/", "filings with a major value", "all years", "blank major excluded from the denominator", src, 1)
    cit = has("citizenship").groupby("firm")["citizenship"].apply(lambda s: (s.value_counts(normalize=True).head(6) * 100).round(1)).rename("share_pct").reset_index().rename(columns={"level_1": "citizenship"})
    save(cit, "perm_citizenship_top", index=False)
    fl = p.pivot_table(index="fiscal_year", columns="firm", values="case_number", aggfunc="count").reindex(columns=FIRMS).fillna(0).astype(int)
    save(fl, "perm_filings_by_year")


# --------------------------------------------------------------------------------------------- Set 2: US federal public sector
def federal():
    a = pd.read_csv(CLEAN / "awards.csv")
    f = a[a.fiscal_year.between(*FED_WINDOW) & (a.award_usd > 0)]
    src = "S2"
    flt = "prime contracts, award start FY2015-2024, value > 0"
    per_firm("FED-001", "2", f.groupby("firm").size().reindex(FIRMS).fillna(0), "FY2015-2024", "awards", "reported", "Federal prime contract awards to the firm", "count of awards", "n/a", flt, "zero-value awards excluded", src)
    per_firm("FED-002", "2", f.groupby("firm")["award_usd"].sum().reindex(FIRMS).fillna(0) / 1e6, "FY2015-2024", "USD millions", "reported", "Total value of federal prime contract awards, attributed to start year",
             "sum of award_usd", "n/a", flt, "zero-value awards excluded", src, 1)
    per_firm("FED-003", "2", f.groupby("firm")["award_usd"].median() / 1e6, "FY2015-2024", "USD millions", "reported", "Median award value", "median award_usd", "n/a", flt, "none", src, 2)
    per_firm("FED-004", "2", f.groupby("firm")["award_usd"].max() / 1e6, "FY2015-2024", "USD millions", "reported", "Largest single award", "max award_usd", "n/a", flt, "none", src, 1)
    dod = f.assign(d=f.agency.eq("Department of Defense")).groupby("firm").apply(lambda g: g.loc[g.d, "award_usd"].sum() / g.award_usd.sum()) * 100
    per_firm("FED-005", "2", dod, "FY2015-2024", "%", "reported", "Share of contract value awarded by the Department of Defense", "value from DoD", "total value", flt, "none", src, 1)
    per_firm("FED-006", "2", f.groupby("firm")["agency"].nunique(), "FY2015-2024", "agencies", "reported", "Distinct awarding agencies", "distinct agency", "n/a", flt, "none", src)
    yv = f.pivot_table(index="fiscal_year", columns="firm", values="award_usd", aggfunc="sum").reindex(index=range(2015, 2025), columns=FIRMS).fillna(0) / 1e6
    yn = f.pivot_table(index="fiscal_year", columns="firm", values="award_id", aggfunc="count").reindex(index=range(2015, 2025), columns=FIRMS).fillna(0).astype(int)
    save(yv.round(2), "federal_value_usd_m_by_year"); save(yn, "federal_awards_by_year")
    top5 = f.agency.value_counts().head(5).index
    ag = f.assign(g=f.agency.where(f.agency.isin(top5), "Other")).pivot_table(index="g", columns="firm", values="award_usd", aggfunc="sum").reindex(columns=FIRMS).fillna(0)
    save((ag / ag.sum() * 100).round(1).sort_values("McKinsey", ascending=False), "federal_agency_share_pct")
    ag_full = f.groupby(["firm", "agency"])["award_usd"].sum().div(1e6).round(1).rename("value_usd_m").reset_index().sort_values(["firm", "value_usd_m"], ascending=[True, False])
    save(ag_full, "federal_value_by_agency", index=False)
    add("FED-007", "2", "Bain", "FY2015-2024", 0, "awards", "reported", "Federal prime contract awards found for Bain & Company (none found is not proof of no public-sector work)",
        "count of awards", "n/a", flt, "n/a", src)
    s = pd.read_csv(CLEAN / "subawards.csv")
    s = s[s.fiscal_year.between(*FED_WINDOW)]
    per_firm("FED-008", "2", s.groupby("firm").size().reindex(FIRMS).fillna(0), "FY2015-2024", "subawards", "reported", "Federal subawards where the firm is the subcontractor", "count of subawards", "n/a",
             "subaward fiscal year FY2015-2024", "none", "S2", )
    per_firm("FED-009", "2", s.groupby("firm")["amount_usd"].sum().reindex(FIRMS).fillna(0) / 1e6, "FY2015-2024", "USD millions", "reported", "Total value of federal subawards to the firm",
             "sum of amount_usd", "n/a", "subaward fiscal year FY2015-2024", "none", "S2", 1)


# --------------------------------------------------------------------------------------------- Set 3: scale and reach
def scale():
    s = pd.read_csv(CLEAN / "firm_scale_points.csv")
    p = s.pivot_table(index=["firm", "year"], columns="metric", values="value")
    v = lambda f, y, m: p.loc[(f, y), m]
    src = "S3"
    add("SCALE-001", "3", "BCG", "2018-2025", round(cagr(v("BCG", 2018, "revenue"), v("BCG", 2025, "revenue"), 7) * 100, 1), "% per year", "reported", "Compound annual growth of reported global revenue",
        "2025 revenue", "2018 revenue", "reported points only", "no interpolation", src)
    add("SCALE-002", "3", "BCG", "2018-2025", round(cagr(v("BCG", 2018, "headcount"), v("BCG", 2025, "headcount"), 7) * 100, 1), "% per year", "reported", "Compound annual growth of reported global headcount",
        "2025 headcount", "2018 headcount", "reported points only", "no interpolation", src)
    for f in ("BCG", "McKinsey"):
        add("SCALE-003", "3", f, "2018-2023", round(cagr(v(f, 2018, "headcount"), v(f, 2023, "headcount"), 5) * 100, 1), "% per year", "reported" if f == "BCG" else "estimated",
            "Compound annual growth of global headcount", "2023 headcount", "2018 headcount", "both endpoints required", "no interpolation", src)
    for f in FIRMS:
        rev, hc = v(f, 2023, "revenue"), v(f, 2023, "headcount")
        basis = "reported" if f == "BCG" else "estimated"
        add("SCALE-004", "3", f, "2023", round(rev * 1e9 / hc / 1e3), "USD thousand per employee", basis, "Revenue per employee", "2023 revenue", "2023 headcount",
            "both values required", "no interpolation", src)
        add("SCALE-005", "3", f, "2023", float(rev), "USD billion", basis, "Global revenue", "n/a", "n/a", "2023", "none", src)
        add("SCALE-006", "3", f, "2023", float(hc), "employees", basis, "Global headcount", "n/a", "n/a", "2023", "none", src)
    cnt = s.groupby(["firm", "type"]).size().unstack(fill_value=0).reindex(FIRMS).fillna(0)
    save(cnt, "scale_points_by_type")
    save(s, "scale_points_all", index=False)
    ver = s.groupby(["firm", "verified"]).size().unstack(fill_value=0).reindex(FIRMS).fillna(0)
    save(ver, "scale_points_verified")
    for f in FIRMS:
        n_rep = int(((s.firm == f) & (s.type == "reported")).sum())
        n_ver = int(((s.firm == f) & (s.verified == "yes")).sum())
        add("SCALE-007", "3", f, "2017-2025", n_rep, "data points", "n/a", "Number of reported (firm- or regulator-published) scale data points collected", "count of rows with type=reported", "n/a", "firm_scale_points.csv", "n/a", src)
        add("SCALE-008", "3", f, "2017-2025", n_ver, "data points", "n/a", "Number of scale data points verified by opening the source page", "count of rows with verified=yes", "n/a", "firm_scale_points.csv", "n/a", src)
    o = pd.read_csv(CLEAN / "office_pages.csv")
    core = o[o.brand == "core"]
    per_firm("OFFICE-001", "3", core.groupby("firm").size().reindex(FIRMS).dropna(), "snapshot Oct 2026", "city office pages", "proxy",
             "Core city office pages listed in the firm's public sitemap (excludes sub-brand offices; not audited)", "count of core office city pages", "n/a",
             "BCG and Bain only; McKinsey site unreachable", "McKinsey not covered", "S4")
    reg = core.pivot_table(index="region", columns="firm", values="city_slug", aggfunc="count").reindex(columns=["BCG", "Bain"]).fillna(0).astype(int)
    save(reg, "office_pages_by_region")
    for f in ["BCG", "Bain"]:
        for region, n in reg[f].items():
            add("OFFICE-002", "3", f, "snapshot Oct 2026", int(n), "city office pages", "proxy", f"Core office city pages in region: {region}", "count", "n/a", "mapped via taxonomy.REGION", "unmapped pages ignored", "S4")


# --------------------------------------------------------------------------------------------- Set 5: industry visibility
def industry():
    d = pd.read_csv(CLEAN / "sec_mentions.csv", dtype={"sic": str})
    o = d[d.is_operating]
    src = "S5"
    per_firm("IND-001", "5", d.groupby("firm").size(), "2015-2025", "filings", "proxy", "SEC filings (all forms) whose text names the firm", "count of distinct filings", "n/a", "2015-2025", "none", src)
    per_firm("IND-002", "5", o.groupby("firm").size(), "2015-2025", "filings", "proxy",
             "Operating-company SEC filings naming the firm (10-K, 8-K, S-1, 20-F, S-4, DRS, 10-Q; excl. funds, blank checks, investment vehicles)",
             "count of distinct filings", "n/a", "operating forms, mapped industry", "filings with no SIC excluded", src)
    per_firm("IND-003", "5", o.groupby("firm")["cik"].nunique(), "2015-2025", "filers", "proxy", "Distinct operating-company filers naming the firm", "distinct cik", "n/a", "as IND-002", "none", src)
    mix = pd.crosstab(o["industry"], o["firm"], normalize="columns").reindex(columns=FIRMS) * 100
    save(mix.round(1).sort_values("McKinsey", ascending=False), "sec_industry_mix_pct")
    save(pd.crosstab(o["industry"], o["firm"]).reindex(columns=FIRMS), "sec_industry_counts")
    per_firm("IND-004", "5", (mix / 100 / 1).pow(2).sum(), "2015-2025", "index 0-1", "proxy", "HHI of industry mix of operating-company filings naming the firm", "sum of squared industry shares", "total filings", "as IND-002", "none", src, 3)
    yr = o.pivot_table(index="year", columns="firm", values="adsh", aggfunc="count").reindex(columns=FIRMS)
    save(yr, "sec_filings_by_year")
    for f in FIRMS:
        for ind, pct in mix[f].items():
            add("IND-005", "5", f, "2015-2025", round(float(pct), 1), "%", "proxy", f"Share of operating filings naming the firm that are by filers in: {ind}", "filings in industry", "all operating filings naming the firm", "as IND-002", "none", src)
    t = pd.read_csv(CLEAN / "industry_taxonomy.csv")
    pg = t.pivot_table(index="common_group", columns="firm", values="page_count", aggfunc="sum").reindex(columns=["BCG", "Bain"]).fillna(0).astype(int)
    save(pg, "industry_practice_pages")
    c = pd.read_csv(CLEAN / "capability_taxonomy.csv")
    pc = c.pivot_table(index="common_group", columns="firm", values="page_count", aggfunc="sum").reindex(columns=["BCG", "Bain"]).fillna(0).astype(int)
    save(pc, "capability_practice_pages")
    for f in ["BCG", "Bain"]:
        add("IND-006", "5", f, "snapshot Oct 2026", int(pg[f].sum()), "pages", "proxy", "Pages under the firm's industry section (publication emphasis, not revenue)", "count", "n/a", "BCG /industries, Bain /industry-expertise", "McKinsey not covered", "S4")
        add("IND-007", "5", f, "snapshot Oct 2026", int(pc[f].sum()), "pages", "proxy", "Pages under the firm's capability/services section (publication emphasis, not revenue)", "count", "n/a", "BCG /capabilities, Bain /consulting-services", "McKinsey not covered", "S4")


# --------------------------------------------------------------------------------------------- Set 7: international public sector
def international():
    src = "S6"
    u = pd.read_csv(CLEAN / "uk_contracts.csv")
    uk = u[u.year.between(2015, 2025) & ~u.is_framework_ceiling]
    per_firm("INTL-001", "7", uk.groupby("firm").size().reindex(FIRMS).fillna(0), "2015-2025", "awards", "reported", "UK public-sector contract awards to the firm (Contracts Finder), excluding framework ceilings",
             "count of awarded notices", "n/a", "award year 2015-2025; value < GBP 50M", "frameworks excluded", src)
    per_firm("INTL-002", "7", uk.groupby("firm")["value_gbp"].sum().reindex(FIRMS).fillna(0) / 1e6, "2015-2025", "GBP millions", "reported", "Total awarded value, excluding framework ceilings", "sum of value_gbp", "n/a", "as INTL-001", "missing values ignored", src, 1)
    per_firm("INTL-003", "7", u[u.year.between(2015, 2025) & u.is_framework_ceiling].groupby("firm").size().reindex(FIRMS).fillna(0), "2015-2025", "awards", "reported",
             "Framework-agreement notices at or above GBP 50M (ceiling values, not spend)", "count", "n/a", "value >= GBP 50M", "n/a", src)
    uy = uk.pivot_table(index="year", columns="firm", values="notice_id", aggfunc="count").reindex(index=range(2015, 2026), columns=FIRMS).fillna(0).astype(int)
    uv = (uk.pivot_table(index="year", columns="firm", values="value_gbp", aggfunc="sum").reindex(index=range(2015, 2026), columns=FIRMS).fillna(0) / 1e6).round(1)
    save(uy, "uk_awards_by_year"); save(uv, "uk_value_gbp_m_by_year")
    top = uk.groupby(["firm", "buyer"])["value_gbp"].sum().div(1e6).round(1).rename("value_gbp_m").reset_index().sort_values(["firm", "value_gbp_m"], ascending=[True, False]).groupby("firm").head(5)
    save(top, "uk_top_buyers", index=False)
    try:
        ca = pd.read_csv(CLEAN / "canada_contracts.csv")
        ca = ca[ca.year.between(2015, 2025)]
        per_firm("INTL-004", "7", ca.groupby("firm").size().reindex(FIRMS).fillna(0), "2015-2025", "contracts", "reported", "Canadian federal contracts over CAD 10K to the firm", "count of contract records", "n/a", "contract year 2015-2025", "none", "S7")
        per_firm("INTL-005", "7", ca.groupby("firm")["value_cad"].sum().reindex(FIRMS).fillna(0) / 1e6, "2015-2025", "CAD millions", "reported", "Total contract value (including amendments as reported)", "sum of value_cad", "n/a", "contract year 2015-2025", "missing ignored", "S7", 1)
        save(ca.pivot_table(index="year", columns="firm", values="reference_number", aggfunc="count").reindex(columns=FIRMS).fillna(0).astype(int), "canada_contracts_by_year")
        save(ca.pivot_table(index="year", columns="firm", values="value_cad", aggfunc="sum").reindex(columns=FIRMS).fillna(0).div(1e6).round(2), "canada_value_cad_m_by_year")
        top = ca.groupby(["firm", "department"])["value_cad"].sum().div(1e6).round(1).rename("value_cad_m").reset_index().sort_values(["firm", "value_cad_m"], ascending=[True, False]).groupby("firm").head(5)
        save(top, "canada_top_departments", index=False)
    except FileNotFoundError:
        print("  Canada not yet available: INTL-004/005 skipped")
    try:
        au = pd.read_csv(CLEAN / "austender_contracts.csv")
        au = au[au.year.between(2015, 2025)]
        per_firm("INTL-006", "7", au.groupby("firm").size().reindex(FIRMS).fillna(0), "2015-2025", "contracts", "reported", "Australian federal contract notices to the firm (AusTender)", "count of contract notices", "n/a", "signed 2015-2025", "none", "S8")
        per_firm("INTL-007", "7", au.groupby("firm")["value_aud"].sum().reindex(FIRMS).fillna(0) / 1e6, "2015-2025", "AUD millions", "reported", "Total notified contract value", "sum of value_aud", "n/a", "signed 2015-2025", "missing ignored", "S8", 1)
        save(au.pivot_table(index="year", columns="firm", values="contract_id", aggfunc="count").reindex(columns=FIRMS).fillna(0).astype(int), "austender_contracts_by_year")
        save(au.pivot_table(index="year", columns="firm", values="value_aud", aggfunc="sum").reindex(columns=FIRMS).fillna(0).div(1e6).round(2), "austender_value_aud_m_by_year")
        top = au.groupby(["firm", "buyer"])["value_aud"].sum().div(1e6).round(1).rename("value_aud_m").reset_index().sort_values(["firm", "value_aud_m"], ascending=[True, False]).groupby("firm").head(5)
        save(top, "austender_top_buyers", index=False)
    except FileNotFoundError:
        print("  AusTender not yet available: INTL-006/007 skipped")


# --------------------------------------------------------------------------------------------- Set 8: publications and attention
def publications():
    b = pd.read_csv(CLEAN / "bcg_publications.csv")
    src = "S4"
    by = b.groupby("year").size()
    save(by.rename("publications").to_frame(), "bcg_publications_by_year")
    add("PUB-001", "8", "BCG", "2013", int(by.loc[2013]), "publication pages", "proxy", "BCG publication pages dated 2013 in the URL", "count of /publications/2013/ URLs", "n/a", "sitemap snapshot Oct 2026", "undated pages not counted", src)
    add("PUB-002", "8", "BCG", "2025", int(by.loc[2025]), "publication pages", "proxy", "BCG publication pages dated 2025 in the URL", "count of /publications/2025/ URLs", "n/a", "sitemap snapshot Oct 2026", "undated pages not counted", src)
    ai = b.groupby("year")["ai_in_slug"].agg(["sum", "size"])
    ai["share_pct"] = (ai["sum"] / ai["size"] * 100).round(1)
    save(ai.rename(columns={"sum": "ai_pages", "size": "all_pages"}), "bcg_ai_publications_by_year")
    add("PUB-003", "8", "BCG", "2019", float(ai.loc[2019, "share_pct"]), "%", "proxy", "Share of BCG publication pages whose URL slug names AI/GenAI", "pages with an AI term in the slug", "all dated pages that year", "slug keyword match", "pages without AI in slug count as non-AI", src)
    add("PUB-004", "8", "BCG", "2025", float(ai.loc[2025, "share_pct"]), "%", "proxy", "Share of BCG publication pages whose URL slug names AI/GenAI", "pages with an AI term in the slug", "all dated pages that year", "slug keyword match", "pages without AI in slug count as non-AI", src)
    add("PUB-005", "8", "BCG", "2025", int(ai.loc[2025, "sum"]), "pages", "proxy", "BCG publication pages with an AI term in the slug", "count", "n/a", "2025", "none", src)
    w = pd.read_csv(CLEAN / "openalex_works.csv")
    per_firm("PUB-006", "8", w[w.year.between(2010, 2025)].groupby("firm").size().reindex(FIRMS).dropna(), "2010-2025", "works", "reported", "Scholarly works with a firm affiliation recorded in OpenAlex", "count", "n/a", "2010-2025", "Bain has no OpenAlex institution record", "S9")
    save(w.pivot_table(index="year", columns="firm", values="work_id", aggfunc="count").fillna(0).astype(int), "openalex_works_by_year")
    a = pd.read_csv(CLEAN / "attention_monthly.csv")
    a["year"] = a["month"].str[:4].astype(int)
    wp = a[(a.source == "wikipedia_pageviews") & a.year.between(2016, 2025)].pivot_table(index="year", columns="firm", values="value", aggfunc="sum").reindex(columns=FIRMS)
    save(wp, "wikipedia_pageviews_by_year")
    per_firm("ATT-001", "8", wp.loc[2016:2025].mean(), "2016-2025", "views per year", "attention", "Average annual English-Wikipedia pageviews of the firm's article", "sum of monthly user pageviews", "10 years", "user agents, all access", "none", "S10")


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    d = hiring()
    capability(d)
    workforce()
    federal()
    scale()
    industry()
    international()
    publications()
    m = pd.DataFrame(ROWS)
    m.to_csv(TABLES / "metrics.csv", index=False)
    print(f"{len(m)} metric values across {m.metric_id.nunique()} metrics; {len(TABLE_NAMES)} series tables -> {TABLES}")
    print(m.groupby("set").metric_id.nunique().to_string())


if __name__ == "__main__":
    main()
