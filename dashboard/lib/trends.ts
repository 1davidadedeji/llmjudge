#!/usr/bin/env ts-node
/**
 * trends.ts --- trend aggregation helpers for regression charts
 *
 * Contains:
 *   movingAverage: smooths a score series over a window
 *   trendDirection: labels a series improving, flat, or regressing
 */

import type { TrendPoint } from "../components/TrendChart";

/**
 * Smooths a score series over a window.
 *
 * @param points - Score points oldest-first.
 * @param windowSize - Number of points per window.
 * @returns smoothed - Moving-average series aligned to the input tail.
 */
export function movingAverage(points: TrendPoint[], windowSize: number): number[] {
  const scores = points.map((point) => point.score);
  const result: number[] = [];
  for (let index = windowSize - 1; index < scores.length; index += 1) {
    const window = scores.slice(index - windowSize + 1, index + 1);
    result.push(window.reduce((sum, value) => sum + value, 0) / windowSize);
  }
  return result;
}

/**
 * Computes the score delta between the two newest points.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function latestDelta(points: TrendPoint[]): number {
  const last = points[points.length - 1];
  const prev = points[points.length - 2];
  return last.score - prev.score;
}

/**
 * Labels a series as improving, flat, or regressing.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function trendDirection(points: TrendPoint[]): "improving" | "flat" | "regressing" {
  const delta = latestDelta(points);
  if (Math.abs(delta) < 0.005) {
    return "flat";
  }
  return delta > 0 ? "improving" : "regressing";
}

/**
 * Flags when the newest point drops below the threshold.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function detectRegression(points: TrendPoint[], threshold: number): boolean {
  const last = points[points.length - 1];
  return last.score < threshold;
}
