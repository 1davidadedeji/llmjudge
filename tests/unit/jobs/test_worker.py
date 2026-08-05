#!/usr/bin/env python3
"""
test_worker.py --- unit tests for the arq eval worker

Contains:
    test_queue_name_stable: queue name constant does not drift
"""

from jobs.arq_worker import (
    QUEUE_NAME,
    RETRY_BACKOFF_BASE_S,
    describe_job,
    retry_backoff_s,
)


def test_queue_name_stable() -> None:
    """Queue name stays stable so enqueuers and workers agree."""
    assert QUEUE_NAME == "llmjudge:eval"

def test_retry_backoff_doubles_each_attempt() -> None:
    """Backoff doubles with each successive retry attempt."""
    assert retry_backoff_s(1) == RETRY_BACKOFF_BASE_S
    assert retry_backoff_s(2) == RETRY_BACKOFF_BASE_S * 2
    assert retry_backoff_s(3) == RETRY_BACKOFF_BASE_S * 4

def test_describe_job_format() -> None:
    """Job labels follow the eval:<repo>:<run> shape."""
    assert describe_job("r-1", "agentflow") == "eval:agentflow:r-1"

def test_queue_name_mentions_eval() -> None:
    """Queue name identifies the eval purpose in its label."""
    assert ":eval" in QUEUE_NAME
