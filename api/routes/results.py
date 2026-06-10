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
def list_runs(repo: str | None = None, store: ResultsStore = Depends(get_store)) -> list[dict]:
    """Lists recent runs, optionally filtered by repo.

    Args:
        repo: Optional repo filter.
        store: Results store dependency.

    Returns:
        runs: Run rows newest-first.
    """
    return store.list_runs(repo=repo)


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
    return run


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
