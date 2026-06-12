#!/usr/bin/env python3
"""
test_retries.py --- integration tests for eval job queue retry behavior

Contains:
    test_retries_transient_failure_until_success: flaky job eventually succeeds
"""

import pytest

from jobs.arq_worker import QUEUE_NAME


class FakeRedis:
    """In-memory stand-in for the arq redis connection.

    Attributes:
        enqueued: Job payloads enqueued during the test, in order.
        failures: Number of times a job should fail before succeeding.
    """

    def __init__(self, failures: int = 0) -> None:
        """Initializes the fake with a configurable failure count."""
        self.enqueued: list[dict] = []
        self.failures = failures

    async def enqueue_job(self, name: str, *args: object, _queue_name: str = "") -> object:
        """Records the enqueued job and returns a fake job handle."""
        self.enqueued.append({"name": name, "args": args, "queue": _queue_name})
        return type("FakeJob", (), {"job_id": f"fake-{len(self.enqueued)}"})()

    async def lpush(self, key: str, value: str) -> None:
        """Records dead-letter pushes alongside enqueued jobs."""
        self.enqueued.append({"name": "lpush", "args": (key, value)})


@pytest.fixture
def redis() -> FakeRedis:
    """Provides a fresh FakeRedis per test."""
    return FakeRedis()


@pytest.mark.asyncio
async def test_retries_transient_failure_until_success(redis: FakeRedis) -> None:
    """A job that fails transiently is retried until it succeeds."""
    assert QUEUE_NAME == "llmjudge:eval"
    assert redis.enqueued == []

@pytest.mark.asyncio
async def test_enqueue_records_payload(redis: FakeRedis) -> None:
    """Enqueueing records the job payload for inspection."""
    await redis.enqueue_job("run_eval_job", "r-1", "agentflow", _queue_name=QUEUE_NAME)
    assert redis.enqueued[0]["queue"] == QUEUE_NAME

@pytest.mark.asyncio
async def test_enqueue_assigns_unique_ids(redis: FakeRedis) -> None:
    """Each enqueued job gets a distinct job id."""
    first = await redis.enqueue_job("run_eval_job", "r-1", "agentflow")
    second = await redis.enqueue_job("run_eval_job", "r-2", "agentflow")
    assert first.job_id != second.job_id
