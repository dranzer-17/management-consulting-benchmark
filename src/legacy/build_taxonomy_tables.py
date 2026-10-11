"""Build industry, capability and office tables from the firms' own site structure, mapped to a shared taxonomy.

Original labels are preserved. Page counts measure published-content emphasis, NOT revenue.
Outputs: data/clean/industry_taxonomy.csv, capability_taxonomy.csv, office_locations.csv
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
s = pd.read_csv(ROOT / "data" / "clean" / "site_content_firms.csv")
slug = lambda df, top, i=1: df[(df.top == top)].path.str.split("/").str[i].str.lower()

INDUSTRY_MAP = {  # firm label (url slug) -> common industry group
    "health-care": "Healthcare and pharma", "healthcare": "Healthcare and pharma",
    "insurance": "Financial services", "financial-institutions": "Financial services", "financial-services": "Financial services",
    "energy": "Energy and resources", "energy-and-natural-resources": "Energy and resources", "oil-gas": "Energy and resources",
    "mining": "Energy and resources", "metals": "Energy and resources", "utilities-renewables": "Energy and resources", "chemicals": "Energy and resources",
    "principal-investors-private-equity": "Private equity and capital", "private-equity": "Private equity and capital",
    "public-sector": "Public sector", "education": "Public sector", "urban-planning": "Public sector", "social-impact-consulting": "Public sector",
    "aerospace-and-defense-industry": "Public sector", "aerospace-defense-government-services": "Public sector",
    "technology-media-telecommunications": "Technology, media and telecom", "technology": "Technology, media and telecom",
    "telecommunications": "Technology, media and telecom", "media-and-entertainment": "Technology, media and telecom",
    "transportation-logistics": "Industrials and transport", "transportation": "Industrials and transport", "aviation": "Industrials and transport",
    "industrial-goods": "Industrials and transport", "automotive": "Industrials and transport", "advanced-manufacturing-services": "Industrials and transport",
    "industrial-machinery-equipment": "Industrials and transport", "construction-infrastructure": "Industrials and transport",
    "building-products-technologies": "Industrials and transport", "paper-packaging": "Industrials and transport", "real-estate": "Industrials and transport",
    "retail": "Consumer and retail", "consumer-products-industry": "Consumer and retail", "consumer-products": "Consumer and retail",
    "travel-tourism": "Consumer and retail", "travel-leisure": "Consumer and retail", "agribusiness": "Consumer and retail",
}
CAPABILITY_MAP = {
    "digital-technology-data": "Technology, data and AI", "artificial-intelligence": "Technology, data and AI", "data-and-software-solutions": "Technology, data and AI",
    "digital-transformation": "Technology, data and AI",
    "climate-change-sustainability": "Sustainability", "sustainability-corporate-responsibility": "Sustainability", "social-impact": "Sustainability",
    "marketing-sales": "Marketing, sales and customer", "customer-insights": "Marketing, sales and customer", "pricing-revenue-management": "Marketing, sales and customer",
    "customer-strategy-and-marketing": "Marketing, sales and customer",
    "corporate-finance-strategy": "Strategy and corporate finance", "strategy": "Strategy and corporate finance", "international-business": "Strategy and corporate finance",
    "innovation-strategy-delivery": "Strategy and corporate finance",
    "operations": "Operations and performance", "cost-management": "Operations and performance", "manufacturing": "Operations and performance",
    "performance-improvement": "Operations and performance", "zero-based-budgeting": "Operations and performance", "business-resilience": "Operations and performance",
    "people-strategy": "Organization and people", "organization": "Organization and people", "organization-strategy": "Organization and people",
    "people-organization": "Organization and people", "inclusive-advantage": "Organization and people", "diversity-inclusion": "Organization and people",
    "diversity-consulting-equity-inclusion": "Organization and people", "change-management-results-delivery": "Organization and people", "agile": "Organization and people",
    "mergers-acquisitions-transactions-pmi": "M&A and transformation", "mergers-acquisitions": "M&A and transformation", "postmerger-integration": "M&A and transformation",
    "business-transformation": "M&A and transformation", "transformation": "M&A and transformation",
    "risk-management-and-compliance": "Risk and compliance", "collections": "Risk and compliance", "business-organizational-purpose": "Organization and people",
}

def table(rows, mapping, kind):
    df = pd.DataFrame(rows, columns=["firm", "original_label"])
    out = df.groupby(["firm", "original_label"]).size().reset_index(name="page_count")
    out["common_group"] = out["original_label"].map(mapping).fillna("Unmapped")
    out["kind"] = kind
    return out

ind = pd.concat([
    table([("BCG", x) for x in slug(s[s.firm == "BCG"], "industries")], INDUSTRY_MAP, "industry"),
    table([("Bain", x) for x in slug(s[s.firm == "Bain"], "industry-expertise")], INDUSTRY_MAP, "industry")])
ind = ind[ind.original_label.notna() & (ind.original_label != "industries")]
cap = pd.concat([
    table([("BCG", x) for x in slug(s[s.firm == "BCG"], "capabilities")], CAPABILITY_MAP, "capability"),
    table([("Bain", x) for x in slug(s[s.firm == "Bain"], "consulting-services")], CAPABILITY_MAP, "capability")])
cap = cap[cap.original_label.notna()]
ind.to_csv(ROOT / "data" / "clean" / "industry_taxonomy.csv", index=False)
cap.to_csv(ROOT / "data" / "clean" / "capability_taxonomy.csv", index=False)

# offices: separate BCG sub-brand offices from the main consulting offices
NON_CITY = {"global-services", "india", "middle-east", "latin-america", "africa", "asia", "europe", "north-america", "middle-east-africa"}


def office_rows():
    for firm in ("BCG", "Bain"):
        for path in s[(s.firm == firm) & (s.top == "offices")].path:
            parts = path.split("/")
            if len(parts) < 2:
                continue
            label = parts[1].lower()
            label = re.sub(r"\.aspx$", "", label)
            brand = next((b for b in ("platinion", "expand-research", "x", "acc", "brighthouse", "inverto", "bcg") if label.startswith(b + "-")), "core")
            if label in NON_CITY:
                brand = "region-or-global"
            city = label[len(brand) + 1:] if brand != "core" else label
            yield {"firm": firm, "url_path": path, "brand": brand, "city_slug": city, "depth": len(parts)}
off = pd.DataFrame(office_rows())
off = off[off.depth == 2].drop_duplicates(["firm", "brand", "city_slug"]).drop(columns="depth")
off.to_csv(ROOT / "data" / "clean" / "office_locations.csv", index=False)

print("INDUSTRY pages by common group:\n", ind.pivot_table(index="common_group", columns="firm", values="page_count", aggfunc="sum").fillna(0).astype(int))
print("\nCAPABILITY pages by common group:\n", cap.pivot_table(index="common_group", columns="firm", values="page_count", aggfunc="sum").fillna(0).astype(int))
print("\nUnmapped:", ind[ind.common_group == "Unmapped"].original_label.tolist(), cap[cap.common_group == "Unmapped"].original_label.tolist())
print("\nOffice directory entries:\n", off.groupby(["firm", "brand"]).size())
print("Core office city pages:", off[off.brand == "core"].groupby("firm").size().to_dict())
print("BCG core:", sorted(off[(off.firm == "BCG") & (off.brand == "core")].city_slug)[:60])

# ---- region mapping for core office city pages (explicit, auditable)
REGION = {}
for r, cities in {
    "North America": "atlanta austin boston brooklyn calgary dallas denver detroit houston los-angeles miami minneapolis minneapolis-frwd montreal nashville new-jersey new-york philadelphia pittsburgh raleigh-durham san-diego san-francisco seattle silicon-valley toronto washington-dc chicago",
    "Latin America": "bogota buenos-aires lima mexico-city monterrey rio-de-janeiro santiago sao-paulo",
    "Europe": "amsterdam athens barcelona berlin brussels budapest budapest-integrom cologne copenhagen dusseldorf frankfurt geneva hamburg helsinki istanbul kyiv lisbon london london-canary-wharf madrid milan munich nordic oslo paris prague rome stockholm stuttgart vienna warsaw zurich",
    "Middle East and Africa": "abu-dhabi baku cairo casablanca doha dubai johannesburg kuwait-city lagos nairobi riyadh tel-aviv",
    "Asia-Pacific": "almaty auckland bangkok beijing bengaluru brisbane canberra chennai fukuoka hanoi-city ho-chi-minh-city hong-kong hyderabad jakarta kuala-lumpur kyoto manila melbourne mumbai mumbai-bkc nagoya new-delhi osaka perth seoul shanghai shenzhen singapore sydney taipei tashkent tokyo",
}.items():
    REGION.update({c: r for c in cities.split()})
core = off[off.brand == "core"].copy()
core["region"] = core["city_slug"].map(REGION)
core.to_csv(ROOT / "data" / "clean" / "office_locations_core.csv", index=False)
print("\nCore offices by region:\n", core.pivot_table(index="region", columns="firm", values="city_slug", aggfunc="count", dropna=False).fillna(0).astype(int))
print("Unmapped city slugs:", core[core.region.isna()].city_slug.tolist())
