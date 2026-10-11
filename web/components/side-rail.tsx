"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import type { ReactNode } from "react"
import { ThemeToggle } from "./theme-toggle"

const icon = (children: ReactNode) => (
  <svg className="h-6 w-6 md:h-[22px] md:w-[22px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    {children}
  </svg>
)

export const NAV = [
  { href: "/", label: "Home", match: ["/"], icon: icon(<><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></>) },
  { href: "/analysis", label: "Analysis", match: ["/analysis"], icon: icon(<><path d="M4 19V5" /><path d="M4 19h16" /><path d="M8 15v-4" /><path d="M12 15V8" /><path d="M16 15v-2" /></>) },
  { href: "/methodology", label: "Methodology", match: ["/methodology"], icon: icon(<><path d="M9 3h6v5l4.5 9a2 2 0 0 1-1.8 3H6.3a2 2 0 0 1-1.8-3L9 8z" /><path d="M8 3h8" /></>) },
  { href: "/data-and-sources", label: "Data & Sources", match: ["/data-and-sources"], icon: icon(<><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" /></>) },
  { href: "/reproducibility", label: "Reproducibility", match: ["/reproducibility"], icon: icon(<><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16" /><path d="M3 21v-5h5" /></>) },
  { href: "/about", label: "About", match: ["/about"], icon: icon(<><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" /></>) },
]

function isActive(pathname: string, match: string[]) {
  return match.some((m) => (m === "/" ? pathname === "/" : pathname === m || pathname.startsWith(`${m}/`)))
}

/** Desktop: fixed left rail with a thin vertical rule (as on kavish.tech). Mobile: bottom tab bar. */
export function SideRail() {
  const pathname = usePathname()
  return (
    <>
      <div aria-hidden className="fixed inset-y-0 left-[15.5rem] z-40 hidden w-px bg-foreground/15 md:block" />

      <header className="fixed left-14 top-10 z-50 hidden md:block">
        <Link href="/" className="block leading-tight">
          <span className="block text-[15px] font-bold">Kavish Shah</span>
          <span className="block text-[13px] text-muted-foreground">Analysis</span>
        </Link>
      </header>

      <nav
        aria-label="Primary"
        className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t border-foreground/10 bg-background/95 px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur-md md:inset-auto md:left-14 md:top-1/2 md:-translate-y-1/2 md:flex-col md:items-start md:justify-center md:gap-8 md:border-0 md:bg-transparent md:p-0 md:backdrop-blur-none"
      >
        {NAV.map((item) => {
          const active = isActive(pathname, item.match)
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`group flex flex-col items-center gap-1 md:flex-row md:gap-3 ${active ? "text-foreground" : "text-foreground/40 hover:text-foreground"} transition-colors duration-200`}
            >
              {item.icon}
              <span className="whitespace-nowrap text-[10px] font-medium tracking-wide md:text-[15px]">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="fixed bottom-8 left-14 z-50 hidden md:block">
        <ThemeToggle />
      </div>
    </>
  )
}
