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
}: {
  points: TrendPoint[];
  threshold: number;
}) {
  return (
    <div className="trend-chart">
      {points.map((point, index) => (
        <div
          key={index}
          className={point.score >= threshold ? "bar bar-pass" : "bar bar-fail"}
          style={{ height: `${point.score * 100}%` }}
          title={formatScore(point.score)}
        />
      ))}
    </div>
  );
}
