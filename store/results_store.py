#!/usr/bin/env python3
"""
results_store.py --- Postgres-backed store for eval runs and metric scores

Contains:
    ResultsStore: persists runs and scores
    ResultsStore.insert_run(): records a new eval run
    ResultsStore.upsert_score(): writes one metric score for a run
    ResultsStore.get_run(): fetches one run with its scores
"""

from datetime import datetime, timezone

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

    def connect(self) -> psycopg.Connection:
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
                " SET score = EXCLUDED.score, updated_at = EXCLUDED.updated_at",
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
            "finished_at": ensure_utc(row[4]) if row[4] is not None else None,
            "scores": {metric: score for metric, score in score_rows},
        }

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
    """Coerces a timestamp to timezone-aware UTC.

    Args:
        value: Timestamp from the database, possibly naive.

    Returns:
        aware: Timezone-aware UTC timestamp.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
