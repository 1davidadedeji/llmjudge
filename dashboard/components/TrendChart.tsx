#!/usr/bin/env ts-node
/**
 * TrendChart.tsx --- regression trend chart for one metric
 *
 * Contains:
 *   TrendChart: renders score history as an inline bar chart
 */

import { formatScore } from "../lib/format";

export interface TrendPoint {
  created_at: string;
  score: number;
}

/**
 * Renders score history as an inline bar chart.
 *
 * @param props.points - Score points oldest-first.
 * @param props.threshold - Pass threshold rendered as a guide.
 * @returns chart - Trend chart element.
 */
export default function TrendChart({
  points,
  threshold,
  height = 8,
}: {
  points: TrendPoint[];
  threshold: number;
  height?: number;
}) {
  return (
    <div className="trend-chart" style={{ height: `${height}rem` }}>
      {points.map((point, index) => (
        <div
          key={index}
          className={point.score >= threshold ? "bar bar-pass" : "bar bar-fail"}
          style={{ height: `${point.score * 100}%` }}
          title={`${point.created_at}: ${formatScore(point.score)}`}
        />
      ))}
    </div>
  );
}

/**
 * Renders the pass/fail legend under a trend chart.
 *
 * @returns legend - Legend element.
 */
export function TrendLegend() {
  return (
    <div className="trend-legend">
      <span className="bar bar-pass" /> at/above threshold
      <span className="bar bar-fail" /> below threshold
    </div>
  );
}
