import type { Metadata } from "next"
import { PageShell, PageTitle } from "@/components/page-shell"
import { DISCLAIMER, PORTFOLIO_URL, REPO_URL } from "@/lib/site"

export const metadata: Metadata = { title: "About", description: "Who produced this research and how independent it is.", alternates: { canonical: "/about" } }

export default function About() {
  return (
    <PageShell>
      <PageTitle eyebrow="About" title="About this research">
        <p>This is an independent analysis by Kavish Shah, a student based in Mumbai, built as a reproducible public-data study of three consulting firms.</p>
      </PageTitle>
      <h2 className="mb-3 mt-10 text-2xl font-bold">Independence</h2>
      <p className="prose-report text-[16px]">{DISCLAIMER} No firm logos or branding are used; firms are identified by name and a neutral color only.</p>
      <h2 className="mb-3 mt-10 text-2xl font-bold">Why it exists</h2>
      <p className="prose-report text-[16px]">To show what can honestly be said about large private firms from public data, and where the data stops. Findings are descriptive, estimates are labelled, and every number can be traced to a source and rerun.</p>
      <h2 className="mb-3 mt-10 text-2xl font-bold">Links</h2>
      <ul className="space-y-1.5 text-[16px]">
        <li><a className="underline underline-offset-2" href={REPO_URL} target="_blank" rel="noopener noreferrer">Source code and data on GitHub</a></li>
        <li><a className="underline underline-offset-2" href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer">kavish.tech</a></li>
      </ul>
    </PageShell>
  )
}
