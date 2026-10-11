# Sources

*Generated from [sources.csv](sources.csv). Do not edit by hand.*

Every chart and table in this study cites a source ID below. Retrieval date for all sources: 2026-10-11 unless noted.

## S1: H-1B LCA and PERM disclosure data

- **Publisher:** US Department of Labor (OFLC)
- **URL:** https://www.dol.gov/agencies/eta/foreign-labor/performance
- **Date range:** FY2015-FY2026 (partial)
- **Fields used:** employer name; job title; SOC code; offered wage; worksite; case status; PERM employee count, citizenship, education
- **License / usage:** US government public data. Accessed through the Hugging Face mirror Nason/dol-visas-database (mirror terms per its dataset card, not independently verified)
- **Access method:** remote DuckDB query of https://huggingface.co/datasets/Nason/dol-visas-database (src/ingest/h1b_lca.py, perm.py)
- **Raw file:** data/raw/lca_firms.csv; data/raw/perm_firms.csv
- **Limitations:** Filings are applications by US employers for foreign-national workers; a proxy for US hiring not headcount. Mirror not re-checked against the original DOL files. FY2026 partial

## S2: Federal prime contract awards and subawards

- **Publisher:** USAspending.gov (US Treasury)
- **URL:** https://api.usaspending.gov
- **Date range:** FY2015-FY2025
- **Fields used:** recipient; awarding agency; award value; start date; NAICS; PSC; subaward fields
- **License / usage:** US government public data
- **Access method:** public API, no key (src/ingest/usaspending_awards.py, usaspending_subawards.py)
- **Raw file:** data/raw/awards_firms.csv; data/raw/subawards_firms.csv
- **Limitations:** Prime and sub awards in the federal system only; recipient search is fuzzy and results are filtered to the firms' legal entity names. Awards are dated by start year

## S3: Revenue headcount offices and countries data points

- **Publisher:** BCG; Bain; secondary sources (Fortune; InfluenceWatch; Umbrex; Wikidata statements)
- **URL:** https://www.prnewswire.com/news/boston-consulting-group-(bcg)/
- **Date range:** 2017-2025 (sparse)
- **Fields used:** revenue; headcount; offices; countries
- **License / usage:** Facts quoted with attribution; each row carries its own URL
- **Access method:** hand-compiled (data/manual/firm_scale_points.csv)
- **Raw file:** data/manual/firm_scale_points.csv
- **Limitations:** Only BCG publishes revenue and headcount. McKinsey and Bain figures are third-party estimates. Rows are marked verified=yes only if the source page was opened and read

## S4: Public website sitemaps (URL paths and last-modified dates only)

- **Publisher:** BCG; Bain
- **URL:** https://www.bcg.com/google_sitemap-content.xml; https://www.bain.com/en/sitemap.xml
- **Date range:** snapshot Oct 2026
- **Fields used:** URL path; lastmod; section; year in path
- **License / usage:** Sitemap files named in each site's robots.txt; no page content crawled
- **Access method:** src/ingest/site_inventory.py
- **Raw file:** data/raw/site_content_firms.csv
- **Limitations:** Counts of published pages are a proxy for emphasis not revenue. McKinsey's site did not respond to automated requests and is not covered. Bain press-release pages are dominated by one region and affected by a site migration

## S5: EDGAR full-text search

- **Publisher:** US SEC
- **URL:** https://efts.sec.gov/LATEST/search-index
- **Date range:** 2015-2025
- **Fields used:** filing form; filer; SIC code; filing date
- **License / usage:** US government public data; SEC fair-access guidance followed (identified user agent; under 10 requests per second)
- **Access method:** src/ingest/sec_edgar.py
- **Raw file:** data/raw/sec_mentions.csv
- **Limitations:** A mention is not proof of a client relationship: names also appear in cited studies and director biographies. Industry mix mostly reflects the SEC filer universe

## S6: Contracts Finder awarded contract notices

- **Publisher:** UK Cabinet Office
- **URL:** https://www.contractsfinder.service.gov.uk
- **Date range:** 2015-2025
- **Fields used:** supplier; buyer; awarded value; date; CPV
- **License / usage:** Open Government Licence v3.0
- **Access method:** src/ingest/uk_contracts.py (quoted-phrase search windowed by publication year)
- **Raw file:** data/raw/uk_contracts_firms.csv
- **Limitations:** Search API has no pagination (windowed to stay under the result cap). Framework agreements list ceiling values (GBP 50M or more excluded from spend totals). Contracts under the notice threshold are absent

## S7: Proactive publication of contracts over CAD 10000

- **Publisher:** Government of Canada
- **URL:** https://open.canada.ca/data/en/dataset/d8f85d91-7dec-4fd1-8055-483b77225d8b
- **Date range:** 2015-2025
- **Fields used:** vendor; department; contract value; date; description
- **License / usage:** Open Government Licence - Canada
- **Access method:** streamed CSV filtered by vendor name (src/ingest/canada_contracts.py); raw file not stored
- **Raw file:** data/raw/canada_contracts_firms.csv
- **Limitations:** Contracts over CAD 10000 only; amendments are reported as listed

## S8: AusTender contract notices (OCDS API)

- **Publisher:** Australian Government (Department of Finance)
- **URL:** https://api.tenders.gov.au
- **Date range:** 2015-2025
- **Fields used:** supplier; procuring entity; contract value; date
- **License / usage:** Creative Commons Attribution (see the API's license field)
- **Access method:** weekly windows paged and filtered by supplier name (src/ingest/austender.py)
- **Raw file:** data/raw/austender_contracts_firms.csv
- **Limitations:** Contract notices only, above reporting thresholds; values are as notified

## S9: Scholarly works by institution

- **Publisher:** OpenAlex
- **URL:** https://openalex.org
- **Date range:** 2010-2025
- **Fields used:** work; year; type; citations; primary topic
- **License / usage:** CC0
- **Access method:** src/ingest/openalex.py
- **Raw file:** data/raw/openalex_works_firms.csv
- **Limitations:** Only McKinsey and BCG have institution records; Bain has none. Counts reflect affiliation recording not research output

## S10: Wikipedia pageviews API

- **Publisher:** Wikimedia Foundation
- **URL:** https://wikimedia.org/api/rest_v1
- **Date range:** 2015-07 to 2025-12
- **Fields used:** monthly user pageviews of each firm's English article
- **License / usage:** CC0
- **Access method:** src/ingest/attention.py
- **Raw file:** data/raw/attention_monthly.csv
- **Limitations:** Measures public attention not business performance

## S11: Entity statements with references

- **Publisher:** Wikidata
- **URL:** https://www.wikidata.org
- **Date range:** 2017-2026
- **Fields used:** revenue; headcount statements and their reference URLs
- **License / usage:** CC0
- **Access method:** src/ingest/wikidata.py
- **Raw file:** data/raw/wikidata_facts.csv
- **Limitations:** Statements are community-maintained; used only to locate leads, each carried into S3 as an estimate with its original reference
