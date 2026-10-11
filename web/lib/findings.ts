// Report content. Prose here carries interpretation and limitations only; every number is pulled at build time from
// the generated data (claims.json statements are tested against metrics by tests/test_pipeline.py).
import type { ChartKind } from "@/components/chart"
import type { Firm } from "@/lib/data"

export type ChartSpec = {
  id: string; kind: ChartKind | "scale"; table?: string; xKey?: string; title: string; units: string; period: string
  caption: string; limitation?: string; sourceNote: string; metricIds: string[]; height?: number; firms?: Firm[]
  /** For single-series tables that store the value in one column (not one column per firm). */
  valueKey?: string; valueFirm?: Firm
}

export type Finding = {
  slug: string; num: number; title: string; short: string; question: string
  period: string; dataset: string; sourceIds: string[]; measures: string
  headline: { metric: string; label: string }[]
  metricIds: string[]; claimIds: string[]
  interpretation: string[]; limitations: string[]
  charts: ChartSpec[]; script: string; tables: string[]; core: boolean
}

const RAW: Finding[] = [
  {
    slug: "hiring-footprint", num: 1, core: true,
    title: "US hiring footprint and filing trends", short: "US hiring footprint",
    question: "Using one consistent public source, how do the three firms compare on US hiring activity, growth, geographic footprint and role mix?",
    period: "FY2015–FY2025 (certified filings; FY2026 is partial and excluded from growth)", dataset: "US Department of Labor H-1B Labor Condition Applications",
    sourceIds: ["S1"], measures: "Certified H-1B filings by the firm: a proxy for US hiring of foreign-national workers, not headcount.",
    headline: [{ metric: "HIRE-001", label: "Certified filings" }, { metric: "HIRE-002", label: "Filing growth, FY2016–24" }],
    metricIds: ["HIRE-001", "HIRE-002", "HIRE-003", "HIRE-004", "HIRE-005", "HIRE-006", "HIRE-007", "HIRE-008"],
    claimIds: ["HIRE-001", "HIRE-002", "HIRE-003", "HIRE-004", "HIRE-005", "HIRE-006"],
    interpretation: [
      "McKinsey and BCG file at broadly similar volumes, while Bain files far fewer. Filings grew at McKinsey and BCG over the period; Bain's grew slowly.",
      "McKinsey often puts many positions on one application, so position totals overstate its hiring relative to the other two. Trends within a firm are more reliable than level differences between firms.",
      "Offered wages for all three firms moved up over the period and came closer together.",
    ],
    limitations: [
      "H-1B filings measure US hiring activity for foreign-national workers. They are not headcount, revenue or global scale, and firms differ in how much they use H-1B.",
      "Growth rates use two endpoints (FY2016 and FY2024), so they are sensitive to those two years.",
      "The data comes from a public mirror of the Department of Labor files and has not been re-checked against the originals.",
    ],
    charts: [
      { id: "chart-filings", kind: "line", table: "lca_filings_by_year", xKey: "fiscal_year", title: "Certified H-1B filings by firm", units: "Filings per fiscal year", period: "FY2015–FY2025",
        caption: "McKinsey and BCG filings rise through the period, with a McKinsey jump around FY2021. Bain stays an order of magnitude smaller.", sourceNote: "US DOL OFLC LCA disclosure data (S1)", metricIds: ["HIRE-001", "HIRE-002"] },
      { id: "chart-wage", kind: "line", table: "lca_median_wage_by_year", xKey: "fiscal_year", title: "Median offered annual base wage", units: "USD per year", period: "FY2015–FY2025",
        caption: "Offered base wages in certified filings.", limitation: "Offered base wage only; excludes bonuses and benefits.", sourceNote: "US DOL OFLC LCA disclosure data (S1)", metricIds: ["HIRE-007"] },
    ],
    script: "src/ingest/h1b_lca.py", tables: ["lca_filings_by_year", "lca_median_wage_by_year", "lca_state_share_top10", "lca_top_occupations"],
  },
  {
    slug: "us-public-sector", num: 2, core: true,
    title: "US federal public-sector contract exposure", short: "US federal contracts",
    question: "How much direct US federal prime-contract work does each firm hold, who buys it, and how has it changed?",
    period: "FY2015–FY2024", dataset: "USAspending.gov prime awards and subawards",
    sourceIds: ["S2"], measures: "Prime contract awards to the firm's legal entity, attributed to the award start year, plus subawards where the firm is the subcontractor.",
    headline: [{ metric: "FED-002", label: "Prime contract value" }, { metric: "FED-005", label: "Share from Defense" }],
    metricIds: ["FED-001", "FED-002", "FED-003", "FED-004", "FED-005", "FED-006", "FED-007", "FED-008", "FED-009"],
    claimIds: ["FED-001", "FED-002", "FED-003"],
    interpretation: [
      "Where McKinsey and BCG hold direct federal contracts, the Department of Defense is the largest buyer for both, but BCG is more concentrated in it. McKinsey sells to a wider set of agencies.",
      "BCG's annual award value is lumpy and fell sharply in the latest years of the period. No prime award was found for Bain.",
      "McKinsey's subaward total is dominated by a single large award.",
    ],
    limitations: [
      "Prime awards are not total public-sector revenue. They exclude subcontract work, state and local government, and non-US governments (see the international finding).",
      "“None found” for Bain means no match in this registry under the matching rule, not that no federal work exists.",
      "Agencies amend awards over time, so totals can change slightly when the data is re-pulled.",
    ],
    charts: [
      { id: "chart-federal", kind: "bar", table: "federal_value_usd_m_by_year", xKey: "fiscal_year", title: "US federal prime contract value by fiscal year", units: "USD millions", period: "FY2015–FY2024",
        caption: "Annual value is uneven for both firms. Bain has no bars because no prime awards were found, which is different from a recorded zero.", sourceNote: "USAspending.gov (S2)", metricIds: ["FED-002"] },
    ],
    script: "src/ingest/usaspending_awards.py", tables: ["federal_awards_by_year", "federal_value_usd_m_by_year", "federal_agency_share_pct", "federal_value_by_agency"], 
  },
  {
    slug: "scale-and-reach", num: 3, core: true,
    title: "Firm scale and global reach", short: "Scale and global reach",
    question: "How do the firms compare on revenue, headcount and global reach, and how well can this be measured from public information?",
    period: "2017–2025 (varies by firm)", dataset: "Firm press releases, regulator filings and secondary sources; firm sitemaps for offices",
    sourceIds: ["S3", "S4"], measures: "Reported figures are published by the firm. Estimates come from secondary sources and are labelled as such.",
    headline: [{ metric: "SCALE-005", label: "Global revenue, 2023" }, { metric: "SCALE-007", label: "Reported data points" }],
    metricIds: ["SCALE-001", "SCALE-002", "SCALE-003", "SCALE-004", "SCALE-005", "SCALE-006", "SCALE-007", "SCALE-008", "OFFICE-001"],
    claimIds: ["SCALE-001", "SCALE-002", "SCALE-003", "SCALE-004", "OFFICE-001"],
    interpretation: [
      "Only BCG publishes a continuous series of revenue and headcount. McKinsey and Bain figures are estimates from secondary sources, so a decade-long revenue comparison across the three is not possible from public information.",
      "Every point is labelled reported or estimated and none are connected by lines, because interpolating across gaps would invent data. Treat the 2023 comparison as indicative.",
    ],
    limitations: [
      "Most McKinsey and Bain figures are unverified: the source page has not been opened and checked against the published number. The verification table on the Data & Sources page shows the count per firm.",
      "Revenue-per-employee figures that use an estimate inherit its uncertainty.",
      "Office-page counts come from public sitemaps and are not audited.",
    ],
    charts: [
      { id: "chart-revenue", kind: "scale", title: "Global revenue data points", units: "USD billion", period: "2017–2025",
        caption: "BCG's points are reported by the firm. McKinsey and Bain points are estimates and are shown hollow.", limitation: "Estimates are not as reliable as reported figures; most McKinsey and Bain points have not been verified against the original source.",
        sourceNote: "Firm releases and secondary sources (S3); see Data & Sources", metricIds: ["SCALE-005", "SCALE-007", "SCALE-008"] },
    ],
    script: "data/manual/firm_scale_points.csv (hand-compiled, source-linked)", tables: ["scale_points_all", "scale_points_by_type", "scale_points_verified", "office_pages_by_region"],
  },
  {
    slug: "capability-emphasis", num: 4, core: true,
    title: "Technical and analytical occupation mix", short: "Technical occupation mix",
    question: "How much do the firms' US hiring filings lean toward technical and analytical occupations, and is that changing?",
    period: "FY2015–FY2025", dataset: "US Department of Labor H-1B Labor Condition Applications",
    sourceIds: ["S1"], measures: "Share of certified filings in SOC major group 15 (Computer and Mathematical Occupations).",
    headline: [{ metric: "CAP-001", label: "Technical share of filings" }, { metric: "CAP-003", label: "Technical share, FY2021–25" }],
    metricIds: ["CAP-001", "CAP-002", "CAP-003", "CAP-004"], claimIds: ["CAP-001", "CAP-002"],
    interpretation: [
      "The technical share of filings rose at all three firms between the early and late parts of the period, at different speeds and from different starting points. This is the clearest common trend in the data.",
      "Management Analysts remain the largest occupation at every firm, and Bain's filings are the most concentrated in it.",
    ],
    limitations: [
      "The measure covers filings only, not the firms' whole workforce, and it uses the occupation code on the application as the classifier.",
      "A higher technical share is not evidence that a firm does more technical work for clients.",
    ],
    charts: [
      { id: "chart-technical", kind: "line", table: "technical_share_by_year", xKey: "fiscal_year", title: "Technical share of certified filings", units: "% of certified filings", period: "FY2015–FY2025",
        caption: "Share of each firm's certified filings in technical occupations.", sourceNote: "US DOL OFLC LCA disclosure data (S1)", metricIds: ["CAP-001", "CAP-002", "CAP-003"] },
    ],
    script: "src/clean.py, src/metrics.py", tables: ["technical_share_by_year", "technical_filings_by_year", "technical_top_occupations"],
  },
  {
    slug: "workforce-and-sponsorship", num: 6, core: true,
    title: "US workforce and permanent-residence sponsorship", short: "US workforce and sponsorship",
    question: "What do labor-certification filings reveal about each firm's US workforce size, the talent it sponsors for permanent residence, and how consistently it succeeds?",
    period: "FY2015–FY2024 (employee counts FY2016–FY2024)", dataset: "US Department of Labor PERM labor-certification disclosure data",
    sourceIds: ["S1"], measures: "The largest US employee count the firm stated on any PERM filing in a year, plus case outcomes and sponsored-worker characteristics.",
    headline: [{ metric: "WORK-002", label: "Max US employees stated, FY2024" }, { metric: "WORK-005", label: "Cases certified" }],
    metricIds: ["WORK-001", "WORK-002", "WORK-003", "WORK-004", "WORK-005", "WORK-006", "WORK-007", "WORK-008", "WORK-009", "WORK-010", "WORK-011"],
    claimIds: ["WORK-001", "WORK-002", "WORK-003"],
    interpretation: [
      "A self-reported US headcount series exists for all three firms. The yearly maximum is used as the firm-wide figure because individual filings sometimes report a smaller entity.",
      "Certification rates differ across the firms, and BCG has the highest share of withdrawn cases. India is the largest citizenship among sponsored workers at all three.",
    ],
    limitations: [
      "PERM covers only workers sponsored for permanent residence, so it describes a subset of the workforce.",
      "The employee-count field is filer-defined and unaudited, and McKinsey's values are rounded in steps.",
    ],
    charts: [
      { id: "chart-perm", kind: "line", table: "perm_us_employees_max_by_year", xKey: "fiscal_year", title: "Largest US employee count stated on PERM filings", units: "Employees", period: "FY2016–FY2024",
        caption: "A rough indicator of US size as stated by the firms themselves.", limitation: "Unaudited and filer-defined.", sourceNote: "US DOL OFLC PERM disclosure data (S1)", metricIds: ["WORK-002", "WORK-003", "WORK-004"] },
    ],
    script: "src/ingest/perm.py", tables: ["perm_us_employees_max_by_year", "perm_filings_by_year", "perm_citizenship_top"],
  },
  {
    slug: "industry-proxies", num: 5, core: false,
    title: "Industry exposure (proxies only)", short: "Industry exposure",
    question: "Can public data show which industries each firm serves?",
    period: "2015–2025", dataset: "SEC EDGAR full-text search; firm website sitemaps",
    sourceIds: ["S4", "S5"], measures: "The industries of operating companies whose SEC filings name the firm, and page counts in each firm's own industry and capability sections.",
    headline: [{ metric: "IND-001", label: "SEC filings naming the firm" }, { metric: "IND-003", label: "Distinct operating filers" }],
    metricIds: ["IND-001", "IND-002", "IND-003", "IND-004", "IND-005", "IND-006", "IND-007"], claimIds: ["IND-001", "IND-002"],
    interpretation: [
      "Industry exposure is not measured: no firm publishes revenue or clients by industry. The chart shows who writes about each firm in SEC filings, which looks similar across the three.",
      "Public-sector bodies do not file with the SEC, so that category is empty by construction.",
    ],
    limitations: [
      "A mention can be a client, an auditor's reference, a litigation party or a risk-factor aside. It shows who writes about the firm, not where the firm earns revenue.",
      "Page counts measure what a firm publishes, not what it earns. McKinsey's site could not be read by automated requests, so it is absent from page counts.",
    ],
    charts: [
      { id: "chart-industry", kind: "hbar", table: "sec_industry_mix_pct", xKey: "industry", title: "Industry mix of SEC filers that name the firm", units: "% of operating-company filings", period: "2015–2025",
        caption: "Healthcare, technology and industrials account for the largest shares at all three firms. This is a proxy for who mentions the firm, not for revenue mix.", limitation: "Mentions are not revenue.", sourceNote: "SEC EDGAR full-text search (S5)", metricIds: ["IND-004", "IND-005"], height: 380 },
    ],
    script: "src/ingest/sec_edgar.py, src/taxonomy.py", tables: ["sec_industry_mix_pct", "sec_industry_counts", "sec_filings_by_year", "industry_practice_pages"],
  },
  {
    slug: "international-public-sector", num: 7, core: false,
    title: "International public-sector contracts", short: "International contracts",
    question: "Outside the US, how much published public-sector contract work do the firms hold?",
    period: "2015–2025", dataset: "UK Contracts Finder, Canada proactive disclosure, Australia AusTender",
    sourceIds: ["S6", "S7", "S8"], measures: "Awards and notices in each country's public contract registry, matched by supplier name with one strict matcher. UK framework ceilings are excluded.",
    headline: [{ metric: "INTL-002", label: "UK award value" }, { metric: "INTL-007", label: "Australia notified value" }],
    metricIds: ["INTL-001", "INTL-002", "INTL-003", "INTL-004", "INTL-005", "INTL-006", "INTL-007"], claimIds: ["INTL-001", "INTL-002", "INTL-003"],
    interpretation: [
      "The leader differs by country: McKinsey holds more in the UK and Canada, while BCG holds far more notices in Australia. Buyers differ as well, and single large contracts dominate some years.",
      "No contract was found for Bain in any of the four public-sector registries used in this study.",
    ],
    limitations: [
      "Each registry publishes only contracts above its own threshold, and not every award is published. Values are not comparable across countries.",
      "“None found” for Bain is not proof of no public-sector work; it may sit under another entity, in subcontracts, or below thresholds.",
    ],
    charts: [
      { id: "chart-uk", kind: "bar", table: "uk_value_gbp_m_by_year", xKey: "year", title: "UK public-sector award value", units: "GBP millions", period: "2015–2025", caption: "Framework-agreement ceilings are excluded.", sourceNote: "UK Contracts Finder (S6)", metricIds: ["INTL-002"] },
      { id: "chart-canada", kind: "bar", table: "canada_value_cad_m_by_year", xKey: "year", title: "Canadian federal contract value", units: "CAD millions", period: "2016–2025", caption: "Contracts over CAD 10,000.", sourceNote: "Government of Canada proactive disclosure (S7)", metricIds: ["INTL-005"] },
      { id: "chart-australia", kind: "bar", table: "austender_value_aud_m_by_year", xKey: "year", title: "Australian federal contract value", units: "AUD millions", period: "2015–2025", caption: "One very large BCG notice dominates 2024.", sourceNote: "AusTender OCDS API (S8)", metricIds: ["INTL-007"] },
    ],
    script: "src/ingest/uk_contracts.py, canada_contracts.py, austender.py", tables: ["uk_value_gbp_m_by_year", "canada_value_cad_m_by_year", "austender_value_aud_m_by_year"],
  },
  {
    slug: "publications-and-attention", num: 8, core: false,
    title: "Publications and public attention", short: "Publications and attention",
    question: "What do the firms publish, and how much public attention do they attract, as a signal of emphasis?",
    period: "2013–2025", dataset: "BCG sitemap, OpenAlex, Wikipedia pageviews",
    sourceIds: ["S4", "S9", "S10"], measures: "BCG publication pages by URL year and AI terms in the URL slug; scholarly works with a firm affiliation; Wikipedia pageviews.",
    headline: [{ metric: "PUB-002", label: "BCG publication pages, 2025" }, { metric: "PUB-004", label: "BCG pages naming AI, 2025" }],
    metricIds: ["PUB-001", "PUB-002", "PUB-003", "PUB-004", "PUB-005", "PUB-006", "ATT-001"], claimIds: ["PUB-001", "PUB-002"],
    interpretation: [
      "BCG's dated publication output grew substantially, and AI-related titles became a much larger share of it.",
      "Scholarly output recorded in OpenAlex is similar for McKinsey and BCG; Bain has no institution record there.",
    ],
    limitations: [
      "Slug matching misses AI content whose URL does not name AI. McKinsey's publication series could not be built because its site is unreachable to automated requests.",
      "Pageviews measure public attention, not business performance, and OpenAlex affiliation strings are inconsistent.",
    ],
    charts: [
      { id: "chart-ai", kind: "line", table: "bcg_ai_publications_by_year", xKey: "year", firms: ["BCG"], valueKey: "share_pct", valueFirm: "BCG", title: "BCG publication pages naming AI in the URL", units: "% of dated publication pages", period: "2013–2025",
        caption: "BCG only: no comparable publication series could be built for the other two.", limitation: "Based on URL slugs only.", sourceNote: "BCG public sitemap (S4)", metricIds: ["PUB-003", "PUB-004", "PUB-005"] },
    ],
    script: "src/ingest/site_inventory.py, openalex.py, attention.py", tables: ["bcg_ai_publications_by_year", "openalex_works_by_year", "wikipedia_pageviews_by_year"],
  },
]

// Numbered in reading order on this site (the repository's finding-set numbers differ: docs/findings/0N_*.md).
export const FINDINGS: Finding[] = RAW.map((f, i) => ({ ...f, num: i + 1 }))
