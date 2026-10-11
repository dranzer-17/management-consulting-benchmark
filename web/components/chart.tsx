"use client"

import { useState } from "react"
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts"
import { FIRMS, FIRM_COLOR, type Firm, type Row } from "@/lib/data"

export type ChartKind = "line" | "bar" | "hbar"
type Props = {
  id: string
  title: string
  units: string
  period: string
  kind: ChartKind
  data: Row[]
  xKey: string
  firms?: Firm[]
  sourceNote: string
  caption: string
  limitation?: string
  metricIds?: string[]
  height?: number
}

const axis = { fontSize: 12, fill: "var(--muted-foreground)" }

/** One chart frame for the whole site: title, units and period above; caption, limitation and source below. */
export function Chart({ title, units, period, kind, data, xKey, firms = FIRMS, sourceNote, caption, limitation, metricIds, height = 300, id }: Props) {
  const [hidden, setHidden] = useState<Firm[]>([])
  const shown = firms.filter((f) => !hidden.includes(f) && data.some((r) => r[f] != null))
  const toggle = (f: Firm) => setHidden((h) => (h.includes(f) ? h.filter((x) => x !== f) : [...h, f]))
  const commonAxes = kind === "hbar"
    ? <><XAxis type="number" tick={axis} /><YAxis type="category" dataKey={xKey} tick={axis} width={170} /></>
    : <><XAxis dataKey={xKey} tick={axis} /><YAxis tick={axis} width={52} /></>
  const tip = <Tooltip contentStyle={{ background: "var(--background)", border: "1px solid var(--border)", fontSize: 13 }} formatter={(v: number | string) => (v == null ? "no record" : v)} />
  return (
    <figure id={id} className="my-8 rounded-lg border border-border bg-card/60 p-4 md:p-5">
      <figcaption className="mb-3">
        <h4 className="text-[17px] font-bold leading-snug">{title}</h4>
        <p className="mt-0.5 text-[13px] text-muted-foreground">{units} · {period}</p>
      </figcaption>

      <div className="mb-2 flex flex-wrap gap-2" role="group" aria-label="Show or hide firms">
        {firms.map((f) => (
          <button key={f} type="button" aria-pressed={!hidden.includes(f)} onClick={() => toggle(f)}
            className={`flex items-center gap-2 rounded-full border border-border px-3 py-1 text-[13px] transition-opacity ${hidden.includes(f) ? "opacity-40" : ""}`}>
            <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: FIRM_COLOR[f] }} aria-hidden />{f}
          </button>
        ))}
      </div>

      <div style={{ height }} role="img" aria-label={`${title}. ${caption}`}>
        <ResponsiveContainer width="100%" height="100%">
          {kind === "line" ? (
            <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="var(--border)" vertical={false} />{commonAxes}{tip}<Legend wrapperStyle={{ display: "none" }} />
              {shown.map((f) => <Line key={f} dataKey={f} stroke={FIRM_COLOR[f]} strokeWidth={2} dot={{ r: 2.5 }} connectNulls={false} isAnimationActive={false} />)}
            </LineChart>
          ) : (
            <BarChart data={data} layout={kind === "hbar" ? "vertical" : "horizontal"} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="var(--border)" vertical={kind === "hbar"} horizontal={kind !== "hbar"} />{commonAxes}{tip}
              {shown.map((f) => <Bar key={f} dataKey={f} fill={FIRM_COLOR[f]} isAnimationActive={false} />)}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <p className="mt-3 text-[14px] leading-relaxed text-foreground/80">{caption}</p>
      {limitation && <p className="mt-2 text-[13px] leading-relaxed text-warn">Limitation: {limitation}</p>}
      <p className="mt-2 text-[12px] text-muted-foreground">
        Source: {sourceNote}{metricIds?.length ? ` · Metrics: ${metricIds.join(", ")}` : ""}
      </p>
    </figure>
  )
}

export type ScalePoint = { firm: Firm; year: number; value: number; type: string; verified: string }

/** Revenue data points. Reported = filled, estimated = hollow; no lines between points, so gaps stay gaps. */
export function ScaleChart({ id, points, title, units, period, caption, limitation, sourceNote, metricIds }: {
  id: string; points: ScalePoint[]; title: string; units: string; period: string; caption: string; limitation: string; sourceNote: string; metricIds: string[]
}) {
  return (
    <figure id={id} className="my-8 rounded-lg border border-border bg-card/60 p-4 md:p-5">
      <figcaption className="mb-3">
        <h4 className="text-[17px] font-bold leading-snug">{title}</h4>
        <p className="mt-0.5 text-[13px] text-muted-foreground">{units} · {period}</p>
      </figcaption>
      <ul className="mb-2 flex flex-wrap gap-x-5 gap-y-1 text-[13px]" aria-label="Legend">
        {FIRMS.map((f) => <li key={f} className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: FIRM_COLOR[f] }} aria-hidden />{f}</li>)}
        <li className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded-full bg-foreground" aria-hidden />filled = reported</li>
        <li className="flex items-center gap-2"><span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-foreground" aria-hidden />hollow = estimate</li>
      </ul>
      <div style={{ height: 300 }} role="img" aria-label={`${title}. ${caption}`}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="var(--border)" />
            <XAxis type="number" dataKey="year" domain={[2016, 2026]} tick={axis} allowDecimals={false} tickCount={6} />
            <YAxis type="number" dataKey="value" tick={axis} width={40} />
            <Tooltip cursor={false} contentStyle={{ background: "var(--background)", border: "1px solid var(--border)", fontSize: 13 }}
              formatter={(v: number | string, name: string) => [name === "year" ? v : `$${v}B`, name === "year" ? "Year" : "Revenue"]} />
            {FIRMS.flatMap((f) => (["reported", "estimated"] as const).map((t) => {
              const d = points.filter((p) => p.firm === f && p.type === t)
              return d.length ? (
                <Scatter key={`${f}${t}`} data={d} isAnimationActive={false}
                  fill={t === "reported" ? FIRM_COLOR[f] : "transparent"} stroke={FIRM_COLOR[f]} strokeWidth={2} />
              ) : null
            }))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-3 text-[14px] leading-relaxed text-foreground/80">{caption}</p>
      <p className="mt-2 text-[13px] leading-relaxed text-warn">Limitation: {limitation}</p>
      <p className="mt-2 text-[12px] text-muted-foreground">Source: {sourceNote} · Metrics: {metricIds.join(", ")}</p>
    </figure>
  )
}
