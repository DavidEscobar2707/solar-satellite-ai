/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'maps.googleapis.com',
      },
      {
        protocol: 'https',
        hostname: '**.googleapis.com',
      },
    ],
  },
  env: {
    // In production (Vercel), use relative URLs since backend is on same domain
    // In development, use localhost:8000
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000'),
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
  },
}

module.exports = nextConfig

