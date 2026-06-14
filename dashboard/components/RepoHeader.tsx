#!/usr/bin/env ts-node
/**
 * RepoHeader.tsx --- repo name, run count, and latest status
 *
 * Contains:
 *   RepoHeader: renders repo name, run count, and latest status
 */

export default function RepoHeader({ name, runCount }: { name: string; runCount: number }) {
  return (
    <header className="repo-header">
      <h2>{name}</h2>
      <span>{runCount} runs</span>
    </header>
  );
}
