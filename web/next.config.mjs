/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Lets a production build for testing live beside `next dev` (NEXT_DIST_DIR=.next-verify npm run build).
  distDir: process.env.NEXT_DIST_DIR || ".next",
}

export default nextConfig
