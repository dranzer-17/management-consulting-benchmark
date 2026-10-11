// Typed access to the JSON the Python pipeline generates (python -m src.export_web). Nothing in the site types a
// number by hand: values come from these files and are formatted here.
import metricsJson from "@/data/metrics.json"
import claimsJson from "@/data/claims.json"
import sourcesJson from "@/data/sources.json"
import summaryJson from "@/data/summary.json"
import tablesJson from "@/data/tables.json"

export type Firm = "McKinsey" | "BCG" | "Bain"
export const FIRMS: Firm[] = ["McKinsey", "BCG", "Bain"]
export const FIRM_COLOR: Record<Firm, string> = {
  McKinsey: "var(--firm-mckinsey)",
  BCG: "var(--firm-bcg)",
  Bain: "var(--firm-bain)",
}

export type Metric = {
  metric_id: string; set: string | number; firm: string; period: string; value: number | string; unit: string; basis: string
  definition: string; numerator: string; denominator: string; filters: string; missing_data: string; source_ids: string
}
export type Claim = { claim_id: string; claim: string; metric: string; source_ids: string; method: string; limitation: string; status: string }
export type Source = {
  source_id: string; publisher: string; dataset: string; url: string; date_accessed: string; date_range: string; fields_used: string
  license_or_usage: string; access_method: string; limitations: string; raw_file: string
}
export type Row = Record<string, string | number | null>

export const metrics = metricsJson as unknown as Metric[]
export const claims = claimsJson as unknown as Claim[]
export const sources = sourcesJson as unknown as Source[]
export const summary = summaryJson as unknown as {
  generated_at: string; repo: string; firms: number; sources: number; source_records: number; source_records_note: string
  datasets: { file: string; source_id: string; rows: number }[]; metric_definitions: number; metric_values: number
  claims: number; claims_verified: number; validation_checks_passed: number; validation_failures: number
  us_filings_fiscal_years: [number, number]; analysis_dimensions: number; downloads: string[]
}
const tables = tablesJson as unknown as Record<string, Row[]>

/** A pipeline table with empty cells turned into null (a missing observation is not a zero). */
export function table(name: string): Row[] {
  const rows = tables[name]
  if (!rows) throw new Error(`Missing table ${name}; run python -m src.export_web`)
  return rows.map((r) => Object.fromEntries(Object.entries(r).map(([k, v]) => [k, v === "" ? null : v])))
}

export const metric = (id: string, firm: string) => metrics.find((m) => m.metric_id === id && m.firm === firm)
export const metricRows = (id: string) => metrics.filter((m) => m.metric_id === id)
export const claim = (id: string) => {
  const c = claims.find((c) => c.claim_id === id)
  if (!c) throw new Error(`Missing claim ${id}`)
  return c
}
export const source = (id: string) => sources.find((s) => s.source_id === id)

const n = (v: number | string) => (typeof v === "number" ? v : Number(v))
const int = (v: number, d = 0) => v.toLocaleString("en-US", { maximumFractionDigits: d })

/** Format a metric value with its unit. */
export function fmtMetric(m: Metric | undefined): string {
  if (!m) return "not found"
  if (m.value === "n/a" || m.value === "") return "n/a"
  const v = n(m.value)
  switch (m.unit) {
    case "USD millions": return `$${int(v)}M`
    case "GBP millions": return `£${int(v)}M`
    case "CAD millions": return `CAD ${int(v)}M`
    case "AUD millions": return `AUD ${int(v)}M`
    case "USD billion": return `$${int(v, 1)}B`
    case "USD thousand per employee": return `$${int(v)}K`
    case "USD": return `$${int(v)}`
    case "%": case "% per year": return `${int(v, 1)}%`
    case "index 0-1": return int(v, 3)
    case "positions per filing": return int(v, 1)
    default: return int(v)
  }
}

/** Metrics where a zero or missing value means "no match found in this registry", not a measured zero. */
export const NONE_FOUND = new Set(["FED-001", "FED-002", "FED-003", "FED-004", "FED-005", "FED-006", "FED-008", "FED-009", "INTL-001", "INTL-002", "INTL-003", "INTL-004", "INTL-005", "INTL-006", "INTL-007"])

/** Display value for a firm's metric: "none found" where a registry search found nothing, else the formatted value. */
export function displayMetric(id: string, firm: string): string {
  const m = metric(id, firm)
  if (NONE_FOUND.has(id) && (!m || Number(m.value) === 0)) return "none found"
  return fmtMetric(m)
}

export const BASIS_LABEL: Record<string, string> = {
  reported: "Reported", estimated: "Estimate", proxy: "Proxy", "reported-on-form": "Self-reported on filing", attention: "Attention", "n/a": "",
}
