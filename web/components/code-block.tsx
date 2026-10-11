"use client"

import { useState } from "react"

/** Monospace block with a copy button. Copies the text exactly as shown. */
export function CodeBlock({ children }: { children: string }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(children)
    } catch {
      const t = document.createElement("textarea")
      t.value = children
      document.body.appendChild(t)
      t.select()
      document.execCommand("copy")
      t.remove()
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  return (
    <div className="group relative my-3">
      <pre className="overflow-x-auto rounded-md border border-border bg-card p-4 pr-12 text-[13px] leading-relaxed">{children}</pre>
      <button
        type="button"
        onClick={copy}
        aria-label={copied ? "Copied" : "Copy to clipboard"}
        className="absolute right-2 top-2 rounded-md border border-border bg-background p-1.5 text-foreground/60 transition-colors hover:text-foreground"
      >
        {copied ? (
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><path d="M20 6 9 17l-5-5" /></svg>
        ) : (
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><rect x="9" y="9" width="13" height="13" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
        )}
      </button>
      <span className="sr-only" role="status">{copied ? "Copied to clipboard" : ""}</span>
    </div>
  )
}
