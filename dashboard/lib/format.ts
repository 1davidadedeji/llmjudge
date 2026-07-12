#!/usr/bin/env ts-node
/**
 * format.ts --- display formatting helpers for the dashboard
 *
 * Contains:
 *   formatScore: renders a 0-1 score as a percentage string
 *   formatTimestamp: renders an ISO timestamp for display
 */

/**
 * Renders a 0-1 score as a percentage string.
 *
 * @param score - Metric score in [0, 1].
 * @returns text - Percentage with one decimal.
 */
export function formatScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

/**
 * Renders an ISO timestamp for display.
 *
 * @param iso - ISO-8601 timestamp string.
 * @returns text - Locale date-time string.
 */
export function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString();
}

/**
 * Truncates long run ids for compact table cells.
 *
 * @param runId - Full run identifier.
 * @param length - Maximum characters to keep.
 * @returns text - Truncated id with an ellipsis when shortened.
 */
export function truncateRunId(runId: string, length = 12): string {
  return runId.length <= length ? runId : `${runId.slice(0, length)}…`;
}

/**
 * Renders a delta with an explicit sign.
 *
 * @param delta - Score delta between two runs.
 * @returns text - Signed percentage string.
 */
export function formatDelta(delta: number): string {
  const sign = delta > 0 ? "+" : "-";
  return `${sign}${Math.abs(delta * 100).toFixed(1)}%`;
}
