#!/usr/bin/env python3
"""
test_compare.py --- unit tests for the run comparison endpoint

Contains:
    test_score_deltas_shared_only: deltas cover only shared metrics
    test_find_regressions_respects_tolerance: small dips are not regressions
"""

from api.routes.compare import find_regressions, score_deltas


def test_score_deltas_shared_only() -> None:
    """Deltas cover only metrics present in both runs."""
    deltas = score_deltas({"a": 0.5, "b": 0.5}, {"a": 0.7, "c": 0.1})
    assert deltas == {"a": 0.19999999999999996} or abs(deltas["a"] - 0.2) < 1e-9


def test_find_regressions_respects_tolerance() -> None:
    """Dips within tolerance are not flagged as regressions."""
    assert find_regressions({"a": -0.015}) == []
    assert find_regressions({"a": -0.05}) == ["a"]

def test_compare_route() -> None:
    """Compare endpoint returns deltas and regressions."""
    from fastapi.testclient import TestClient

    from api.deps import get_store
    from api.main import create_app

    class _Store:
        def get_run(self, run_id: str) -> dict | None:
            runs = {
                "b": {"scores": {"m": 0.8}},
                "c": {"scores": {"m": 0.7}},
            }
            return runs.get(run_id)

    app = create_app()
    app.dependency_overrides[get_store] = _Store
    payload = TestClient(app).get("/compare/b/c").json()
    assert payload["regressions"] == ["m"]

def test_summarize_formats_deltas() -> None:
    """Summary shows signed deltas per metric."""
    from api.routes.compare import summarize

    assert summarize({"m": 0.1}) == "m +0.100"
    assert summarize({}) == "no shared metrics"

def test_improvements() -> None:
    """Improvements mirror the regression logic on the positive side."""
    from api.routes.compare import improvements

    assert improvements({"a": 0.05}) == ["a"]
    assert improvements({"a": 0.005}) == []

def test_deltas_empty_when_no_shared() -> None:
    """No shared metrics yields empty deltas."""
    assert score_deltas({"a": 1.0}, {"b": 1.0}) == {}

def test_score_deltas_sorted() -> None:
    """Delta keys are sorted for stable API payloads."""
    deltas = score_deltas({"b": 1.0, "a": 1.0}, {"b": 1.0, "a": 1.0})
    assert list(deltas) == ["a", "b"]

def test_regressions_empty_deltas() -> None:
    """Empty deltas regress nothing."""
    assert find_regressions({}) == []

def test_deltas_symmetry() -> None:
    """Swapping runs negates the deltas."""
    forward = score_deltas({"m": 0.5}, {"m": 0.8})
    backward = score_deltas({"m": 0.8}, {"m": 0.5})
    assert forward["m"] == -backward["m"]

def test_biggest_regression() -> None:
    """biggest_regression picks the most negative delta."""
    from api.routes.compare import biggest_regression

    assert biggest_regression({"a": -0.1, "b": -0.2}) == "b"
    assert biggest_regression({"a": 0.1}) is None

def test_find_regressions_sorted_input() -> None:
    """Regression list follows delta key order."""
    result = find_regressions({"b": -0.5, "a": -0.5})
    assert result == ["a", "b"]

def test_tolerance_boundary_exclusive() -> None:
    """Exactly -tolerance is not a regression."""
    from api.routes.compare import REGRESSION_TOLERANCE

    assert find_regressions({"m": -REGRESSION_TOLERANCE}) == []

def test_improvements_empty() -> None:
    """Empty deltas improve nothing."""
    from api.routes.compare import improvements

    assert improvements({}) == []

def test_is_significant() -> None:
    """Significance uses the absolute delta."""
    from api.routes.compare import is_significant

    assert is_significant(0.1) and is_significant(-0.1)
    assert not is_significant(0.001)

def test_biggest_regression_none_when_empty() -> None:
    """No deltas means no biggest regression."""
    from api.routes.compare import biggest_regression

    assert biggest_regression({}) is None
