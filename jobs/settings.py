#!/usr/bin/env python3
"""
settings.py --- queue settings shared by worker and enqueuers

Contains:
    QueueConfig: tunable knobs for the eval job queue
    load_queue_config(): builds a QueueConfig from environment variables
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class QueueConfig:
    """Holds tunable knobs for the eval job queue.

    Attributes:
        redis_url: Connection string for the Redis instance backing arq.
        job_timeout_s: Maximum wall-clock seconds one eval job may run.
        max_tries: Maximum attempts for a job before it is dead-lettered.
    """

    redis_url: str
    job_timeout_s: int
    max_tries: int


def load_queue_config() -> QueueConfig:
    """Builds a QueueConfig from environment variables.

    Returns:
        config: QueueConfig with defaults for any unset variable.
    """
    return QueueConfig(
        redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        queue_name=os.environ.get("EVAL_QUEUE_NAME", DEFAULT_QUEUE_NAME),
        job_timeout_s=int(os.environ.get("EVAL_JOB_TIMEOUT_S", "900")),
        max_tries=int(os.environ.get("EVAL_JOB_MAX_TRIES", "3")),
    )

def dead_letter_key(queue_name: str) -> str:
    """Derives the dead-letter queue key for a queue.

    Args:
        queue_name: Name of the primary queue.

    Returns:
        key: Redis key of the associated dead-letter queue.
    """
    return f"{queue_name}:dead"

DEFAULT_QUEUE_NAME = "llmjudge:eval"
