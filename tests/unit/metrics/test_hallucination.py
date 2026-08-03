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

def test_three_claims_one_contradicted() -> None:
    """One contradiction in three claims scores 0.667."""
    metric = HallucinationMetric(StubJudge(["no", "yes", "no"]))
    assert abs(metric.measure(make_case("A. B. C.", ["ctx"])) - 2 / 3) < 1e-9

def test_prompt_contains_claim() -> None:
    """Contradiction prompt embeds the claim being judged."""
    judge = StubJudge(["no"])
    HallucinationMetric(judge).measure(make_case("unique-claim-text.", ["ctx"]))
    assert "unique-claim-text." in judge.calls[0]

def test_empty_answer_scores_one() -> None:
    """Empty answer hallucinates nothing."""
    assert HallucinationMetric(StubJudge([])).measure(make_case("", ["ctx"])) == 1.0

def test_falls_back_to_retrieval_context() -> None:
    """Retrieval context is used when context is empty."""
    judge = StubJudge(["yes"])
    metric = HallucinationMetric(judge)
    case = LLMTestCase(input="q", actual_output="A.", retrieval_context=["retrieved"])
    assert metric.measure(case) == 0.0
    assert "retrieved" in judge.calls[0]

def test_context_preferred_over_retrieval() -> None:
    """Explicit context wins over retrieval context."""
    judge = StubJudge(["no"])
    metric = HallucinationMetric(judge)
    case = LLMTestCase(input="q", actual_output="A.", context=["explicit"], retrieval_context=["r"])
    metric.measure(case)
    assert "explicit" in judge.calls[0]

def test_verdict_case_insensitive() -> None:
    """Verdict parsing ignores casing."""
    metric = HallucinationMetric(StubJudge(["YES"]))
    assert metric.is_contradicted("c", "ctx")

def test_threshold_default() -> None:
    """Default threshold is 0.9."""
    assert HallucinationMetric(StubJudge([])).threshold == 0.9

def test_measure_returns_float() -> None:
    """Hallucination score is a plain float."""
    metric = HallucinationMetric(StubJudge(["no"]))
    assert isinstance(metric.measure(make_case("A.", ["ctx"])), float)

def test_metric_name_stable() -> None:
    """Metric name is the stable registry key."""
    assert HallucinationMetric.name == "hallucination"

def test_extract_claims_basic() -> None:
    """Claim extraction splits sentences."""
    metric = HallucinationMetric(StubJudge([]))
    assert metric.extract_claims("A. B? C!") == ["A.", "B?", "C!"]

def test_score_bounded() -> None:
    """Score stays within [0, 1]."""
    metric = HallucinationMetric(StubJudge(["yes"] * 4))
    score = metric.measure(make_case("A. B. C. D.", ["ctx"]))
    assert 0.0 <= score <= 1.0

def test_single_claim_contradicted() -> None:
    """One contradicted claim on a one-claim answer scores zero."""
    metric = HallucinationMetric(StubJudge(["yes"]))
    assert metric.measure(make_case("Solo.", ["ctx"])) == 0.0

def test_hallucination_rate_inverse() -> None:
    """Rate is the complement of the score."""
    from metrics.hallucination import hallucination_rate

    assert hallucination_rate(0.75) == 0.25

def test_prompt_version_pinned() -> None:
    """Prompt version is pinned for attributable score changes."""
    from metrics.hallucination import CONTRADICTION_PROMPT_VERSION

    assert CONTRADICTION_PROMPT_VERSION == 1

def test_contradicted_claims_filtered() -> None:
    """Only verdict-flagged claims are returned."""
    from metrics.hallucination import contradicted_claims

    assert contradicted_claims(["a", "b"], [False, True]) == ["b"]

def test_five_claims_two_contradicted() -> None:
    """Two contradictions in five claims score 0.6."""
    metric = HallucinationMetric(StubJudge(["yes", "no", "yes", "no", "no"]))
    assert abs(metric.measure(make_case("A. B. C. D. E.", ["ctx"])) - 0.6) < 1e-9

def test_judge_call_count_matches_claims() -> None:
    """One judge call per claim."""
    judge = StubJudge(["no"] * 3)
    HallucinationMetric(judge).measure(make_case("A. B. C.", ["ctx"]))
    assert len(judge.calls) == 3
