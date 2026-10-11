# Finding Set 7: International Public-Sector Contracts (UK, Canada, Australia)

*Independent research using publicly available data. Not affiliated with McKinsey & Company, Boston Consulting Group or Bain & Company.*

## Question
Outside the US, how much published public-sector contract work do the firms hold, and how do they differ?

## Data and method
- **UK Contracts Finder (S6):** awarded notices 2015-2025. Framework-agreement ceilings (notices of GBP 50M or more) are excluded from totals because they are ceilings, not spend.
- **Canada proactive disclosure (S7):** federal contracts over CAD 10,000. The 640 MB CSV was downloaded and filtered by vendor name.
- **Australia AusTender (S8):** every OCDS contract notice published 2015-2025 (about 765,000), paged by week and filtered by supplier name.
- Supplier names are matched with the one strict matcher in `src/common.py`.
- Metrics: INTL-001 to INTL-007.

## Findings
| | McKinsey | BCG | Bain |
|---|---|---|---|
| UK awards, 2015-2025 | 135 worth GBP 308M | 108 worth GBP 270M | none found |
| Canada contracts, 2015-2025 | 34 worth CAD 121M | 15 worth CAD 45M | none found |
| Australia notices, 2015-2025 | 15 worth AUD 21M | 195 worth AUD 284M | none found |

1. **McKinsey leads in the UK and Canada; BCG leads in Australia.** In Australia BCG holds about 13 times as many notices as McKinsey.
2. **Buyers differ.** In Canada McKinsey's largest buyers are Immigration, Refugees and Citizenship (CAD 47.6M), Public Services and Procurement (29.6M) and National Defence (25.9M); BCG's value is mostly National Defence (39.2M). In Australia BCG's largest buyer is the Department of Foreign Affairs and Trade aid program (AUD 99.0M).
3. **Single contracts dominate some years.** One AUD 99M notice accounts for most of BCG's 2024 Australian value.
4. **No contract was found for Bain in any of the four public-sector registries** (US, UK, Canada, Australia).

## Limitations
- Each registry publishes only contracts above its own threshold, and not every award is published.
- "None found" for Bain is not proof of no public-sector work. It may sit under different legal entities, in subcontracts, or below thresholds.
- Values are as notified; Canadian values include amendments as reported.
- Counts and values are not comparable across countries (different thresholds, currencies and publication rules).
