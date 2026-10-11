import type { ReactNode } from "react"

/** Standard page frame: leaves room for the side rail on desktop and the tab bar on mobile. */
export function PageShell({ children, wide = false }: { children: ReactNode; wide?: boolean }) {
  return (
    <main id="main" className="px-4 pb-28 pt-12 md:pb-24 md:pl-[18.5rem] md:pr-10 md:pt-24">
      <div className={`mx-auto ${wide ? "max-w-[1000px]" : "max-w-[720px]"}`}>{children}</div>
    </main>
  )
}

export function PageStub({ title, phase }: { title: string; phase: string }) {
  return (
    <PageShell>
      <h1 className="text-3xl font-bold md:text-5xl">{title}</h1>
      <p className="prose-report mt-6">This page is built in {phase}. It is intentionally empty for now.</p>
    </PageShell>
  )
}
