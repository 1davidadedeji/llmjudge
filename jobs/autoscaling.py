#!/usr/bin/env python3
"""
autoscaling.py --- worker autoscaling policy for the eval job queue

Contains:
    AutoscalePolicy: min/max workers and scale thresholds
    desired_workers(): computes worker count from queue depth
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AutoscalePolicy:
    """Min/max workers and the queue-depth thresholds between them.

    Attributes:
        min_workers: Workers kept running even with an empty queue.
        max_workers: Upper bound on concurrent workers.
        scale_up_depth: Queue depth per worker that triggers scaling out.
        cooldown_s: Minimum seconds between scaling actions.
    """

    min_workers: int
    max_workers: int
    scale_up_depth: int
    cooldown_s: int


DEFAULT_POLICY = AutoscalePolicy(min_workers=1, max_workers=12, scale_up_depth=4, cooldown_s=120)


def desired_workers(queue_depth: int, policy: AutoscalePolicy = DEFAULT_POLICY) -> int:
    """Computes the worker count appropriate for the current queue depth.

    Args:
        queue_depth: Number of eval jobs currently waiting in the queue.
        policy: Autoscaling policy to apply.

    Returns:
        workers: Desired worker count, clamped to the policy bounds.
    """
    if queue_depth <= 0:
        return policy.min_workers
    wanted = (queue_depth + policy.scale_up_depth - 1) // policy.scale_up_depth
    return max(policy.min_workers, min(policy.max_workers, wanted))

def should_scale_up(queue_depth: int, current: int, policy: AutoscalePolicy = DEFAULT_POLICY) -> bool:
    """Reports whether the fleet should scale out.

    Args:
        queue_depth: Number of eval jobs currently waiting in the queue.
        current: Number of workers currently running.
        policy: Autoscaling policy to apply.

    Returns:
        scale_up: True when desired capacity exceeds current capacity.
    """
    return desired_workers(queue_depth, policy) > current

def should_scale_down(queue_depth: int, current: int, policy: AutoscalePolicy = DEFAULT_POLICY) -> bool:
    """Reports whether the fleet should scale in.

    Args:
        queue_depth: Number of eval jobs currently waiting in the queue.
        current: Number of workers currently running.
        policy: Autoscaling policy to apply.

    Returns:
        scale_down: True when current capacity exceeds desired capacity.
    """
    return desired_workers(queue_depth, policy) < current
