#!/usr/bin/env python3
"""
compare.py --- run comparison endpoint

Contains:
    router: APIRouter with the comparison endpoint
    compare_runs(): diffs two runs' scores per metric
    score_deltas(): computes per-metric score deltas
    find_regressions(): lists metrics that regressed past a tolerance
"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_store
from store.results_store import ResultsStore

router = APIRouter(prefix="/compare", tags=["compare"])

REGRESSION_TOLERANCE = 0.01


def score_deltas(base: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    """Computes per-metric score deltas between two runs.

    Args:
        base: Scores from the base run.
        candidate: Scores from the candidate run.

    Returns:
        deltas: candidate minus base for metrics present in both.
    """
    shared = set(base) & set(candidate)
    return {metric: candidate[metric] - base[metric] for metric in sorted(shared)}


def find_regressions(
    deltas: dict[str, float], tolerance: float = REGRESSION_TOLERANCE
) -> list[str]:
    """Lists metrics that regressed past the tolerance.

    Args:
        deltas: Per-metric deltas from score_deltas().
        tolerance: Negative delta magnitude that counts as a regression.

    Returns:
        regressions: Metric names whose delta is below -tolerance.
    """
    return [metric for metric, delta in deltas.items() if delta < -tolerance]


@router.get("/{base_run}/{candidate_run}")
def compare_runs(
    base_run: str, candidate_run: str, store: ResultsStore = Depends(get_store)
) -> dict:
    """Diffs two runs' scores per metric.

    Args:
        base_run: Run id of the baseline.
        candidate_run: Run id of the candidate.
        store: Results store dependency.

    Returns:
        comparison: Per-metric deltas and the regression list.
    """
    base = store.get_run(base_run)
    candidate = store.get_run(candidate_run)
    if base is None or candidate is None:
        raise HTTPException(status_code=404, detail="run not found")
    deltas = score_deltas(base["scores"], candidate["scores"])
    return {
        "base": base_run,
        "candidate": candidate_run,
        "deltas": deltas,
        "regressions": find_regressions(deltas),
        "improvements": improvements(deltas),
    }

def summarize(deltas: dict[str, float]) -> str:
    """Builds a one-line summary of score deltas.

    Args:
        deltas: Per-metric deltas from score_deltas().

    Returns:
        summary: Compact delta listing for logs and PR comments.
    """
    if not deltas:
        return "no shared metrics"
    return ", ".join(f"{metric} {delta:+.3f}" for metric, delta in deltas.items())

def improvements(deltas: dict[str, float], tolerance: float = REGRESSION_TOLERANCE) -> list[str]:
    """Lists metrics that improved past the tolerance.

    Args:
        deltas: Per-metric deltas from score_deltas().
        tolerance: Positive delta magnitude that counts as an improvement.

    Returns:
        improved: Metric names whose delta exceeds +tolerance.
    """
    return [metric for metric, delta in deltas.items() if delta > tolerance]
