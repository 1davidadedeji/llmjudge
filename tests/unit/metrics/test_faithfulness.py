#!/usr/bin/env python3
"""
test_faithfulness.py --- unit tests for the faithfulness metric

Contains:
    test_all_claims_entailed_scores_one: grounded answer gets full marks
    test_no_claims_scores_one: empty answer is vacuously faithful
"""

from harness.test_case import LLMTestCase
from metrics.faithfulness import FaithfulnessMetric
from metrics.judge import StubJudge


def make_case(answer: str, context: list[str]) -> LLMTestCase:
    """Builds a minimal RAG test case.

    Args:
        answer: Generated answer text.
        context: Retrieved context passages.

    Returns:
        test_case: LLMTestCase wrapping the answer and context.
    """
    return LLMTestCase(input="q", actual_output=answer, retrieval_context=context)


def test_all_claims_entailed_scores_one() -> None:
    """Grounded answer gets a perfect faithfulness score."""
    metric = FaithfulnessMetric(StubJudge(["yes", "yes"]))
    case = make_case("The sky is blue. Water is wet.", ["The sky is blue and water is wet."])
    assert metric.measure(case) == 1.0


def test_no_claims_scores_one() -> None:
    """Empty answer is vacuously faithful."""
    metric = FaithfulnessMetric(StubJudge([]))
    assert metric.measure(make_case("", ["anything"])) == 1.0

def test_threshold_out_of_range_rejected() -> None:
    """Thresholds outside [0, 1] raise a ValueError."""
    import pytest

    with pytest.raises(ValueError):
        FaithfulnessMetric(StubJudge([]), threshold=1.5)

def test_half_claims_entailed() -> None:
    """Mixed verdicts yield a fractional score."""
    metric = FaithfulnessMetric(StubJudge(["yes", "no"]))
    case = make_case("The sky is blue. The moon is made of cheese.", ["The sky is blue."])
    assert metric.measure(case) == 0.5
