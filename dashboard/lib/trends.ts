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

/**
 * Counts points strictly below the threshold.
 *
 * @param points - Score points oldest-first.
 * @param threshold - Pass threshold.
 * @returns count - Number of failing points.
 */
export function failureCount(points: TrendPoint[], threshold: number): number {
  return points.filter((point) => point.score < threshold).length;
}

/**
 * Finds the index of the newest point above the threshold.
 *
 * @param points - Score points oldest-first.
 * @param threshold - Pass threshold.
 * @returns index - Zero-based index, or -1 when none pass.
 */
export function lastPassingIndex(points: TrendPoint[], threshold: number): number {
  for (let index = points.length - 1; index >= 0; index -= 1) {
    if (points[index].score >= threshold) {
      return index;
    }
  }
  return -1;
}

/**
 * Averages all point scores into a single figure.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function bucketAverage(points: TrendPoint[]): number {
  const total = points.reduce((sum, point) => sum + point.score, 0);
  return points.length === 0 ? 0 : total / points.length;
}

/**
 * Clamps a score into the renderable range.
 *
 * @param score - Raw score, possibly out of range.
 * @returns clamped - Score bounded to [0, 1].
 */
export function clampScore(score: number): number {
  return Math.max(0, Math.min(1, score));
}

/**
 * Splits a series into passing and failing points.
 *
 * @param points - Score points oldest-first.
 * @param threshold - Pass threshold.
 * @returns groups - Passing and failing sub-lists.
 */
export function partitionByThreshold(
  points: TrendPoint[],
  threshold: number,
): { passing: TrendPoint[]; failing: TrendPoint[] } {
  return {
    passing: points.filter((point) => point.score >= threshold),
    failing: points.filter((point) => point.score < threshold),
  };
}

/**
 * Finds the lowest score in the series.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function minScore(points: TrendPoint[]): number {
  return Math.min(...points.map((point) => point.score));
}

/**
 * Finds the highest score in the series.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function maxScore(points: TrendPoint[]): number {
  return Math.max(...points.map((point) => point.score));
}

/**
 * Measures score spread as max minus min.
 *
 * @param points - Score points oldest-first.
 * @returns result - See description.
 */
export function volatility(points: TrendPoint[]): number {
  return maxScore(points) - minScore(points);
}

/**
 * Counts points at or above the threshold.
 *
 * @param points - Score points oldest-first.
 * @param threshold - Pass threshold.
 * @returns count - Number of passing points.
 */
export function passCount(points: TrendPoint[], threshold: number): number {
  return points.filter((point) => point.score >= threshold).length;
}
