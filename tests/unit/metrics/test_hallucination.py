#!/usr/bin/env python3
"""
test_hallucination.py --- unit tests for the hallucination metric

Contains:
    test_no_contradictions_scores_one: clean answer gets full marks
    test_all_contradicted_scores_zero: fully hallucinated answer scores zero
"""

from harness.test_case import LLMTestCase
from metrics.hallucination import HallucinationMetric
from metrics.judge import StubJudge


def make_case(answer: str, context: list[str]) -> LLMTestCase:
    """Builds a test case with reference context.

    Args:
        answer: Generated answer text.
        context: Reference context passages.

    Returns:
        test_case: LLMTestCase wrapping the answer and context.
    """
    return LLMTestCase(input="q", actual_output=answer, context=context)


def test_no_contradictions_scores_one() -> None:
    """Clean answer gets a perfect score."""
    metric = HallucinationMetric(StubJudge(["no", "no"]))
    assert metric.measure(make_case("A. B.", ["ctx"])) == 1.0


def test_all_contradicted_scores_zero() -> None:
    """Fully hallucinated answer scores zero."""
    metric = HallucinationMetric(StubJudge(["yes", "yes"]))
    assert metric.measure(make_case("A. B.", ["ctx"])) == 0.0

def test_partial_contradiction() -> None:
    """Some contradicted claims yield a fractional score."""
    metric = HallucinationMetric(StubJudge(["no", "yes"]))
    assert metric.measure(make_case("A. B.", ["ctx"])) == 0.5
