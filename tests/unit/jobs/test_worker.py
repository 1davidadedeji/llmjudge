#!/usr/bin/env python3
"""
test_worker.py --- unit tests for the arq eval worker

Contains:
    test_queue_name_stable: queue name constant does not drift
"""

from jobs.arq_worker import QUEUE_NAME


def test_queue_name_stable() -> None:
    """Queue name stays stable so enqueuers and workers agree."""
    assert QUEUE_NAME == "llmjudge:eval"
