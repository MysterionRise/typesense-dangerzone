/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow images from picsum
  images: {
    domains: ['picsum.photos'],
  },
  // Environment variables available to browser
  env: {
    NEXT_PUBLIC_TYPESENSE_HOST: process.env.NEXT_PUBLIC_TYPESENSE_HOST || 'localhost',
    NEXT_PUBLIC_TYPESENSE_PORT: process.env.NEXT_PUBLIC_TYPESENSE_PORT || '8108',
    NEXT_PUBLIC_TYPESENSE_PROTOCOL: process.env.NEXT_PUBLIC_TYPESENSE_PROTOCOL || 'http',
    NEXT_PUBLIC_TYPESENSE_SEARCH_ONLY_API_KEY: process.env.NEXT_PUBLIC_TYPESENSE_SEARCH_ONLY_API_KEY || 'xyz123_demo_key_change_in_production',
  },
}

module.exports = nextConfig
