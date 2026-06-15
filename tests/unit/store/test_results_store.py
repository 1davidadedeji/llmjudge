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
