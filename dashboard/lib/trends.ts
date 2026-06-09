#!/usr/bin/env ts-node
/**
 * trends.ts --- trend aggregation helpers for regression charts
 *
 * Contains:
 *   movingAverage: smooths a score series over a window
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
