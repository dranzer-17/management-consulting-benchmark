import type { ReactNode } from "react"
import { Footer } from "./footer"

/** Standard page frame: leaves room for the side rail on desktop and the tab bar on mobile. */
export function PageShell({ children, wide = false }: { children: ReactNode; wide?: boolean }) {
  return (
    <main id="main" className="px-4 pb-28 pt-12 md:pb-24 md:pl-[18.5rem] md:pr-10 md:pt-24">
      <div className={`mx-auto ${wide ? "max-w-[1000px]" : "max-w-[720px]"}`}>{children}<Footer /></div>
    </main>
  )
}

export function PageTitle({ eyebrow, title, children }: { eyebrow?: string; title: string; children?: ReactNode }) {
  return (
    <header className="mb-10">
      {eyebrow && <p className="mb-3 text-[13px] font-medium uppercase tracking-[0.14em] text-muted-foreground">{eyebrow}</p>}
      <h1 className="text-3xl font-bold leading-tight md:text-[44px]">{title}</h1>
      {children && <div className="prose-report mt-5">{children}</div>}
    </header>
  )
}
