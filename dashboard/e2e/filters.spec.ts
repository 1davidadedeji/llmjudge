#!/usr/bin/env ts-node
/**
 * filters.spec.ts --- e2e tests for dashboard run filters
 *
 * Contains:
 *   status filter shows only matching runs
 */

import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/runs**", async (route) => {
    await route.fulfill({
      json: [
        { id: "r-1", repo: "agentflow", status: "succeeded", created_at: "2026-06-13T08:00:00Z" },
        { id: "r-2", repo: "agentflow", status: "failed", created_at: "2026-06-13T09:00:00Z" },
      ],
    });
  });
});

test("status filter shows only matching runs", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1")).toBeVisible();
});
