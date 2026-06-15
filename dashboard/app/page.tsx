#!/usr/bin/env ts-node
/**
 * page.tsx --- dashboard home: latest runs across repos
 *
 * Contains:
 *   HomePage: lists the most recent eval runs
 */

import RunTable from "../components/RunTable";
import { fetchRuns } from "../lib/api";

export default async function HomePage() {
  const runs = await fetchRuns();
  return (
    <section>
      <h2>Latest eval runs</h2>
      <RunTable runs={runs} />
    </section>
  );
}
