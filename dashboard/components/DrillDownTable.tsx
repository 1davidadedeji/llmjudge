#!/usr/bin/env ts-node
/**
 * DrillDownTable.tsx --- runs table for the drill-down view
 *
 * Contains:
 *   DrillDownTable: renders runs table for the drill-down view
 */

import type { RunSummary } from "../lib/api";
import StatusBadge from "./StatusBadge";

export default function DrillDownTable({ runs }: { runs: RunSummary[] }) {
  return (
    <table className="drill-table">
      <tbody>
        {runs.map((run) => (
          <tr key={run.id}>
            <td>{run.id}</td>
            <td>
              <StatusBadge status={run.status} />
            </td>
            <td>{run.created_at}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
