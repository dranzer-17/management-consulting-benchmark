import Link from "next/link"
import type { ReactNode } from "react"
import { Chart, ScaleChart, type ScalePoint } from "./chart"
import type { ChartSpec } from "@/lib/findings"
import { BASIS_LABEL, FIRMS, FIRM_COLOR, claim, displayMetric, metric, metricRows, source, table, type Firm } from "@/lib/data"

export function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} className="mt-16">
      <h2 className="text-2xl font-bold md:text-[28px]"><a href={`#${id}`} className="hover:underline">{title}</a></h2>
      <div className="mt-5">{children}</div>
    </section>
  )
}

export function Label({ children, tone = "plain" }: { children: ReactNode; tone?: "plain" | "evidence" | "limits" }) {
  const cls = tone === "limits" ? "text-warn" : tone === "evidence" ? "text-primary" : "text-muted-foreground"
  return <h4 className={`mb-2 mt-7 text-[12px] font-bold uppercase tracking-[0.14em] ${cls}`}>{children}</h4>
}

export function FirmDot({ firm }: { firm: Firm }) {
  return <span className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full align-baseline" style={{ background: FIRM_COLOR[firm] }} aria-hidden />
}

/** One metric across the three firms, with its basis (reported / estimate / proxy). */
export function Headline({ metricId, label }: { metricId: string; label: string }) {
  const rows = metricRows(metricId)
  const bases = new Set(rows.map((r) => r.basis))
  const mixed = bases.size > 1
  const basis = mixed ? "Mixed basis" : BASIS_LABEL[rows[0]?.basis] ?? ""
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-[13px] font-semibold">{label}</p>
      <p className="text-[12px] text-muted-foreground">{rows[0]?.period} · {basis || "—"} · <span className="tabular-nums">{metricId}</span></p>
      <dl className="mt-2 space-y-0.5 text-[15px]">
        {FIRMS.map((f) => {
          const v = displayMetric(metricId, f)
          return (
            <div key={f} className="flex justify-between gap-4">
              <dt><FirmDot firm={f} />{f}</dt>
              <dd className={`tabular-nums ${v === "none found" ? "text-muted-foreground" : "font-semibold"}`}>
                {v}{mixed && v !== "none found" && <span className="ml-1.5 text-[11px] font-normal uppercase tracking-wide text-muted-foreground">{BASIS_LABEL[metric(metricId, f)?.basis ?? ""]}</span>}
              </dd>
            </div>
          )
        })}
      </dl>
    </div>
  )
}

/** Definition, numerator, denominator, filters and missing-data rule for each metric ID, straight from metrics.csv. */
export function Provenance({ metricIds }: { metricIds: string[] }) {
  return (
    <details className="mt-3 rounded-md border border-border px-4 py-2 text-[14px]">
      <summary className="cursor-pointer py-1 font-semibold">Metric definitions and provenance ({metricIds.length})</summary>
      <div className="overflow-x-auto pb-2">
        <table className="mt-2 w-full min-w-[640px] text-left text-[13px]">
          <thead className="text-muted-foreground"><tr><th className="py-1 pr-3">ID</th><th className="pr-3">Definition</th><th className="pr-3">Numerator / denominator</th><th className="pr-3">Filters and missing data</th><th>Basis</th></tr></thead>
          <tbody>
            {metricIds.map((id) => {
              const m = metricRows(id)[0]
              if (!m) return null
              return (
                <tr key={id} className="border-t border-border align-top">
                  <td className="py-2 pr-3 font-semibold tabular-nums">{id}</td>
                  <td className="pr-3">{m.definition}<div className="text-muted-foreground">{m.period} · {m.unit}</div></td>
                  <td className="pr-3">{m.numerator}{m.denominator && m.denominator !== "n/a" ? ` / ${m.denominator}` : ""}</td>
                  <td className="pr-3">{m.filters}<div className="text-muted-foreground">Missing data: {m.missing_data}</div></td>
                  <td>{BASIS_LABEL[m.basis] || m.basis}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </details>
  )
}

export function ClaimList({ ids }: { ids: string[] }) {
  return (
    <ul className="space-y-3">
      {ids.map((id) => {
        const c = claim(id)
        return (
          <li key={id} className="prose-report border-l-2 border-primary pl-4 text-[16px]">
            {c.claim}
            <span className="mt-1 block text-[12px] text-muted-foreground">
              {c.claim_id} · {c.source_ids} · checked against the data on every test run
            </span>
          </li>
        )
      })}
    </ul>
  )
}

export function FindingChart({ spec }: { spec: ChartSpec }) {
  if (spec.kind === "scale") {
    const pts = table("scale_points_all").filter((r) => r.metric === "revenue").map((r) => ({
      firm: r.firm as Firm, year: Number(r.year), value: Number(r.value), type: String(r.type), verified: String(r.verified),
    })) as ScalePoint[]
    return <ScaleChart id={spec.id} points={pts} title={spec.title} units={spec.units} period={spec.period} caption={spec.caption}
      limitation={spec.limitation ?? ""} sourceNote={spec.sourceNote} metricIds={spec.metricIds} />
  }
  let data = table(spec.table!)
  if (spec.valueKey && spec.valueFirm) data = data.map((r) => ({ [spec.xKey!]: r[spec.xKey!], [spec.valueFirm!]: r[spec.valueKey!] }))
  const firms = spec.firms ?? FIRMS
  if (!firms.some((f) => data.some((r) => r[f] != null))) throw new Error(`Chart ${spec.id} has no data: table ${spec.table} has no column for ${firms.join(", ")}`)
  return <Chart id={spec.id} kind={spec.kind} data={data} xKey={spec.xKey!} firms={spec.firms}
    title={spec.title} units={spec.units} period={spec.period} caption={spec.caption} limitation={spec.limitation}
    sourceNote={spec.sourceNote} metricIds={spec.metricIds} height={spec.height} />
}

export function SourceLinks({ ids }: { ids: string[] }) {
  return (
    <>
      {ids.map((id, i) => {
        const s = source(id)
        return (
          <span key={id}>
            {i > 0 && ", "}
            <Link href={`/data-and-sources#${id}`} className="underline underline-offset-2">{id}</Link>
            {s ? ` (${s.publisher})` : ""}
          </span>
        )
      })}
    </>
  )
}
