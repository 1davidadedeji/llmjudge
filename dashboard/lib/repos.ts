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

/**
 * Counts runs per status for the filter bar badges.
 *
 * @param runs - Runs to count.
 * @returns counts - Mapping of status to run count.
 */
export function countByStatus(runs: RunSummary[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const run of runs) {
    counts[run.status] = (counts[run.status] ?? 0) + 1;
  }
  return counts;
}
