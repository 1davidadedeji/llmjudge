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

def test_is_passing_uses_threshold() -> None:
    """is_passing compares the score against the metric threshold."""
    from metrics.faithfulness import FaithfulnessMetric
    from metrics.judge import StubJudge

    metric = FaithfulnessMetric(StubJudge([]), threshold=0.8)
    assert metric.is_passing(0.8) and not metric.is_passing(0.7)

def test_registry_covers_core_metrics() -> None:
    """Registry contains the core metric names."""
    from metrics.registry import METRIC_REGISTRY

    assert "faithfulness" in METRIC_REGISTRY
    assert "hallucination" in METRIC_REGISTRY

def test_build_metric_unknown_raises() -> None:
    """Building an unregistered metric raises KeyError."""
    import pytest

    from metrics.registry import build_metric

    with pytest.raises(KeyError):
        build_metric("not-a-metric")

def test_score_band_mapping() -> None:
    """Score bands follow the documented cutoffs."""
    from metrics.base import score_band

    assert score_band(0.9) == "strong"
    assert score_band(0.6) == "ok"
    assert score_band(0.1) == "weak"

def test_metric_error_is_exception() -> None:
    """MetricError derives from Exception."""
    from metrics.base import MetricError

    assert issubclass(MetricError, Exception)

def test_registry_values_are_base_metrics() -> None:
    """Every registered class implements BaseMetric."""
    from metrics.base import BaseMetric
    from metrics.registry import METRIC_REGISTRY

    for cls in METRIC_REGISTRY.values():
        assert issubclass(cls, BaseMetric)

def test_describe_metric_renders_threshold() -> None:
    """Description includes the metric threshold."""
    from metrics.base import describe_metric
    from metrics.faithfulness import FaithfulnessMetric
    from metrics.judge import StubJudge

    text = describe_metric(FaithfulnessMetric(StubJudge([]), threshold=0.8))
    assert "faithfulness" in text and "0.8" in text

def test_all_registry_metrics_have_names() -> None:
    """Every registered metric class exposes a stable name."""
    from metrics.registry import METRIC_REGISTRY

    for key, cls in METRIC_REGISTRY.items():
        assert cls.name == key
