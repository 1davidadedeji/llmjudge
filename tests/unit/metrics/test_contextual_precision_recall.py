#!/usr/bin/env python3
"""
test_contextual_precision_recall.py --- unit tests for retrieval quality metrics

Contains:
    test_precision_perfect_ranking: all-relevant ranking scores one
    test_recall_full_coverage: fully supported expectation scores one
"""

from harness.test_case import LLMTestCase
from metrics.contextual_precision_recall import ContextualPrecisionMetric, ContextualRecallMetric
from metrics.judge import StubJudge


def make_case(passages: list[str], expected: str | None = None) -> LLMTestCase:
    """Builds a retrieval test case.

    Args:
        passages: Ranked retrieved passages.
        expected: Expected answer text, if any.

    Returns:
        test_case: LLMTestCase wrapping the retrieval data.
    """
    return LLMTestCase(
        input="q", actual_output="a", expected_output=expected, retrieval_context=passages
    )


def test_precision_perfect_ranking() -> None:
    """All-relevant ranking scores a perfect precision."""
    metric = ContextualPrecisionMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case(["p1", "p2"])) == 1.0


def test_recall_full_coverage() -> None:
    """Fully supported expectation scores a perfect recall."""
    metric = ContextualRecallMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case(["p1", "p2"], expected="exp")) == 1.0
