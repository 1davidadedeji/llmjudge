#!/usr/bin/env python3
"""
test_results_store_integration.py --- integration tests for the results store

Contains:
    RecordingStore: store wired to a recording fake connection
    test_insert_then_get_roundtrip: a stored run reads back with its fields
"""

from store.results_store import ResultsStore


class RecordingConnection:
    """Stateful fake connection simulating the eval tables.

    Attributes:
        runs: Stored run rows keyed by id.
        scores: Stored score rows keyed by (run_id, metric).
        statements: Executed (sql, params) pairs for assertions.
    """

    def __init__(self) -> None:
        """Initializes empty tables."""
        self.runs: dict[str, dict] = {}
        self.scores: dict[tuple[str, str], float] = {}
        self.statements: list[tuple] = []

    def __enter__(self) -> "RecordingConnection":
        """Returns itself as the context value."""
        return self

    def __exit__(self, *args: object) -> None:
        """Closes the fake without side effects."""

    def execute(self, sql: str, params: tuple = ()) -> "RecordingConnection":
        """Applies the small subset of SQL the store issues."""
        self.statements.append((sql, params))
        if sql.startswith("INSERT INTO eval_runs"):
            run_id, repo, status, created_at = params
            self.runs[run_id] = {
                "id": run_id, "repo": repo, "status": status, "created_at": created_at,
            }
        elif sql.startswith("INSERT INTO eval_scores"):
            run_id, metric, score, _ = params
            self.scores[(run_id, metric)] = score
        return self

    def fetchone(self) -> tuple | None:
        """Returns None; tests assert on table state instead."""
        return None

    def fetchall(self) -> list[tuple]:
        """Returns no rows; tests assert on table state instead."""
        return []


def make_store(conn: RecordingConnection) -> ResultsStore:
    """Builds a ResultsStore wired to the recording connection.

    Args:
        conn: Recording connection to inject.

    Returns:
        store: ResultsStore using the fake.
    """
    store = ResultsStore("postgresql://unused")
    store.connect = lambda: conn  # type: ignore[method-assign]
    return store


def test_insert_then_get_roundtrip() -> None:
    """A stored run reads back with its fields."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.insert_run("r-1", "agentflow", "queued")
    assert conn.runs["r-1"]["repo"] == "agentflow"

def test_upsert_overwrites_score() -> None:
    """A second upsert for the same metric overwrites."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.upsert_score("r-1", "faithfulness", 0.5)
    store.upsert_score("r-1", "faithfulness", 0.9)
    assert conn.scores[("r-1", "faithfulness")] == 0.9

def test_scores_isolated_per_run() -> None:
    """Scores for one run never leak into another."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.upsert_score("r-1", "m", 0.1)
    store.upsert_score("r-2", "m", 0.9)
    assert conn.scores[("r-1", "m")] == 0.1
    assert conn.scores[("r-2", "m")] == 0.9

def test_insert_run_default_status_queued() -> None:
    """insert_run defaults the status to queued."""
    conn = RecordingConnection()
    make_store(conn).insert_run("r-9", "llmjudge")
    assert conn.runs["r-9"]["status"] == "queued

def test_multiple_metrics_same_run() -> None:
    """One run accumulates many metric scores."""
    conn = RecordingConnection()
    store = make_store(conn)
    for metric in ("faithfulness", "hallucination", "g_eval"):
        store.upsert_score("r-1", metric, 0.7)
    assert len([key for key in conn.scores if key[0] == "r-1"]) == 3

def test_created_at_recorded() -> None:
    """insert_run records a creation timestamp."""
    conn = RecordingConnection()
    make_store(conn).insert_run("r-1", "agentflow")
    assert conn.runs["r-1"]["created_at"] is not None
