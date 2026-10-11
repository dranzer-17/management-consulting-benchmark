"""Clean stage: reads the as-received extracts in data/raw/ and data/manual/, writes standardized tables to data/clean/.

Raw files are never modified. Every transformation here is deterministic and documented in methodology.md.
Run: python -m src.clean
"""
import ast
import re

import pandas as pd

from src.common import CLEAN, MANUAL, RAW, firm_of
from src.taxonomy import (CAPABILITY_MAP, INDUSTRY_MAP, REGION, sic_to_industry, topic_of)

ANNUAL = {"Year": 1, "Hour": 2080, "Week": 52, "Month": 12, "Bi-Weekly": 26}  # pay unit -> periods per year
OPERATING_FORMS = {"10-K", "8-K", "S-1", "20-F", "S-4", "DRS", "10-Q", "S-1/A", "424B4", "424B1", "40-F"}
EXCLUDED_INDUSTRIES = {"Blank-check / SPAC", "Investment vehicles and PE"}
NON_CITY = {"global-services", "india", "middle-east", "latin-america", "africa", "asia", "europe", "north-america", "middle-east-africa"}
OFFICE_BRANDS = ("platinion", "expand-research", "x", "acc", "brighthouse", "inverto", "bcg")


def fiscal_year(dates):
    """US federal fiscal year: starts 1 October."""
    d = pd.to_datetime(dates, errors="coerce")
    return d.dt.year + (d.dt.month >= 10)


def write(df, name):
    CLEAN.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN / name, index=False)
    print(f"  {name}: {len(df):,} rows")


def parse_field(s, key):
    return ast.literal_eval(s).get(key) if isinstance(s, str) else None


def lca():
    d = pd.read_csv(RAW / "lca_firms.csv", dtype={"soc_code": str, "naics_code": str})
    wage = d["wage_rate_of_pay_from"] * d["wage_unit_of_pay"].map(ANNUAL)
    out = pd.DataFrame({
        "case_number": d["case_number"], "firm": d["firm"], "fiscal_year": d["fiscal_year"], "case_status": d["case_status"],
        "certified": d["case_status"].str.upper().str.startswith("CERTIFIED"),
        "job_title": d["job_title"].str.title(), "soc_code": d["soc_code"], "soc_title": d["soc_title"].str.title(),
        "is_technical": d["soc_code"].astype(str).str.startswith("15"),
        "worksite_state": d["worksite_state"], "worksite_city": d["worksite_city"],
        "positions": d["total_worker_positions"].fillna(1).astype(int),
        "wage_annual": wage.where(wage.between(30_000, 1_000_000)),     # outside $30K-$1M treated as entry errors
        "pw_wage_level": d["pw_wage_level"], "received_date": d["received_date"]})
    write(out.drop_duplicates("case_number"), "lca.csv")


def perm():
    d = pd.read_csv(RAW / "perm_firms.csv")
    out = pd.DataFrame({
        "case_number": d["case_number"], "firm": d["firm"], "fiscal_year": d["fiscal_year"],
        "outcome": d["case_status"].str.replace("-EXPIRED", "", regex=False),
        "employer_num_employees": d["employer_num_employees"], "job_title": d["job_title"].str.title(),
        "soc_code": d["soc_code"], "citizenship": d["country_of_citizenship"].str.title(),
        "minimum_education": d["minimum_education"], "major": d["major_field_of_study"].str.lower().fillna(""),
        "worksite_state": d["worksite_state"]})
    write(out.drop_duplicates("case_number"), "perm.csv")


def awards():
    d = pd.read_csv(RAW / "awards_firms.csv")
    out = pd.DataFrame({
        "award_id": d["Award ID"], "firm": d["firm"], "fiscal_year": d["fiscal_year"], "start_date": d["Start Date"],
        "agency": d["Awarding Agency"], "sub_agency": d["Awarding Sub Agency"], "award_usd": d["Award Amount"],
        "naics_desc": d["NAICS"].map(lambda s: parse_field(s, "description")), "psc_desc": d["PSC"].map(lambda s: parse_field(s, "description"))})
    write(out.drop_duplicates(["firm", "award_id"]), "awards.csv")


def subawards():
    d = pd.read_csv(RAW / "subawards_firms.csv")
    out = pd.DataFrame({
        "subaward_id": d["Sub-Award ID"], "firm": d["firm"], "fiscal_year": d["fiscal_year"], "amount_usd": d["Sub-Award Amount"],
        "prime_recipient": d["Prime Recipient Name"], "agency": d["Awarding Agency"], "description": d["Sub-Award Description"]})
    write(out, "subawards.csv")


def uk():
    d = pd.read_csv(RAW / "uk_contracts_firms.csv")
    date = pd.to_datetime(d["awardedDate"], errors="coerce", utc=True)
    out = pd.DataFrame({"notice_id": d["noticeIdentifier"], "firm": d["firm"], "year": date.dt.year, "buyer": d["organisationName"],
                        "title": d["title"], "value_gbp": d["awardedValue"], "cpv": d["cpvDescription"]})
    out["is_framework_ceiling"] = out["value_gbp"] >= 50_000_000   # config/firms.yml: framework_value_ceiling_gbp
    write(out.drop_duplicates(["firm", "notice_id"]), "uk_contracts.csv")


def canada():
    p = RAW / "canada_contracts_firms.csv"
    if not p.exists():
        print("  canada_contracts_firms.csv missing: skipped")
        return
    d = pd.read_csv(p, dtype=str)
    d["firm"] = d["vendor_name"].map(firm_of)           # re-match with the strict shared pattern
    d = d.dropna(subset=["firm"])
    date = pd.to_datetime(d["contract_date"], errors="coerce")
    out = pd.DataFrame({"reference_number": d["reference_number"], "firm": d["firm"], "year": date.dt.year,
                        "department": d["owner_org_title"], "value_cad": pd.to_numeric(d["contract_value"], errors="coerce"),
                        "original_value_cad": pd.to_numeric(d.get("original_value"), errors="coerce"),
                        "description": d.get("description_en"), "commodity_type": d.get("commodity_type")})
    write(out.drop_duplicates(["firm", "reference_number", "value_cad", "year"]), "canada_contracts.csv")


def austender():
    p = RAW / "austender_contracts_firms.csv"
    if not p.exists():
        print("  austender_contracts_firms.csv missing: skipped")
        return
    d = pd.read_csv(p)
    d["firm"] = d["supplier"].map(firm_of)               # re-match with the strict shared pattern
    d = d.dropna(subset=["firm"])
    date = pd.to_datetime(d["date_signed"], errors="coerce", utc=True)
    out = pd.DataFrame({"contract_id": d["contract_id"], "firm": d["firm"], "year": date.dt.year, "buyer": d["buyer"],
                        "value_aud": pd.to_numeric(d["value"], errors="coerce"), "title": d["title"], "description": d["description"]})
    write(out.drop_duplicates(["firm", "contract_id"]), "austender_contracts.csv")


def sec():
    d = pd.read_csv(RAW / "sec_mentions.csv", dtype={"sic": str})
    d["year"] = d["file_date"].str[:4].astype(int)
    d["industry"] = d["sic"].map(sic_to_industry)
    d["is_operating"] = d["form"].isin(OPERATING_FORMS) & d["industry"].notna() & ~d["industry"].isin(EXCLUDED_INDUSTRIES)
    d["company"] = d["company"].str.replace(r"\s+\(CIK.*", "", regex=True)
    write(d.drop_duplicates(["firm", "adsh"]), "sec_mentions.csv")


def site():
    s = pd.read_csv(RAW / "site_content_firms.csv")
    write(s, "site_inventory.csv")
    slug = lambda df, top, i=1: df[df.top == top].path.str.split("/").str[i].str.lower()

    b = s[(s.firm == "BCG") & (s.top == "publications") & s.year_in_path.between(2013, 2025)].copy()
    b["slug"] = b["path"].str.split("/").str[-1]
    b["topic"] = b["slug"].map(topic_of)
    b["ai_in_slug"] = b["slug"].str.contains(r"(?:^|-)(?:ai|genai|gen-ai|generative|artificial-intelligence|agentic)(?:-|$)")
    write(b[["firm", "url", "year_in_path", "slug", "topic", "ai_in_slug"]].rename(columns={"year_in_path": "year"}), "bcg_publications.csv")

    p = s[(s.firm == "Bain") & s.path.str.contains("press-releases")].copy()
    parts = p["path"].str.split("/")
    p["region"], p["year"] = parts.str[3], parts.str[4]
    p = p[p.year.str.fullmatch(r"20\d{2}", na=False)].assign(year=lambda x: x.year.astype(int))
    p["topic"] = p["path"].str.split("/").str[-1].map(topic_of)
    write(p[["firm", "url", "year", "region", "topic"]], "bain_press_releases.csv")

    def table(rows, mapping, kind):
        df = pd.DataFrame(rows, columns=["firm", "original_label"]).dropna()
        out = df.groupby(["firm", "original_label"]).size().reset_index(name="page_count")
        out["common_group"] = out["original_label"].map(mapping).fillna("Unmapped")
        out["kind"] = kind
        return out
    ind = pd.concat([table([("BCG", x) for x in slug(s[s.firm == "BCG"], "industries")], INDUSTRY_MAP, "industry"),
                     table([("Bain", x) for x in slug(s[s.firm == "Bain"], "industry-expertise")], INDUSTRY_MAP, "industry")])
    cap = pd.concat([table([("BCG", x) for x in slug(s[s.firm == "BCG"], "capabilities")], CAPABILITY_MAP, "capability"),
                     table([("Bain", x) for x in slug(s[s.firm == "Bain"], "consulting-services")], CAPABILITY_MAP, "capability")])
    write(ind[ind.original_label != "industries"], "industry_taxonomy.csv")
    write(cap, "capability_taxonomy.csv")

    rows = []
    for firm in ("BCG", "Bain"):
        for path in s[(s.firm == firm) & (s.top == "offices")].path:
            parts = path.split("/")
            if len(parts) != 2:
                continue
            label = re.sub(r"\.aspx$", "", parts[1].lower())
            brand = next((b_ for b_ in OFFICE_BRANDS if label.startswith(b_ + "-")), "core")
            if label in NON_CITY:
                brand = "region-or-global"
            rows.append({"firm": firm, "brand": brand, "city_slug": label[len(brand) + 1:] if brand not in ("core", "region-or-global") else label})
    off = pd.DataFrame(rows).drop_duplicates(["firm", "brand", "city_slug"])
    off["region"] = off["city_slug"].map(REGION).where(off["brand"] == "core")
    write(off, "office_pages.csv")


def passthrough():
    ow = pd.read_csv(RAW / "openalex_works_firms.csv")
    write(ow, "openalex_works.csv")
    write(pd.read_csv(RAW / "wikidata_facts.csv"), "wikidata_facts.csv")
    write(pd.read_csv(RAW / "attention_monthly.csv"), "attention_monthly.csv")
    write(pd.read_csv(MANUAL / "firm_scale_points.csv"), "firm_scale_points.csv")


def main():
    print("Cleaning raw extracts ->", CLEAN)
    for step in (lca, perm, awards, subawards, uk, canada, austender, sec, site, passthrough):
        step()


if __name__ == "__main__":
    main()
