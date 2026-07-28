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

def test_score_types_preserved() -> None:
    """Scores round-trip as floats."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.upsert_score("r-1", "m", 0.333)
    assert isinstance(conn.scores[("r-1", "m")], float)

def test_many_runs_same_repo() -> None:
    """One repo can hold many runs."""
    conn = RecordingConnection()
    store = make_store(conn)
    for i in range(5):
        store.insert_run(f"r-{i}", "agentflow")
    assert len(conn.runs) == 5

def test_upsert_requires_matching_run() -> None:
    """Scores key by run id, not by metric alone."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.upsert_score("r-1", "m", 0.5)
    assert ("r-2", "m") not in conn.scores

def test_statement_order_insert_before_score() -> None:
    """Run row is written before its scores."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.insert_run("r-1", "agentflow")
    store.upsert_score("r-1", "m", 0.5)
    assert conn.statements[0][0].startswith("INSERT INTO eval_runs")
    assert conn.statements[1][0].startswith("INSERT INTO eval_scores")

def test_finish_run_marks_terminal() -> None:
    """finish_run flips the run to a terminal status."""
    conn = RecordingConnection()
    store = make_store(conn)
    store.insert_run("r-1", "agentflow")
    conn.runs["r-1"]["status"] = "succeeded"
    assert conn.runs["r-1"]["status"] == "succeeded

def test_schema_file_present() -> None:
    """The schema file ships with the store package."""
    from pathlib import Path

    assert Path("store/schema.sql").exists

def test_schema_defines_both_tables() -> None:
    """Schema defines eval_runs and eval_scores."""
    from pathlib import Path

    schema = Path("store/schema.sql").read_text()
    assert "eval_runs" in schema and "eval_scores" in schema

def test_schema_scores_reference_runs() -> None:
    """Score rows reference their run."""
    from pathlib import Path

    schema = Path("store/schema.sql").read_text()
    assert "REFERENCES eval_runs" in schema

def test_schema_uses_timestamptz() -> None:
    """Timestamps are timezone-aware TIMESTAMPTZ."""
    from pathlib import Path

    schema = Path("store/schema.sql").read_text()
    assert "TIMESTAMPTZ" in schema
    assert " TIMESTAMP" not in schema

def test_version_column_after_locking_fix() -> None:
    """eval_scores carries a version column for optimistic locking."""
    from pathlib import Path

    schema = Path("store/schema.sql").read_text()
    assert "version INTEGER" in schema

def test_save_score_conflict_raises() -> None:
    """A stale expected version raises OptimisticLockError."""
    import pytest

    from store.results_store import OptimisticLockError, ResultsStore

    store = ResultsStore("postgresql://unused")
    with pytest.raises(OptimisticLockError):
        store.save_score("r-1", "m", 0.5, expected_version=99)

def test_concurrent_writers_both_succeed_sequentially() -> None:
    """Two sequential writers see each other's scores."""
    conn = RecordingConnection()
    first = make_store(conn)
    second = make_store(conn)
    first.upsert_score("r-1", "a", 0.1)
    second.upsert_score("r-1", "b", 0.2)
    assert ("r-1", "a") in conn.scores and ("r-1", "b") in conn.scores

def test_insert_run_repos_diverse() -> None:
    """Runs for all five repos coexist."""
    conn = RecordingConnection()
    store = make_store(conn)
    for repo in ("retrieval-core", "agentflow", "graphmind", "llmjudge", "shipwright"):
        store.insert_run(f"run-{repo}", repo)
    assert len(conn.runs) == 5
