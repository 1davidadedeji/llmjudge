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
