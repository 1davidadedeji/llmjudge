#!/usr/bin/env ts-node
/**
 * repos.ts --- helpers for the per-repo drill-down view
 *
 * Contains:
 *   REPOS: repos tracked by the dashboard
 *   filterByStatus: filters runs by status
 */

import type { RunSummary } from "./api";

export const REPOS = ["retrieval-core", "agentflow", "graphmind", "llmjudge", "shipwright"];

/**
 * Filters runs by status.
 *
 * @param runs - Runs to filter.
 * @param status - Status to keep; null keeps everything.
 * @returns filtered - Runs matching the status.
 */
export function filterByStatus(runs: RunSummary[], status: string | null): RunSummary[] {
  if (status === null) {
    return runs;
  }
  return runs.filter((run) => run.status === status);
}
