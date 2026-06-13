#!/usr/bin/env ts-node
/**
 * playwright.config.ts --- e2e test configuration for the dashboard
 *
 * Contains:
 *   config: Playwright projects and web server settings
 */

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: "http://localhost:3000",
  },
  webServer: {
    command: "npm run dev",
    port: 3000,
    reuseExistingServer: true,
  },
});
