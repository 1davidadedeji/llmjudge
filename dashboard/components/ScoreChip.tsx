#!/usr/bin/env ts-node
/**
 * ScoreChip.tsx --- small chip showing one metric score
 *
 * Contains:
 *   ScoreChip: renders a metric name and formatted score
 */

import { formatScore } from "../lib/format";

/**
 * Renders a metric name and formatted score.
 *
 * @param props.name - Metric name.
 * @param props.score - Metric score in [0, 1].
 * @returns chip - Score chip element.
 */
export default function ScoreChip({ name, score }: { name: string; score: number }) {
  return (
    <span className="score-chip">
      {name}: {formatScore(score)}
    </span>
  );
}
