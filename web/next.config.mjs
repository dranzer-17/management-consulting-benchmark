// The whole site lives under this path: research.kavish.tech/mbb (so the root stays free for other projects).
const BASE = "/mbb"

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  basePath: BASE,
  env: { NEXT_PUBLIC_BASE_PATH: BASE },
  async redirects() {
    return [
      { source: "/", destination: BASE, permanent: false, basePath: false },
      { source: "/benchmarks", destination: "/research", permanent: true },
      { source: "/benchmarks/mckinsey-vs-bcg-vs-bain", destination: "/research", permanent: true },
    ]
  },
  // Lets a production build for testing live beside `next dev` (NEXT_DIST_DIR=.next-verify npm run build).
  distDir: process.env.NEXT_DIST_DIR || ".next",
}

export default nextConfig
