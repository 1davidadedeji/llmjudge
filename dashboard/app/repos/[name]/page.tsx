#!/usr/bin/env ts-node
/**
 * page.tsx --- per-repo drill-down view
 *
 * Contains:
 *   RepoPage: renders one repo's runs and metric breakdown
 */

import DrillDownTable from "../../../components/DrillDownTable";
import RepoHeader from "../../../components/RepoHeader";
import { fetchRuns } from "../../../lib/api";

export default async function RepoPage({ params }: { params: { name: string } }) {
  const runs = await fetchRuns(params.name);
  const sorted = sortNewestFirst(runs);
  return (
    <section>
      <RepoHeader name={params.name} runCount={runs.length} />
      <DrillDownTable runs={sorted} />
    </section>
  );
}
