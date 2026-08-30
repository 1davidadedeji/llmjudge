#!/usr/bin/env ts-node
/**
 * page.tsx --- per-repo drill-down view
 *
 * Contains:
 *   RepoPage: renders one repo's runs and metric breakdown
 */

import DrillDownTable from "../../../components/DrillDownTable";
import MetricBreakdown from "../../../components/MetricBreakdown";
import { sortNewestFirst } from "../../../lib/repos";
import RepoHeader from "../../../components/RepoHeader";
import { fetchRuns } from "../../../lib/api";

export default async function RepoPage({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const runs = await fetchRuns(name);
  const sorted = sortNewestFirst(runs);
  return (
    <section>
      <RepoHeader name={name} runCount={runs.length} />
      <MetricBreakdown scores={{}} />
      <DrillDownTable runs={sorted} />
    </section>
  );
}
