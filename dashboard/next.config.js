#!/usr/bin/env node
/**
 * next.config.js --- Next.js configuration for the llmjudge dashboard
 *
 * Contains:
 *   nextConfig: static export settings and API rewrites
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
