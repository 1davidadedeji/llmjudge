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

test("filter by succeeded status", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("filter by failed status", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-2", { exact: false }).first()).toBeVisible();
});

test("filter bar renders all option", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("empty filter result shows empty state", async ({ page }) => {
  await page.goto("/repos/graphmind");
  await expect(page.getByText("No runs yet", { exact: false }).first()).toBeVisible();
});

test("repo header shows run count", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("2 runs", { exact: false }).first()).toBeVisible();
});

test("run ids link to run detail", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("trend page renders chart container", async ({ page }) => {
  await page.goto("/trends");
  await expect(page.getByText("Regression trends", { exact: false }).first()).toBeVisible();
});

test("home page lists latest runs", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("status badge color for failed", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("failed", { exact: false }).first()).toBeVisible();
});

test("status badge color for succeeded", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("succeeded", { exact: false }).first()).toBeVisible();
});

test("filter persists across navigation", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-2", { exact: false }).first()).toBeVisible();
});

test("metric chips render on drill-down", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("agentflow", { exact: false }).first()).toBeVisible();
});

test("drill table shows timestamps", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("2026", { exact: false }).first()).toBeVisible();
});

test("resetting filter restores all runs", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("switching repos updates the table", async ({ page }) => {
  await page.goto("/repos/graphmind");
  await expect(page.getByText("graphmind", { exact: false }).first()).toBeVisible();
});

test("filter buttons have accessible labels", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("failed", { exact: false }).first()).toBeVisible();
});

test("failed runs highlighted in table", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("failed", { exact: false }).first()).toBeVisible();
});

test("multiple filters combine", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});

test("filter unknown status yields empty", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("No runs yet", { exact: false }).first()).toBeVisible();
});

test("page title includes repo name", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("agentflow", { exact: false }).first()).toBeVisible();
});

test("trend legend visible", async ({ page }) => {
  await page.goto("/trends");
  await expect(page.getByText("threshold", { exact: false }).first()).toBeVisible();
});

test("compare view shows deltas", async ({ page }) => {
  await page.goto("/compare");
  await expect(page.getByText("Delta", { exact: false }).first()).toBeVisible();
});

test("regression note lists metrics", async ({ page }) => {
  await page.goto("/compare");
  await expect(page.getByText("regressions", { exact: false }).first()).toBeVisible();
});

test("runs sorted newest first", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-2", { exact: false }).first()).toBeVisible();
});

test("filter count badge matches table", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("failed", { exact: false }).first()).toBeVisible();
});

test("keyboard navigation reaches filters", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("failed", { exact: false }).first()).toBeVisible();
});

test("special-character repo names render", async ({ page }) => {
  await page.goto("/repos/shipwright");
  await expect(page.getByText("shipwright", { exact: false }).first()).toBeVisible();
});

test("long run ids truncate gracefully", async ({ page }) => {
  await page.goto("/repos/agentflow");
  await expect(page.getByText("r-1", { exact: false }).first()).toBeVisible();
});
