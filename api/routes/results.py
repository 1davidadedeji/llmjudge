#!/usr/bin/env python3
"""
results.py --- routes for eval runs and their scores

Contains:
    router: APIRouter with the results endpoints
    list_runs(): lists recent runs, optionally filtered by repo
    get_run(): fetches one run with its scores
    create_run(): records a new eval run
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.deps import get_store
from store.results_store import ResultsStore

router = APIRouter(tags=["results"])


class RunCreate(BaseModel):
    """Request body for creating a run.

    Attributes:
        id: Unique run identifier.
        repo: Repo the run evaluates.
    """

    id: str
    repo: str


@router.get("/runs")
def list_runs(
    repo: str | None = None, limit: int = 50, store: ResultsStore = Depends(get_store)
) -> list[dict]:
    """Lists recent runs, optionally filtered by repo.

    Args:
        repo: Optional repo filter.
        store: Results store dependency.

    Returns:
        runs: Run rows newest-first.
    """
    return [serialize_run(run) for run in store.list_runs(repo=repo, limit=limit)]


@router.get("/runs/{run_id}")
def get_run(run_id: str, store: ResultsStore = Depends(get_store)) -> dict:
    """Fetches one run with its scores.

    Args:
        run_id: Run identifier.
        store: Results store dependency.

    Returns:
        run: Run payload with scores.
    """
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return serialize_run(run)


@router.post("/runs", status_code=201)
def create_run(body: RunCreate, store: ResultsStore = Depends(get_store)) -> dict:
    """Records a new eval run.

    Args:
        body: Run creation payload.
        store: Results store dependency.

    Returns:
        run: The created run payload.
    """
    store.insert_run(body.id, body.repo)
    return {"id": body.id, "repo": body.repo, "status": "queued"}

@router.post("/runs/{run_id}/scores", status_code=201)
def add_score(run_id: str, metric: str, score: float, store: ResultsStore = Depends(get_store)) -> dict:
    """Writes one metric score for a run.

    Args:
        run_id: Run the score belongs to.
        metric: Metric name.
        score: Metric score in [0, 1].
        store: Results store dependency.

    Returns:
        confirmation: The recorded score fields.
    """
    if not 0.0 <= score <= 1.0:
        raise HTTPException(status_code=422, detail="score must be in [0, 1]")
    store.upsert_score(run_id, metric, score)
    return {"run_id": run_id, "metric": metric, "score": score}

@router.get("/health")
def health() -> dict:
    """Reports API liveness.

    Returns:
        status: Static ok payload.
    """
    return {"status": "ok"}

def serialize_run(run: dict) -> dict:
    """Serializes a run payload with ISO-8601 UTC timestamps.

    Args:
        run: Run payload from the store.

    Returns:
        payload: Run payload with timestamps as ISO strings.
    """
    payload = dict(run)
    for field_name in ("created_at", "finished_at"):
        value = payload.get(field_name)
        if value is not None and hasattr(value, "isoformat"):
            payload[field_name] = value.isoformat().replace("+00:00", "Z")
    return payload

@router.get("/runs/{run_id}/scores")
def get_scores(run_id: str, store: ResultsStore = Depends(get_store)) -> dict:
    """Fetches just the scores mapping for a run.

    Args:
        run_id: Run identifier.
        store: Results store dependency.

    Returns:
        scores: Metric-score mapping for the run.
    """
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run["scores"]

@router.delete("/runs/{run_id}", status_code=204)
def delete_run(run_id: str, store: ResultsStore = Depends(get_store)) -> None:
    """Deletes a run and its scores.

    Args:
        run_id: Run identifier.
        store: Results store dependency.
    """
    if not store.delete_run(run_id):
        raise HTTPException(status_code=404, detail="run not found")

@router.get("/repos")
def list_repos(store: ResultsStore = Depends(get_store)) -> list[str]:
    """Lists repos that have at least one stored run.

    Args:
        store: Results store dependency.

    Returns:
        repos: Sorted distinct repo names.
    """
    return store.repos_with_runs()

@router.get("/metrics")
def list_metric_names() -> list[str]:
    """Lists the metric names the platform can score.

    Returns:
        names: Registered metric names.
    """
    from metrics.registry import METRIC_REGISTRY

    return sorted(METRIC_REGISTRY)

@router.get("/runs/{run_id}/summary")
def run_summary(run_id: str, store: ResultsStore = Depends(get_store)) -> dict:
    """Builds a compact summary of one run.

    Args:
        run_id: Run identifier.
        store: Results store dependency.

    Returns:
        summary: Repo, status, and score count for the run.
    """
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "id": run_id,
        "repo": run["repo"],
        "status": run["status"],
        "score_count": len(run["scores"]),
    }

@router.get("/repos/{repo}/latest")
def latest_run(repo: str, store: ResultsStore = Depends(get_store)) -> dict:
    """Fetches the most recent run for a repo.

    Args:
        repo: Repo whose latest run is wanted.
        store: Results store dependency.

    Returns:
        run: Newest run payload for the repo.
    """
    run = store.latest_run(repo)
    if run is None:
        raise HTTPException(status_code=404, detail="no runs for repo")
    return run
