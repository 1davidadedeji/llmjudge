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
        return {
            "id": row[0],
            "repo": row[1],
            "status": row[2],
            "created_at": row[3],
            "finished_at": row[4],
            "scores": {metric: score for metric, score in score_rows},
        }
