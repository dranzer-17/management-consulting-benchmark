import type { Metadata } from "next"
import { BASE_PATH } from "@/lib/site"
import { PageShell, PageTitle } from "@/components/page-shell"
import { BASIS_LABEL, metrics, sources, summary, table } from "@/lib/data"

export const metadata: Metadata = { title: "Data & Sources", description: "Every source, dataset, scale data point and metric definition behind the analysis.", alternates: { canonical: `${BASE_PATH}/data-and-sources` } }

const H = ({ id, children }: { id?: string; children: string }) => <h2 id={id} className="mb-3 mt-14 text-2xl font-bold">{children}</h2>
const th = "py-2 pr-3 text-left font-semibold text-muted-foreground"

export default function DataAndSources() {
  const scale = table("scale_points_all")
  const verified = table("scale_points_verified")
  const seen = new Set<string>()
  const dictionary = metrics.filter((m) => (seen.has(m.metric_id) ? false : (seen.add(m.metric_id), true)))
  return (
    <PageShell wide>
      <div className="max-w-[64rem]">
        <PageTitle title="What the study is built on">
          <p>{summary.sources} public sources, {summary.source_records.toLocaleString("en-US")} cleaned records and {summary.metric_definitions} defined metrics. Retrieval dates are in each source entry.</p>
        </PageTitle>
      </div>

      <H id="sources">Sources</H>
      <div className="space-y-4">
        {sources.map((s) => (
          <section key={s.source_id} id={s.source_id} className="rounded-lg border border-border p-4">
            <h3 className="text-[16px] font-bold">{s.source_id}. {s.dataset}</h3>
            <dl className="mt-2 grid gap-x-6 gap-y-1 text-[14px] md:grid-cols-[130px_1fr]">
              <dt className="text-muted-foreground">Publisher</dt><dd>{s.publisher}</dd>
              <dt className="text-muted-foreground">URL</dt><dd className="break-all"><a className="underline underline-offset-2" href={s.url} target="_blank" rel="noopener noreferrer">{s.url}</a></dd>
              <dt className="text-muted-foreground">Retrieved</dt><dd>{s.date_accessed} · covers {s.date_range}</dd>
              <dt className="text-muted-foreground">Fields used</dt><dd>{s.fields_used}</dd>
              <dt className="text-muted-foreground">License / use</dt><dd>{s.license_or_usage}</dd>
              <dt className="text-muted-foreground">Access method</dt><dd>{s.access_method}</dd>
              <dt className="text-muted-foreground">Limitations</dt><dd className="text-warn">{s.limitations}</dd>
            </dl>
          </section>
        ))}
      </div>

      <H id="datasets">Dataset coverage</H>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[480px] text-[14px]">
          <thead><tr><th className={th}>Clean table</th><th className={th}>Source</th><th className={`${th} text-right`}>Rows</th></tr></thead>
          <tbody>
            {summary.datasets.map((d) => (
              <tr key={d.file} className="border-t border-border"><td className="py-1.5 pr-3 font-mono text-[13px]">{d.file}</td><td className="pr-3">{d.source_id}</td><td className="text-right tabular-nums">{d.rows.toLocaleString("en-US")}</td></tr>
            ))}
            <tr className="border-t-2 border-border font-semibold"><td className="py-2">Total source records</td><td /><td className="text-right tabular-nums">{summary.source_records.toLocaleString("en-US")}</td></tr>
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[12px] text-muted-foreground">{summary.source_records_note}.</p>

      <H id="scale-points">Scale data points and verification status</H>
      <p className="prose-report text-[16px]">
        These hand-compiled figures feed the scale finding. “Verified” means the source page was opened and the figure confirmed. Open the URL to check any point yourself.
      </p>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[360px] max-w-[480px] text-[14px]">
          <thead><tr><th className={th}>Firm</th><th className={th}>Verified</th><th className={th}>Not verified</th></tr></thead>
          <tbody>{verified.map((r) => <tr key={String(r.firm)} className="border-t border-border"><td className="py-1.5">{r.firm}</td><td>{r.yes}</td><td className="text-warn">{r.no}</td></tr>)}</tbody>
        </table>
      </div>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[760px] text-[13px]">
          <thead><tr>{["Firm", "Year", "Metric", "Value", "Basis", "Confidence", "Verified", "Source"].map((h) => <th key={h} className={th}>{h}</th>)}</tr></thead>
          <tbody>
            {scale.map((r, i) => (
              <tr key={i} className="border-t border-border align-top">
                <td className="py-1.5 pr-3">{r.firm}</td><td className="pr-3">{r.year}</td><td className="pr-3">{r.metric}</td>
                <td className="pr-3 tabular-nums">{Number(r.value).toLocaleString("en-US")} {String(r.unit).replace("usd_billion", "USD bn")}</td>
                <td className="pr-3">{r.type === "estimated" ? "Estimate" : "Reported"}</td><td className="pr-3">{r.confidence}</td>
                <td className={`pr-3 ${r.verified === "yes" ? "" : "text-warn"}`}>{r.verified}</td>
                <td><a className="underline underline-offset-2" href={String(r.source_url)} target="_blank" rel="noopener noreferrer">link</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <H id="dictionary">Metric dictionary</H>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-[13px]">
          <thead><tr>{["ID", "Definition", "Period", "Unit", "Basis", "Filters", "Missing data", "Source"].map((h) => <th key={h} className={th}>{h}</th>)}</tr></thead>
          <tbody>
            {dictionary.map((m) => (
              <tr key={m.metric_id} className="border-t border-border align-top">
                <td className="py-1.5 pr-3 font-semibold tabular-nums">{m.metric_id}</td><td className="pr-3">{m.definition}</td><td className="pr-3">{m.period}</td>
                <td className="pr-3">{m.unit}</td><td className="pr-3">{BASIS_LABEL[m.basis] || m.basis}</td><td className="pr-3">{m.filters}</td><td className="pr-3">{m.missing_data}</td><td>{m.source_ids}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <H id="downloads">Downloads</H>
      <ul className="space-y-1.5 text-[15px]">{summary.downloads.map((f) => <li key={f}><a className="underline underline-offset-2" href={`${BASE_PATH}/data/${f}`} download>{f}</a></li>)}</ul>
    </PageShell>
  )
}
