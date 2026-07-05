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
