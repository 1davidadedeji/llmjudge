#!/usr/bin/env ts-node
/**
 * page.tsx --- trend view: metric score history per repo
 *
 * Contains:
 *   TrendsPage: renders trend charts for the latest runs
 */

import TrendChart from "../../components/TrendChart";

export default function TrendsPage() {
  return (
    <section>
      <h2>Regression trends</h2>
      <TrendChart points={points} threshold={0.8} />
    </section>
  );
}
