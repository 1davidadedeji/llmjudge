#!/usr/bin/env ts-node
/**
 * page.tsx --- per-repo drill-down view
 *
 * Contains:
 *   RepoPage: renders one repo's runs and metric breakdown
 */

import { fetchRuns } from "../../../lib/api";

export default async function RepoPage({ params }: { params: { name: string } }) {
  const runs = await fetchRuns(params.name);
  return (
    <section>
      <RepoHeader name={params.name} runCount={runs.length} />
    </section>
  );
}
