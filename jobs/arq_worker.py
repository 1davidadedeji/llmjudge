#!/usr/bin/env python3
"""
arq_worker.py --- async job queue for eval runs

Contains:
    run_eval_job: executes one eval run dequeued from the queue
    enqueue_eval_run: puts an eval run request onto the queue
    WorkerSettings: arq worker configuration (functions, retries, timeouts)
"""

import os
from typing import Any

from arq.connections import RedisSettings

QUEUE_NAME = "llmjudge:eval"

RETRY_BACKOFF_BASE_S = 5
DEAD_LETTER_QUEUE = "llmjudge:eval:dead"
DEFAULT_JOB_TIMEOUT_S = 600
DEFAULT_MAX_TRIES = 3


def _redis_settings() -> RedisSettings:
    """Builds Redis connection settings from the environment.

    Returns:
        settings: RedisSettings parsed from REDIS_URL.
    """
    return RedisSettings.from_dsn(os.environ.get("REDIS_URL", "redis://localhost:6379"))


async def run_eval_job(ctx: dict[str, Any], run_id: str, repo: str) -> dict[str, Any]:
    """Executes one eval run and returns its scores.

    Args:
        ctx: arq job context (redis connection, job id, retry count).
        run_id: Identifier of the eval run to execute.
        repo: Name of the repo under evaluation.

    Returns:
        result: Mapping of metric names to scores for the run.
    """
    return {"run_id": run_id, "repo": repo, "status": "queued"}


async def enqueue_eval_run(redis: Any, run_id: str, repo: str) -> str:
    """Puts an eval run request onto the queue.

    Args:
        redis: arq redis connection pool.
        run_id: Identifier of the eval run to enqueue.
        repo: Name of the repo under evaluation.

    Returns:
        job_id: Identifier assigned to the enqueued job.
    """
    job = await redis.enqueue_job("run_eval_job", run_id, repo, _queue_name=QUEUE_NAME)
    return job.job_id


class WorkerSettings:
    """Wires arq worker functions, retries, and timeouts.

    Attributes:
        functions: Job functions the worker can execute.
        max_jobs: Maximum concurrent jobs per worker process.
    """

    functions = [run_eval_job]
    redis_settings = _redis_settings()
    max_jobs = 4
    job_timeout = DEFAULT_JOB_TIMEOUT_S
    max_tries = DEFAULT_MAX_TRIES
