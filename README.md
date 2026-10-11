# McKinsey, BCG and Bain: A Public-Data Benchmarking Study

An independent, consulting-style comparison of McKinsey & Company, Boston Consulting Group (BCG) and Bain & Company, built only from publicly available data.

> **Disclaimer:** This is independent research. It is not affiliated with, endorsed by, or based on any confidential information from McKinsey, BCG or Bain.

## Central question
How have the three firms positioned themselves over the past decade, and what differentiates their growth, geographic presence, industry exposure, capabilities and strategic priorities?

## Headline results
Full synthesis, hypotheses and verdicts in the [executive summary](docs/executive_summary.md).

| | McKinsey | BCG | Bain |
|---|---|---|---|
| Scale, 2023 (revenue / headcount) | about $16B / about 45K *(estimated)* | $12.3B / 32K *(reported)* | about $6B / about 19K *(estimated, low confidence)* |
| US H-1B filing growth, FY2016 to FY2024 | 12.5% a year | 10.4% a year | 2.2% a year |
| US footprint (states / cities) | 45 / 155 | 35 / 57 | 19 / 32 |
| Technical share of filings, FY2021 to FY2025 | 38.0% | 24.0% | 8.8% |
| Federal prime contracts, FY2015 to FY2024 | $762M, 53% Defense | $826M, 68% Defense | None found |
| Australian federal contract notices, 2015-2025 | 15, AUD 21M | 195, AUD 284M | None found |

Main takeaways:
- McKinsey has the broadest and most technical US profile; BCG is the most transparent and shows steady growth; Bain is smaller, more concentrated and least technical.
- All three shifted toward technical and analytical roles over the decade.
- A decade-long revenue comparison is **not possible** from public sources: only BCG reports financials. McKinsey and Bain figures are estimates.
- **Industry exposure cannot be measured** from public data, because no firm publishes an industry revenue split.

Read these as descriptive findings. H-1B filings are a proxy for US hiring, not headcount or revenue, and no statistical significance tests were run.

## Finding sets
| # | Domain | Source | Write-up |
|---|---|---|---|
| 1 | Scale and hiring footprint | DOL H-1B filings | [Set 1](docs/findings/01_scale_hiring_footprint.md) |
| 2 | US public-sector exposure | USAspending.gov | [Set 2](docs/findings/02_public_sector_exposure.md) |
| 3 | Firm scale and global reach | Press releases, filings, secondary sources | [Set 3](docs/findings/03_firm_scale_and_reach.md) |
| 4 | Capability emphasis | DOL H-1B occupations | [Set 4](docs/findings/04_capability_emphasis.md) |
| 5 | Industry exposure (proxies only) | SEC EDGAR, firm sitemaps | [Set 5](docs/findings/05_industry_proxies.md) |
| 6 | US workforce and talent | DOL PERM filings | [Set 6](docs/findings/06_us_workforce_and_talent.md) |
| 7 | International public sector | UK, Canada, Australia registries | [Set 7](docs/findings/07_international_public_sector.md) |
| 8 | Publications and attention | Sitemaps, OpenAlex, Wikipedia | [Set 8](docs/findings/08_publications_and_attention.md) |

Each write-up states its data, method, findings and limitations. Every source is logged in [sources.md](sources.md) and every written claim in [claims.csv](claims.csv), where an automated test checks it against the computed metrics. The method is in [docs/methodology.md](docs/methodology.md).

## Website
`web/` is a Next.js site published at `research.kavish.tech/mbb` (Home, Research, Methodology, Data & Sources, Reproducibility, About). It reads only the JSON in `web/data/`, which `python -m src.export_web` generates from the pipeline outputs, so no research number is typed into the frontend. Run it with `cd web && npm install && npm run dev`, then open http://localhost:3000/mbb. The earlier single-file preview is kept in `web_static_preview/`.

## SQL database
[`src/build_database.py`](src/build_database.py) loads the clean data into a SQLite star schema ([`sql/schema.sql`](sql/schema.sql)): one firm dimension and three fact tables (H-1B filings, federal awards, firm-scale data points). Analytical queries are in [`sql/queries/`](sql/queries/); `python -m src.run_queries` runs them all. Results match the Python metrics.

## Repository structure
```
├── config/            Firm definitions
├── data/
│   ├── raw/           As-received public extracts (gitignored; make ingest re-creates them)
│   ├── manual/        Hand-compiled, source-linked scale points
│   └── clean/         Standardized tables produced by src/clean.py
├── docs/              Executive summary, methodology, finding write-ups, figures
├── outputs/           metrics.csv, year-by-year tables, charts
├── sql/               Schema and analytical queries
├── src/
│   ├── ingest/        One script per public source
│   ├── clean.py  metrics.py  figures.py  validate.py  export_web.py  build_database.py
│   └── legacy/        Original exploratory scripts, superseded by the pipeline above (not runnable on the current layout)
├── tests/             Validation, claim checks, matcher and taxonomy tests
├── web/               Next.js website (served under /mbb)
├── claims.csv  sources.csv  sources.md  Makefile  requirements.txt
```

## Reproducing the results
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest pyyaml
make reproduce   # clean, metrics, figures, sources, website data, validation (needs data/raw/)
make test        # validation plus every registered claim
make ingest      # re-download the raw data from the public sources (slow)
python -m src.build_database && python -m src.run_queries
```
Extraction needs internet access. Registry data can change slightly as agencies amend records, so re-running may give slightly different totals. `src.ingest.canada_contracts` accepts a locally downloaded copy of the 640 MB CSV as an argument.

## Limitations
- H-1B, PERM and US federal-contract data cover the **US only**; the UK, Canada and Australia are covered through contract registries only.
- Most McKinsey and Bain scale figures are secondary-source estimates that were not verified against the original pages; each is labelled in the data.
- "None found" for a firm (Bain in every contract registry) is not proof of no work.
- Industry mix and strategic priorities are not measured; SEC-mention and sitemap counts are proxies.
- The H-1B data comes from a public mirror of the Department of Labor files and has not been re-checked against the originals.
- No significance tests were run; findings are descriptive.
