import type { ReactNode } from "react"
import { Footer } from "./footer"

/** Standard page frame: leaves room for the side rail on desktop and the tab bar on mobile. */
/** Standard page frame: room for the side rail, and one footer that is identical on every page and sits at the bottom edge. */
export function PageShell({ children }: { children: ReactNode; wide?: boolean }) {
  return (
    <div className="flex min-h-screen flex-col">
      <main id="main" className="flex-1 px-4 pb-16 pt-12 md:pl-[18.5rem] md:pr-10 md:pt-24">
        <div className="max-w-[1600px]">{children}</div>
      </main>
      <Footer />
    </div>
  )
}

export function PageTitle({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <header className="mb-10">
      <h1 className="text-3xl font-bold leading-tight md:text-[44px]">{title}</h1>
      {children && <div className="prose-report mt-5">{children}</div>}
    </header>
  )
}
