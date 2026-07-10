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

/**
 * Filters runs to those created on or after a date.
 *
 * @param runs - Runs to filter.
 * @param sinceIso - ISO date lower bound.
 * @returns filtered - Runs created at or after the bound.
 */
export function sinceDate(runs: RunSummary[], sinceIso: string): RunSummary[] {
  return runs.filter((run) => run.created_at >= sinceIso);
}

/**
 * Filters runs to those created before a date.
 *
 * @param runs - Runs to filter.
 * @param untilIso - ISO date upper bound.
 * @returns filtered - Runs created before the bound.
 */
export function untilDate(runs: RunSummary[], untilIso: string): RunSummary[] {
  return runs.filter((run) => run.created_at < untilIso);
}

/**
 * Chains status and date filters into one pass.
 *
 * @param runs - Runs to filter.
 * @param status - Status to keep; null keeps everything.
 * @param sinceIso - Optional ISO lower bound.
 * @returns filtered - Runs matching every active filter.
 */
export function applyFilters(
  runs: RunSummary[],
  status: string | null,
  sinceIso?: string,
): RunSummary[] {
  let filtered = filterByStatus(runs, status);
  if (sinceIso) {
    filtered = sinceDate(filtered, sinceIso);
  }
  return filtered;
}

/**
 * Lists the distinct statuses present in a run list.
 *
 * @param runs - Runs to inspect.
 * @returns statuses - Sorted distinct status strings.
 */
export function statusesOf(runs: RunSummary[]): string[] {
  return [...new Set(runs.map((run) => run.status))].sort();
}

/**
 * Counts runs created per calendar day.
 *
 * @param runs - Runs to bucket.
 * @returns counts - Mapping of ISO date to run count.
 */
export function runsPerDay(runs: RunSummary[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const run of runs) {
    const day = run.created_at.slice(0, 10);
    counts[day] = (counts[day] ?? 0) + 1;
  }
  return counts;
}
