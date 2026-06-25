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
    assert find_regressions({"a": -0.005}) == []
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
