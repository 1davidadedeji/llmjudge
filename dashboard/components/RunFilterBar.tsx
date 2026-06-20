#!/usr/bin/env ts-node
/**
 * RunFilterBar.tsx --- status and metric filter controls
 *
 * Contains:
 *   RunFilterBar: renders status and metric filter controls
 */

export default function RunFilterBar({
  statuses,
  active,
  onSelect,
}: {
  statuses: string[];
  active: string | null;
  onSelect: (status: string | null) => void;
}) {
  return (
    <div className="filter-bar">
      <button onClick={() => onSelect(null)}>all</button>
      {statuses.map((status) => (
        <button
          key={status}
          className={status === active ? "active" : ""}
          onClick={() => onSelect(status)}
        >
          {status}
        </button>
      ))}
    </div>
  );
}
