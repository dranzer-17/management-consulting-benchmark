import type { Metadata } from "next"
import Link from "next/link"
import { CodeBlock } from "@/components/code-block"
import { PageShell, PageTitle } from "@/components/page-shell"
import { summary } from "@/lib/data"
import { REPO_URL, BASE_PATH } from "@/lib/site"

export const metadata: Metadata = { title: "Methodology", description: "How the data was collected, cleaned, measured and checked.", alternates: { canonical: `${BASE_PATH}/methodology` } }

const H = ({ children }: { children: string }) => <h2 className="mb-3 mt-12 text-2xl font-bold">{children}</h2>

export default function Methodology() {
  return (
    <PageShell>
      <PageTitle title="How the numbers are produced">
        <p>Every number on this site comes from a scripted pipeline over public data. This page explains the stages and the rules the study follows.</p>
      </PageTitle>

      <H>Pipeline</H>
      <CodeBlock>{`src/ingest/*.py   -> data/raw/      as-received public extracts (never edited)
src/clean.py      -> data/clean/    standardized tables, one strict firm-name matcher
src/metrics.py    -> outputs/       metrics.csv and year-by-year tables
src/figures.py    -> outputs/       charts
src/validate.py   ->                checks raw, clean and metrics agree
src/export_web.py -> web/data/      the JSON this website reads`}</CodeBlock>

      <H>Rules the study follows</H>
      <ol className="prose-report list-decimal space-y-3 pl-5 text-[16px]">
        <li><strong>No invented data.</strong> Gaps stay gaps. Charts do not interpolate between points, and each scale figure is labelled reported or estimated, and verified or not.</li>
        <li><strong>One name matcher.</strong> A single set of patterns attributes records to a firm. They are strict on purpose, so unrelated companies with similar names (a fencing company called “McKinsey”, a tax firm starting with “Bain”) are excluded.</li>
        <li><strong>Every metric is defined.</strong> {summary.metric_definitions} metrics, each with definition, numerator, denominator, filters, missing-data rule, source and basis.</li>
        <li><strong>Every claim is tested.</strong> {summary.claims} written claims are registered with their source and limitation, and an automated test fails if the data stops supporting one.</li>
        <li><strong>The website holds no second copy of the numbers.</strong> It reads generated JSON, so a statistic cannot drift from the analysis.</li>
      </ol>

      <H>Data quality checks</H>
      <p className="prose-report text-[16px]">{summary.validation_checks_passed} automated checks run on every build: expected firm names only, no duplicate records, missing values, valid date ranges and categories, source and claim references, and an independent recomputation of headline metrics directly from the raw files rather than through the metrics script.</p>

      <H>Reading the measures</H>
      <ul className="prose-report list-disc space-y-2 pl-5 text-[16px]">
        <li><strong>H-1B and PERM filings</strong> measure US hiring and sponsorship activity, not headcount or revenue. Firms differ in how many positions they put on one application.</li>
        <li><strong>Federal prime contracts</strong> cover direct awards in the US registry. Subcontract work is reported separately.</li>
        <li><strong>UK, Canada and Australia contracts</strong> cover published awards above each registry’s threshold. UK framework ceilings are excluded from totals.</li>
        <li><strong>SEC mentions</strong> show who writes about a firm, not where it earns revenue.</li>
        <li><strong>Sitemap counts</strong> measure what a firm publishes, not what it earns.</li>
        <li><strong>Scale figures</strong> other than BCG’s are secondary-source estimates; verification status is listed per data point on the Data &amp; Sources page.</li>
      </ul>

      <H>What was not done</H>
      <ul className="prose-report list-disc space-y-2 pl-5 text-[16px]">
        <li>No significance tests or causal analysis. Findings are descriptive.</li>
        <li>No industry-revenue measure, because no public source exists.</li>
        <li>McKinsey’s website could not be read by automated requests, so McKinsey is absent from sitemap-based counts. Only sitemaps named in robots.txt were read, and no pages were crawled.</li>
        <li>The Power BI dashboard and slide deck planned in the original brief have not been built.</li>
      </ul>

      <p className="mt-10 text-[16px]">
        Full method text lives in the repository: <a className="underline underline-offset-2" href={`${REPO_URL}/blob/main/docs/methodology.md`} target="_blank" rel="noopener noreferrer">docs/methodology.md</a>. To rerun everything, see <Link className="underline underline-offset-2" href="/reproducibility">Reproducibility</Link>.
      </p>
    </PageShell>
  )
}
