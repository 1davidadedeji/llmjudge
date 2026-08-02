#!/usr/bin/env ts-node
/**
 * RunTable.tsx --- table of recent eval runs
 *
 * Contains:
 *   RunTable: renders run summaries in a table
 */

import type { RunSummary } from "../lib/api";
import EmptyState from "./EmptyState";
import StatusBadge from "./StatusBadge";

/**
 * Renders run summaries in a table.
 *
 * @param props.runs - Run summaries to render.
 * @returns table - Runs table element.
 */
export default function RunTable({ runs }: { runs: RunSummary[] }) {
  if (runs.length === 0) {
    return <EmptyState message="No runs yet" />;
  }
  return (
    <table className="run-table">
      <thead>
        <tr>
          <th>Run</th>
          <th>Repo</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => (
          <tr key={run.id}>
            <td>{run.id}</td>
            <td>{run.repo}</td>
            <td>
              <StatusBadge status={run.status} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
