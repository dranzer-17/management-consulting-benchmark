import type { Metadata } from "next"
import Link from "next/link"
import { ClaimList, FindingChart, FirmDot, Label, Provenance, Section, SourceLinks } from "@/components/report-parts"
import { PageShell } from "@/components/page-shell"
import { Toc } from "@/components/toc"
import { BASIS_LABEL, FIRMS, metric, metricRows, summary, type Firm } from "@/lib/data"
import { NONE_FOUND, fmtMetric } from "@/lib/data"
import { FINDINGS } from "@/lib/findings"
import { DISCLAIMER, PUBLISHED, REPO_URL, UPDATED, longDate, BASE_PATH } from "@/lib/site"

export const metadata: Metadata = {
  title: "McKinsey vs BCG vs Bain: a public-data benchmark",
  description: "An independent comparison of scale, US hiring, public-sector contracts and technical emphasis at McKinsey, BCG and Bain, built only from public sources.",
  alternates: { canonical: `${BASE_PATH}/research` },
}

const TOC = [
  ["abstract", "Abstract"], ["summary", "Executive summary"], ["scope", "Questions and scope"], ["data", "Data and definitions"],
  ...FINDINGS.map((f) => [f.slug, `${f.num}. ${f.short}`]), ["comparison", "Cross-firm comparison"], ["interpretation", "Interpretation"],
  ["limitations", "Limitations"], ["conclusion", "Conclusion"], ["references", "References"],
]

const SUMMARY_CLAIMS = ["HIRE-001", "CAP-002", "FED-002", "SCALE-004", "INTL-003"]
const COMPARE: [string, string][] = [
  ["HIRE-001", "US H-1B filings, certified"], ["HIRE-002", "Filing growth per year"], ["HIRE-003", "US worksite states"],
  ["CAP-003", "Technical share of filings, FY2021–25"], ["WORK-002", "Max US employees stated on PERM, FY2024"],
  ["FED-002", "US federal prime contract value"], ["INTL-002", "UK award value"], ["INTL-005", "Canadian contract value"], ["INTL-007", "Australian contract value"],
  ["SCALE-005", "Global revenue, 2023"], ["SCALE-006", "Global headcount, 2023"],
]

function Cell({ id, firm }: { id: string; firm: Firm }) {
  const m = metric(id, firm)
  if (!m) return <span>n/a</span>
  if (NONE_FOUND.has(id) && Number(m.value) === 0) return <span className="text-muted-foreground">none found</span>
  const tag = m.basis === "estimated" ? "estimate" : m.basis === "reported" && id.startsWith("SCALE") ? "reported" : ""
  return <span>{fmtMetric(m)}{tag && <span className="ml-1 text-[11px] uppercase tracking-wide text-muted-foreground">{tag}</span>}</span>
}

export default function Report() {
  const [fy0, fy1] = summary.us_filings_fiscal_years
  return (
    <PageShell wide>
      <div className="grid gap-12 xl:grid-cols-[minmax(0,720px)_200px]">
        <article>
          <header>
            <h1 className="text-3xl font-bold leading-tight md:text-[42px]">McKinsey, BCG and Bain: what public data can and cannot show</h1>
            <p className="mt-4 text-[14px] text-muted-foreground">
              Kavish Shah · Published {longDate(PUBLISHED)} · Last updated {longDate(UPDATED)} · <a className="underline underline-offset-2" href={REPO_URL} target="_blank" rel="noopener noreferrer">Source code</a>
            </p>
            <p className="mt-6 rounded-md bg-warn-bg px-4 py-3 text-[14px] text-warn">{DISCLAIMER}</p>
          </header>

          <Section id="abstract" title="Abstract">
            <p className="prose-report">
              This report compares McKinsey, BCG and Bain using only public sources. Public data supports a clear relative profile of each
              firm in US hiring behavior, a partial view of scale, and no direct view of industry mix. It reports what each source can and
              cannot show, labels estimates and proxies, and makes every number traceable to a source file and a calculation.
            </p>
          </Section>

          <Section id="summary" title="Executive summary">
            <p className="prose-report mb-4">The statements below are registered claims. Each is checked against the computed metrics whenever the pipeline runs.</p>
            <ClaimList ids={SUMMARY_CLAIMS} />
            <Label>Implications</Label>
            <p className="prose-report mb-3">These follow from the findings; they are suggestions, not proven causal claims.</p>
            <ol className="prose-report list-decimal space-y-2 pl-5 text-[16px]">
              <li>Treat BCG as the reference firm for any quantitative benchmark, because it is the only one with reported, continuous figures. Label McKinsey and Bain comparisons as estimates.</li>
              <li>Do not read H-1B filings as headcount. Differences between firms mix hiring scale with filing practice.</li>
              <li>The rising technical share of filings is the clearest strategic signal in the data: all three moved the same way, at different speeds.</li>
              <li>A fuller industry view needs different data, such as client-side disclosures or job postings by industry, each with its own terms-of-use and quality review.</li>
            </ol>
          </Section>

          <Section id="scope" title="Research questions and scope">
            <p className="prose-report">How have the three firms positioned themselves, and what differentiates their US hiring, geographic presence, capabilities, public-sector exposure and scale? The study covers US filings from FY{fy0} to FY{fy1} and public contracts in four countries. It does not cover client work, private revenue by industry, strategy, or any confidential information.</p>
          </Section>

          <Section id="data" title="Data sources and definitions">
            <p className="prose-report">
              {summary.sources} public sources supply {summary.source_records.toLocaleString("en-US")} cleaned records. Every metric has a stated definition, numerator, denominator, filters and missing-data rule, shown under each finding and in the full list on the <Link className="underline underline-offset-2" href="/data-and-sources">Data &amp; Sources</Link> page. A metric’s basis is one of: reported (published by the firm or regulator), estimate (third-party), proxy (an indirect measure) or self-reported on a filing.
            </p>
          </Section>

          {FINDINGS.map((f) => (
            <Section key={f.slug} id={f.slug} title={`${f.num}. ${f.title}`}>
              <Label>Research question</Label>
              <p className="prose-report">{f.question}</p>

              <Label>Metric and definition</Label>
              <p className="prose-report text-[16px]">{f.measures} Period: {f.period}. Data: {f.dataset}.</p>
              <Provenance metricIds={f.metricIds} />

              <Label tone="evidence">Evidence</Label>
              <ClaimList ids={f.claimIds} />
              {f.charts.map((c) => <FindingChart key={c.id} spec={c} />)}

              <Label>Interpretation</Label>
              <div className="prose-report space-y-3 text-[16px]">{f.interpretation.map((t, i) => <p key={i}>{t}</p>)}</div>

              <Label tone="limits">Limitations</Label>
              <ul className="list-disc space-y-2 rounded-md bg-warn-bg px-8 py-4 text-[14.5px] leading-relaxed text-warn">
                {f.limitations.map((t, i) => <li key={i}>{t}</li>)}
              </ul>

              <Label>Sources and reproducibility</Label>
              <p className="text-[14px] leading-relaxed text-muted-foreground">
                Sources: <SourceLinks ids={f.sourceIds} />. Code: <code className="rounded bg-card px-1">{f.script}</code>. Tables: {f.tables.map((t) => `outputs/tables/${t}.csv`).join(", ")}. See <Link className="underline underline-offset-2" href="/reproducibility">Reproducibility</Link>.
              </p>
            </Section>
          ))}

          <Section id="comparison" title="Cross-firm comparison">
            <p className="prose-report mb-4">Selected metrics side by side. Read each row with its basis and period: rows differ in what they measure, and a missing value is shown as “none found”, never as a measured zero.</p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[620px] text-left text-[14px]">
                <thead className="text-muted-foreground">
                  <tr><th className="py-2 pr-3 font-semibold">Metric</th>{FIRMS.map((f) => <th key={f} className="pr-3 font-semibold"><FirmDot firm={f} />{f}</th>)}<th className="font-semibold">Basis</th></tr>
                </thead>
                <tbody>
                  {COMPARE.map(([id, label]) => {
                    const m = metric(id, "BCG")
                    return (
                      <tr key={id} className="border-t border-border align-top">
                        <td className="py-2 pr-3">{label}<div className="text-[12px] text-muted-foreground">{id} · {m?.period}</div></td>
                        {FIRMS.map((f) => <td key={f} className="pr-3 tabular-nums"><Cell id={id} firm={f} /></td>)}
                        <td className="text-[13px] text-muted-foreground">{new Set(metricRows(id).map((r) => r.basis)).size > 1 ? "Mixed (see tags)" : BASIS_LABEL[m?.basis ?? ""] || "—"}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Section>

          <Section id="interpretation" title="Interpretation and implications">
            <div className="prose-report space-y-3 text-[16px]">
              <p>McKinsey has the broadest and most technical US hiring profile in this data. BCG is the most transparent and shows steady growth in its own reported figures. Bain is smaller and more concentrated, with the least technical mix and no public contracts found in any registry used.</p>
              <p>These are descriptive differences. The study ran no significance tests and makes no causal claim about why the firms differ.</p>
            </div>
          </Section>

          <Section id="limitations" title="Limitations and uncertainty">
            <ul className="prose-report list-disc space-y-2 pl-5 text-[16px]">
              <li>H-1B and PERM filings describe US hiring of foreign-national workers, not an entire workforce. US federal prime awards are not all public-sector revenue.</li>
              <li>Most McKinsey and Bain scale figures are secondary-source estimates that have not been verified against the original page.</li>
              <li>“None found” in a registry is not proof that no work exists.</li>
              <li>Industry mix and strategic priorities are not measured; SEC mentions and sitemap counts are proxies.</li>
              <li>The H-1B and PERM data comes from a public mirror of Department of Labor files and has not been re-checked against the originals.</li>
            </ul>
          </Section>

          <Section id="conclusion" title="Conclusion">
            <p className="prose-report">Public data supports a relative profile of the three firms on US hiring, public contracts and technical emphasis, a limited view of scale anchored on BCG’s reported figures, and no direct view of industry exposure. The value of the study is as much in what it declines to claim as in what it measures.</p>
          </Section>

          <Section id="references" title="References and reproducibility">
            <p className="prose-report text-[16px]">
              Every source, with URL, retrieval date, license and limitations, is on the <Link className="underline underline-offset-2" href="/data-and-sources">Data &amp; Sources</Link> page. To regenerate every number and chart in this report, follow <Link className="underline underline-offset-2" href="/reproducibility">Reproducibility</Link>.
            </p>
          </Section>
        </article>

        <aside className="hidden xl:block"><Toc items={TOC as [string, string][]} /></aside>
      </div>
    </PageShell>
  )
}
