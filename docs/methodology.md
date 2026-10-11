# Methodology

*Independent analysis using publicly available data. Not affiliated with McKinsey & Company, Boston Consulting Group or Bain & Company.*

## Pipeline
```
src/ingest/*.py   ->  data/raw/      as-received extracts of public sources (never edited)
src/clean.py      ->  data/clean/    standardized tables, one strict firm-name matcher
src/metrics.py    ->  outputs/tables metrics.csv plus year-by-year tables
src/figures.py    ->  outputs/figures
src/validate.py   ->  checks raw, clean and metrics agree; recomputes headline numbers independently from raw
src/export_web.py ->  web/data.js    everything the website shows
```
`make reproduce` runs clean through export without network access. `make ingest` re-downloads the raw data.

## Rules the study follows
1. **No invented data.** Gaps stay gaps. Charts do not interpolate between points, and each scale figure is labelled *reported* or *estimated* and *verified* or not.
2. **One name matcher.** `src/common.py` defines the only patterns used to attribute a record to a firm. They are strict on purpose, so unrelated companies with similar names ("Bain & Schindele", "McKinsey Fencing") are excluded.
3. **Every metric is defined.** `outputs/tables/metrics.csv` records the definition, numerator, denominator, filters, missing-data rule, source and basis (reported, proxy or estimate) for every value.
4. **Every claim is tested.** `claims.csv` registers each written claim with its source and limitation; `tests/test_pipeline.py` fails if the data no longer supports it.
5. **Limitations travel with the number.** Each finding write-up and each claim states what the measure does not show.

## Interpretation notes
- **H-1B and PERM filings** measure US hiring activity and sponsorship practice, not headcount or revenue. Firms differ in how many positions they put on one application.
- **Federal contracts** cover direct prime awards in the US registry. Subcontract work is reported separately and is dominated by a few large awards.
- **UK, Canada and Australia contracts** cover published public-sector awards above each registry's reporting threshold. Framework-agreement ceilings are excluded from totals.
- **SEC filing mentions** show who writes about each firm, not where it earns revenue.
- **Sitemap-based counts** measure what a firm publishes, not what it earns.
- **Scale figures** other than BCG's are secondary-source estimates; the verification table on the website shows which have been confirmed against the original page.

## Not done
No significance tests or causal analysis; no industry-revenue measure (no public source exists); McKinsey's website could not be read by automated requests from the collection environment, so McKinsey is absent from the sitemap-based counts.
