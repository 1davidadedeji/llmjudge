#!/usr/bin/env python3
"""
test_autoscaling.py --- unit tests for worker autoscaling policy

Contains:
    test_desired_workers_empty_queue: empty queue keeps the minimum
    test_desired_workers_scales_with_depth: deeper queue wants more workers
"""

from jobs.autoscaling import DEFAULT_POLICY, desired_workers, should_scale_up


def test_desired_workers_empty_queue() -> None:
    """Empty queue keeps the minimum worker count."""
    assert desired_workers(0) == DEFAULT_POLICY.min_workers


def test_desired_workers_scales_with_depth() -> None:
    """Deeper queue requests proportionally more workers."""
    assert desired_workers(4) == 1
    assert desired_workers(5) == 2


def test_desired_workers_capped_at_max() -> None:
    """Desired count never exceeds the policy maximum."""
    assert desired_workers(10_000) == DEFAULT_POLICY.max_workers


def test_should_scale_up() -> None:
    """Scale-up signal fires only when desired exceeds current."""
    assert should_scale_up(50, 2)
    assert not should_scale_up(1, 8)

def test_should_scale_down() -> None:
    """Scale-in signal fires only when current exceeds desired."""
    assert should_scale_down(0, 4)
    assert not should_scale_down(50, 2)
