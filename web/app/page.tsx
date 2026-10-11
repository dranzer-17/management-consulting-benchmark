import { PageShell } from "@/components/page-shell"

const FIRMS = [
  { name: "McKinsey", cls: "bg-mckinsey" },
  { name: "BCG", cls: "bg-bcg" },
  { name: "Bain", cls: "bg-bain" },
]

/** Phase 1 placeholder: proves the design system (type, color, rail, dark mode). Replaced in Phase 3. */
export default function Home() {
  return (
    <PageShell>
      <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.14em] text-muted-foreground">Independent research</p>
      <h1 className="text-3xl font-bold leading-tight md:text-[44px]">Management Consulting Competitive Benchmarking</h1>
      <p className="prose-report mt-6">
        An independent, data-driven examination of the observable differences in scale, talent signals, geographic footprint,
        and public-sector exposure across McKinsey, BCG, and Bain.
      </p>

      <ul className="mt-8 flex flex-wrap gap-x-6 gap-y-2" aria-label="Firm color key">
        {FIRMS.map((f) => (
          <li key={f.name} className="flex items-center gap-2 text-[15px]">
            <span className={`inline-block h-3 w-3 rounded-full ${f.cls}`} aria-hidden />
            {f.name}
          </li>
        ))}
      </ul>

      <p className="mt-10 rounded-md bg-warn-bg px-4 py-3 text-[14px] text-warn">
        Independent research. Not affiliated with, endorsed by, or based on confidential information from McKinsey &amp; Company,
        Boston Consulting Group or Bain &amp; Company.
      </p>

      <p className="mt-10 text-sm text-muted-foreground">Design system preview (Phase 1). Content arrives in Phase 3.</p>
    </PageShell>
  )
}
