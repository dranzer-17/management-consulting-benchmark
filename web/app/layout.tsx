import type { Metadata, Viewport } from "next"
import "@fontsource-variable/space-grotesk"
import "@fontsource-variable/dm-sans"
import type { ReactNode } from "react"
import { SideRail } from "@/components/side-rail"
import { ThemeProvider } from "@/components/theme-provider"
import { BASE_PATH } from "@/lib/site"
import "./globals.css"

const SITE = "https://big-3-analysis.kavish.tech"

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: { default: "Kavish Shah | Research", template: "%s | Kavish Shah | Research" },
  description:
    "Independent, data-driven research built only from public sources. Not affiliated with, or endorsed by, any firm it studies.",
  alternates: { canonical: `${BASE_PATH}` },
  openGraph: { title: "Kavish Shah | Research", url: `${SITE}${BASE_PATH}`, siteName: "Kavish Shah | Research", type: "website" },
}

export const viewport: Viewport = { width: "device-width", initialScale: 1 }

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
          <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded focus:bg-foreground focus:px-3 focus:py-2 focus:text-background">
            Skip to content
          </a>
          <SideRail />
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
