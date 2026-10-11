import Link from "next/link"
import { PageShell } from "@/components/page-shell"

export const metadata = { title: "Page not found" }

export default function NotFound() {
  return (
    <PageShell>
      <h1 className="text-3xl font-bold md:text-5xl">Page not found</h1>
      <p className="prose-report mt-6">That address does not exist on this site.</p>
      <p className="mt-6"><Link href="/" className="link-arrow">Back to the research</Link></p>
    </PageShell>
  )
}
