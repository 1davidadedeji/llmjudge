#!/usr/bin/env ts-node
/**
 * MetricBreakdown.tsx --- per-metric latest scores for one repo
 *
 * Contains:
 *   MetricBreakdown: renders per-metric latest scores for one repo
 */

import ScoreChip from "./ScoreChip";

export default function MetricBreakdown({ scores }: { scores: Record<string, number> }) {
  return (
    <div className="metric-breakdown">
      {Object.entries(scores).map(([name, score]) => (
        <ScoreChip key={name} name={name} score={score} />
      ))}
    </div>
  );
}
