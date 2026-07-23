#!/usr/bin/env python3
"""
test_results_store.py --- unit tests for the Postgres results store

Contains:
    FakeConnection: in-memory connection capturing executed statements
    test_insert_run_sql: insert_run issues the expected statement
"""

from store.results_store import ResultsStore


class FakeCursor:
    """In-memory cursor capturing executed statements.

    Attributes:
        statements: (sql, params) pairs executed so far.
    """

    def __init__(self) -> None:
        """Initializes empty capture state."""
        self.statements: list[tuple] = []
        self.rows: list[tuple] = []
        self.one: tuple | None = None

    def execute(self, sql: str, params: tuple = ()) -> "FakeCursor":
        """Captures the statement instead of executing it."""
        self.statements.append((sql, params))
        return self

    def fetchone(self) -> tuple | None:
        """Returns the canned single row."""
        return self.one

    def fetchall(self) -> list[tuple]:
        """Returns the canned row list."""
        return self.rows


class FakeConnection(FakeCursor):
    """Fake connection supporting the context-manager protocol."""

    def __enter__(self) -> "FakeConnection":
        """Returns itself as the context value."""
        return self

    def __exit__(self, *args: object) -> None:
        """Closes the fake without side effects."""


def make_store(conn: FakeConnection) -> ResultsStore:
    """Builds a ResultsStore wired to a fake connection.

    Args:
        conn: Fake connection to inject.

    Returns:
        store: ResultsStore using the fake.
    """
    store = ResultsStore("postgresql://unused")
    store.connect = lambda: conn  # type: ignore[method-assign]
    return store


def test_insert_run_sql() -> None:
    """insert_run issues an INSERT with the run fields."""
    conn = FakeConnection()
    make_store(conn).insert_run("r-1", "agentflow")
    sql, params = conn.statements[0]
    assert "INSERT INTO eval_runs" in sql
    assert params[:3] == ("r-1", "agentflow", "queued")

def test_upsert_score_sql() -> None:
    """upsert_score issues an upsert with the score fields."""
    conn = FakeConnection()
    make_store(conn).upsert_score("r-1", "faithfulness", 0.9)
    sql, params = conn.statements[0]
    assert "ON CONFLICT" in sql
    assert params[:3] == ("r-1", "faithfulness", 0.9)

def test_list_runs_filters_by_repo() -> None:
    """list_runs adds a WHERE clause only when a repo filter is given."""
    conn = FakeConnection()
    make_store(conn).list_runs(repo="graphmind")
    sql, params = conn.statements[0]
    assert "WHERE repo = %s" in sql
    assert params[0] == "graphmind"

def test_list_runs_no_filter() -> None:
    """list_runs without a repo lists everything."""
    conn = FakeConnection()
    make_store(conn).list_runs()
    sql, _ = conn.statements[0]
    assert "WHERE" not in sql

def test_ensure_utc_naive() -> None:
    """Naive timestamps are coerced to aware UTC."""
    from datetime import datetime, timezone

    from store.results_store import ensure_utc

    naive = datetime(2026, 6, 19, 12, 0, 0)
    assert ensure_utc(naive).tzinfo == timezone.utc

def test_finish_run_updates_status() -> None:
    """finish_run sets status and finished_at."""
    conn = FakeConnection()
    make_store(conn).finish_run("r-1", "succeeded")
    sql, params = conn.statements[0]
    assert "UPDATE eval_runs" in sql
    assert params[0] == "succeeded"
    assert params[2] == "r-1"

def test_get_run_missing_returns_none() -> None:
    """get_run returns None for an unknown run id."""
    conn = FakeConnection()
    assert make_store(conn).get_run("nope") is None

def test_get_run_assembles_scores() -> None:
    """get_run merges the scores rows into a mapping."""
    conn = FakeConnection()
    conn.one = ("r-1", "agentflow", "succeeded", None, None)
    conn.rows = [("faithfulness", 0.9), ("hallucination", 1.0)]
    run = make_store(conn).get_run("r-1")
    assert run["scores"] == {"faithfulness": 0.9, "hallucination": 1.0}

def test_metric_history_joins_runs() -> None:
    """metric_history joins scores to runs and filters by repo+metric."""
    conn = FakeConnection()
    make_store(conn).metric_history("agentflow", "faithfulness")
    sql, params = conn.statements[0]
    assert "JOIN eval_runs" in sql
    assert params[:2] == ("agentflow", "faithfulness")

def test_optimistic_lock_error_raised_on_stale_version() -> None:
    """save_score refuses to write over a newer version."""
    import pytest

    from store.results_store import OptimisticLockError, ResultsStore

    store = ResultsStore("postgresql://unused")
    with pytest.raises(OptimisticLockError):
        store.save_score("r-1", "faithfulness", 0.9, expected_version=3)

def test_ensure_utc_already_aware() -> None:
    """Aware timestamps pass through ensure_utc unchanged."""
    from datetime import datetime, timezone

    from store.results_store import ensure_utc

    aware = datetime(2026, 7, 21, 8, 0, 0, tzinfo=timezone.utc)
    assert ensure_utc(aware) == aware

def test_scores_for_runs_empty() -> None:
    """scores_for_runs short-circuits on an empty id list."""
    conn = FakeConnection()
    assert make_store(conn).scores_for_runs([]) == {}
    assert conn.statements == []

def test_average_score_window() -> None:
    """average_score bounds the window with an interval clause."""
    conn = FakeConnection()
    make_store(conn).average_score("agentflow", "faithfulness", days=3)
    sql, params = conn.statements[0]
    assert "INTERVAL" in sql
    assert params == ("agentflow", "faithfulness", 3)
