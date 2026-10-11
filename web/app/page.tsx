import Link from "next/link"
import { GithubIcon } from "@/components/github-icon"
import { FindingChart } from "@/components/report-parts"
import { PageShell } from "@/components/page-shell"
import { FINDINGS } from "@/lib/findings"
import { summary } from "@/lib/data"
import { DISCLAIMER, REPORT_PATH, REPO_URL, BASE_PATH } from "@/lib/site"

const FEATURED = ["chart-filings", "chart-technical", "chart-revenue"]
const allCharts = FINDINGS.flatMap((f) => f.charts)

export const metadata = { title: { absolute: "McKinsey vs BCG vs Bain | Kavish Shah | Analysis" }, alternates: { canonical: BASE_PATH } }

export default function Home() {
  const [fy0, fy1] = summary.us_filings_fiscal_years
  const coverage = [
    { n: summary.firms.toString(), l: "firms compared" },
    { n: summary.source_records.toLocaleString("en-US"), l: "source records processed" },
    { n: summary.sources.toString(), l: "public data sources" },
    { n: `FY${fy0}–${fy1}`, l: "US filing years covered" },
    { n: summary.metric_definitions.toString(), l: "defined metrics" },
    { n: summary.validation_checks_passed.toString(), l: "automated validation checks passing" },
  ]
  return (
    <PageShell wide>
      <div className="max-w-[64rem]">
        <h1>
          <span className="block text-4xl font-bold leading-tight md:text-[56px]">McKinsey vs BCG vs Bain</span>
          <span className="mt-3 block text-xl font-medium leading-snug text-muted-foreground md:text-[26px]">Management Consulting Competitive Benchmarking</span>
        </h1>
        <p className="prose-report mt-5">
          An independent, data-driven examination of the observable differences in scale, talent signals, geographic footprint, and
          public-sector exposure across McKinsey, BCG, and Bain.
        </p>
        <p className="prose-report mt-4 text-[16px]">
          The study covers US hiring filings from FY{fy0} to FY{fy1}, US federal and UK, Canadian and Australian public contracts,
          firm-published scale figures, and public web footprints, drawn from {summary.sources} public sources. Where a figure is an
          estimate or a proxy, it is labelled as one.
        </p>
        <p className="mt-6 flex flex-wrap gap-x-7 gap-y-2 text-[17px]">
          <Link className="link-arrow" href={REPORT_PATH}>Read the analysis <span aria-hidden>↗</span></Link>
          <Link className="link-arrow" href="/data-and-sources">Explore the data <span aria-hidden>↗</span></Link>
          <Link className="link-arrow" href="/methodology">View methodology <span aria-hidden>↗</span></Link>
          <a className="link-arrow" href={REPO_URL} target="_blank" rel="noopener noreferrer"><GithubIcon />Source code <span aria-hidden>↗</span></a>
        </p>
        <p className="mt-8 rounded-md bg-warn-bg px-4 py-3 text-[14px] text-warn">{DISCLAIMER}</p>
      </div>

      <section aria-labelledby="coverage" className="mt-16">
        <h2 id="coverage" className="text-2xl font-bold">Analysis coverage</h2>
        <dl className="mt-5 grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-border bg-border md:grid-cols-3">
          {coverage.map((c) => (
            <div key={c.l} className="bg-background p-4">
              <dd className="text-2xl font-bold tabular-nums md:text-[28px]">{c.n}</dd>
              <dt className="mt-1 text-[13px] text-muted-foreground">{c.l}</dt>
            </div>
          ))}
        </dl>
        <p className="mt-3 text-[12px] text-muted-foreground">
          Counts are generated from the pipeline outputs. Records are rows in the clean source tables; derived tables are not double counted.
        </p>
      </section>

      <section aria-labelledby="latest" className="mt-16">
        <h2 id="latest" className="text-2xl font-bold">The analysis</h2>
        <Link href={REPORT_PATH} className="mt-5 block rounded-lg border border-border p-5 transition-colors hover:bg-card">
          <p className="text-[12px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">Report · {summary.analysis_dimensions} analysis dimensions</p>
          <h3 className="mt-1 text-[19px] font-bold">McKinsey, BCG and Bain: what public data can and cannot show</h3>
          <p className="prose-report mt-2 text-[15px]">US hiring, public-sector contracts, firm scale, technical emphasis and workforce signals, each with its question, definition, evidence and limits.</p>
          <p className="mt-3 text-[15px] font-semibold underline underline-offset-4">Read the report <span aria-hidden>↗</span></p>
        </Link>
      </section>

      <section aria-labelledby="featured" className="mt-16">
        <h2 id="featured" className="text-2xl font-bold">Featured visualizations</h2>
        {FEATURED.map((id) => <FindingChart key={id} spec={allCharts.find((c) => c.id === id)!} />)}
        <p><Link href={REPORT_PATH} className="link-arrow">All charts and findings <span aria-hidden>↗</span></Link></p>
      </section>

      <section aria-labelledby="method" className="mt-16">
        <h2 id="method" className="text-2xl font-bold">Methodology and reproducibility</h2>
        <ul className="prose-report mt-4 list-disc space-y-2 pl-5 text-[16px]">
          <li><strong>Where the data comes from:</strong> government registries (US Labor, USAspending, SEC, UK, Canada, Australia), firm releases and public sitemaps, OpenAlex, Wikipedia and Wikidata.</li>
          <li><strong>How it is cleaned:</strong> raw extracts are never edited; one strict name matcher attributes records to firms.</li>
          <li><strong>How metrics are calculated:</strong> every metric has a stated numerator, denominator, filters and missing-data rule.</li>
          <li><strong>How quality is checked:</strong> {summary.validation_checks_passed} validation checks and {summary.claims} registered claims are tested on every run.</li>
          <li><strong>How to reproduce it:</strong> one command regenerates every table, chart and number on this site.</li>
        </ul>
        <p className="mt-5 flex gap-7 text-[16px]">
          <Link href="/methodology" className="link-arrow">Methodology <span aria-hidden>↗</span></Link>
          <Link href="/reproducibility" className="link-arrow">Reproducibility <span aria-hidden>↗</span></Link>
        </p>
      </section>

      <section aria-labelledby="downloads" className="mt-16">
        <h2 id="downloads" className="text-2xl font-bold">Downloads and source code</h2>
        <ul className="mt-4 space-y-1.5 text-[16px]">
          {summary.downloads.map((f) => (
            <li key={f}><a className="underline underline-offset-2" href={`${BASE_PATH}/data/${f}`} download>{f}</a></li>
          ))}
          <li><a className="underline underline-offset-2" href={REPO_URL} target="_blank" rel="noopener noreferrer">GitHub repository</a></li>
        </ul>
        <p className="mt-4 text-[13px] text-muted-foreground">
          Not yet available: a PDF report, a presentation and a Power BI dashboard. They will be linked here only when they exist.
        </p>
      </section>
    </PageShell>
  )
}
