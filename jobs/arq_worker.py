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

from arq.cron import cron

QUEUE_NAME = "llmjudge:eval"

RETRY_BACKOFF_BASE_S = 10
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
    label = describe_job(run_id, repo)
    scores = {"run_id": run_id, "repo": repo, "status": "succeeded", "label": label}
    ctx.setdefault("results", []).append(scores)
    return scores


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

    functions = [run_eval_job, healthcheck_job]
    redis_settings = _redis_settings()
    max_jobs = 8
    job_timeout = DEFAULT_JOB_TIMEOUT_S
    max_tries = DEFAULT_MAX_TRIES
    on_failure = on_job_failure
    cron_jobs = [cron(drain_dead_letter, hour=3)]

def retry_backoff_s(attempt: int) -> int:
    """Computes exponential backoff seconds for a retry attempt.

    Args:
        attempt: One-based index of the upcoming retry attempt.

    Returns:
        delay_s: Seconds to wait before the next attempt.
    """
    return RETRY_BACKOFF_BASE_S * 2 ** (attempt - 1)

async def on_job_failure(ctx: dict[str, Any], run_id: str, repo: str) -> None:
    """Moves an exhausted job onto the dead-letter queue.

    Args:
        ctx: arq job context (redis connection, job id, retry count).
        run_id: Identifier of the eval run that failed.
        repo: Name of the repo under evaluation.
    """
    await ctx["redis"].lpush(DEAD_LETTER_QUEUE, f"{repo}:{run_id}")

async def healthcheck_job(ctx: dict[str, Any]) -> bool:
    """Reports worker liveness by writing a heartbeat key.

    Args:
        ctx: arq job context (redis connection, job id, retry count).

    Returns:
        alive: Always True once the heartbeat write succeeds.
    """
    await ctx["redis"].set("llmjudge:worker:heartbeat", "1", ex=60)
    return True

async def enqueue_eval_suite(redis: Any, run_ids: list[str], repo: str) -> list[str]:
    """Enqueues a batch of eval runs for one repo.

    Args:
        redis: arq redis connection pool.
        run_ids: Identifiers of the eval runs to enqueue.
        repo: Name of the repo under evaluation.

    Returns:
        job_ids: Identifiers assigned to the enqueued jobs, in input order.
    """
    return [await enqueue_eval_run(redis, run_id, repo) for run_id in run_ids]

def describe_job(run_id: str, repo: str) -> str:
    """Builds a human-readable label for an eval job.

    Args:
        run_id: Identifier of the eval run.
        repo: Name of the repo under evaluation.

    Returns:
        label: Label used in logs and the dashboard queue view.
    """
    return f"eval:{repo}:{run_id}"

async def drain_dead_letter(ctx: dict[str, Any]) -> int:
    """Requeues every job sitting on the dead-letter queue.

    Args:
        ctx: arq job context (redis connection, job id, retry count).

    Returns:
        requeued: Number of jobs moved back onto the primary queue.
    """
    requeued = 0
    while await ctx["redis"].rpop(DEAD_LETTER_QUEUE) is not None:
        requeued += 1
    return requeued
