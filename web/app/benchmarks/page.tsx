import type { Metadata } from "next"
import Link from "next/link"
import { Headline } from "@/components/report-parts"
import { PageShell, PageTitle } from "@/components/page-shell"
import { FINDINGS } from "@/lib/findings"
import { summary } from "@/lib/data"
import { REPORT_PATH } from "@/lib/site"

export const metadata: Metadata = {
  title: "Research",
  description: "Independent research reports built from public data, with every finding’s question, metric, evidence and limits.",
  alternates: { canonical: "/benchmarks" },
}

export default function ResearchIndex() {
  return (
    <PageShell wide>
      <div className="max-w-[720px]">
        <PageTitle eyebrow="Research" title="Reports and findings">
          <p>Each report states its question, defines every metric, shows the evidence, and says what the data cannot establish.</p>
        </PageTitle>
        <Link href={REPORT_PATH} className="block rounded-lg border border-border p-5 transition-colors hover:bg-card">
          <p className="text-[12px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">Report · {summary.research_dimensions} research dimensions</p>
          <h2 className="mt-1 text-[22px] font-bold">McKinsey, BCG and Bain: what public data can and cannot show</h2>
          <p className="prose-report mt-2 text-[15px]">
            An independent examination of scale, talent signals, geographic footprint and public-sector exposure across the three firms.
          </p>
          <p className="mt-3 text-[15px] font-semibold underline underline-offset-4">Read the full report <span aria-hidden>↗</span></p>
        </Link>
      </div>

      <section aria-labelledby="findings" className="mt-14">
        <h2 id="findings" className="text-2xl font-bold">Findings in this report</h2>
        <p className="prose-report mt-3 max-w-[720px] text-[16px]">
          The first five are the core findings; the last three extend the picture with proxy and international evidence.
        </p>
        <ol className="mt-6 space-y-5">
          {FINDINGS.map((f) => (
            <li key={f.slug} className="rounded-lg border border-border p-5">
              <p className="text-[12px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">{f.core ? "Core finding" : "Extended analysis"} · {f.period}</p>
              <h3 className="mt-1 text-[19px] font-bold"><Link href={`${REPORT_PATH}#${f.slug}`} className="hover:underline">{f.title}</Link></h3>
              <p className="prose-report mt-2 text-[15px]">{f.question}</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">{f.headline.map((h) => <Headline key={h.metric} metricId={h.metric} label={h.label} />)}</div>
              <p className="mt-3 text-[13px] text-muted-foreground">Data: {f.dataset}. {f.measures}</p>
              <p className="mt-3 text-[15px]"><Link href={`${REPORT_PATH}#${f.slug}`} className="link-arrow">Detailed analysis <span aria-hidden>↗</span></Link></p>
            </li>
          ))}
        </ol>
      </section>
    </PageShell>
  )
}
