#!/usr/bin/env ts-node
/**
 * page.tsx --- trend view: metric score history per repo
 *
 * Contains:
 *   TrendsPage: renders trend charts for the latest runs
 */

import TrendChart from "../../components/TrendChart";

const points: { created_at: string; score: number }[] = [];

export default function TrendsPage() {
  return (
    <section>
      <h2>Regression trends</h2>
      <p>Newest {points.length} runs</p>
      <TrendChart points={points} threshold={0.8} />
    </section>
  );
}
