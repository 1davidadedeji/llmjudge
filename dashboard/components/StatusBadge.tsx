#!/usr/bin/env ts-node
/**
 * StatusBadge.tsx --- colored badge for run status
 *
 * Contains:
 *   StatusBadge: renders a run status with color coding
 */

const STATUS_COLORS: Record<string, string> = {
  queued: "#9e9e9e",
  running: "#4c9aff",
  succeeded: "#3fb950",
  failed: "#f85149",
};

/**
 * Renders a run status with color coding.
 *
 * @param props.status - Run status string.
 * @returns badge - Colored status badge element.
 */
export default function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? "#9e9e9e";
  return (
    <span className="status-badge" style={{ backgroundColor: color }}>
      {status}
    </span>
  );
}
