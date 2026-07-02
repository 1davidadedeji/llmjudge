#!/usr/bin/env python3
"""
test_base.py --- unit tests for the shared metric interface

Contains:
    test_clamp_score_bounds: clamping keeps scores in range
"""

from metrics.base import clamp_score


def test_clamp_score_bounds() -> None:
    """Clamping bounds scores to [0, 1]."""
    assert clamp_score(1.4) == 1.0
    assert clamp_score(-0.2) == 0.0
    assert clamp_score(0.5) == 0.5

def test_clamp_preserves_boundary() -> None:
    """Clamp leaves exact boundary values alone."""
    assert clamp_score(0.0) == 0.0
    assert clamp_score(1.0) == 1.0

def test_base_metric_abstract() -> None:
    """BaseMetric cannot be instantiated directly."""
    import pytest

    from metrics.base import BaseMetric

    with pytest.raises(TypeError):
        BaseMetric()

def test_faithfulness_is_base_metric() -> None:
    """Faithfulness implements the shared interface."""
    from metrics.base import BaseMetric
    from metrics.faithfulness import FaithfulnessMetric
    from metrics.judge import StubJudge

    metric = FaithfulnessMetric(StubJudge([]))
    assert isinstance(metric, BaseMetric)
