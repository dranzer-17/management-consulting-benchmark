import Link from "next/link"
import { GithubIcon } from "./github-icon"
import { DISCLAIMER, PORTFOLIO_URL, PUBLISHED, REPO_URL, UPDATED, longDate } from "@/lib/site"

export function Footer() {
  return (
    <footer className="mt-24 border-t border-border pt-8 text-[13px] leading-relaxed text-muted-foreground">
      <p>{DISCLAIMER} Findings are descriptive and rest on proxies and, in places, unverified estimates; see each finding’s limitations.</p>
      <p className="mt-3">
        Research by Kavish Shah · Published {longDate(PUBLISHED)} · Last updated {longDate(UPDATED)}
      </p>
      <p className="mt-3 flex flex-wrap gap-x-5 gap-y-1">
        <Link href="/methodology" className="underline underline-offset-2">Methodology</Link>
        <Link href="/reproducibility" className="underline underline-offset-2">Reproducibility</Link>
        <a href={REPO_URL} className="inline-flex items-center gap-1.5 underline underline-offset-2" rel="noopener noreferrer" target="_blank"><GithubIcon className="h-3.5 w-3.5" />Source code</a>
        <a href={PORTFOLIO_URL} className="underline underline-offset-2" rel="noopener noreferrer" target="_blank">kavish.tech</a>
      </p>
    </footer>
  )
}
