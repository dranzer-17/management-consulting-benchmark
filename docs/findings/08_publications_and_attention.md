# Finding Set 8: Publications and Public Attention

*Independent research using publicly available data. Not affiliated with McKinsey & Company, Boston Consulting Group or Bain & Company.*

## Question
What do the firms publish and how much public attention do they attract, as a signal of strategic emphasis?

## Data and method
- **BCG sitemap (S4):** publication pages dated by the year in the URL; AI emphasis measured by AI or GenAI terms in the URL slug.
- **OpenAlex (S9):** scholarly works with a firm affiliation, 2010-2025.
- **Wikipedia pageviews (S10):** monthly views of each firm's English article, 2016-2025.
- Metrics: PUB-001 to PUB-006, ATT-001.

## Findings
1. **BCG's publishing volume tripled:** dated publication pages rose from 202 in 2013 to 650 in 2025.
2. **AI is a fast-growing share of that output:** from 3.4% of pages in 2019 to 18.5% in 2025 (120 pages).
3. **Scholarly output is similar for McKinsey (799 works) and BCG (876).** OpenAlex has no institution record for Bain.
4. **Public attention is ordered McKinsey, BCG, Bain:** average annual Wikipedia views of about 639,000, 319,000 and 252,000.

## Limitations
- Slug matching misses AI content whose URL does not name AI and counts pages that merely mention it.
- Bain and McKinsey publication series could not be built from sitemaps (Bain is covered only through press releases; McKinsey's site is unreachable).
- Pageviews measure public attention, not business performance.
- Affiliation strings in OpenAlex are inconsistent, so scholarly counts are approximate.
