# Finding Set 5: Industry Exposure (Proxies Only)

*Independent research using publicly available data. Not affiliated with McKinsey & Company, Boston Consulting Group or Bain & Company.*

## Question
Can public data show which industries each firm serves?

## Short answer
**No.** No firm publishes revenue or client lists by industry. This set reports two indirect signals, and neither measures exposure.

## Data and method
- **SEC EDGAR full-text search (S5):** filings 2015-2025 whose text names the firm. Operating-company filings (10-K, 8-K, S-1, 20-F, S-4, DRS, 10-Q, excluding funds and blank-check companies) are classified into industries from the filer's SIC code (`src/taxonomy.py`).
- **Firm website sitemaps (S4):** page counts under each firm's own industry and capability sections. McKinsey's site does not respond to automated requests from the collection environment, so only BCG and Bain are covered.
- Metrics: IND-001 to IND-007 in [metrics.csv](../../outputs/tables/metrics.csv).

## Findings
1. **McKinsey is named far more often in SEC filings:** 21,583 filings (7,486 operating-company filings from 1,765 filers), against BCG 10,065 (3,276; 872) and Bain 9,506 (2,893; 707).
2. **The industry mix of those filers is similar across the firms.** Healthcare and pharma, and technology and telecom, lead for all three (McKinsey 26.6% and 21.6%, BCG 25.5% and 19.1%, Bain 19.6% and 23.3%). The concentration index is nearly identical (0.177, 0.176, 0.173).
3. **Public-sector filers are 0% for every firm.** That reflects who files with the SEC, not the firms' public-sector work (see Sets 2 and 7).
4. **Publication emphasis:** BCG's site lists 170 industry pages and 292 capability pages; Bain's lists 121 and 163.

## Limitations
- A mention in an SEC filing can be a client, an auditor's reference, a litigation party or a risk-factor aside. It shows who writes about the firm, not where the firm earns revenue.
- Page counts measure what a firm publishes, not what it earns.
- Industry classification uses the filer's SIC code, which can lag its current business.
- McKinsey is absent from the sitemap-based counts.
