"use client"

import { useEffect, useState } from "react"

/** "On this page" list. The section currently being read is shown bold and in full-contrast text. */
export function Toc({ items }: { items: [string, string][] }) {
  const [active, setActive] = useState(items[0]?.[0] ?? "")

  useEffect(() => {
    let frame = 0
    const update = () => {
      frame = 0
      // The active section is the last one whose heading has scrolled past a line just under the top of the viewport.
      const line = 140
      let current = items[0]?.[0] ?? ""
      for (const [id] of items) {
        const el = document.getElementById(id)
        if (el && el.getBoundingClientRect().top <= line) current = id
      }
      // At the very bottom of the page, the last section is the one being read.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) current = items[items.length - 1][0]
      setActive(current)
    }
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update) }
    update()
    window.addEventListener("scroll", onScroll, { passive: true })
    window.addEventListener("resize", onScroll)
    return () => {
      window.removeEventListener("scroll", onScroll)
      window.removeEventListener("resize", onScroll)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [items])

  return (
    <nav aria-label="On this page" className="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto text-[13px]">
      <p className="mb-3 font-bold">On this page</p>
      <ul className="space-y-2 border-l border-border pl-3">
        {items.map(([id, label]) => {
          const on = id === active
          return (
            <li key={id} className={on ? "-ml-[13px] border-l-2 border-foreground pl-[11px]" : ""}>
              <a href={`#${id}`} aria-current={on ? "location" : undefined}
                className={`transition-colors ${on ? "font-bold text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                {label}
              </a>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
