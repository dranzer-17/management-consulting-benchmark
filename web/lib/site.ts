import { summary } from "./data"

export const SITE_URL = "https://research.kavish.tech"
export const REPO_URL = summary.repo
export const PORTFOLIO_URL = "https://kavish.tech"
export const REPORT_PATH = "/benchmarks/mckinsey-vs-bcg-vs-bain"
export const PUBLISHED = "2026-10-11"
export const UPDATED = summary.generated_at
export const longDate = (iso: string) => new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" })
export const DISCLAIMER =
  "Independent research using publicly available data. Not affiliated with, endorsed by, or based on confidential information from McKinsey & Company, Boston Consulting Group or Bain & Company."
