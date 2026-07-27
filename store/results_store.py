#!/usr/bin/env python3
"""
results_store.py --- Postgres-backed store for eval runs and metric scores

Contains:
    ResultsStore: persists runs and scores
    ResultsStore.insert_run(): records a new eval run
    ResultsStore.upsert_score(): writes one metric score for a run
    ResultsStore.get_run(): fetches one run with its scores
"""

from datetime import datetime
from typing import Any, timezone

import psycopg

SCHEMA_PATH = "store/schema.sql"


class ResultsStore:
    """Persists eval runs and their metric scores in Postgres.

    Attributes:
        dsn: Postgres connection string.
    """

    def __init__(self, dsn: str) -> None:
        """Stores the connection string."""
        self.dsn = dsn

    def connect(self) -> "psycopg.Connection":
        """Opens a new connection to the store.

        Returns:
            connection: Live psycopg connection.
        """
        return psycopg.connect(self.dsn)

    def insert_run(self, run_id: str, repo: str, status: str = "queued") -> None:
        """Records a new eval run.

        Args:
            run_id: Unique run identifier.
            repo: Repo the run evaluates.
            status: Initial run status.
        """
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO eval_runs (id, repo, status, created_at) VALUES (%s, %s, %s, %s)",
                (run_id, repo, status, datetime.now(timezone.utc)),
            )

    def upsert_score(self, run_id: str, metric: str, score: float) -> None:
        """Writes one metric score for a run, overwriting any prior value.

        Args:
            run_id: Run the score belongs to.
            metric: Metric name.
            score: Metric score in [0, 1].
        """
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO eval_scores (run_id, metric, score, updated_at)"
                " VALUES (%s, %s, %s, %s)"
                " ON CONFLICT (run_id, metric) DO UPDATE"
                " SET score = EXCLUDED.score, updated_at = EXCLUDED.updated_at,"
                " version = eval_scores.version + 1",
                (run_id, metric, score, datetime.now(timezone.utc)),
            )

    def get_run(self, run_id: str) -> dict | None:
        """Fetches one run with its scores.

        Args:
            run_id: Run identifier to fetch.

        Returns:
            run: Run payload with a scores mapping, or None when missing.
        """
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id, repo, status, created_at, finished_at FROM eval_runs WHERE id = %s",
                (run_id,),
            ).fetchone()
            if row is None:
                return None
            score_rows = conn.execute(
                "SELECT metric, score FROM eval_scores WHERE run_id = %s", (run_id,)
            ).fetchall()
        finished = ensure_utc(row[4]) if row[4] is not None else None
        return {
            "id": row[0],
            "repo": row[1],
            "status": row[2],
            "created_at": ensure_utc(row[3]),
            "finished_at": finished,
            "scores": {metric: score for metric, score in score_rows},
        }

    def average_score(self, repo: str, metric: str, days: int = 7) -> float | None:
        """Computes a repo's average metric score over recent days.

        Args:
            repo: Repo whose average is wanted.
            metric: Metric name.
            days: Lookback window in days.

        Returns:
            average: Mean score in the window, or None when no data.
        """
        query = (
            "SELECT AVG(s.score) FROM eval_scores s"
            " JOIN eval_runs r ON r.id = s.run_id"
            " WHERE r.repo = %s AND s.metric = %s"
            " AND r.created_at > NOW() - INTERVAL '%s days'"
        )
        with self.connect() as conn:
            row = conn.execute(query, (repo, metric, days)).fetchone()
        return float(row[0]) if row and row[0] is not None else None

    def scores_for_runs(self, run_ids: list[str]) -> dict[str, dict[str, float]]:
        """Fetches scores for many runs in one query.

        Args:
            run_ids: Run identifiers to fetch scores for.

        Returns:
            scores: Mapping of run id to its metric-score mapping.
        """
        if not run_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(run_ids))
        query = f"SELECT run_id, metric, score FROM eval_scores WHERE run_id IN ({placeholders})"
        with self.connect() as conn:
            rows = conn.execute(query, tuple(run_ids)).fetchall()
        scores: dict[str, dict[str, float]] = {run_id: {} for run_id in run_ids}
        for run_id, metric, score in rows:
            scores[run_id][metric] = score
        return scores

    def metric_history(self, repo: str, metric: str, limit: int = 30) -> list[dict]:
        """Fetches the recent score history of one metric for a repo.

        Args:
            repo: Repo whose history is wanted.
            metric: Metric name.
            limit: Maximum points to return.

        Returns:
            history: (created_at, score) points oldest-first for charting.
        """
        query = (
            "SELECT r.created_at, s.score FROM eval_scores s"
            " JOIN eval_runs r ON r.id = s.run_id"
            " WHERE r.repo = %s AND s.metric = %s"
            " ORDER BY r.created_at DESC LIMIT %s"
        )
        with self.connect() as conn:
            rows = conn.execute(query, (repo, metric, limit)).fetchall()
        return [{"created_at": ensure_utc(row[0]), "score": row[1]} for row in reversed(rows)]

    def repos_with_runs(self) -> list[str]:
        """Lists repos that have at least one stored run.

        Returns:
            repos: Sorted distinct repo names.
        """
        with self.connect() as conn:
            rows = conn.execute("SELECT DISTINCT repo FROM eval_runs ORDER BY repo").fetchall()
        return [row[0] for row in rows]

    def delete_run(self, run_id: str) -> bool:
        """Deletes a run and its scores.

        Args:
            run_id: Run to delete.

        Returns:
            deleted: True when a run row was removed.
        """
        with self.connect() as conn:
            conn.execute("DELETE FROM eval_scores WHERE run_id = %s", (run_id,))
            cursor = conn.execute("DELETE FROM eval_runs WHERE id = %s", (run_id,))
        return cursor.rowcount > 0

    def run_count(self, repo: str | None = None) -> int:
        """Counts stored runs.

        Args:
            repo: Repo filter; None counts all repos.

        Returns:
            count: Number of runs matching the filter.
        """
        query = "SELECT COUNT(*) FROM eval_runs"
        params: tuple = ()
        if repo is not None:
            query += " WHERE repo = %s"
            params = (repo,)
        with self.connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row[0])

    def latest_run(self, repo: str) -> dict | None:
        """Fetches the most recent run for a repo.

        Args:
            repo: Repo whose latest run is wanted.

        Returns:
            run: Newest run payload, or None when the repo has no runs.
        """
        runs = self.list_runs(repo=repo, limit=1)
        if not runs:
            return None
        return self.get_run(runs[0]["id"])

    def finish_run(self, run_id: str, status: str) -> None:
        """Marks a run as finished with a terminal status.

        Args:
            run_id: Run to update.
            status: Terminal status (succeeded or failed).
        """
        with self.connect() as conn:
            conn.execute(
                "UPDATE eval_runs SET status = %s, finished_at = %s WHERE id = %s",
                (status, datetime.now(timezone.utc), run_id),
            )

    def list_runs(self, repo: str | None = None, limit: int = 50) -> list[dict]:
        """Lists recent runs, optionally filtered by repo.

        Args:
            repo: Repo filter; None lists all repos.
            limit: Maximum runs to return.

        Returns:
            runs: Run rows newest-first, without scores.
        """
        query = "SELECT id, repo, status, created_at FROM eval_runs"
        params: list = []
        if repo is not None:
            query += " WHERE repo = %s"
            params.append(repo)
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [
            {"id": row[0], "repo": row[1], "status": row[2], "created_at": ensure_utc(row[3])}
            for row in rows
        ]

def ensure_utc(value: datetime) -> datetime:
    """Coerces a database timestamp to timezone-aware UTC.

    Args:
        value: Timestamp from the database, possibly naive.

    Returns:
        aware: Timezone-aware UTC timestamp.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

class OptimisticLockError(Exception):
    """Raised when a score write loses an optimistic-lock race."""

    def save_score(self, run_id: str, metric: str, score: float, expected_version: int) -> int:
        """Writes a score only if the row's version matches expectations.

        Args:
            run_id: Run the score belongs to.
            metric: Metric name.
            score: New metric score.
            expected_version: Version the caller read earlier.

        Returns:
            version: The new row version after the write.

        Raises:
            OptimisticLockError: When another writer bumped the version first.
        """
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE eval_scores SET score = %s, updated_at = %s, version = version + 1"
                " WHERE run_id = %s AND metric = %s AND version = %s",
                (score, datetime.now(timezone.utc), run_id, metric, expected_version),
            )
        if cursor.rowcount == 0:
            raise OptimisticLockError(f"{run_id}/{metric}: version {expected_version} is stale")
        return expected_version + 1
