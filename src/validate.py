"""Validation stage: checks that raw, clean and metric outputs are consistent. Fails loudly instead of silently changing results.

Checks: expected firm names, duplicates, missing values, date ranges, valid values, source/claim references, and
independent recomputation of headline metrics directly from the raw files (not via src/metrics.py).
Run: python -m src.validate        (exit code 1 if any check fails)
"""
import json
import re
import sys

import pandas as pd

from src.common import CLEAN, FIRMS, MANUAL, RAW, ROOT, TABLES

FAILURES, PASSED = [], []


def check(name, ok, detail=""):
    (PASSED if ok else FAILURES).append(f"{name}{(': ' + detail) if detail and not ok else ''}")


def read(path, **kw):
    return pd.read_csv(path, **kw)


def firm_names():
    for f in sorted(CLEAN.glob("*.csv")):
        d = read(f, nrows=None)
        if "firm" in d.columns:
            bad = set(d["firm"].dropna().unique()) - set(FIRMS)
            check(f"firm labels valid in {f.name}", not bad, f"unexpected firm labels {bad}")
            check(f"no missing firm in {f.name}", d["firm"].notna().all())


def employer_names():
    """Raw employer names must match the intended entity for each firm (guards against fuzzy-match contamination)."""
    pats = {"McKinsey": r"mckinsey", "BCG": r"boston consulting group", "Bain": r"^bain\s+(?:&(?:amp;)?\s*|and\s+)?(?:company|co\b)"}
    for fname, col in [("lca_firms.csv", "employer_name"), ("perm_firms.csv", "employer_name")]:
        d = read(RAW / fname)
        for f, pat in pats.items():
            names = d.loc[d.firm == f, col].dropna()
            check(f"{fname}: {f} names match expected entity", names.str.contains(pat, case=False, regex=True).all(),
                  str(names[~names.str.contains(pat, case=False, regex=True)].unique()[:5]))
    a = read(RAW / "awards_firms.csv")
    check("awards: recipient names match firm legal entities", a["Recipient Name"].str.contains("MCKINSEY|BOSTON CONSULTING|BAIN", case=False).all())
    check("awards: no unrelated 'McKinsey Fencing'-type recipients", not a["Recipient Name"].str.contains("FENCING|STEEL", case=False).any())


def duplicates():
    keys = {"lca.csv": ["case_number"], "perm.csv": ["case_number"], "awards.csv": ["firm", "award_id"], "uk_contracts.csv": ["firm", "notice_id"],
            "sec_mentions.csv": ["firm", "adsh"], "firm_scale_points.csv": ["firm", "year", "metric"]}
    for f, k in keys.items():
        d = read(CLEAN / f)
        check(f"no duplicate keys in {f}", not d.duplicated(k).any(), f"{int(d.duplicated(k).sum())} duplicates on {k}")


def ranges_and_values():
    l = read(CLEAN / "lca.csv")
    check("lca: fiscal years within 2015-2026", l.fiscal_year.between(2015, 2026).all())
    check("lca: wages in $30K-$1M when present", l.wage_annual.dropna().between(30_000, 1_000_000).all())
    check("lca: positions positive", (l.positions >= 1).all())
    check("lca: every firm has filings in every FY2016-2025", all(l[(l.firm == f) & l.certified].groupby("fiscal_year").size().reindex(range(2016, 2026)).notna().all() for f in FIRMS))
    p = read(CLEAN / "perm.csv")
    check("perm: fiscal years within 2015-2026", p.fiscal_year.between(2015, 2026).all())
    check("perm: outcome values valid", set(p.outcome.dropna().unique()) <= {"CERTIFIED", "DENIED", "WITHDRAWN"}, str(set(p.outcome.unique())))
    a = read(CLEAN / "awards.csv")
    check("awards: no negative values", (a.award_usd >= 0).all())
    s = read(CLEAN / "sec_mentions.csv", dtype={"sic": str})
    check("sec: filing years within 2015-2025", s.year.between(2015, 2025).all())
    check("sec: SIC missing share below 25%", s.sic.isna().mean() < 0.25, f"{s.sic.isna().mean():.1%}")
    u = read(CLEAN / "uk_contracts.csv")
    check("uk: values non-negative", (u.value_gbp.dropna() >= 0).all())
    sc = read(CLEAN / "firm_scale_points.csv")
    check("scale: type values valid", set(sc.type) <= {"reported", "estimated"})
    check("scale: confidence values valid", set(sc.confidence) <= {"high", "medium", "low"})
    check("scale: every point has a source URL", sc.source_url.notna().all() and sc.source_url.str.startswith("http").all())
    check("scale: verified flag valid", set(sc.verified) <= {"yes", "no"})
    check("scale: reported points all have confidence high or medium", sc[sc.type == "reported"].confidence.isin(["high", "medium"]).all())
    check("scale: McKinsey has no 'reported' points (it publishes no financials)", not ((sc.firm == "McKinsey") & (sc.type == "reported")).any())


def recompute_from_raw():
    """Independent re-derivation of headline numbers from the raw files, compared with outputs/tables/metrics.csv."""
    m = read(TABLES / "metrics.csv")
    val = lambda mid, f: float(m[(m.metric_id == mid) & (m.firm == f)].value.iloc[0])
    raw = read(RAW / "lca_firms.csv")
    cert = raw[raw.case_status.str.upper().str.startswith("CERTIFIED") & raw.fiscal_year.between(2015, 2025)]
    for f in FIRMS:
        check(f"HIRE-001 recomputed from raw ({f})", len(cert[cert.firm == f]) == val("HIRE-001", f), f"{len(cert[cert.firm == f])} vs {val('HIRE-001', f)}")
    aw = read(RAW / "awards_firms.csv")
    aw["fy"] = pd.to_datetime(aw["Start Date"]).dt.year + (pd.to_datetime(aw["Start Date"]).dt.month >= 10)
    aw = aw[aw.fy.between(2015, 2024) & (aw["Award Amount"] > 0)]
    for f in ("McKinsey", "BCG"):
        check(f"FED-001 recomputed from raw ({f})", len(aw[aw.firm == f]) == val("FED-001", f))
        check(f"FED-002 recomputed from raw ({f})", abs(aw[aw.firm == f]["Award Amount"].sum() / 1e6 - val("FED-002", f)) < 0.1)
    pr = read(RAW / "perm_firms.csv")
    for f in FIRMS:
        check(f"WORK-002 recomputed from raw ({f})", pr[(pr.firm == f) & (pr.fiscal_year == 2024)].employer_num_employees.max() == val("WORK-002", f))
    sec = read(RAW / "sec_mentions.csv")
    for f in FIRMS:
        check(f"IND-001 recomputed from raw ({f})", sec[sec.firm == f].adsh.nunique() == val("IND-001", f))
    uk = read(RAW / "uk_contracts_firms.csv")
    uk["y"] = pd.to_datetime(uk.awardedDate, errors="coerce", utc=True).dt.year
    uk = uk[uk.y.between(2015, 2025) & (uk.awardedValue < 50_000_000)]
    for f in ("McKinsey", "BCG"):
        check(f"INTL-001 recomputed from raw ({f})", uk[uk.firm == f].noticeIdentifier.nunique() == val("INTL-001", f))
    sc = read(MANUAL / "firm_scale_points.csv").pivot_table(index=["firm", "year"], columns="metric", values="value")
    check("BCG 2025 revenue matches the firm's release ($14.4B)", sc.loc[("BCG", 2025), "revenue"] == 14.4)
    check("BCG 2024 revenue matches the firm's release ($13.5B)", sc.loc[("BCG", 2024), "revenue"] == 13.5)
    check("BCG 2023 revenue matches the firm's release ($12.3B)", sc.loc[("BCG", 2023), "revenue"] == 12.3)


def references():
    src = read(ROOT / "sources.csv")
    check("source ids unique", src.source_id.is_unique)
    m = read(TABLES / "metrics.csv")
    unknown = {s.strip() for ids in m.source_ids.dropna() for s in str(ids).split(";")} - set(src.source_id)
    check("every metric cites a registered source", not unknown, str(unknown))
    check("metric values are finite", pd.to_numeric(m.value, errors="coerce").notna().all())
    cl = read(ROOT / "claims.csv")
    check("claim ids unique", cl.claim_id.is_unique)
    ids = set(m.metric_id)
    for _, r in cl.iterrows():
        for chk in json.loads(r.checks):
            check(f"claim {r.claim_id}: metric {chk['metric']} exists", chk["metric"] in ids)
        for s in str(r.source_ids).split(";"):
            check(f"claim {r.claim_id}: source {s.strip()} registered", s.strip() in set(src.source_id))
    check("no claim marked rejected is still shown", not (cl.status == "rejected").any() or cl[cl.status == "rejected"].output_locations.isna().all())
    # privacy: no personal email addresses anywhere in tracked text files
    for p in list(ROOT.glob("src/**/*.py")) + list(ROOT.glob("*.md")) + list(ROOT.glob("*.csv")) + list(ROOT.glob("docs/**/*.md")):
        check(f"no personal email in {p.relative_to(ROOT)}", not re.search(r"[\w.]+@(gmail|outlook|yahoo|hotmail)\.com", p.read_text(errors="ignore")))


def run():
    for fn in (firm_names, employer_names, duplicates, ranges_and_values, recompute_from_raw, references):
        try:
            fn()
        except Exception as e:  # a crashed check is a failure, not a pass
            FAILURES.append(f"{fn.__name__} raised {type(e).__name__}: {e}")
    return FAILURES


if __name__ == "__main__":
    fails = run()
    print(f"{len(PASSED)} checks passed, {len(fails)} failed")
    for f in fails:
        print("  FAIL:", f)
    sys.exit(1 if fails else 0)
