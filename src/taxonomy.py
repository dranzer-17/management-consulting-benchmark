"""Shared taxonomy: maps SIC codes to industry groups and URL/title keywords to topic groups.

Industry groups mirror the study brief: financial services, technology and telecom, healthcare and pharma,
energy, consumer goods and retail, industrials, public sector, private equity / investment vehicles.
Every mapping rule is explicit so it can be audited and changed.
"""
import re


def sic_to_industry(sic):
    """Map a 4-digit SIC code to an industry group. Returns None for unmapped or missing codes."""
    try:
        s = int(sic)
    except (TypeError, ValueError):
        return None
    if s == 6770:
        return "Blank-check / SPAC"
    if 6200 <= s <= 6299 or s in (6726, 6799, 6211):
        return "Investment vehicles and PE"
    if 8700 <= s <= 8749 and s != 8731:
        return "Professional services"
    if 6000 <= s <= 6499 or 6700 <= s <= 6799:
        return "Financial services and real estate"
    if s in (2833, 2834, 2835, 2836, 3841, 3842, 3843, 3844, 3845, 3851, 8000, 8011, 8050, 8051, 8060, 8062, 8071, 8082, 8090, 8093, 8731, 5122, 5047, 3826) or 8000 <= s <= 8099:
        return "Healthcare and pharma"
    if 3570 <= s <= 3579 or 3660 <= s <= 3679 or s in (3674, 3690, 3812) or 7370 <= s <= 7379 or s in (4812, 4813, 4822, 4899, 4841, 4832, 4833, 7373):
        return "Technology and telecom"
    if 1300 <= s <= 1399 or 2900 <= s <= 2999 or 4900 <= s <= 4991 or 1200 <= s <= 1299 or s in (1000, 1040, 1090):
        return "Energy, utilities and resources"
    if 5200 <= s <= 5999 or 2000 <= s <= 2199 or s in (2300, 2320, 2330, 2340, 2390, 3140, 3021, 2844, 2840, 2860, 7000, 7011, 5812, 5810, 7990, 7200, 7500):
        return "Consumer, retail and leisure"
    if 1500 <= s <= 1799 or 2200 <= s <= 2899 or 3000 <= s <= 3569 or 3580 <= s <= 3659 or 3680 <= s <= 3999 or 4000 <= s <= 4799 or 5000 <= s <= 5199 or 7300 <= s <= 7369 or 8700 <= s <= 8799:
        return "Industrials and transport"
    if 9100 <= s <= 9999:
        return "Public sector"
    return "Other"


# topic taxonomy: keyword rules applied to URL slugs and titles (lowercase, hyphen or space separated)
TOPIC_RULES = [
    ("Technology and AI", r"\b(ai|artificial-intelligence|generative|genai|gen-ai|digital|data|analytics|technology|tech|cyber|software|cloud|automation|machine-learning|llm|agentic)\b"),
    ("Sustainability and energy", r"\b(climate|sustainab\w*|net-zero|esg|energy|renewable|carbon|decarboni\w*|green|hydrogen|electric|ev)\b"),
    ("Private capital", r"\b(private-equity|private-capital|private-markets|venture|buyout|m-and-a|mergers|deals?|due-diligence|investor|lbo)\b"),
    ("Healthcare and life sciences", r"\b(health\w*|pharma\w*|life-sciences|medtech|biotech|medical|patient|clinical)\b"),
    ("Financial services", r"\b(bank\w*|insurance|financial|fintech|payments|wealth|asset-management)\b"),
    ("Consumer and retail", r"\b(consumer|retail|e-commerce|ecommerce|brand|shopper|cpg|fashion|food|grocery)\b"),
    ("Operations and supply chain", r"\b(operations|supply-chain|manufactur\w*|procurement|logistics|industrial|cost|lean|productivity)\b"),
    ("Organization and people", r"\b(organi[sz]ation\w*|talent|leadership|culture|workforce|people|hr|change|agile|ceo)\b"),
    ("Strategy and growth", r"\b(strategy|strategic|growth|innovation|transformation|competitive|market)\b"),
    ("Public sector", r"\b(government|public-sector|public|state|policy|defen[cs]e|military|city|cities)\b"),
]


def topic_of(text):
    t = re.sub(r"[_/]+", "-", str(text).lower())
    for name, pat in TOPIC_RULES:
        if re.search(pat, t):
            return name
    return "Other / unclassified"


# ---- site-structure taxonomies: each firm's own page-section label mapped to a common group
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

# ---- office city slug -> region (explicit, auditable)
_REGION_SRC = {
    "North America": "atlanta austin boston brooklyn calgary dallas denver detroit houston los-angeles miami minneapolis minneapolis-frwd montreal nashville new-jersey new-york philadelphia pittsburgh raleigh-durham san-diego san-francisco seattle silicon-valley toronto washington-dc chicago",
    "Latin America": "bogota buenos-aires lima mexico-city monterrey rio-de-janeiro santiago sao-paulo",
    "Europe": "amsterdam athens barcelona berlin brussels budapest budapest-integrom cologne copenhagen dusseldorf frankfurt geneva hamburg helsinki istanbul kyiv lisbon london london-canary-wharf madrid milan munich nordic oslo paris prague rome stockholm stuttgart vienna warsaw zurich",
    "Middle East and Africa": "abu-dhabi baku cairo casablanca doha dubai johannesburg kuwait-city lagos nairobi riyadh tel-aviv",
    "Asia-Pacific": "almaty auckland bangkok beijing bengaluru brisbane canberra chennai fukuoka hanoi-city ho-chi-minh-city hong-kong hyderabad jakarta kuala-lumpur kyoto manila melbourne mumbai mumbai-bkc nagoya new-delhi osaka perth seoul shanghai shenzhen singapore sydney taipei tashkent tokyo",
}
REGION = {c: r for r, cities in _REGION_SRC.items() for c in cities.split()}
